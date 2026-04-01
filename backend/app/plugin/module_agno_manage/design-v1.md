# AI 管理平台设计文档 v1

基于 Agno 框架，用 FastAPI + PostgreSQL（asyncpg）构建的综合 AI 资源管理平台。

---

## 一、架构设计

### 1.1 分层架构

```
┌─────────────────────────────────────────────────┐
│           管理层  /management/*                   │
│   FastAPI CRUD API  ←→  ag_* 表            │
└──────────────────┬──────────────────────────────┘
                   │ 启动/动态创建时 Hydrate
┌──────────────────▼──────────────────────────────┐
│           RuntimeRegistry（内存单例）              │
│   agents[] / model_cache / knowledge_cache(LRU) │
└──────────────────┬──────────────────────────────┘
                   │ base_app 共享同一 FastAPI 实例
┌──────────────────▼──────────────────────────────┐
│           AgentOS（直接复用，不重写）               │
│   /agents/{id}/runs  /sessions  /memory  ...    │
└──────────────────┬──────────────────────────────┘
                   │ 持久化运行时数据
┌──────────────────▼──────────────────────────────┐
│           Agno 原生表（只读，不修改）               │
│   agno_sessions / agno_user_memory / agno_traces│
└─────────────────────────────────────────────────┘
```

**四层职责：**
- **管理层**：你负责的部分，CRUD ag_* 表，暴露 /management/* 路由
- **RuntimeRegistry**：内存单例，把 DB 配置翻译成活的 Agno 对象
- **AgentOS**：Agno 内置 FastAPI，直接复用所有运行时路由
- **Agno 原生表**：Agno 自动管理，不要手动操作

### 1.2 两个核心机制

**机制一：Callable Factory（热插拔）**

```python
agent = Agent(
    tools=lambda: resolve_tools(agent_id),      # 每次 run() 时动态读取
    knowledge=lambda: resolve_knowledge(agent_id),
    cache_callables=False,   # ⚠️ 必须关闭，否则绑定变更对有 session 的用户不生效
)
# 只改 ag_bindings 表，下次 run 自动生效，无需重建 Agent 实例
```

**机制二：共享可变列表（动态注册）**

```python
agent_pool: List[Agent] = []
os_app = AgentOS(base_app=app, agents=agent_pool)  # 传引用

# 动态创建后 append，AgentOS 路由立即可发现
agent_pool.append(new_agent)
```

### 1.3 技术选型

| 层 | 技术 |
|----|------|
| Web 框架 | FastAPI（与 AgentOS 共享同一实例） |
| 数据库 | PostgreSQL + asyncpg（SQLAlchemy async） |
| 认证 | AgentOS 内置 JWT（`authorization=True`） |
| 内存管理 | 冷热分层 + LRU 淘汰（MCP/Knowledge） |
| 渠道集成 | AgentOS interfaces（Slack/Telegram/WhatsApp/AgUI） |

### 1.4 内存冷热策略

| 对象 | 策略 | 理由 |
|------|------|------|
| Agent / Model / Toolkit | 热区，全量常驻 | 纯 Python 对象，极轻 |
| Knowledge (pgvector) | 常驻 + 共享 engine | 同一连接池 |
| Knowledge (外部) | LRU maxsize=50 | 外部连接按需 |
| MCP HTTP | LRU maxsize=30 | 轻量 |
| MCP stdio | LRU maxsize=10 | 每个持有子进程 |

---

## 二、与 Agno 的交互流程

### 2.1 启动流程

```
应用启动
  │
  ├─ lifespan 开始
  │   ├─ 初始化 AsyncPostgresDb（Agno DB）
  │   ├─ 初始化 SQLAlchemy engine（管理层 DB）
  │   ├─ 创建 RuntimeRegistry
  │   ├─ 按序预热：
  │   │   models → embedders → vectordbs
  │   │   → knowledge → mcp → toolkits → agents → teams
  │   └─ registry.agents 列表已就绪
  │
  ├─ AgentOS(base_app=app, agents=registry.agents)
  │   ├─ 把 /agents/{id}/runs 等路由挂到 app
  │   ├─ 启动调度器 poller
  │   └─ 初始化 agno_* 原生表
  │
  └─ 应用就绪，接受请求
```

### 2.2 运行时热插拔流程

```
管理员操作：给 agent_1 关闭 knowledge_b
  │
  ├─ PATCH /management/agents/agent_1/bindings/knowledge_b
  │   body: {"enabled": false}
  │
  ├─ BindingService → BindingRepo.set_enabled(...)
  │   UPDATE ag_bindings SET enabled=false
  │
  ├─ 无需重建 Agent 实例（cache_callables=False）
  │
  └─ 用户下次请求 POST /agents/agent_1/runs
      │
      └─ Agno 调用 knowledge=lambda: resolve_knowledge('agent_1')
          │
          └─ _resolve_knowledge() 查 ag_bindings
              → enabled=false → 不返回 knowledge_b ✓
```

### 2.3 完整案例：动态创建 Agent 并调用

```
1. POST /management/models
   body: {name:"gpt4o", provider:"openai", model_id:"gpt-4o", api_key:"sk-xxx"}
   → DB 写 ag_models
   → registry.register_model(id, row)

2. POST /management/toolkits
   body: {name:"搜索工具", module_path:"agno.tools.duckduckgo", class_name:"DuckDuckGoTools"}
   → DB 写 ag_toolkits
   → registry.register_toolkit(id, row)

3. POST /management/agents  ← 创建时直接绑定，一次请求搞定
   body: {
     name:"搜索助手", model_id:"<model_uuid>", instructions:"你是一个搜索助手",
     tool_ids: ["<toolkit_uuid>"],          ← 创建时同步写 ag_bindings
     knowledge_ids: ["<knowledge_uuid>"],
     mcp_ids: [], hook_ids: [], guardrail_ids: []
   }
   → 事务内：DB 写 ag_agents + ag_bindings
   → registry.create_agent(row)  ← agent_pool.append(agent)
   → AgentOS 立即可路由

4. POST /agents/<id>/runs  （AgentOS 路由，非管理路由）
   body: {message:"搜索最新 AI 新闻", user_id:"user_123"}
   → Agno 执行，tools=lambda 返回 DuckDuckGoTools
   → 流式返回结果

-- 运行后热插拔（无需重建 Agent）--

5. PATCH /management/agents/<id>/bindings/<toolkit_uuid>
   body: {enabled: false}
   → UPDATE ag_bindings SET enabled=false
   → 下次 run 自动生效，toolkit 不再被调用
```

---

## 三、后端模块模板

每个模块的目录结构：

```
modules/<module_name>/
├── model.py      # SQLAlchemy ORM 表定义
├── schemas.py    # Pydantic 请求/响应模型
├── repo.py       # 纯 DB 操作（不感知 Agno）
├── service.py    # 业务逻辑（唯一调用 registry 的层）
└── router.py     # HTTP 路由（只管参数/响应/状态码）
```

**层次原则：**
- `router` → 调 `service`，不直接碰 DB 和 registry
- `service` → 调 `repo`（DB）+ `registry`（运行时），协调两者
- `repo` → 只管 SQL，零 Agno 知识
- `registry` → 只管运行时对象，零 DB 知识

---

## 四、公共基础设施

### core/db.py

```python
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
import os

DATABASE_URL = os.environ["DATABASE_URL"]  # postgresql+asyncpg://...

engine = create_async_engine(DATABASE_URL, echo=False, pool_size=10, max_overflow=20)
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)


class Base(DeclarativeBase):
    pass
```

### core/deps.py

```python
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession
from core.db import AsyncSessionLocal
from core.registry import RuntimeRegistry

_registry: RuntimeRegistry | None = None


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session


def get_registry() -> RuntimeRegistry:
    assert _registry is not None
    return _registry
```

### core/sync_db.py（同步 DB，供 callable factory 使用）

```python
"""
callable factory 在 Agno run() 时同步调用，无法使用 async SQLAlchemy。
SyncBindingRepo 使用独立的同步连接池（psycopg2），专门供 resolve_* 使用。
"""
import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

_sync_engine = create_engine(
    os.environ["DATABASE_URL"].replace("+asyncpg", ""),  # 转为同步 URL
    pool_size=5, max_overflow=10
)
SyncSession = sessionmaker(bind=_sync_engine)


class SyncBindingRepo:
    @staticmethod
    def get_active(owner_id: str, owner_type: str = "agent", resource_type: str | None = None):
        """
        同步查询 ag_bindings，返回 enabled=true 的绑定行。
        在 callable factory（resolve_tools/resolve_knowledge 等）中调用。
        """
        sql = """
            SELECT resource_type, resource_id::text
            FROM ag_bindings
            WHERE owner_id = :owner_id
              AND owner_type = :owner_type
              AND enabled = true
        """
        params = {"owner_id": owner_id, "owner_type": owner_type}
        if resource_type:
            sql += " AND resource_type = :resource_type"
            params["resource_type"] = resource_type

        with SyncSession() as session:
            rows = session.execute(text(sql), params).fetchall()

        # 返回轻量 namedtuple-like 对象
        from collections import namedtuple
        Binding = namedtuple("Binding", ["resource_type", "resource_id"])
        return [Binding(r.resource_type, r.resource_id) for r in rows]
```

class SyncTeamMemberRepo:
    @staticmethod
    def get_active(team_id: str):
        """同步查询 ag_team_members，返回 enabled=true 的成员行（按 member_order 排序）。"""
        sql = """
            SELECT member_id::text, member_type, member_order, role
            FROM ag_team_members
            WHERE team_id = :team_id AND enabled = true
            ORDER BY member_order
        """
        with SyncSession() as session:
            rows = session.execute(text(sql), {"team_id": team_id}).fetchall()
        from collections import namedtuple
        Member = namedtuple("Member", ["member_id", "member_type", "member_order", "role"])
        return [Member(r.member_id, r.member_type, r.member_order, r.role) for r in rows]
```

> **为什么需要同步 DB**：Agno 的 callable factory 通过 `invoke_callable_factory()` 同步调用，无法 await。因此 resolve_tools / resolve_knowledge 必须走同步查询。使用独立连接池（psycopg2），与主 asyncpg 连接池隔离。

---

### core/registry.py

```python
from collections import OrderedDict
from typing import Dict, List, Optional
import os


class LRUCache:
    def __init__(self, maxsize: int):
        self.maxsize = maxsize
        self._cache: OrderedDict = OrderedDict()

    def get(self, key: str):
        if key in self._cache:
            self._cache.move_to_end(key)
            return self._cache[key]
        return None

    def set(self, key: str, value):
        if key in self._cache:
            self._cache.move_to_end(key)
        else:
            if len(self._cache) >= self.maxsize:
                _, evicted = self._cache.popitem(last=False)
                if hasattr(evicted, "close"):
                    try:
                        evicted.close()
                    except Exception:
                        pass
        self._cache[key] = value

    def pop(self, key: str):
        return self._cache.pop(key, None)

    def remove(self, key: str) -> None:
        """驱逐指定 key，触发 close() 回调（如 MCP subprocess）"""
        obj = self._cache.pop(key, None)
        if obj is not None and hasattr(obj, "close"):
            try:
                obj.close()
            except Exception:
                pass

    def clear(self) -> None:
        """清空所有缓存，对每个有 close 方法的对象调用 close()"""
        for obj in self._cache.values():
            if hasattr(obj, "close"):
                try:
                    obj.close()
                except Exception:
                    pass
        self._cache.clear()


class RuntimeRegistry:
    def __init__(self):
        # ── 运行时实例（热区，AgentOS 直接引用） ────────────────
        self.agents: List = []
        self.teams: List = []
        self.workflows: List = []
        self._agents_map: Dict[str, object] = {}
        self._teams_map: Dict[str, object] = {}
        self._workflows_map: Dict[str, object] = {}
        # ── 构建好的对象缓存 ─────────────────────────────────────
        self._model_cache: Dict[str, object] = {}
        self._embedder_cache: Dict[str, object] = {}
        self._toolkit_map: Dict[str, object] = {}
        self._hook_map: Dict[str, object] = {}      # {id: {func, hook_type}}
        self._guardrail_map: Dict[str, object] = {} # {id: {obj, hook_type}}
        # ── 行数据缓存（供冷启动和子管理器构建使用） ─────────────
        self._vectordb_rows: Dict[str, object] = {}
        self._mcp_rows: Dict[str, object] = {}
        self._kb_rows: Dict[str, object] = {}
        self._skill_rows: Dict[str, object] = {}
        self._memory_manager_rows: Dict[str, object] = {}
        self._learning_rows: Dict[str, object] = {}
        self._reasoning_rows: Dict[str, object] = {}
        self._compression_rows: Dict[str, object] = {}
        self._session_summary_rows: Dict[str, object] = {}
        self._culture_rows: Dict[str, object] = {}
        # ── 冷区（LRU 按需加载） ──────────────────────────────────
        self._knowledge_cache = LRUCache(maxsize=50)
        self._mcp_cache = LRUCache(maxsize=20)
        # ── 共享资源 ──────────────────────────────────────────────
        self._agno_db = None          # lifespan 注入
        self._shared_pg_engine = None # pgvector 共享连接池

    # ── Model 注册 ───────────────────────────────────────────────

    def register_model(self, model_id: str, row) -> None:
        """根据 row.provider 构建 Agno Model 实例并存入 _model_cache。"""
        provider = row.provider
        mid = row.model_id
        api_key = row.api_key
        base_url = row.base_url
        config = dict(row.config or {})

        if provider == "openai":
            from agno.models.openai import OpenAIChat
            obj = OpenAIChat(id=mid, api_key=api_key, base_url=base_url, **config)
        elif provider == "anthropic":
            from agno.models.anthropic import Claude
            obj = Claude(id=mid, api_key=api_key, **config)
        elif provider == "google":
            from agno.models.google import Gemini
            obj = Gemini(id=mid, api_key=api_key, **config)
        elif provider == "ollama":
            from agno.models.ollama import Ollama
            obj = Ollama(id=mid, host=base_url, **config)
        elif provider == "groq":
            from agno.models.groq import Groq
            obj = Groq(id=mid, api_key=api_key, **config)
        elif provider == "deepseek":
            from agno.models.deepseek import DeepSeek
            obj = DeepSeek(id=mid, api_key=api_key, base_url=base_url, **config)
        elif provider == "mistral":
            from agno.models.mistral import MistralChat
            obj = MistralChat(id=mid, api_key=api_key, **config)
        elif provider == "azure":
            from agno.models.azure import AzureOpenAI
            obj = AzureOpenAI(id=mid, api_key=api_key, azure_endpoint=base_url, **config)
        elif provider == "cohere":
            from agno.models.cohere import CohereChat
            obj = CohereChat(id=mid, api_key=api_key, **config)
        elif provider == "together":
            from agno.models.together import Together
            obj = Together(id=mid, api_key=api_key, **config)
        elif provider == "openai_like":
            from agno.models.openai import OpenAIChat
            obj = OpenAIChat(id=mid, api_key=api_key, base_url=base_url, **config)
        else:
            raise ValueError(f"Unsupported model provider: {provider}")

        self._model_cache[model_id] = obj

    def unregister_model(self, model_id: str) -> None:
        self._model_cache.pop(model_id, None)

    def _resolve_secret(self, key_ref: str | None) -> str | None:
        if not key_ref:
            return None
        return os.environ.get(key_ref)

    def _decrypt_env(self, env_config: dict) -> dict:
        return {k: self._resolve_secret(v) or v for k, v in env_config.items()}

    def _get_shared_pg_engine(self):
        if self._shared_pg_engine is None:
            from sqlalchemy import create_engine
            self._shared_pg_engine = create_engine(
                os.environ["VECTOR_DB_URL"], pool_size=5, max_overflow=10
            )
        return self._shared_pg_engine

    # ── resolve（callable factory 调用）──────────────────────

    def resolve_tools(self, agent_id: str) -> list:
        """每次 run() 时被 callable factory 调用，读最新绑定"""
        from modules.bindings.repo import SyncBindingRepo
        tools = []
        for b in SyncBindingRepo.get_active(agent_id, "agent"):
            if b.resource_type == "toolkit":
                t = self._toolkit_map.get(b.resource_id)
                if t:
                    tools.append(t)
            elif b.resource_type == "mcp":
                # get_or_build_mcp 处理 LRU 冷启动
                mcp_row = self._mcp_rows.get(b.resource_id)
                if mcp_row:
                    t = self.get_or_build_mcp(b.resource_id, mcp_row)
                    tools.append(t)
        return tools

    def resolve_knowledge(self, agent_id: str):
        from modules.bindings.repo import SyncBindingRepo
        kbs = []
        for b in SyncBindingRepo.get_active(agent_id, "agent", resource_type="knowledge"):
            kb_row = self._kb_rows.get(b.resource_id)
            if kb_row:
                # get_or_build_knowledge 处理 LRU 冷启动
                kb = self.get_or_build_knowledge(b.resource_id, kb_row)
                kbs.append(kb)
        # Agno knowledge 参数接受单个 Knowledge 实例
        return kbs[0] if kbs else None
```

### main.py

```python
from contextlib import asynccontextmanager
from fastapi import FastAPI
from agno.os import AgentOS
from agno.db.postgres import AsyncPostgresDb
from agno.os.config import AuthorizationConfig
import core.deps as deps
from core.registry import RuntimeRegistry

# 路由注册（按模块导入）
from modules.models.router import router as models_router
from modules.embedders.router import router as embedders_router
from modules.vectordbs.router import router as vectordbs_router
from modules.mcp.router import router as mcp_router
from modules.toolkits.router import router as toolkits_router
from modules.knowledge.router import router as knowledge_router
from modules.agents.router import router as agents_router
from modules.teams.router import router as teams_router
from modules.workflows.router import router as workflows_router
from modules.bindings.router import router as bindings_router
from modules.schedules.router import router as schedules_router
from modules.rbac.router import router as rbac_router
from modules.skills.router import router as skills_router
from modules.hooks.router import router as hooks_router
from modules.guardrails.router import router as guardrails_router
from modules.memory.router import router as memory_router
from modules.learning.router import router as learning_router
from modules.submanagers.router import router as submanagers_router
from modules.integrations.router import router as integrations_router
from modules.logs.router import router as logs_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    registry = RuntimeRegistry()
    deps._registry = registry

    # Agno DB 实例注入 registry（子管理器需要）
    agno_db = AsyncPostgresDb(url=os.environ["DATABASE_URL"])
    registry._agno_db = agno_db

    from core.db import AsyncSessionLocal
    async with AsyncSessionLocal() as db:
        from modules.models.repo import ModelRepo
        from modules.embedders.repo import EmbedderRepo
        from modules.vectordbs.repo import VectorDbRepo
        from modules.mcp.repo import McpRepo
        from modules.toolkits.repo import ToolkitRepo
        from modules.knowledge.repo import KnowledgeRepo
        from modules.skills.repo import SkillRepo
        from modules.hooks.repo import HookRepo
        from modules.guardrails.repo import GuardrailRepo
        from modules.memory.repo import MemoryManagerRepo
        from modules.learning.repo import LearningConfigRepo
        from modules.submanagers.repo import ReasoningRepo, CompressionRepo, SessionSummaryRepo, CultureRepo
        from modules.agents.repo import AgentRepo
        from modules.teams.repo import TeamRepo
        from modules.workflows.repo import WorkflowRepo, WorkflowNodeRepo
        from modules.integrations.repo import IntegrationRepo

        # ── 第一层：无依赖的基础组件 ──────────────────────────────
        for row in await ModelRepo(db).get_all_enabled():
            registry.register_model(str(row.id), row)

        for row in await EmbedderRepo(db).get_all_enabled():
            registry.register_embedder(str(row.id), row)

        # ── 第二层：依赖 embedder 的组件 ─────────────────────────
        for row in await VectorDbRepo(db).get_all_enabled():
            registry._vectordb_rows[str(row.id)] = row   # 存行，按需冷启动

        for row in await KnowledgeRepo(db).get_all_enabled():
            registry._kb_rows[str(row.id)] = row          # 存行，按需冷启动

        # ── 第三层：工具类 ────────────────────────────────────────
        for row in await ToolkitRepo(db).get_all_enabled():
            registry.register_toolkit(str(row.id), row)

        for row in await McpRepo(db).get_all_enabled():
            registry._mcp_rows[str(row.id)] = row         # 存行，LRU 冷启动

        # Skill 行数据（构建 Agent 时 build_skills() 按需读取）
        for row in await SkillRepo(db).get_all_enabled():
            registry._skill_rows[str(row.id)] = row

        for row in await HookRepo(db).get_all_enabled():
            registry.register_hook(str(row.id), row)

        for row in await GuardrailRepo(db).get_all_enabled():
            registry.register_guardrail(str(row.id), row)

        # ── 第四层：子管理器行数据（构建 Agent 时按需实例化） ──────
        for row in await MemoryManagerRepo(db).get_all_enabled():
            registry._memory_manager_rows[str(row.id)] = row

        for row in await LearningConfigRepo(db).get_all_enabled():
            registry._learning_rows[str(row.id)] = row

        for row in await ReasoningRepo(db).get_all_enabled():
            registry._reasoning_rows[str(row.id)] = row

        for row in await CompressionRepo(db).get_all_enabled():
            registry._compression_rows[str(row.id)] = row

        for row in await SessionSummaryRepo(db).get_all_enabled():
            registry._session_summary_rows[str(row.id)] = row

        for row in await CultureRepo(db).get_all_enabled():
            registry._culture_rows[str(row.id)] = row

        # ── 第五层：Agent（依赖所有上层） ────────────────────────
        for row in await AgentRepo(db).get_all_enabled():
            await registry.create_agent(row)

        # ── 第六层：Team（依赖 Agent）─────────────────────────────
        for row in await TeamRepo(db).get_all_enabled():
            await registry.create_team(row)

        # ── 第七层：Workflow（依赖 Agent/Team）───────────────────
        for row in await WorkflowRepo(db).get_all_enabled():
            node_rows = await WorkflowNodeRepo(db).get_by_workflow(row.id)
            await registry.create_workflow(row, node_rows)

        # ── 第八层：Integrations（依赖 Agent/Team，路由在 AgentOS 启动时挂载）
        interfaces = await build_interfaces(db, registry)

    # AgentOS 在 lifespan 内创建（此时 registry.agents/teams/workflows 已填充）
    agent_os = AgentOS(
        base_app=app,
        agents=registry.agents,     # 传引用，后续 append 自动可路由
        teams=registry.teams,
        workflows=registry.workflows,
        interfaces=interfaces,
        db=agno_db,
        tracing=True,
        scheduler=True,
        authorization=True,
        authorization_config=AuthorizationConfig(
            verification_keys=[os.environ.get("JWT_PUBLIC_KEY", "")],
            algorithm="RS256",
        ),
        run_hooks_in_background=True,
    )
    deps._agent_os = agent_os

    yield
    # ── shutdown：关闭 MCP 连接/子进程 ─────────────────────────
    for mcp in registry._mcp_cache._cache.values():
        if hasattr(mcp, "close"):
            try:
                mcp.close()
            except Exception:
                pass


app = FastAPI(title="AI Platform", lifespan=lifespan)

# 管理路由（lifespan 执行前注册，无顺序依赖）
app.include_router(models_router,    prefix="/management/models",    tags=["models"])
app.include_router(embedders_router, prefix="/management/embedders", tags=["embedders"])
app.include_router(vectordbs_router, prefix="/management/vectordbs", tags=["vectordbs"])
app.include_router(mcp_router,       prefix="/management/mcp",       tags=["mcp"])
app.include_router(toolkits_router,  prefix="/management/toolkits",  tags=["toolkits"])
app.include_router(knowledge_router, prefix="/management/knowledge",  tags=["knowledge"])
app.include_router(agents_router,    prefix="/management/agents",     tags=["agents"])
app.include_router(teams_router,     prefix="/management/teams",      tags=["teams"])
app.include_router(workflows_router, prefix="/management/workflows",  tags=["workflows"])
app.include_router(bindings_router,  prefix="/management/bindings",   tags=["bindings"])
app.include_router(schedules_router,   prefix="/management/schedules",        tags=["schedules"])
app.include_router(rbac_router,        prefix="/management/rbac",             tags=["rbac"])
app.include_router(skills_router,      prefix="/management/skills",           tags=["skills"])
app.include_router(hooks_router,       prefix="/management/hooks",            tags=["hooks"])
app.include_router(guardrails_router,  prefix="/management/guardrails",       tags=["guardrails"])
app.include_router(memory_router,      prefix="/management/memory-managers",  tags=["memory"])
app.include_router(learning_router,    prefix="/management/learning-configs", tags=["learning"])
app.include_router(submanagers_router, prefix="/management/sub-managers",     tags=["sub-managers"])
app.include_router(integrations_router,prefix="/management/integrations",     tags=["integrations"])
app.include_router(logs_router,        prefix="/management",                  tags=["logs"])
# AgentOS 路由由 AgentOS(base_app=app) 在 lifespan 内自动挂载
```

### 公共触发器与索引

```sql
-- 自动更新 updated_at 的触发器函数
CREATE OR REPLACE FUNCTION fn_update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- 宏：给表创建触发器（对每张有 updated_at 的表执行）
-- CREATE TRIGGER trg_<table>_updated_at
--     BEFORE UPDATE ON <table>
--     FOR EACH ROW EXECUTE FUNCTION fn_update_updated_at();
```

---

## 五、模块详细设计

---

### 5.1 Models（模型管理）

#### 表设计

```sql
CREATE TABLE ag_models (
    id            SERIAL NOT NULL,
    uuid          varchar(64) NOT NULL,
    name          varchar(255) NOT NULL,
    model_id      varchar(255) NOT NULL,
    provider      varchar(50) NOT NULL,
    api_key       text,
    base_url      varchar(500),
    config        jsonb NOT NULL DEFAULT '{}',
    status        varchar(10) NOT NULL DEFAULT '0',
    description   text,
    created_time  timestamp without time zone NOT NULL,
    updated_time  timestamp without time zone NOT NULL,
    created_id    integer,
    updated_id    integer,
    PRIMARY KEY(id),
    CONSTRAINT ag_models_created_id_fkey FOREIGN KEY(created_id) REFERENCES sys_user(id),
    CONSTRAINT ag_models_updated_id_fkey FOREIGN KEY(updated_id) REFERENCES sys_user(id)
);
CREATE UNIQUE INDEX ag_models_uuid_key      ON public.ag_models USING btree (uuid);
CREATE INDEX ix_ag_models_provider          ON public.ag_models USING btree (provider);
CREATE INDEX ix_ag_models_status            ON public.ag_models USING btree (status);
CREATE INDEX ix_ag_models_created_id        ON public.ag_models USING btree (created_id);
CREATE INDEX ix_ag_models_updated_id        ON public.ag_models USING btree (updated_id);

COMMENT ON TABLE  ag_models                 IS '平台模型管理表';
COMMENT ON COLUMN ag_models.id              IS '主键ID';
COMMENT ON COLUMN ag_models.uuid            IS 'UUID全局唯一标识';
COMMENT ON COLUMN ag_models.name            IS '模型名称';
COMMENT ON COLUMN ag_models.model_id        IS '模型标识符（传给Agno Model的id参数）';
COMMENT ON COLUMN ag_models.provider        IS '模型提供商(openai/anthropic/google/ollama/deepseek)';
COMMENT ON COLUMN ag_models.api_key         IS 'API密钥（明文存储）';
COMMENT ON COLUMN ag_models.base_url        IS '自定义API地址（用于ollama/vllm/lmstudio）';
COMMENT ON COLUMN ag_models.config          IS '模型配置参数（temperature/max_tokens/top_p等）';
COMMENT ON COLUMN ag_models.status          IS '是否启用(0:启用 1:禁用)';
COMMENT ON COLUMN ag_models.description     IS '备注/描述';
COMMENT ON COLUMN ag_models.created_time    IS '创建时间';
COMMENT ON COLUMN ag_models.updated_time    IS '更新时间';
COMMENT ON COLUMN ag_models.created_id      IS '创建人ID';
COMMENT ON COLUMN ag_models.updated_id      IS '更新人ID';
```

#### 与 Agno 的交互流程

```
ag_models 一行
  │
  ├─ provider = "openai"
  │   └─ OpenAIChat(id=model_id, api_key=row.api_key,
  │                 base_url=base_url, **config)
  │
  ├─ provider = "anthropic"
  │   └─ Claude(id=model_id, api_key=row.api_key, **config)
  │
  ├─ provider = "google"
  │   └─ Gemini(id=model_id, api_key=row.api_key, **config)
  │
  └─ provider = "ollama"
      └─ Ollama(id=model_id, host=base_url, **config)

注册到 registry._model_cache[id]
Agent 创建时：Agent(model=registry.get_model(model_id))
```

#### 代码结构

```
modules/models/
├── model.py      # PlatformModel ORM
├── schemas.py    # ModelCreate / ModelUpdate / ModelResponse
├── repo.py       # ModelRepo（async CRUD）
├── service.py    # ModelService（调 repo + registry）
└── router.py     # GET/POST/PATCH/DELETE /management/models
```

#### 代码实现

**model.py**
```python
from uuid import uuid4
from sqlalchemy import Boolean, String, JSON, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from core.db import Base


class PlatformModel(Base):
    __tablename__ = "ag_models"

    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    model_id: Mapped[str] = mapped_column(String(255), nullable=False)
    provider: Mapped[str] = mapped_column(String(50), nullable=False)
    api_key: Mapped[str | None] = mapped_column(Text)
    base_url: Mapped[str | None] = mapped_column(String(500))
    config: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
```

**schemas.py**
```python
from uuid import UUID
from typing import Any
from pydantic import BaseModel, Field


class ModelCreate(BaseModel):
    name: str
    model_id: str
    provider: str
    api_key: str | None = None
    base_url: str | None = None
    config: dict[str, Any] = Field(default_factory=dict)
    enabled: bool = True


class ModelUpdate(BaseModel):
    name: str | None = None
    api_key: str | None = None
    base_url: str | None = None
    config: dict[str, Any] | None = None
    enabled: bool | None = None


class ModelResponse(BaseModel):
    id: UUID
    name: str
    model_id: str
    provider: str
    base_url: str | None
    enabled: bool
    model_config = {"from_attributes": True}
```

**repo.py**
```python
from uuid import UUID
from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from .model import PlatformModel


class ModelRepo:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_all_enabled(self) -> list[PlatformModel]:
        r = await self.db.execute(
            select(PlatformModel).where(PlatformModel.enabled == True)
        )
        return r.scalars().all()

    async def get_by_id(self, mid: UUID) -> PlatformModel | None:
        r = await self.db.execute(
            select(PlatformModel).where(PlatformModel.id == mid)
        )
        return r.scalar_one_or_none()

    async def create(self, data: dict) -> PlatformModel:
        row = PlatformModel(**data)
        self.db.add(row)
        await self.db.commit()
        await self.db.refresh(row)
        return row

    async def update(self, mid: UUID, data: dict) -> PlatformModel | None:
        await self.db.execute(
            update(PlatformModel).where(PlatformModel.id == mid).values(**data)
        )
        await self.db.commit()
        return await self.get_by_id(mid)

    async def delete(self, mid: UUID) -> None:
        await self.db.execute(delete(PlatformModel).where(PlatformModel.id == mid))
        await self.db.commit()
```

**service.py**
```python
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from core.registry import RuntimeRegistry
from .repo import ModelRepo
from .schemas import ModelCreate, ModelUpdate


class ModelService:
    def __init__(self, db: AsyncSession, registry: RuntimeRegistry):
        self.repo = ModelRepo(db)
        self.reg = registry

    async def list_all(self):
        return await self.repo.get_all_enabled()

    async def create(self, body: ModelCreate):
        row = await self.repo.create(body.model_dump())
        self.reg.register_model(str(row.id), row)
        return row

    async def update(self, mid: UUID, body: ModelUpdate):
        data = body.model_dump(exclude_none=True)
        row = await self.repo.update(mid, data)
        if row:
            self.reg.register_model(str(mid), row)  # 重建运行时对象
        return row

    async def delete(self, mid: UUID) -> bool:
        row = await self.repo.get_by_id(mid)
        if not row:
            return False
        await self.repo.delete(mid)
        self.reg.unregister_model(str(mid))
        return True
```

**router.py**
```python
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from core.deps import get_db, get_registry
from core.registry import RuntimeRegistry
from .schemas import ModelCreate, ModelUpdate, ModelResponse
from .service import ModelService

router = APIRouter()


def svc(db: AsyncSession = Depends(get_db),
        reg: RuntimeRegistry = Depends(get_registry)) -> ModelService:
    return ModelService(db, reg)


@router.get("", response_model=list[ModelResponse])
async def list_models(s: ModelService = Depends(svc)):
    return await s.list_all()


@router.post("", response_model=ModelResponse, status_code=201)
async def create_model(body: ModelCreate, s: ModelService = Depends(svc)):
    return await s.create(body)


@router.patch("/{mid}", response_model=ModelResponse)
async def update_model(mid: UUID, body: ModelUpdate, s: ModelService = Depends(svc)):
    row = await s.update(mid, body)
    if not row:
        raise HTTPException(404, "Not found")
    return row


@router.delete("/{mid}", status_code=204)
async def delete_model(mid: UUID, s: ModelService = Depends(svc)):
    if not await s.delete(mid):
        raise HTTPException(404, "Not found")
```

---

### 5.2 Embedders（向量化模型）

#### 表设计

```sql
CREATE TABLE ag_embedders (
    id            SERIAL NOT NULL,
    uuid          varchar(64) NOT NULL,
    name          varchar(255) NOT NULL,
    provider      varchar(50) NOT NULL,
    model_id      varchar(255) NOT NULL,
    api_key       text,
    base_url      varchar(500),
    dimensions    integer,
    config        jsonb NOT NULL DEFAULT '{}',
    status        varchar(10) NOT NULL DEFAULT '0',
    description   text,
    created_time  timestamp without time zone NOT NULL,
    updated_time  timestamp without time zone NOT NULL,
    created_id    integer,
    updated_id    integer,
    PRIMARY KEY(id),
    CONSTRAINT ag_embedders_created_id_fkey FOREIGN KEY(created_id) REFERENCES sys_user(id),
    CONSTRAINT ag_embedders_updated_id_fkey FOREIGN KEY(updated_id) REFERENCES sys_user(id)
);
CREATE UNIQUE INDEX ag_embedders_uuid_key   ON public.ag_embedders USING btree (uuid);
CREATE INDEX ix_ag_embedders_provider       ON public.ag_embedders USING btree (provider);
CREATE INDEX ix_ag_embedders_status         ON public.ag_embedders USING btree (status);
CREATE INDEX ix_ag_embedders_created_id     ON public.ag_embedders USING btree (created_id);
CREATE INDEX ix_ag_embedders_updated_id     ON public.ag_embedders USING btree (updated_id);

COMMENT ON TABLE  ag_embedders              IS '嵌入模型管理表';
COMMENT ON COLUMN ag_embedders.id           IS '主键ID';
COMMENT ON COLUMN ag_embedders.uuid         IS 'UUID全局唯一标识';
COMMENT ON COLUMN ag_embedders.name         IS '嵌入器名称';
COMMENT ON COLUMN ag_embedders.provider     IS '提供商(openai/azure/ollama/cohere/google/huggingface等)';
COMMENT ON COLUMN ag_embedders.model_id     IS '嵌入模型标识（如text-embedding-3-small）';
COMMENT ON COLUMN ag_embedders.api_key      IS 'API密钥';
COMMENT ON COLUMN ag_embedders.base_url     IS '自定义端点地址（openai_like/ollama/vllm）';
COMMENT ON COLUMN ag_embedders.dimensions   IS '向量维度';
COMMENT ON COLUMN ag_embedders.config       IS '其他构造参数（azure api_version/cohere input_type等）';
COMMENT ON COLUMN ag_embedders.status       IS '是否启用(0:启用 1:禁用)';
COMMENT ON COLUMN ag_embedders.description  IS '备注/描述';
COMMENT ON COLUMN ag_embedders.created_time IS '创建时间';
COMMENT ON COLUMN ag_embedders.updated_time IS '更新时间';
COMMENT ON COLUMN ag_embedders.created_id   IS '创建人ID';
COMMENT ON COLUMN ag_embedders.updated_id   IS '更新人ID';
```

#### provider 与 Agno 类的映射

| provider | Agno 类 | 特殊参数 |
|----------|---------|---------|
| `openai` | `agno.knowledge.embedder.openai.OpenAIEmbedder` | `api_key`, `base_url`, `dimensions` |
| `azure` | `agno.knowledge.embedder.azure_openai.AzureOpenAIEmbedder` | `api_key`, `base_url`, config 含 `api_version` |
| `ollama` | `agno.knowledge.embedder.ollama.OllamaEmbedder` | `base_url` 映射为 `host`，无 api_key |
| `cohere` | `agno.knowledge.embedder.cohere.CohereEmbedder` | `api_key` |
| `google` | `agno.knowledge.embedder.google.GeminiEmbedder` | `api_key`, `dimensions` |
| `huggingface` | `agno.knowledge.embedder.huggingface.HuggingfaceCustomEmbedder` | `api_key` |
| `openai_like` | `agno.knowledge.embedder.openai_like.OpenAILikeEmbedder` | `api_key`, `base_url`（必填） |
| `fastembed` | `agno.knowledge.embedder.fastembed.FastEmbedEmbedder` | 本地模型，无 api_key |
| `sentence_transformer` | `agno.knowledge.embedder.sentence_transformer.SentenceTransformerEmbedder` | 本地模型 |
| `vllm` | `agno.knowledge.embedder.vllm.VllmEmbedder` | `base_url`（必填） |
| `jina` | `agno.knowledge.embedder.jina.JinaEmbedder` | `api_key` |
| `voyageai` | `agno.knowledge.embedder.voyageai.VoyageAIEmbedder` | `api_key` |
| `mistral` | `agno.knowledge.embedder.mistral.MistralEmbedder` | `api_key` |

#### registry 中的构建方法

```python
def register_embedder(self, embedder_id: str, row) -> None:
    provider = row.provider
    model_id = row.model_id
    api_key = row.api_key
    base_url = row.base_url
    dimensions = row.dimensions
    config = row.config or {}

    if provider == "openai":
        from agno.knowledge.embedder.openai import OpenAIEmbedder
        obj = OpenAIEmbedder(id=model_id, api_key=api_key, base_url=base_url,
                             dimensions=dimensions, **config)
    elif provider == "azure":
        from agno.knowledge.embedder.azure_openai import AzureOpenAIEmbedder
        obj = AzureOpenAIEmbedder(id=model_id, api_key=api_key, base_url=base_url,
                                  dimensions=dimensions, **config)
    elif provider == "ollama":
        from agno.knowledge.embedder.ollama import OllamaEmbedder
        obj = OllamaEmbedder(id=model_id, host=base_url, **config)
    elif provider == "cohere":
        from agno.knowledge.embedder.cohere import CohereEmbedder
        obj = CohereEmbedder(id=model_id, api_key=api_key, **config)
    elif provider == "google":
        from agno.knowledge.embedder.google import GeminiEmbedder
        obj = GeminiEmbedder(id=model_id, api_key=api_key, dimensions=dimensions, **config)
    elif provider == "huggingface":
        from agno.knowledge.embedder.huggingface import HuggingfaceCustomEmbedder
        obj = HuggingfaceCustomEmbedder(id=model_id, api_key=api_key, **config)
    elif provider == "openai_like":
        from agno.knowledge.embedder.openai_like import OpenAILikeEmbedder
        obj = OpenAILikeEmbedder(id=model_id, api_key=api_key, base_url=base_url,
                                 dimensions=dimensions, **config)
    elif provider == "fastembed":
        from agno.knowledge.embedder.fastembed import FastEmbedEmbedder
        obj = FastEmbedEmbedder(id=model_id, **config)
    elif provider == "sentence_transformer":
        from agno.knowledge.embedder.sentence_transformer import SentenceTransformerEmbedder
        obj = SentenceTransformerEmbedder(id=model_id, **config)
    elif provider == "vllm":
        from agno.knowledge.embedder.vllm import VllmEmbedder
        obj = VllmEmbedder(id=model_id, base_url=base_url, **config)
    elif provider == "jina":
        from agno.knowledge.embedder.jina import JinaEmbedder
        obj = JinaEmbedder(id=model_id, api_key=api_key, **config)
    elif provider == "voyageai":
        from agno.knowledge.embedder.voyageai import VoyageAIEmbedder
        obj = VoyageAIEmbedder(id=model_id, api_key=api_key, **config)
    elif provider == "mistral":
        from agno.knowledge.embedder.mistral import MistralEmbedder
        obj = MistralEmbedder(id=model_id, api_key=api_key, **config)
    else:
        raise ValueError(f"Unsupported embedder provider: {provider}")

    self._embedder_cache[embedder_id] = obj
```

#### CRUD 差异（相对 5.1 Models 模式）

> router.py / service.py / repo.py 结构同 5.1 Models。以下仅列出差异点。

- **create**：写 DB 后调用 `registry.register_embedder(str(row.id), row)` 加入缓存。
- **update**：重新调用 `registry.register_embedder(str(row.id), row)`，覆盖旧对象；若 `model_id`/`api_key`/`base_url` 变更，同时调用 `registry._knowledge_cache.clear()` 使依赖此 embedder 的 Knowledge LRU 失效，下次访问重建。
- **delete**：`registry._embedder_cache.pop(embedder_id, None)`；同时 `registry._knowledge_cache.clear()`。

---

### 5.3 VectorDBs（向量库）

#### 表设计

```sql
CREATE TABLE ag_vectordbs (
    id            SERIAL NOT NULL,
    uuid          varchar(64) NOT NULL,
    name          varchar(255) NOT NULL,
    provider      varchar(50) NOT NULL,
    embedder_id   integer NOT NULL,
    config        jsonb NOT NULL DEFAULT '{}',
    status        varchar(10) NOT NULL DEFAULT '0',
    description   text,
    created_time  timestamp without time zone NOT NULL,
    updated_time  timestamp without time zone NOT NULL,
    created_id    integer,
    updated_id    integer,
    PRIMARY KEY(id),
    CONSTRAINT ag_vectordbs_embedder_id_fkey FOREIGN KEY(embedder_id) REFERENCES ag_embedders(id),
    CONSTRAINT ag_vectordbs_created_id_fkey  FOREIGN KEY(created_id)  REFERENCES sys_user(id),
    CONSTRAINT ag_vectordbs_updated_id_fkey  FOREIGN KEY(updated_id)  REFERENCES sys_user(id)
);
CREATE UNIQUE INDEX ag_vectordbs_uuid_key   ON public.ag_vectordbs USING btree (uuid);
CREATE INDEX ix_ag_vectordbs_provider       ON public.ag_vectordbs USING btree (provider);
CREATE INDEX ix_ag_vectordbs_embedder_id    ON public.ag_vectordbs USING btree (embedder_id);
CREATE INDEX ix_ag_vectordbs_status         ON public.ag_vectordbs USING btree (status);
CREATE INDEX ix_ag_vectordbs_created_id     ON public.ag_vectordbs USING btree (created_id);
CREATE INDEX ix_ag_vectordbs_updated_id     ON public.ag_vectordbs USING btree (updated_id);

COMMENT ON TABLE  ag_vectordbs              IS '向量数据库管理表';
COMMENT ON COLUMN ag_vectordbs.id           IS '主键ID';
COMMENT ON COLUMN ag_vectordbs.uuid         IS 'UUID全局唯一标识';
COMMENT ON COLUMN ag_vectordbs.name         IS '向量库名称';
COMMENT ON COLUMN ag_vectordbs.provider     IS '向量库类型(pgvector/qdrant/chroma/pinecone/milvus等)';
COMMENT ON COLUMN ag_vectordbs.embedder_id  IS '关联嵌入模型ID';
COMMENT ON COLUMN ag_vectordbs.config       IS '连接配置（table_name/collection/url等，按provider不同）';
COMMENT ON COLUMN ag_vectordbs.status       IS '是否启用(0:启用 1:禁用)';
COMMENT ON COLUMN ag_vectordbs.description  IS '备注/描述';
COMMENT ON COLUMN ag_vectordbs.created_time IS '创建时间';
COMMENT ON COLUMN ag_vectordbs.updated_time IS '更新时间';
COMMENT ON COLUMN ag_vectordbs.created_id   IS '创建人ID';
COMMENT ON COLUMN ag_vectordbs.updated_id   IS '更新人ID';
```

#### provider 与 config 必填字段

| provider | config 必填字段 | 说明 |
|----------|----------------|------|
| `pgvector` | `table_name` | 共享 pg_engine，无需 db_url |
| `qdrant` | `collection` | url/host 可选，默认 localhost |
| `chroma` | `collection` 或 `name` | path 默认 tmp/chromadb |
| `pinecone` | `index_name`, `api_key` | |
| `weaviate` | `collection` | url 可选 |
| `milvus` | `collection` | uri 可选 |
| `mongodb` | `collection`, `connection_string` | |
| `redis` | `index_name`, `redis_url` | |
| `lancedb` | `table_name`, `uri` | |

#### registry 中的构建方法

```python
def build_vectordb(self, row) -> Any:
    """根据 ag_vectordbs 行构建 VectorDb 实例（供 Knowledge 调用）"""
    embedder = self._embedder_cache.get(str(row.embedder_id)) if row.embedder_id else None
    config = dict(row.config or {})
    provider = row.provider

    if provider == "pgvector":
        from agno.vectordb.pgvector import PgVector
        # 共享 engine，避免每个知识库建独立连接池
        return PgVector(
            table_name=config.pop("table_name"),
            schema=config.pop("schema", "ai"),
            db_engine=self._get_shared_pg_engine(),
            embedder=embedder,
            **config,
        )
    elif provider == "qdrant":
        from agno.vectordb.qdrant import Qdrant
        return Qdrant(
            collection=config.pop("collection"),
            embedder=embedder,
            url=config.pop("url", None),
            **config,
        )
    elif provider == "chroma":
        from agno.vectordb.chroma import ChromaDb
        return ChromaDb(
            collection=config.pop("collection", None),
            name=config.pop("name", None),
            embedder=embedder,
            path=config.pop("path", "tmp/chromadb"),
            **config,
        )
    elif provider == "pinecone":
        from agno.vectordb.pineconedb import PineconeDb
        return PineconeDb(
            index_name=config.pop("index_name"),
            embedder=embedder,
            api_key=config.pop("api_key", None),
            **config,
        )
    elif provider == "weaviate":
        from agno.vectordb.weaviate import Weaviate
        return Weaviate(
            collection=config.pop("collection"),
            embedder=embedder,
            **config,
        )
    elif provider == "milvus":
        from agno.vectordb.milvus import Milvus
        return Milvus(
            collection=config.pop("collection"),
            embedder=embedder,
            **config,
        )
    elif provider == "mongodb":
        from agno.vectordb.mongodb import MongoDb
        return MongoDb(
            collection=config.pop("collection"),
            connection_string=config.pop("connection_string"),
            embedder=embedder,
            **config,
        )
    elif provider == "redis":
        from agno.vectordb.redis import RedisVectorDb
        return RedisVectorDb(
            index_name=config.pop("index_name"),
            redis_url=config.pop("redis_url"),
            embedder=embedder,
            **config,
        )
    elif provider == "lancedb":
        from agno.vectordb.lancedb import LanceDb
        return LanceDb(
            table_name=config.pop("table_name"),
            uri=config.pop("uri"),
            embedder=embedder,
            **config,
        )
    else:
        raise ValueError(f"Unsupported vectordb provider: {provider}")
```

#### CRUD 差异（相对 5.1 Models 模式）

> router.py / service.py / repo.py 结构同 5.1 Models。

- **VectorDB 不直接注册进热区**，只写行缓存 `_vectordb_rows`；实例在 Knowledge 首次访问时冷启动。
- **create**：写 DB 后 `registry._vectordb_rows[str(row.id)] = row`。
- **update**：更新行缓存；同时调用 `registry._knowledge_cache.clear()` 淘汰所有依赖此 vectordb 的 Knowledge 对象，下次访问触发重建。
- **delete**：`registry._vectordb_rows.pop(vid, None)`；`registry._knowledge_cache.clear()`。
- **注意**：`pgvector` 的 `table_name` 变更等同于新建一个向量表，需手动迁移数据后再更新。

---

### 5.4 MCP Servers

#### 表设计

```sql
CREATE TABLE ag_mcp_servers (
    id                 SERIAL NOT NULL,
    uuid               varchar(64) NOT NULL,
    name               varchar(255) NOT NULL,
    transport          varchar(20) NOT NULL,
    command            text,
    url                varchar(500),
    env_config         jsonb NOT NULL DEFAULT '{}',
    include_tools      jsonb,
    exclude_tools      jsonb,
    tool_name_prefix   varchar(100),
    timeout_seconds    integer NOT NULL DEFAULT 10,
    refresh_connection boolean NOT NULL DEFAULT false,
    status             varchar(10) NOT NULL DEFAULT '0',
    description        text,
    created_time       timestamp without time zone NOT NULL,
    updated_time       timestamp without time zone NOT NULL,
    created_id         integer,
    updated_id         integer,
    PRIMARY KEY(id),
    CONSTRAINT ag_mcp_servers_created_id_fkey FOREIGN KEY(created_id) REFERENCES sys_user(id),
    CONSTRAINT ag_mcp_servers_updated_id_fkey FOREIGN KEY(updated_id) REFERENCES sys_user(id)
);
CREATE UNIQUE INDEX ag_mcp_servers_uuid_key   ON public.ag_mcp_servers USING btree (uuid);
CREATE INDEX ix_ag_mcp_servers_transport      ON public.ag_mcp_servers USING btree (transport);
CREATE INDEX ix_ag_mcp_servers_status         ON public.ag_mcp_servers USING btree (status);
CREATE INDEX ix_ag_mcp_servers_created_id     ON public.ag_mcp_servers USING btree (created_id);
CREATE INDEX ix_ag_mcp_servers_updated_id     ON public.ag_mcp_servers USING btree (updated_id);

COMMENT ON TABLE  ag_mcp_servers                  IS 'MCP服务管理表';
COMMENT ON COLUMN ag_mcp_servers.id               IS '主键ID';
COMMENT ON COLUMN ag_mcp_servers.uuid             IS 'UUID全局唯一标识';
COMMENT ON COLUMN ag_mcp_servers.name             IS 'MCP服务名称';
COMMENT ON COLUMN ag_mcp_servers.transport        IS '传输协议(stdio/sse/streamable-http)';
COMMENT ON COLUMN ag_mcp_servers.command          IS 'stdio启动命令';
COMMENT ON COLUMN ag_mcp_servers.url              IS 'HTTP/SSE服务地址';
COMMENT ON COLUMN ag_mcp_servers.env_config       IS '环境变量配置';
COMMENT ON COLUMN ag_mcp_servers.include_tools    IS '仅包含的工具列表';
COMMENT ON COLUMN ag_mcp_servers.exclude_tools    IS '排除的工具列表';
COMMENT ON COLUMN ag_mcp_servers.tool_name_prefix IS '工具名称前缀';
COMMENT ON COLUMN ag_mcp_servers.timeout_seconds  IS '连接超时秒数';
COMMENT ON COLUMN ag_mcp_servers.refresh_connection IS '是否刷新连接';
COMMENT ON COLUMN ag_mcp_servers.status           IS '是否启用(0:启用 1:禁用)';
COMMENT ON COLUMN ag_mcp_servers.description      IS '备注/描述';
COMMENT ON COLUMN ag_mcp_servers.created_time     IS '创建时间';
COMMENT ON COLUMN ag_mcp_servers.updated_time     IS '更新时间';
COMMENT ON COLUMN ag_mcp_servers.created_id       IS '创建人ID';
COMMENT ON COLUMN ag_mcp_servers.updated_id       IS '更新人ID';
```

#### 与 Agno 交互流程

```
ag_mcp_servers 一行
  │  （首次访问时冷启动，LRU maxsize=20）
  │
  ├─ transport = "stdio"
  │   MCPTools(command="uvx mcp-server-brave-search",
  │            env={"BRAVE_API_KEY": resolve("BRAVE_KEY")},
  │            transport="stdio")
  │   → 启动子进程，持有连接
  │
  └─ transport = "streamable-http"
      MCPTools(url="http://mcp-server:8080",
               transport="streamable-http")
      → 建 HTTP 连接

LRU 淘汰时：mcp.close() → 子进程终止/连接关闭
```

#### registry 中的构建方法

```python
def get_or_build_mcp(self, mcp_id: str, row) -> Any:
    """LRU 冷热管理：首次访问时构建，stdio 最多 10 个（持有子进程），http 最多 30 个"""
    obj = self._mcp_cache.get(mcp_id)
    if obj:
        return obj

    from agno.tools.mcp import MCPTools
    config = row.config or {}

    if row.transport == "stdio":
        # stdio：启动本地子进程，严格限制数量（每个持有一个进程）
        obj = MCPTools(
            command=row.command,
            transport="stdio",
            env=config.get("env"),
            include_tools=row.include_tools,
            exclude_tools=row.exclude_tools,
            tool_name_prefix=row.tool_name_prefix,
            timeout_seconds=row.timeout_seconds,
            refresh_connection=row.refresh_connection,
        )
    else:
        # sse / streamable-http：HTTP 连接，相对轻量
        obj = MCPTools(
            url=row.url,
            transport=row.transport,  # "sse" or "streamable-http"
            include_tools=row.include_tools,
            exclude_tools=row.exclude_tools,
            tool_name_prefix=row.tool_name_prefix,
            timeout_seconds=row.timeout_seconds,
            refresh_connection=row.refresh_connection,
        )

    self._mcp_cache.set(mcp_id, obj)
    return obj
```

> **注意**：`resolve_tools()` 中调用 `get_or_build_mcp()`，LRU 淘汰时自动调用 `mcp.close()`（见 LRUCache.set 实现）。

#### CRUD 差异（相对 5.1 Models 模式）

> router.py / service.py / repo.py 结构同 5.1 Models。

- **MCP 只存行缓存**（`_mcp_rows`），不预连接；连接在 `resolve_tools()` 中按需建立。
- **create**：写 DB 后 `registry._mcp_rows[str(row.id)] = row`。
- **update**：更新行缓存；同时驱逐 LRU：`registry._mcp_cache.remove(mcp_id)`（若 LRUCache 有 remove 方法）或直接 `registry._mcp_cache = LRUCache(maxsize=20)` 重置。stdio 类型的 MCP 驱逐时会触发旧子进程关闭。
- **delete**：`registry._mcp_rows.pop(mcp_id, None)`；驱逐 LRU 同上。

---

### 5.5 Toolkits（工具）

#### 表设计

```sql
CREATE TABLE ag_toolkits (
    id                    SERIAL NOT NULL,
    uuid                  varchar(64) NOT NULL,
    name                  varchar(255) NOT NULL,
    type                  varchar(20) NOT NULL,
    module_path           varchar(500) NOT NULL,
    class_name            varchar(255),
    func_name             varchar(255),
    config                jsonb NOT NULL DEFAULT '{}',
    instructions          text,
    requires_confirmation boolean NOT NULL DEFAULT false,
    approval_type         varchar(20),
    stop_after_call       boolean NOT NULL DEFAULT false,
    show_result           boolean NOT NULL DEFAULT false,
    cache_results         boolean NOT NULL DEFAULT false,
    cache_ttl             integer NOT NULL DEFAULT 3600,
    status                varchar(10) NOT NULL DEFAULT '0',
    description           text,
    created_time          timestamp without time zone NOT NULL,
    updated_time          timestamp without time zone NOT NULL,
    created_id            integer,
    updated_id            integer,
    PRIMARY KEY(id),
    CONSTRAINT ag_toolkits_created_id_fkey FOREIGN KEY(created_id) REFERENCES sys_user(id),
    CONSTRAINT ag_toolkits_updated_id_fkey FOREIGN KEY(updated_id) REFERENCES sys_user(id)
);
CREATE UNIQUE INDEX ag_toolkits_uuid_key    ON public.ag_toolkits USING btree (uuid);
CREATE INDEX ix_ag_toolkits_type            ON public.ag_toolkits USING btree (type);
CREATE INDEX ix_ag_toolkits_status          ON public.ag_toolkits USING btree (status);
CREATE INDEX ix_ag_toolkits_created_id      ON public.ag_toolkits USING btree (created_id);
CREATE INDEX ix_ag_toolkits_updated_id      ON public.ag_toolkits USING btree (updated_id);

COMMENT ON TABLE  ag_toolkits                      IS '工具包管理表';
COMMENT ON COLUMN ag_toolkits.id                   IS '主键ID';
COMMENT ON COLUMN ag_toolkits.uuid                 IS 'UUID全局唯一标识';
COMMENT ON COLUMN ag_toolkits.name                 IS '工具包名称';
COMMENT ON COLUMN ag_toolkits.type                 IS '类型(toolkit:整个类 function:单个函数)';
COMMENT ON COLUMN ag_toolkits.module_path          IS 'Python模块路径';
COMMENT ON COLUMN ag_toolkits.class_name           IS '类名（type=toolkit时使用）';
COMMENT ON COLUMN ag_toolkits.func_name            IS '函数名（type=function时使用）';
COMMENT ON COLUMN ag_toolkits.config               IS '初始化参数';
COMMENT ON COLUMN ag_toolkits.instructions         IS '工具使用说明';
COMMENT ON COLUMN ag_toolkits.requires_confirmation IS '是否需要确认';
COMMENT ON COLUMN ag_toolkits.approval_type        IS '审批类型(NULL/required/audit)';
COMMENT ON COLUMN ag_toolkits.stop_after_call      IS '调用后是否停止';
COMMENT ON COLUMN ag_toolkits.show_result          IS '是否展示结果';
COMMENT ON COLUMN ag_toolkits.cache_results        IS '是否缓存结果';
COMMENT ON COLUMN ag_toolkits.cache_ttl            IS '缓存TTL秒数';
COMMENT ON COLUMN ag_toolkits.status               IS '是否启用(0:启用 1:禁用)';
COMMENT ON COLUMN ag_toolkits.description          IS '备注/描述';
COMMENT ON COLUMN ag_toolkits.created_time         IS '创建时间';
COMMENT ON COLUMN ag_toolkits.updated_time         IS '更新时间';
COMMENT ON COLUMN ag_toolkits.created_id           IS '创建人ID';
COMMENT ON COLUMN ag_toolkits.updated_id           IS '更新人ID';
```

#### registry 中的构建方法

```python
def register_toolkit(self, toolkit_id: str, row) -> None:
    import importlib
    mod = importlib.import_module(row.module_path)
    config = row.config or {}

    if row.type == "toolkit":
        cls = getattr(mod, row.class_name)
        instance = cls(**config)
    else:
        func = getattr(mod, row.func_name)
        from agno.tools.function import Function
        instance = Function(entrypoint=func, **config)

    # 应用 approval 装饰器
    if row.approval_type in ("required", "audit"):
        from agno.approval import approval as approval_decorator
        for func in instance.functions.values():
            approval_decorator(type=row.approval_type)(func)

    self._toolkit_map[toolkit_id] = instance
```

#### CRUD 差异（相对 5.1 Models 模式）

> router.py / service.py / repo.py 结构同 5.1 Models。

- **create**：写 DB 后调用 `registry.register_toolkit(str(row.id), row)` 加入热区 `_toolkit_map`。
- **update**：重新调用 `registry.register_toolkit(str(row.id), row)`，用新实例覆盖旧实例。下次 `resolve_tools()` 返回的就是新对象，**无需重建 Agent**（callable factory 热生效）。
- **delete**：`registry._toolkit_map.pop(toolkit_id, None)`。同时删除 `ag_bindings` 中该 toolkit 的所有绑定，避免 `resolve_tools()` 返回 None。

---

### 5.6 Skills（技能）

#### 表设计

```sql
CREATE TABLE ag_skills (
    id            SERIAL NOT NULL,
    uuid          varchar(64) NOT NULL,
    name          varchar(255) NOT NULL,
    instructions  text NOT NULL,
    source_path   varchar(500),
    scripts       jsonb NOT NULL DEFAULT '[]',
    "references"  jsonb NOT NULL DEFAULT '[]',
    allowed_tools jsonb,
    metadata_config      jsonb NOT NULL DEFAULT '{}',
    status        varchar(10) NOT NULL DEFAULT '0',
    description   text,
    created_time  timestamp without time zone NOT NULL,
    updated_time  timestamp without time zone NOT NULL,
    created_id    integer,
    updated_id    integer,
    PRIMARY KEY(id),
    CONSTRAINT ag_skills_created_id_fkey FOREIGN KEY(created_id) REFERENCES sys_user(id),
    CONSTRAINT ag_skills_updated_id_fkey FOREIGN KEY(updated_id) REFERENCES sys_user(id)
);
CREATE UNIQUE INDEX ag_skills_uuid_key   ON public.ag_skills USING btree (uuid);
CREATE INDEX ix_ag_skills_status         ON public.ag_skills USING btree (status);
CREATE INDEX ix_ag_skills_created_id     ON public.ag_skills USING btree (created_id);
CREATE INDEX ix_ag_skills_updated_id     ON public.ag_skills USING btree (updated_id);

COMMENT ON TABLE  ag_skills                IS '技能管理表';
COMMENT ON COLUMN ag_skills.id             IS '主键ID';
COMMENT ON COLUMN ag_skills.uuid           IS 'UUID全局唯一标识';
COMMENT ON COLUMN ag_skills.name           IS '技能名称';
COMMENT ON COLUMN ag_skills.instructions   IS '注入Agent system prompt的技能指令';
COMMENT ON COLUMN ag_skills.source_path    IS '本地磁盘路径（可选）';
COMMENT ON COLUMN ag_skills.scripts        IS '脚本文件名列表';
COMMENT ON COLUMN ag_skills."references"   IS '参考文件名列表';
COMMENT ON COLUMN ag_skills.allowed_tools  IS '允许使用的工具列表';
COMMENT ON COLUMN ag_skills.metadata_config       IS '元数据';
COMMENT ON COLUMN ag_skills.status         IS '是否启用(0:启用 1:禁用)';
COMMENT ON COLUMN ag_skills.description    IS '备注/描述';
COMMENT ON COLUMN ag_skills.created_time   IS '创建时间';
COMMENT ON COLUMN ag_skills.updated_time   IS '更新时间';
COMMENT ON COLUMN ag_skills.created_id     IS '创建人ID';
COMMENT ON COLUMN ag_skills.updated_id     IS '更新人ID';
```

#### 与 Agno 交互流程

```
ag_skills 一行 + ag_bindings（owner=agent, resource_type='skill'）
  │
  ├─ 启动时：registry.load_skill_rows() 将所有 enabled 行存入 _skill_rows
  │
  └─ create_agent 时：
       bindings = SyncBindingRepo.get_active(agent_id, "agent", resource_type='skill')
       skills_obj = registry.build_skills(agent_id, bindings)
       Agent(skills=skills_obj, ...)

注意：Skills 不支持 callable factory 热插拔（Agno 不对 skills 参数逐 run 回调）。
变更 skill 绑定后需调用 registry.rebuild_agent(agent_id) 重建 Agent 实例。
```

**Skills vs Tools 的区别：**

| 方面 | Tools | Skills |
|------|-------|--------|
| 热插拔方式 | callable factory，无需重建 | 需重建 Agent 实例 |
| Agno 参数 | `tools=lambda: ...` | `skills=Skills(loaders=[...])` |
| 运行时行为 | 每次 run 重新解析 | 启动/重建时一次性加载 |
| 变更频率 | 高（可随时开关） | 低（少量变更） |

#### DBSkillLoader（自定义加载器）

```python
# app/skills/db_loader.py
from agno.skills.loaders.base import SkillLoader
from agno.skills.skill import Skill


class DBSkillLoader(SkillLoader):
    """从 _skill_rows 缓存构建 Skill 对象（不读 DB，不读文件系统）。"""

    def __init__(self, skill_rows: list):
        self._rows = skill_rows   # 已过滤好的行列表

    def load(self) -> list[Skill]:
        skills = []
        for row in self._rows:
            skills.append(Skill(
                name=row.name,
                description=row.description or "",
                instructions=row.instructions,
                source_path=row.source_path or "",
                scripts=row.scripts or [],
                references=row.references or [],
                metadata_config=row.metadata_config or {},
                allowed_tools=row.allowed_tools,
            ))
        return skills
```

#### registry 中的构建方法

```python
def load_skill_rows(self, rows: list) -> None:
    """启动时将所有 skill 行缓存到 _skill_rows。"""
    for row in rows:
        self._skill_rows[str(row.id)] = row

def build_skills(self, agent_id: str, bindings: list) -> Any | None:
    """
    根据 bindings 列表（resource_type='skill'）构建 Skills 实例。
    bindings 来自 SyncBindingRepo.get_active(agent_id, "agent", resource_type='skill')。
    """
    from agno.skills import Skills
    from app.skills.db_loader import DBSkillLoader

    rows = []
    for b in bindings:
        row = self._skill_rows.get(b.resource_id)
        if row and row.enabled:
            rows.append(row)

    if not rows:
        return None

    return Skills(loaders=[DBSkillLoader(rows)])

async def rebuild_agent(self, agent_id: str) -> None:
    """
    热更新：重建 Agent 实例并原子替换列表中的引用。
    用于 Skill/Memory/Learning 等不走 callable factory 的字段变更。
    需要从 DB 重新读取最新的 agent 行。
    """
    old = self._agents_map.get(agent_id)
    if old is None:
        return

    # 从 DB 重新读取最新行（调用方已更新 DB）
    from modules.agents.repo import AgentRepo
    from core.db import AsyncSessionLocal
    async with AsyncSessionLocal() as db:
        row = await AgentRepo(db).get(agent_id)
    if not row:
        return

    new_agent = await self.create_agent(row)  # 传 row，与 create_agent 签名一致
    # 注意：create_agent 内部会 append 到 self.agents，需先从列表移除旧实例
    self.agents[:] = [a for a in self.agents if (a.agent_id or a.id) != agent_id]

    # 替换共享列表中的引用（AgentOS 持有同一个 list 对象）
    for i, a in enumerate(self.agents):
        if (a.agent_id or a.id) == agent_id:
            self.agents[i] = new_agent
            break
```

#### router.py

```python
# app/skills/router.py
from uuid import UUID
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from core.deps import get_db, get_registry
from .schemas import SkillCreate, SkillUpdate, SkillResponse
from .service import SkillService

router = APIRouter(prefix="/skills", tags=["Skills"])


def svc(db=Depends(get_db), reg=Depends(get_registry)):
    return SkillService(db, reg)


@router.get("", response_model=list[SkillResponse])
async def list_skills(s=Depends(svc)):
    return await s.list()


@router.post("", response_model=SkillResponse, status_code=201)
async def create_skill(body: SkillCreate, s=Depends(svc)):
    return await s.create(body)


@router.get("/{skill_id}", response_model=SkillResponse)
async def get_skill(skill_id: UUID, s=Depends(svc)):
    return await s.get(str(skill_id))


@router.patch("/{skill_id}", response_model=SkillResponse)
async def update_skill(skill_id: UUID, body: SkillUpdate, s=Depends(svc)):
    return await s.update(str(skill_id), body)


@router.delete("/{skill_id}", status_code=204)
async def delete_skill(skill_id: UUID, s=Depends(svc)):
    await s.delete(str(skill_id))
```

#### service.py

```python
# app/skills/service.py
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from .schemas import SkillCreate, SkillUpdate


class SkillService:
    def __init__(self, db: AsyncSession, registry):
        self.db = db
        self.reg = registry

    async def list(self):
        result = await self.db.execute(
            text("SELECT * FROM ag_skills WHERE enabled=true ORDER BY name")
        )
        return result.fetchall()

    async def get(self, skill_id: str):
        result = await self.db.execute(
            text("SELECT * FROM ag_skills WHERE id=:id"), {"id": skill_id}
        )
        row = result.fetchone()
        if not row:
            raise ValueError(f"Skill {skill_id} not found")
        return row

    async def create(self, body: SkillCreate):
        result = await self.db.execute(
            text("""
                INSERT INTO ag_skills
                    (name, description, instructions, source_path, scripts, references, allowed_tools, metadata_config)
                VALUES (:name, :desc, :instructions, :source_path,
                        :scripts::jsonb, :references::jsonb, :allowed_tools::jsonb, :metadata_config::jsonb)
                RETURNING *
            """),
            {
                "name": body.name,
                "desc": body.description,
                "instructions": body.instructions,
                "source_path": body.source_path,
                "scripts": body.scripts_json,
                "references": body.references_json,
                "allowed_tools": body.allowed_tools_json,
                "metadata_config": body.metadata_json,
            },
        )
        await self.db.commit()
        row = result.fetchone()
        # 更新 registry 缓存
        self.reg.load_skill_rows([row])
        return row

    async def update(self, skill_id: str, body: SkillUpdate):
        result = await self.db.execute(
            text("""
                UPDATE ag_skills SET
                    name=COALESCE(:name, name),
                    description=COALESCE(:desc, description),
                    instructions=COALESCE(:instructions, instructions),
                    metadata_config=COALESCE(:metadata_config::jsonb, metadata_config)
                WHERE id=:id RETURNING *
            """),
            {"id": skill_id, "name": body.name, "desc": body.description,
             "instructions": body.instructions, "metadata_config": body.metadata_json},
        )
        await self.db.commit()
        row = result.fetchone()
        # 更新 registry 缓存
        if row:
            self.reg.load_skill_rows([row])
        return row

    async def delete(self, skill_id: str):
        await self.db.execute(
            text("UPDATE ag_skills SET enabled=false WHERE id=:id"),
            {"id": skill_id},
        )
        await self.db.commit()
        # 从缓存移除
        self.reg._skill_rows.pop(skill_id, None)
```

---

### 5.7 Knowledge Bases（知识库）

#### 表设计

```sql
CREATE TABLE ag_knowledge_bases (
    id              SERIAL NOT NULL,
    uuid            varchar(64) NOT NULL,
    name            varchar(255) NOT NULL,
    vectordb_id     integer NOT NULL,
    max_results     integer NOT NULL DEFAULT 10,
    reader_type     varchar(50),
    reader_config   jsonb NOT NULL DEFAULT '{}',
    default_filters jsonb,
    status          varchar(10) NOT NULL DEFAULT '0',
    description     text,
    created_time    timestamp without time zone NOT NULL,
    updated_time    timestamp without time zone NOT NULL,
    created_id      integer,
    updated_id      integer,
    PRIMARY KEY(id),
    CONSTRAINT ag_knowledge_bases_vectordb_id_fkey FOREIGN KEY(vectordb_id) REFERENCES ag_vectordbs(id),
    CONSTRAINT ag_knowledge_bases_created_id_fkey  FOREIGN KEY(created_id)  REFERENCES sys_user(id),
    CONSTRAINT ag_knowledge_bases_updated_id_fkey  FOREIGN KEY(updated_id)  REFERENCES sys_user(id)
);
CREATE UNIQUE INDEX ag_knowledge_bases_uuid_key  ON public.ag_knowledge_bases USING btree (uuid);
CREATE INDEX ix_ag_knowledge_bases_vectordb_id   ON public.ag_knowledge_bases USING btree (vectordb_id);
CREATE INDEX ix_ag_knowledge_bases_status        ON public.ag_knowledge_bases USING btree (status);
CREATE INDEX ix_ag_knowledge_bases_created_id    ON public.ag_knowledge_bases USING btree (created_id);
CREATE INDEX ix_ag_knowledge_bases_updated_id    ON public.ag_knowledge_bases USING btree (updated_id);

COMMENT ON TABLE  ag_knowledge_bases                IS '知识库管理表';
COMMENT ON COLUMN ag_knowledge_bases.id             IS '主键ID';
COMMENT ON COLUMN ag_knowledge_bases.uuid           IS 'UUID全局唯一标识';
COMMENT ON COLUMN ag_knowledge_bases.name           IS '知识库名称';
COMMENT ON COLUMN ag_knowledge_bases.vectordb_id    IS '关联向量数据库ID';
COMMENT ON COLUMN ag_knowledge_bases.max_results    IS '最大检索结果数';
COMMENT ON COLUMN ag_knowledge_bases.reader_type    IS '文档读取器类型(pdf/web/docx/csv/json/text)';
COMMENT ON COLUMN ag_knowledge_bases.reader_config  IS '读取器配置参数';
COMMENT ON COLUMN ag_knowledge_bases.default_filters IS '默认搜索过滤条件';
COMMENT ON COLUMN ag_knowledge_bases.status         IS '是否启用(0:启用 1:禁用)';
COMMENT ON COLUMN ag_knowledge_bases.description    IS '备注/描述';
COMMENT ON COLUMN ag_knowledge_bases.created_time   IS '创建时间';
COMMENT ON COLUMN ag_knowledge_bases.updated_time   IS '更新时间';
COMMENT ON COLUMN ag_knowledge_bases.created_id     IS '创建人ID';
COMMENT ON COLUMN ag_knowledge_bases.updated_id     IS '更新人ID';

CREATE TABLE ag_documents (
    id            SERIAL NOT NULL,
    uuid          varchar(64) NOT NULL,
    kb_id         integer NOT NULL,
    name          varchar(500),
    storage_type  varchar(20) NOT NULL DEFAULT 'local',
    storage_path  text NOT NULL,
    doc_status    varchar(20) NOT NULL DEFAULT 'pending',
    error_msg     text,
    metadata_config      jsonb NOT NULL DEFAULT '{}',
    status        varchar(10) NOT NULL DEFAULT '0',
    description   text,
    created_time  timestamp without time zone NOT NULL,
    updated_time  timestamp without time zone NOT NULL,
    created_id    integer,
    updated_id    integer,
    PRIMARY KEY(id),
    CONSTRAINT ag_documents_kb_id_fkey         FOREIGN KEY(kb_id)      REFERENCES ag_knowledge_bases(id) ON DELETE CASCADE,
    CONSTRAINT ag_documents_created_id_fkey    FOREIGN KEY(created_id) REFERENCES sys_user(id),
    CONSTRAINT ag_documents_updated_id_fkey    FOREIGN KEY(updated_id) REFERENCES sys_user(id)
);
CREATE UNIQUE INDEX ag_documents_uuid_key   ON public.ag_documents USING btree (uuid);
CREATE INDEX ix_ag_documents_kb_id          ON public.ag_documents USING btree (kb_id);
CREATE INDEX ix_ag_documents_doc_status     ON public.ag_documents USING btree (kb_id, doc_status);
CREATE INDEX ix_ag_documents_status         ON public.ag_documents USING btree (status);
CREATE INDEX ix_ag_documents_created_id     ON public.ag_documents USING btree (created_id);
CREATE INDEX ix_ag_documents_updated_id     ON public.ag_documents USING btree (updated_id);

COMMENT ON TABLE  ag_documents               IS '知识库文档管理表';
COMMENT ON COLUMN ag_documents.id            IS '主键ID';
COMMENT ON COLUMN ag_documents.uuid          IS 'UUID全局唯一标识';
COMMENT ON COLUMN ag_documents.kb_id         IS '所属知识库ID';
COMMENT ON COLUMN ag_documents.name          IS '文档名称';
COMMENT ON COLUMN ag_documents.storage_type  IS '存储类型(local/s3/gcs/url)';
COMMENT ON COLUMN ag_documents.storage_path  IS '存储路径或URL';
COMMENT ON COLUMN ag_documents.doc_status    IS '处理状态(pending/processing/indexed/failed)';
COMMENT ON COLUMN ag_documents.error_msg     IS '处理失败错误信息';
COMMENT ON COLUMN ag_documents.metadata_config      IS '文档元数据';
COMMENT ON COLUMN ag_documents.status        IS '是否启用(0:启用 1:禁用)';
COMMENT ON COLUMN ag_documents.description   IS '备注/描述';
COMMENT ON COLUMN ag_documents.created_time  IS '创建时间';
COMMENT ON COLUMN ag_documents.updated_time  IS '更新时间';
COMMENT ON COLUMN ag_documents.created_id    IS '创建人ID';
COMMENT ON COLUMN ag_documents.updated_id    IS '更新人ID';
```

#### 与 Agno 交互流程

```
ag_knowledge_bases 一行
  │  （首次访问冷启动，LRU maxsize=50）
  │
  ├─ 1. 取 vectordb_id → build_vectordb(row)
  │      → PgVector(table_name=..., db_engine=shared_engine, embedder=...)
  │
  └─ 2. Knowledge(name=row.name, vector_db=vectordb, max_results=row.max_results)

文档索引流程：
  POST /management/knowledge/{id}/documents
    → 存文件到对象存储
    → ag_documents status='pending'
    → 后台任务：
        kb = registry.get_or_build_knowledge(kb_id, row)
        kb.load_document(path)   # 分块 → embed → 写入 vector_db
        ag_documents status='indexed'
```

#### registry 中的构建方法

```python
def get_or_build_knowledge(self, kb_id: str, row) -> Any:
    """LRU 冷热管理：依赖 vectordb（已在 build_vectordb 中构建）"""
    obj = self._knowledge_cache.get(kb_id)
    if obj:
        return obj

    from agno.knowledge import Knowledge

    # 1. 构建底层 vectordb
    vectordb_row = self._vectordb_rows.get(str(row.vectordb_id))
    if not vectordb_row:
        raise ValueError(f"VectorDB {row.vectordb_id} not found")
    vector_db = self.build_vectordb(vectordb_row)

    # 2. 构建 Knowledge 实例
    obj = Knowledge(
        name=row.name,
        vector_db=vector_db,
        max_results=row.max_results,
        search_filters=row.default_filters,
    )

    self._knowledge_cache.set(kb_id, obj)
    return obj

def register_knowledge_row(self, kb_id: str, row) -> None:
    """启动时预存 row 引用，供 get_or_build_knowledge 使用"""
    self._vectordb_rows[str(row.vectordb_id)] = row  # 需同步存 vectordb row
    self._kb_rows[kb_id] = row
```

> `_vectordb_rows` 和 `_kb_rows` 是 RuntimeRegistry 新增的 dict，启动预热时顺序：vectordb rows → knowledge rows → agents。

#### CRUD 差异（相对 5.1 Models 模式）

> router.py / service.py / repo.py 结构同 5.1 Models。KB 额外有 `/documents` 子资源路由。

- **create KB**：写 DB 后 `registry._kb_rows[str(row.id)] = row`（懒建，LRU 首次访问时构建）。
- **update KB**：更新行缓存，驱逐 LRU：`registry._knowledge_cache.remove(kb_id)`。
- **delete KB**：`registry._kb_rows.pop(kb_id, None)`；`registry._knowledge_cache.remove(kb_id)`；删除 ag_bindings 对应绑定。
- **上传文档**（`POST /knowledge/{id}/documents`）：保存文件 → 写 ag_documents status='pending' → **后台任务**（BackgroundTasks）调用 `kb.load_document(path)` 完成向量化，完成后更新 status='indexed'。
- **文档索引失败**：status='failed' + error_msg；不影响其他文档。

---

### 5.8 Hooks（中间件）

#### 表设计

```sql
CREATE TABLE ag_hooks (
    id                  SERIAL NOT NULL,
    uuid                varchar(64) NOT NULL,
    name                varchar(255) NOT NULL,
    hook_type           varchar(20) NOT NULL,
    module_path         varchar(500) NOT NULL,
    func_name           varchar(255) NOT NULL,
    config              jsonb NOT NULL DEFAULT '{}',
    run_in_background   boolean NOT NULL DEFAULT false,
    status              varchar(10) NOT NULL DEFAULT '0',
    description         text,
    created_time        timestamp without time zone NOT NULL,
    updated_time        timestamp without time zone NOT NULL,
    created_id          integer,
    updated_id          integer,
    PRIMARY KEY(id),
    CONSTRAINT ag_hooks_created_id_fkey FOREIGN KEY(created_id) REFERENCES sys_user(id),
    CONSTRAINT ag_hooks_updated_id_fkey FOREIGN KEY(updated_id) REFERENCES sys_user(id)
);
CREATE UNIQUE INDEX ag_hooks_uuid_key   ON public.ag_hooks USING btree (uuid);
CREATE INDEX ix_ag_hooks_hook_type      ON public.ag_hooks USING btree (hook_type);
CREATE INDEX ix_ag_hooks_status         ON public.ag_hooks USING btree (status);
CREATE INDEX ix_ag_hooks_created_id     ON public.ag_hooks USING btree (created_id);
CREATE INDEX ix_ag_hooks_updated_id     ON public.ag_hooks USING btree (updated_id);

COMMENT ON TABLE  ag_hooks                    IS '钩子中间件管理表';
COMMENT ON COLUMN ag_hooks.id                 IS '主键ID';
COMMENT ON COLUMN ag_hooks.uuid               IS 'UUID全局唯一标识';
COMMENT ON COLUMN ag_hooks.name               IS 'Hook名称';
COMMENT ON COLUMN ag_hooks.hook_type          IS 'Hook类型(pre/post/tool)';
COMMENT ON COLUMN ag_hooks.module_path        IS 'Python模块路径';
COMMENT ON COLUMN ag_hooks.func_name          IS '函数名';
COMMENT ON COLUMN ag_hooks.config             IS '额外配置参数';
COMMENT ON COLUMN ag_hooks.run_in_background  IS '是否后台运行（不阻塞响应）';
COMMENT ON COLUMN ag_hooks.status             IS '是否启用(0:启用 1:禁用)';
COMMENT ON COLUMN ag_hooks.description        IS '备注/描述';
COMMENT ON COLUMN ag_hooks.created_time       IS '创建时间';
COMMENT ON COLUMN ag_hooks.updated_time       IS '更新时间';
COMMENT ON COLUMN ag_hooks.created_id         IS '创建人ID';
COMMENT ON COLUMN ag_hooks.updated_id         IS '更新人ID';
```

#### registry 中的构建方法

```python
def register_hook(self, hook_id: str, row) -> None:
    """动态 import hook 函数，存入 _hook_map"""
    import importlib
    mod = importlib.import_module(row.module_path)
    func = getattr(mod, row.func_name)

    # 如需后台运行，用 @hook(run_in_background=True) 包装
    if row.run_in_background:
        from agno.hooks.decorator import hook
        func = hook(run_in_background=True)(func)

    self._hook_map[hook_id] = {"func": func, "hook_type": row.hook_type}

def resolve_hooks(self, agent_id: str, hook_type: str) -> list:
    """Callable factory 调用，返回指定类型的 hook 函数列表"""
    from modules.bindings.repo import SyncBindingRepo
    result = []
    for b in SyncBindingRepo.get_active(agent_id, "agent", resource_type="hook"):
        entry = self._hook_map.get(b.resource_id)
        if entry and entry["hook_type"] == hook_type:
            result.append(entry["func"])
    return result
```

> Agent 创建时：`pre_hooks=lambda: resolve_hooks(aid, "pre")`, `post_hooks=lambda: resolve_hooks(aid, "post")`, `tool_hooks=lambda: resolve_hooks(aid, "tool")`

#### CRUD 差异（相对 5.1 Models 模式）

> router.py / service.py / repo.py 结构同 5.1 Models。

- **Hook 存的是 Python 可调用对象**，写在 `config.function_path`（`module:function` 格式）或 `config.code`（内联代码字符串）。
- **create / update**：写 DB 后重新调用 `registry.register_hook(str(row.id), row)`，覆盖 `_hook_map` 中的旧函数。下次 run 时 callable factory 自动取到新函数，**无需重建 Agent**。
- **delete**：`registry._hook_map.pop(hook_id, None)`；删除 ag_bindings 对应绑定。

---

### 5.9 Guardrails（护栏）

#### 表设计

```sql
CREATE TABLE ag_guardrails (
    id            SERIAL NOT NULL,
    uuid          varchar(64) NOT NULL,
    name          varchar(255) NOT NULL,
    type          varchar(50) NOT NULL,
    hook_type     varchar(20) NOT NULL,
    config        jsonb NOT NULL DEFAULT '{}',
    module_path   varchar(500),
    class_name    varchar(255),
    status        varchar(10) NOT NULL DEFAULT '0',
    description   text,
    created_time  timestamp without time zone NOT NULL,
    updated_time  timestamp without time zone NOT NULL,
    created_id    integer,
    updated_id    integer,
    PRIMARY KEY(id),
    CONSTRAINT ag_guardrails_created_id_fkey FOREIGN KEY(created_id) REFERENCES sys_user(id),
    CONSTRAINT ag_guardrails_updated_id_fkey FOREIGN KEY(updated_id) REFERENCES sys_user(id)
);
CREATE UNIQUE INDEX ag_guardrails_uuid_key   ON public.ag_guardrails USING btree (uuid);
CREATE INDEX ix_ag_guardrails_type           ON public.ag_guardrails USING btree (type);
CREATE INDEX ix_ag_guardrails_hook_type      ON public.ag_guardrails USING btree (hook_type);
CREATE INDEX ix_ag_guardrails_status         ON public.ag_guardrails USING btree (status);
CREATE INDEX ix_ag_guardrails_created_id     ON public.ag_guardrails USING btree (created_id);
CREATE INDEX ix_ag_guardrails_updated_id     ON public.ag_guardrails USING btree (updated_id);

COMMENT ON TABLE  ag_guardrails              IS '护栏管理表';
COMMENT ON COLUMN ag_guardrails.id           IS '主键ID';
COMMENT ON COLUMN ag_guardrails.uuid         IS 'UUID全局唯一标识';
COMMENT ON COLUMN ag_guardrails.name         IS '护栏名称';
COMMENT ON COLUMN ag_guardrails.type         IS '护栏类型(openai_moderation/pii/prompt_injection/custom)';
COMMENT ON COLUMN ag_guardrails.hook_type    IS '作用阶段(pre/post)';
COMMENT ON COLUMN ag_guardrails.config       IS '护栏配置参数';
COMMENT ON COLUMN ag_guardrails.module_path  IS '自定义护栏模块路径（type=custom时使用）';
COMMENT ON COLUMN ag_guardrails.class_name   IS '自定义护栏类名（type=custom时使用）';
COMMENT ON COLUMN ag_guardrails.status       IS '是否启用(0:启用 1:禁用)';
COMMENT ON COLUMN ag_guardrails.description  IS '备注/描述';
COMMENT ON COLUMN ag_guardrails.created_time IS '创建时间';
COMMENT ON COLUMN ag_guardrails.updated_time IS '更新时间';
COMMENT ON COLUMN ag_guardrails.created_id   IS '创建人ID';
COMMENT ON COLUMN ag_guardrails.updated_id   IS '更新人ID';
```

#### registry 中的构建方法

```python
def register_guardrail(self, guardrail_id: str, row) -> None:
    config = row.config or {}

    if row.type == "openai_moderation":
        from agno.guardrails.openai import OpenAIModerationGuardrail
        obj = OpenAIModerationGuardrail(
            moderation_model=config.get("moderation_model", "omni-moderation-latest"),
            raise_for_categories=config.get("raise_for_categories"),
        )
    elif row.type == "pii":
        from agno.guardrails.pii import PIIDetectionGuardrail
        obj = PIIDetectionGuardrail(
            mask_pii=config.get("mask_pii", False),
            enable_email_check=config.get("enable_email_check", True),
        )
    elif row.type == "prompt_injection":
        from agno.guardrails.prompt_injection import PromptInjectionGuardrail
        obj = PromptInjectionGuardrail(
            injection_patterns=config.get("injection_patterns"),
        )
    elif row.type == "custom":
        import importlib
        mod = importlib.import_module(row.module_path)
        cls = getattr(mod, row.class_name)
        obj = cls(**config)
    else:
        raise ValueError(f"Unsupported guardrail type: {row.type}")

    self._guardrail_map[guardrail_id] = {"obj": obj, "hook_type": row.hook_type}

def resolve_guardrails(self, agent_id: str, hook_type: str) -> list:
    """返回指定 pre/post 的 guardrail 列表，和 hooks 一同放入 pre_hooks/post_hooks"""
    from modules.bindings.repo import SyncBindingRepo
    result = []
    for b in SyncBindingRepo.get_active(agent_id, "agent", resource_type="guardrail"):
        entry = self._guardrail_map.get(b.resource_id)
        if entry and entry["hook_type"] == hook_type:
            result.append(entry["obj"])
    return result
```

#### CRUD 差异（相对 5.1 Models 模式）

> router.py / service.py / repo.py 结构同 5.1 Models。

- **create / update**：写 DB 后调用 `registry.register_guardrail(str(row.id), row)`，覆盖 `_guardrail_map`。下次 run 时通过 callable factory 生效，**无需重建 Agent**。
- **delete**：`registry._guardrail_map.pop(guardrail_id, None)`；删除 ag_bindings 对应绑定。
- 4 种类型（`input_filter` / `output_filter` / `content_filter` / `semantic`）存入 `hook_type` 字段，`resolve_guardrails()` 按 hook_type 过滤。

---

### 5.10 Memory Managers

#### 表设计

```sql
CREATE TABLE ag_memory_managers (
    id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name         VARCHAR(255) NOT NULL,
    -- Agno: MemoryManager.model
    model_id     UUID REFERENCES ag_models(id),
    -- Agno: MemoryManager.delete_memories
    delete_memories  BOOLEAN NOT NULL DEFAULT false,
    -- Agno: MemoryManager.update_memories
    update_memories  BOOLEAN NOT NULL DEFAULT true,
    -- Agno: MemoryManager.add_memories
    add_memories     BOOLEAN NOT NULL DEFAULT true,
    -- Agno: MemoryManager.clear_memories
    clear_memories   BOOLEAN NOT NULL DEFAULT false,
    -- Agno: MemoryManager.memory_capture_instructions
    memory_capture_instructions TEXT,
    additional_instructions     TEXT,
    enabled      BOOLEAN NOT NULL DEFAULT true,
    created_at   TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at   TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TRIGGER trg_memory_managers_updated_at
    BEFORE UPDATE ON ag_memory_managers
    FOR EACH ROW EXECUTE FUNCTION fn_update_updated_at();
```

#### registry 中的构建方法

```python
def build_memory_manager(self, row, agno_db) -> Any:
    """
    构建 MemoryManager，注入 Agno DB（agno_user_memory 表由 Agno 自动管理）。
    每次 create_agent 调用，不缓存（内含状态）。
    """
    from agno.memory.manager import MemoryManager
    model = self._model_cache.get(str(row.model_id)) if row.model_id else None
    return MemoryManager(
        model=model,
        db=agno_db,
        delete_memories=row.delete_memories,
        update_memories=row.update_memories,
        add_memories=row.add_memories,
        memory_capture_instructions=row.memory_capture_instructions,
    )
```

#### CRUD 差异（相对 5.1 Models 模式）

> router.py / service.py / repo.py 结构同 5.1 Models。

- **Memory Manager 不缓存**：每次 `create_agent` 时实时构建，不存入任何 map。
- **create**：写 DB，加入 `_memory_manager_rows`。
- **update**：更新行缓存 `_memory_manager_rows[mid] = row`；查出所有 `memory_manager_id=mid` 的 agent，逐一调用 `registry.rebuild_agent(agent_id)`（重建 Agent 实例）。
- **delete**：同上；rebuild 受影响的 agents（它们将以 `memory=None` 重建）。

---

### 5.11 Learning Configs

#### 表设计

```sql
CREATE TABLE ag_learning_configs (
    id        UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name      VARCHAR(255) NOT NULL,
    -- Agno: LearningMachine.model
    model_id  UUID REFERENCES ag_models(id),
    namespace VARCHAR(255) NOT NULL DEFAULT 'global',
    -- Agno: LearningMachine.user_profile（UserProfileConfig）
    -- {enabled, mode: always/agentic/propose/hitl, enable_update_profile}
    user_profile      JSONB,
    -- Agno: LearningMachine.user_memory（UserMemoryConfig）
    user_memory       JSONB,
    -- Agno: LearningMachine.session_context（SessionContextConfig）
    session_context   JSONB,
    -- Agno: LearningMachine.entity_memory（EntityMemoryConfig）
    entity_memory     JSONB,
    -- Agno: LearningMachine.learned_knowledge（LearnedKnowledgeConfig）
    learned_knowledge JSONB,
    -- Agno: LearningMachine.decision_log（DecisionLogConfig）
    decision_log      JSONB,
    enabled   BOOLEAN NOT NULL DEFAULT true,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TRIGGER trg_learning_configs_updated_at
    BEFORE UPDATE ON ag_learning_configs
    FOR EACH ROW EXECUTE FUNCTION fn_update_updated_at();
```
    """构建 LearningMachine，每次 create_agent 调用，不缓存"""
    from agno.learn.machine import LearningMachine
    model = self._model_cache.get(str(row.model_id)) if row.model_id else None
    return LearningMachine(
        db=agno_db,
        model=model,
        namespace=row.namespace,
        user_profile=row.user_profile or False,
        user_memory=row.user_memory or False,
        session_context=row.session_context or False,
        entity_memory=row.entity_memory or False,
        learned_knowledge=row.learned_knowledge or False,
        decision_log=row.decision_log or False,
    )
```

#### CRUD 差异（相对 5.1 Models 模式）

> router.py / service.py / repo.py 结构同 5.1 Models。

- 与 5.10 相同：**不缓存**，每次 `create_agent` 时构建。
- **update / delete**：更新 `_learning_rows`，rebuild 所有 `learning_config_id=lid` 的 agents。

---

### 5.12 Sub-Managers（推理/压缩/摘要/文化）

```sql
-- Agno: ReasoningConfig
CREATE TABLE ag_reasoning_configs (
    id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name         VARCHAR(255) NOT NULL,
    -- Agno: ReasoningConfig.model
    model_id     UUID REFERENCES ag_models(id),
    -- Agno: Agent.reasoning_min_steps
    min_steps    INT NOT NULL DEFAULT 1,
    -- Agno: Agent.reasoning_max_steps
    max_steps    INT NOT NULL DEFAULT 10,
    use_json_mode BOOLEAN NOT NULL DEFAULT false,
    tool_call_limit INT,
    debug_mode   BOOLEAN NOT NULL DEFAULT false,
    enabled      BOOLEAN NOT NULL DEFAULT true,
    created_at   TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at   TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TRIGGER trg_reasoning_configs_updated_at
    BEFORE UPDATE ON ag_reasoning_configs
    FOR EACH ROW EXECUTE FUNCTION fn_update_updated_at();

-- Agno: CompressionManager
CREATE TABLE ag_compression_configs (
    id                           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name                         VARCHAR(255) NOT NULL,
    -- Agno: CompressionManager.model
    model_id                     UUID REFERENCES ag_models(id),
    -- Agno: CompressionManager.compress_tool_results_limit
    compress_tool_results_limit  INT,
    -- Agno: CompressionManager.compress_token_limit
    compress_token_limit         INT,
    compress_tool_call_instructions TEXT,
    enabled                      BOOLEAN NOT NULL DEFAULT true,
    created_at                   TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at                   TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TRIGGER trg_compression_configs_updated_at
    BEFORE UPDATE ON ag_compression_configs
    FOR EACH ROW EXECUTE FUNCTION fn_update_updated_at();

-- Agno: SessionSummaryManager
CREATE TABLE ag_sess_summary_configs (
    id                      UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name                    VARCHAR(255) NOT NULL,
    -- Agno: SessionSummaryManager.model
    model_id                UUID REFERENCES ag_models(id),
    session_summary_prompt  TEXT,
    summary_request_message TEXT DEFAULT 'Provide the summary of the conversation.',
    enabled                 BOOLEAN NOT NULL DEFAULT true,
    created_at              TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at              TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TRIGGER trg_session_summary_configs_updated_at
    BEFORE UPDATE ON ag_sess_summary_configs
    FOR EACH ROW EXECUTE FUNCTION fn_update_updated_at();

-- Agno: CultureManager（实验性）
CREATE TABLE ag_culture_configs (
    id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name         VARCHAR(255) NOT NULL,
    model_id     UUID REFERENCES ag_models(id),
    add_knowledge    BOOLEAN NOT NULL DEFAULT true,
    update_knowledge BOOLEAN NOT NULL DEFAULT true,
    delete_knowledge BOOLEAN NOT NULL DEFAULT true,
    clear_knowledge  BOOLEAN NOT NULL DEFAULT true,
    culture_capture_instructions TEXT,
    additional_instructions      TEXT,
    debug_mode   BOOLEAN NOT NULL DEFAULT false,
    enabled      BOOLEAN NOT NULL DEFAULT true,
    created_at   TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at   TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TRIGGER trg_culture_configs_updated_at
    BEFORE UPDATE ON ag_culture_configs
    FOR EACH ROW EXECUTE FUNCTION fn_update_updated_at();
```

#### registry 中的构建方法

```python
def build_reasoning_config(self, row) -> Any:
    from agno.reasoning.manager import ReasoningConfig
    model = self._model_cache.get(str(row.model_id)) if row.model_id else None
    return ReasoningConfig(
        model=model,
        min_steps=row.min_steps,
        max_steps=row.max_steps,
        use_json_mode=row.use_json_mode,
        tool_call_limit=row.tool_call_limit,
        debug_mode=row.debug_mode,
    )

def build_compression_manager(self, row) -> Any:
    from agno.compression.manager import CompressionManager
    model = self._model_cache.get(str(row.model_id)) if row.model_id else None
    return CompressionManager(
        model=model,
        compress_tool_results_limit=row.compress_tool_results_limit,
        compress_token_limit=row.compress_token_limit,
        compress_tool_call_instructions=row.compress_tool_call_instructions,
    )

def build_session_summary_manager(self, row, agno_db) -> Any:
    from agno.session.summary import SessionSummaryManager
    model = self._model_cache.get(str(row.model_id)) if row.model_id else None
    return SessionSummaryManager(
        model=model,
        db=agno_db,
        session_summary_prompt=row.session_summary_prompt,
        summary_request_message=row.summary_request_message,
    )

def build_culture_manager(self, row, agno_db) -> Any:
    from agno.culture.manager import CultureManager
    model = self._model_cache.get(str(row.model_id)) if row.model_id else None
    return CultureManager(
        model=model,
        db=agno_db,
        add_knowledge=row.add_knowledge,
        update_knowledge=row.update_knowledge,
        delete_knowledge=row.delete_knowledge,
        clear_knowledge=row.clear_knowledge,
        culture_capture_instructions=row.culture_capture_instructions,
        additional_instructions=row.additional_instructions,
        debug_mode=row.debug_mode,
    )
```

#### CRUD 差异（相对 5.1 Models 模式）

> router.py / service.py / repo.py 结构同 5.1 Models。4 种 sub-manager（reasoning/compression/session_summary/culture）各自一套路由，或合并为 `/sub-managers?type=reasoning`。

- **所有 Sub-Manager 均不缓存**（每次 `create_agent` 时重建）。
- **update / delete**：更新对应行缓存（`_reasoning_rows` / `_compression_rows` / `_session_summary_rows` / `_culture_rows`）；查出所有使用此 config_id 的 agents，逐一 `registry.rebuild_agent(agent_id)`。
- **注意**：`ag_culture_configs` 对应 `_culture_rows`（需在 `RuntimeRegistry.__init__` 和 lifespan 中补充此字段；可在下个版本添加）。

---

### 5.13 Agents（核心）

#### 表设计

```sql
CREATE TABLE ag_agents (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name        VARCHAR(255) NOT NULL,
    description TEXT,

    -- ── 模型 ───────────────────────────────────────────────
    -- Agno: Agent.model
    model_id              UUID REFERENCES ag_models(id),
    -- Agno: Agent.reasoning_model
    reasoning_model_id    UUID REFERENCES ag_models(id),
    -- Agno: Agent.response_model（output schema 对应的模型）
    output_model_id       UUID REFERENCES ag_models(id),
    -- Agno: Agent.parser_model
    parser_model_id       UUID REFERENCES ag_models(id),

    -- ── 子管理器 ────────────────────────────────────────────
    -- Agno: Agent.memory → MemoryManager
    memory_manager_id     UUID REFERENCES ag_memory_managers(id),
    -- Agno: Agent.learning → LearningMachine
    learning_config_id    UUID REFERENCES ag_learning_configs(id),
    -- Agno: Agent.reasoning_config → ReasoningConfig
    reasoning_config_id   UUID REFERENCES ag_reasoning_configs(id),
    -- Agno: Agent.compression_manager → CompressionManager
    compression_config_id UUID REFERENCES ag_compression_configs(id),
    -- Agno: Agent.session_summary_manager → SessionSummaryManager
    session_summary_config_id UUID REFERENCES ag_sess_summary_configs(id),
    -- Agno: Agent.culture_manager → CultureManager
    culture_config_id     UUID REFERENCES ag_culture_configs(id),

    -- ── 提示词 ─────────────────────────────────────────────
    -- Agno: Agent.instructions
    instructions          TEXT,
    -- Agno: Agent.expected_output
    expected_output       TEXT,
    -- Agno: Agent.additional_context
    additional_context    TEXT,

    -- ── 推理 ────────────────────────────────────────────────
    -- Agno: Agent.reasoning
    reasoning             BOOLEAN NOT NULL DEFAULT false,
    reasoning_min_steps   INT     NOT NULL DEFAULT 1,
    reasoning_max_steps   INT     NOT NULL DEFAULT 10,

    -- ── 学习 ────────────────────────────────────────────────
    -- Agno: Agent.learning
    learning              BOOLEAN NOT NULL DEFAULT false,

    -- ── 知识库 ─────────────────────────────────────────────
    -- Agno: Agent.search_knowledge
    search_knowledge              BOOLEAN NOT NULL DEFAULT true,
    -- Agno: Agent.update_knowledge
    update_knowledge              BOOLEAN NOT NULL DEFAULT false,
    -- Agno: Agent.add_knowledge_to_context
    add_knowledge_to_context      BOOLEAN NOT NULL DEFAULT false,
    -- Agno: Agent.enable_agentic_knowledge_filters
    enable_agentic_knowledge_filters BOOLEAN NOT NULL DEFAULT false,

    -- ── 记忆 ────────────────────────────────────────────────
    -- Agno: Agent.enable_agentic_state
    enable_agentic_state          BOOLEAN NOT NULL DEFAULT false,
    -- Agno: Agent.enable_agentic_memory
    enable_agentic_memory         BOOLEAN NOT NULL DEFAULT false,
    -- Agno: Agent.update_memory_on_run
    update_memory_on_run          BOOLEAN NOT NULL DEFAULT false,
    -- Agno: Agent.add_memories_to_context
    add_memories_to_context       BOOLEAN NOT NULL DEFAULT false,

    -- ── 历史 ────────────────────────────────────────────────
    -- Agno: Agent.add_history_to_context
    add_history_to_context        BOOLEAN NOT NULL DEFAULT false,
    -- Agno: Agent.num_history_runs
    num_history_runs              INT,
    -- Agno: Agent.num_history_messages
    num_history_messages          INT,
    -- Agno: Agent.search_past_sessions
    search_past_sessions          BOOLEAN NOT NULL DEFAULT false,
    num_past_sessions_to_search   INT,

    -- ── 会话摘要 ────────────────────────────────────────────
    -- Agno: Agent.enable_session_summaries
    enable_session_summaries      BOOLEAN NOT NULL DEFAULT false,
    add_session_summary_to_context BOOLEAN NOT NULL DEFAULT false,

    -- ── 工具控制 ────────────────────────────────────────────
    -- Agno: Agent.tool_call_limit
    tool_call_limit               INT,
    -- Agno: Agent.tool_choice  none/auto/specific
    tool_choice                   VARCHAR(50),

    -- ── 输出格式 ────────────────────────────────────────────
    -- Agno: Agent.response_model（Pydantic schema）
    output_schema                 JSONB,
    -- Agno: Agent.output_schema（input validation）
    input_schema                  JSONB,
    -- Agno: Agent.use_json_mode
    use_json_mode                 BOOLEAN NOT NULL DEFAULT false,
    -- Agno: Agent.structured_outputs
    structured_outputs            BOOLEAN,
    -- Agno: Agent.parse_response
    parse_response                BOOLEAN NOT NULL DEFAULT true,

    -- ── 重试 ────────────────────────────────────────────────
    -- Agno: Agent.retries
    retries                       INT NOT NULL DEFAULT 0,
    delay_between_retries         INT NOT NULL DEFAULT 1,
    exponential_backoff           BOOLEAN NOT NULL DEFAULT false,

    -- ── 上下文 ──────────────────────────────────────────────
    -- Agno: Agent.add_datetime_to_context
    add_datetime_to_context       BOOLEAN NOT NULL DEFAULT false,
    add_name_to_context           BOOLEAN NOT NULL DEFAULT false,
    -- Agno: Agent.compress_tool_results
    compress_tool_results         BOOLEAN NOT NULL DEFAULT false,

    -- ── 流式 ────────────────────────────────────────────────
    -- Agno: Agent.stream
    stream                        BOOLEAN NOT NULL DEFAULT false,
    stream_events                 BOOLEAN NOT NULL DEFAULT false,
    store_events                  BOOLEAN NOT NULL DEFAULT false,

    -- ── Markdown ────────────────────────────────────────────
    -- Agno: Agent.markdown
    markdown                      BOOLEAN NOT NULL DEFAULT false,

    -- ── Follow-up ───────────────────────────────────────────
    followups                     BOOLEAN NOT NULL DEFAULT false,
    num_followups                 INT     NOT NULL DEFAULT 3,

    -- ── 调试 ────────────────────────────────────────────────
    -- Agno: Agent.debug_mode
    debug_mode                    BOOLEAN NOT NULL DEFAULT false,
    debug_level                   INT     NOT NULL DEFAULT 1,

    -- ── A2A / Remote ────────────────────────────────────────
    -- Agno: AgentOS(a2a_interface=True) 时此 Agent 对外暴露 A2A
    a2a_enabled                   BOOLEAN NOT NULL DEFAULT false,
    -- Agno: RemoteAgent(base_url=, agent_id=, protocol=)
    is_remote                     BOOLEAN NOT NULL DEFAULT false,
    remote_url                    VARCHAR(500),
    remote_agent_id               VARCHAR(255),

    metadata_config   JSONB NOT NULL DEFAULT '{}',
    enabled    BOOLEAN NOT NULL DEFAULT true,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TRIGGER trg_agents_updated_at
    BEFORE UPDATE ON ag_agents
    FOR EACH ROW EXECUTE FUNCTION fn_update_updated_at();

CREATE INDEX idx_agents_model_id ON ag_agents(model_id);
CREATE INDEX idx_agents_enabled  ON ag_agents(enabled);
```

#### 与 Agno 的交互流程

```
POST /management/agents
  body: {name, model_id, instructions, tool_ids:[...], knowledge_ids:[...], ...}
  │
  ├─ AgentService.create(body)
  │   ├─ 事务开始
  │   ├─ AgentRepo.create(data)        → ag_agents 写入
  │   ├─ BindingRepo.bulk_create(...)  → ag_bindings 批量写入
  │   ├─ 事务提交
  │   └─ registry.create_agent(row)
  │       │
  │       ├─ 1. 取模型：registry._model_cache[model_id]
  │       │         → Agent(model=OpenAIChat(...))
  │       │
  │       ├─ 2. 取子管理器：
  │       │   memory_manager_id → MemoryManager(model=..., ...)
  │       │   learning_config_id → LearningMachine(...)
  │       │   reasoning_config_id → ReasoningConfig(...)
  │       │
  │       ├─ 3. callable factory（热插拔核心）：
  │       │   tools=lambda: registry.resolve_tools(agent_id)
  │       │   knowledge=lambda: registry.resolve_knowledge(agent_id)
  │       │   cache_callables=False  ← 必须
  │       │
  │       ├─ 4. 布尔开关直接映射
  │       │
  │       ├─ 5. agent.initialize_agent()
  │       │
  │       └─ 6. registry.agents.append(agent)
  │             ← AgentOS 立即可路由 /agents/{id}/runs
  │
  └─ 返回 AgentResponse

PATCH /management/agents/{id}  （更新布尔开关）
  ├─ 轻量字段(markdown/debug_mode等): setattr(agent, k, v)  不重建
  └─ 重量字段(model_id/instructions): 重建 Agent 对象，原子替换列表
```

#### schemas.py（AgentCreate）

```python
class AgentCreate(BaseModel):
    name: str
    model_id: UUID
    instructions: str | None = None
    # 创建时直接绑定，可选
    tool_ids:      list[UUID] = []
    knowledge_ids: list[UUID] = []
    mcp_ids:       list[UUID] = []
    hook_ids:      list[UUID] = []
    guardrail_ids: list[UUID] = []
    # 其他 agent 字段...
    enabled: bool = True
```

#### service.py（核心部分）

```python
_BINDING_FIELDS = {"tool_ids", "knowledge_ids", "mcp_ids", "hook_ids", "guardrail_ids"}
_RESOURCE_TYPE_MAP = {
    "tool_ids": "toolkit",
    "knowledge_ids": "knowledge",
    "mcp_ids": "mcp",
    "hook_ids": "hook",
    "guardrail_ids": "guardrail",
}

class AgentService:
    def __init__(self, db: AsyncSession, registry: RuntimeRegistry):
        self.db = db
        self.repo = AgentRepo(db)
        self.binding_repo = AsyncBindingRepo(db)
        self.reg = registry

    async def create(self, body: AgentCreate):
        data = body.model_dump()
        binding_ids = {k: data.pop(k) for k in _BINDING_FIELDS}

        async with self.db.begin():
            # 1. 创建 agent 行
            row = await self.repo.create(data)

            # 2. 批量写 bindings
            bindings = []
            for field, ids in binding_ids.items():
                for rid in ids:
                    bindings.append({
                        "owner_type": "agent",
                        "owner_id": str(row.id),
                        "resource_type": _RESOURCE_TYPE_MAP[field],
                        "resource_id": str(rid),
                        "priority": 0,
                    })
            if bindings:
                await self.binding_repo.bulk_create(bindings)

        # 3. 注册到 runtime（事务提交后）
        await self.reg.create_agent(row)
        return row

    async def update(self, agent_id: UUID, body: AgentUpdate):
        REBUILD_FIELDS = {"model_id", "instructions", "expected_output",
                          "memory_manager_id", "learning_config_id"}
        data = body.model_dump(exclude_none=True)
        row = await self.repo.update(agent_id, data)
        if not row:
            return None

        if any(k in REBUILD_FIELDS for k in data):
            # 重建 Agent 对象，原子替换（rebuild_agent 自行重新读 DB）
            await self.reg.rebuild_agent(str(agent_id))
        else:
            # 直接 setattr，无需重建
            PATCHABLE = {
                "markdown", "debug_mode", "stream", "search_knowledge",
                "update_knowledge", "enable_agentic_memory", "tool_call_limit",
                "retries", "add_history_to_context", "compress_tool_results",
            }
            agent = self.reg._agents_map.get(str(agent_id))
            if agent:
                for k, v in data.items():
                    if k in PATCHABLE:
                        setattr(agent, k, v)
        return row

    async def delete(self, agent_id: UUID) -> bool:
        if not await self.repo.get_by_id(agent_id):
            return False
        await self.repo.delete(agent_id)
        self.reg.delete_agent(str(agent_id))
        return True
```

#### registry.create_agent（核心）

```python
async def create_agent(self, row) -> object:
    import importlib
    from agno.agent import Agent

    agent_id = str(row.id)

    # 如果是远程 Agent
    if row.is_remote:
        from agno.agent.remote import RemoteAgent
        agent = RemoteAgent(
            base_url=row.remote_url,
            agent_id=row.remote_agent_id,
            protocol="agentos",
        )
        self._agents_map[agent_id] = agent
        self.agents.append(agent)
        return agent

    # ── 构建子管理器（每次 create 新建实例，不缓存） ──────────────
    agno_db = self._agno_db  # lifespan 时注入

    memory_manager = (
        self.build_memory_manager(self._memory_manager_rows[str(row.memory_manager_id)], agno_db)
        if row.memory_manager_id else None
    )
    learning = (
        self.build_learning_machine(self._learning_rows[str(row.learning_config_id)], agno_db)
        if row.learning_config_id else None
    )
    reasoning_config = (
        self.build_reasoning_config(self._reasoning_rows[str(row.reasoning_config_id)])
        if row.reasoning_config_id else None
    )
    compression_manager = (
        self.build_compression_manager(self._compression_rows[str(row.compression_config_id)])
        if row.compression_config_id else None
    )
    session_summary_manager = (
        self.build_session_summary_manager(
            self._session_summary_rows[str(row.session_summary_config_id)], agno_db
        )
        if row.session_summary_config_id else None
    )
    culture_manager = (
        self.build_culture_manager(self._culture_rows[str(row.culture_config_id)], agno_db)
        if row.culture_config_id else None
    )

    # Skills：启动时从 DB 构建一次；变更需 rebuild_agent()
    skill_bindings = SyncBindingRepo.get_active(agent_id, "agent", resource_type="skill")
    skills_obj = self.build_skills(agent_id, skill_bindings)

    agent = Agent(
        id=agent_id,
        name=row.name,
        description=row.description,
        model=self._model_cache.get(str(row.model_id)) if row.model_id else None,
        reasoning_model=self._model_cache.get(str(row.reasoning_model_id)) if row.reasoning_model_id else None,
        instructions=row.instructions,
        expected_output=row.expected_output,
        additional_context=row.additional_context,
        # ── callable factory（热插拔核心）─────────────────────────
        tools=lambda aid=agent_id: self.resolve_tools(aid),
        knowledge=lambda aid=agent_id: self.resolve_knowledge(aid),
        # pre/post_hooks 合并 hooks + guardrails（两者都走 hook 注入机制）
        pre_hooks=lambda aid=agent_id: (
            self.resolve_hooks(aid, "pre") + self.resolve_guardrails(aid, "pre")
        ),
        post_hooks=lambda aid=agent_id: (
            self.resolve_hooks(aid, "post") + self.resolve_guardrails(aid, "post")
        ),
        tool_hooks=lambda aid=agent_id: self.resolve_hooks(aid, "tool"),
        cache_callables=False,       # ⚠️ 必须
        # Skills 在 agent 创建时固定（不走 callable factory）
        skills=skills_obj,
        # ── 子管理器 ──────────────────────────────────────────────
        memory=memory_manager,
        learning=learning,
        reasoning_config=reasoning_config,
        compression_manager=compression_manager,
        session_summary_manager=session_summary_manager,
        culture_manager=culture_manager,
        # ── 布尔开关 ──────────────────────────────────────────────
        reasoning=row.reasoning,
        markdown=row.markdown,
        stream=row.stream,
        stream_events=row.stream_events,
        search_knowledge=row.search_knowledge,
        update_knowledge=row.update_knowledge,
        enable_agentic_memory=row.enable_agentic_memory,
        update_memory_on_run=row.update_memory_on_run,
        add_history_to_context=row.add_history_to_context,
        num_history_runs=row.num_history_runs,
        tool_call_limit=row.tool_call_limit,
        retries=row.retries,
        debug_mode=row.debug_mode,
        store_events=True,           # AgentOS 追踪需要
    )
    agent.initialize_agent()

    self._agents_map[agent_id] = agent
    self.agents.append(agent)
    return agent
```

#### router.py

```python
# app/agents/router.py
from uuid import UUID
from fastapi import APIRouter, Depends
from core.deps import get_db, get_registry
from .schemas import AgentCreate, AgentUpdate, AgentResponse
from .service import AgentService

router = APIRouter(prefix="/agents", tags=["Agents"])


def svc(db=Depends(get_db), reg=Depends(get_registry)):
    return AgentService(db, reg)


@router.get("", response_model=list[AgentResponse])
async def list_agents(s=Depends(svc)):
    return await s.list()


@router.post("", response_model=AgentResponse, status_code=201)
async def create_agent(body: AgentCreate, s=Depends(svc)):
    return await s.create(body)


@router.get("/{agent_id}", response_model=AgentResponse)
async def get_agent(agent_id: UUID, s=Depends(svc)):
    return await s.get(str(agent_id))


@router.patch("/{agent_id}", response_model=AgentResponse)
async def update_agent(agent_id: UUID, body: AgentUpdate, s=Depends(svc)):
    return await s.update(str(agent_id), body)


@router.delete("/{agent_id}", status_code=204)
async def delete_agent(agent_id: UUID, s=Depends(svc)):
    await s.delete(str(agent_id))
```

#### AgentRepo（差异部分）

```python
# app/agents/repo.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text


class AgentRepo:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_all_enabled(self):
        result = await self.db.execute(
            text("SELECT * FROM ag_agents WHERE enabled=true ORDER BY created_at")
        )
        return result.fetchall()

    async def get(self, agent_id: str):
        result = await self.db.execute(
            text("SELECT * FROM ag_agents WHERE id=:id"), {"id": agent_id}
        )
        return result.fetchone()

    async def create(self, data: dict):
        from sqlalchemy import text
        cols = ", ".join(data.keys())
        vals = ", ".join(f":{k}" for k in data.keys())
        result = await self.db.execute(
            text(f"INSERT INTO ag_agents ({cols}) VALUES ({vals}) RETURNING *"),
            data,
        )
        return result.fetchone()

    async def update(self, agent_id, data: dict):
        from sqlalchemy import text
        sets = ", ".join(f"{k}=:{k}" for k in data.keys())
        data["_id"] = str(agent_id)
        result = await self.db.execute(
            text(f"UPDATE ag_agents SET {sets} WHERE id=:_id RETURNING *"),
            data,
        )
        return result.fetchone()

    async def delete(self, agent_id: str):
        """软删除（enabled=false），保留 agno_sessions 历史"""
        from sqlalchemy import text
        await self.db.execute(
            text("UPDATE ag_agents SET enabled=false WHERE id=:id"), {"id": agent_id}
        )
        await self.db.commit()
```

**AgentService.delete 的 registry 清理：**

```python
async def delete(self, agent_id: str):
    await self.repo.delete(agent_id)
    # 从共享列表移除（AgentOS 立即不可路由）
    self.reg.agents[:] = [a for a in self.reg.agents
                          if (a.agent_id or a.id) != agent_id]
    self.reg._agents_map.pop(agent_id, None)
```

---

### 5.14 Bindings（热插拔绑定）

#### 表设计

```sql
CREATE TABLE ag_bindings (
    id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    -- agent/team
    owner_type    VARCHAR(50) NOT NULL,
    owner_id      UUID NOT NULL,
    -- toolkit/skill/mcp/knowledge/hook/guardrail/reasoning_tool
    resource_type VARCHAR(50) NOT NULL,
    resource_id   UUID NOT NULL,
    enabled       BOOLEAN NOT NULL DEFAULT true,
    -- 多个同类资源时排序（数字小优先）
    priority      INT NOT NULL DEFAULT 0,
    -- 覆盖资源默认 config（如特定 Agent 使用不同 API Key）
    config_override JSONB NOT NULL DEFAULT '{}',
    created_at    TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at    TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE(owner_type, owner_id, resource_type, resource_id)
);

CREATE TRIGGER trg_bindings_updated_at
    BEFORE UPDATE ON ag_bindings
    FOR EACH ROW EXECUTE FUNCTION fn_update_updated_at();

-- 热路径核心索引（每次 run 都查）
CREATE INDEX idx_bindings_owner      ON ag_bindings(owner_type, owner_id);
CREATE INDEX idx_bindings_owner_type ON ag_bindings(owner_type, owner_id, resource_type);
CREATE INDEX idx_bindings_enabled    ON ag_bindings(owner_id, enabled);
```

#### 与 Agno 交互流程

```
热插拔流程（无需重建 Agent）：

管理员：PATCH /management/agents/{id}/bindings/{resource_id}
  body: {"enabled": false}
  │
  ├─ BindingRepo.set_enabled(owner_id, resource_id, false)
  │   UPDATE ag_bindings SET enabled=false WHERE ...
  │
  └─ 无需通知 RuntimeRegistry（factory 每次 run 重新读 DB）

用户下次发消息：
  POST /agents/{id}/runs
  │
  └─ Agno 内部调用 tools=lambda:
      → resolve_tools(agent_id)
      → SyncBindingRepo.get_active(agent_id)   ← 读最新 DB
      → enabled=false 的 binding 不返回
      → 本次 run 不包含已关闭的工具 ✓
```

#### schemas.py

```python
# app/bindings/schemas.py
from uuid import UUID
from pydantic import BaseModel


class BindingCreate(BaseModel):
    resource_type: str   # toolkit / skill / mcp / knowledge / hook / guardrail
    resource_id: UUID
    priority: int = 0
    config_override: dict = {}


class BindingUpdate(BaseModel):
    enabled: bool | None = None
    priority: int | None = None
    config_override: dict | None = None


class BindingResponse(BaseModel):
    id: UUID
    owner_type: str
    owner_id: UUID
    resource_type: str
    resource_id: UUID
    enabled: bool
    priority: int
    config_override: dict
```

#### AsyncBindingRepo

```python
# app/bindings/repo.py
import json
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text


class AsyncBindingRepo:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def list(self, owner_id: str, owner_type: str = "agent") -> list:
        result = await self.db.execute(
            text("""SELECT * FROM ag_bindings
                    WHERE owner_id=:oid AND owner_type=:otype
                    ORDER BY resource_type, priority"""),
            {"oid": owner_id, "otype": owner_type},
        )
        return result.fetchall()

    async def create(self, owner_id: str, owner_type: str, body) -> object:
        result = await self.db.execute(
            text("""
                INSERT INTO ag_bindings
                    (owner_type, owner_id, resource_type, resource_id, priority, config_override)
                VALUES (:otype, :oid, :rtype, :rid, :priority, :cfg::jsonb)
                ON CONFLICT (owner_type, owner_id, resource_type, resource_id)
                DO UPDATE SET enabled=true, priority=EXCLUDED.priority,
                              config_override=EXCLUDED.config_override
                RETURNING *
            """),
            {
                "otype": owner_type,
                "oid": owner_id,
                "rtype": body.resource_type,
                "rid": str(body.resource_id),
                "priority": body.priority,
                "cfg": json.dumps(body.config_override),
            },
        )
        await self.db.commit()
        return result.fetchone()

    async def bulk_create(self, bindings: list[dict]) -> None:
        """
        批量插入绑定，用于 AgentService.create / TeamService.create 事务内调用。
        bindings 列表元素：
          {"owner_type": str, "owner_id": str,
           "resource_type": str, "resource_id": str, "priority": int}
        调用方负责 commit（事务由 AgentService 统一管理）。
        """
        if not bindings:
            return
        for b in bindings:
            await self.db.execute(
                text("""
                    INSERT INTO ag_bindings
                        (owner_type, owner_id, resource_type, resource_id, priority)
                    VALUES (:otype, :oid, :rtype, :rid, :priority)
                    ON CONFLICT (owner_type, owner_id, resource_type, resource_id) DO NOTHING
                """),
                {
                    "otype": b["owner_type"],
                    "oid": b["owner_id"],
                    "rtype": b["resource_type"],
                    "rid": b["resource_id"],
                    "priority": b.get("priority", 0),
                },
            )
        # 不在此处 commit，由调用方事务统一提交

    async def set_enabled(self, owner_id: str, resource_id: str, enabled: bool) -> object:
        result = await self.db.execute(
            text("""UPDATE ag_bindings SET enabled=:enabled
                    WHERE owner_id=:oid AND resource_id=:rid RETURNING *"""),
            {"enabled": enabled, "oid": owner_id, "rid": resource_id},
        )
        await self.db.commit()
        return result.fetchone()

    async def update(self, owner_id: str, resource_id: str, body) -> object:
        sets = []
        params = {"oid": owner_id, "rid": resource_id}
        if body.enabled is not None:
            sets.append("enabled=:enabled")
            params["enabled"] = body.enabled
        if body.priority is not None:
            sets.append("priority=:priority")
            params["priority"] = body.priority
        if body.config_override is not None:
            sets.append("config_override=:cfg::jsonb")
            params["cfg"] = json.dumps(body.config_override)
        if not sets:
            return None
        result = await self.db.execute(
            text(f"UPDATE ag_bindings SET {', '.join(sets)} "
                 "WHERE owner_id=:oid AND resource_id=:rid RETURNING *"),
            params,
        )
        await self.db.commit()
        return result.fetchone()

    async def delete(self, owner_id: str, resource_id: str) -> None:
        await self.db.execute(
            text("DELETE FROM ag_bindings WHERE owner_id=:oid AND resource_id=:rid"),
            {"oid": owner_id, "rid": resource_id},
        )
        await self.db.commit()
```

#### BindingService

```python
# app/bindings/service.py
from .repo import AsyncBindingRepo


class BindingService:
    def __init__(self, db, registry):
        self.repo = AsyncBindingRepo(db)
        self.reg = registry

    async def list(self, owner_id: str, owner_type: str = "agent"):
        return await self.repo.list(owner_id, owner_type)

    async def create(self, owner_id: str, owner_type: str, body):
        return await self.repo.create(owner_id, owner_type, body)

    async def update(self, owner_id: str, resource_id: str, body):
        """
        热插拔核心：只改 DB。
        下次 run 时 callable factory 自动读取最新绑定，无需通知 registry。
        （skill 绑定变更例外：需额外调用 self.reg.rebuild_agent(owner_id)）
        """
        row = await self.repo.update(owner_id, resource_id, body)
        return row

    async def delete(self, owner_id: str, resource_id: str):
        await self.repo.delete(owner_id, resource_id)
```

#### router.py（挂在 /management/agents/{agent_id}/bindings）

```python
# app/bindings/router.py
from uuid import UUID
from fastapi import APIRouter, Depends
from core.deps import get_db, get_registry
from .schemas import BindingCreate, BindingUpdate, BindingResponse
from .service import BindingService

router = APIRouter()


def svc(db=Depends(get_db), reg=Depends(get_registry)):
    return BindingService(db, reg)


@router.get("/{agent_id}/bindings", response_model=list[BindingResponse])
async def list_bindings(agent_id: UUID, s=Depends(svc)):
    return await s.list(str(agent_id), "agent")


@router.post("/{agent_id}/bindings", status_code=201)
async def add_binding(agent_id: UUID, body: BindingCreate, s=Depends(svc)):
    return await s.create(str(agent_id), "agent", body)


@router.patch("/{agent_id}/bindings/{resource_id}")
async def update_binding(agent_id: UUID, resource_id: UUID,
                         body: BindingUpdate, s=Depends(svc)):
    return await s.update(str(agent_id), str(resource_id), body)


@router.delete("/{agent_id}/bindings/{resource_id}", status_code=204)
async def remove_binding(agent_id: UUID, resource_id: UUID, s=Depends(svc)):
    await s.delete(str(agent_id), str(resource_id))
```

---

### 5.15 Teams

#### 表设计

```sql
CREATE TABLE ag_teams (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name        VARCHAR(255) NOT NULL,
    description TEXT,

    -- Agno: Team.model
    model_id            UUID REFERENCES ag_models(id),
    -- Agno: Team.memory → MemoryManager
    memory_manager_id   UUID REFERENCES ag_memory_managers(id),

    -- Agno: Team.mode  route/coordinate/collaborate/tasks
    mode                VARCHAR(20) NOT NULL DEFAULT 'route',
    -- Agno: Team.respond_directly
    respond_directly            BOOLEAN NOT NULL DEFAULT false,
    -- Agno: Team.delegate_to_all_members
    delegate_to_all_members     BOOLEAN NOT NULL DEFAULT false,
    determine_input_for_members BOOLEAN NOT NULL DEFAULT true,
    max_iterations              INT     NOT NULL DEFAULT 10,

    instructions    TEXT,
    expected_output TEXT,
    markdown        BOOLEAN NOT NULL DEFAULT false,

    add_team_history_to_members  BOOLEAN NOT NULL DEFAULT false,
    num_team_history_runs        INT     NOT NULL DEFAULT 3,
    share_member_interactions    BOOLEAN NOT NULL DEFAULT false,
    add_member_tools_to_context  BOOLEAN NOT NULL DEFAULT false,
    read_chat_history            BOOLEAN NOT NULL DEFAULT false,
    search_past_sessions         BOOLEAN NOT NULL DEFAULT false,
    num_past_sessions_to_search  INT,

    search_knowledge             BOOLEAN NOT NULL DEFAULT true,
    update_knowledge             BOOLEAN NOT NULL DEFAULT false,
    enable_agentic_knowledge_filters BOOLEAN NOT NULL DEFAULT false,

    enable_agentic_state         BOOLEAN NOT NULL DEFAULT false,
    enable_agentic_memory        BOOLEAN NOT NULL DEFAULT false,
    update_memory_on_run         BOOLEAN NOT NULL DEFAULT false,

    enable_session_summaries     BOOLEAN NOT NULL DEFAULT false,
    add_session_summary_to_context BOOLEAN NOT NULL DEFAULT false,

    tool_call_limit              INT,
    stream                       BOOLEAN NOT NULL DEFAULT false,
    stream_events                BOOLEAN NOT NULL DEFAULT false,
    debug_mode                   BOOLEAN NOT NULL DEFAULT false,

    metadata_config   JSONB NOT NULL DEFAULT '{}',
    enabled    BOOLEAN NOT NULL DEFAULT true,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE ag_team_members (
    id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    team_id      UUID NOT NULL REFERENCES ag_teams(id) ON DELETE CASCADE,
    -- agent/team（嵌套 Team）
    member_type  VARCHAR(20) NOT NULL,
    member_id    UUID NOT NULL,
    -- Agno: member.role
    role         VARCHAR(255),
    member_order INT NOT NULL DEFAULT 0,
    enabled      BOOLEAN NOT NULL DEFAULT true,
    created_at   TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE(team_id, member_type, member_id)   -- 防止重复添加
);

CREATE TRIGGER trg_teams_updated_at
    BEFORE UPDATE ON ag_teams
    FOR EACH ROW EXECUTE FUNCTION fn_update_updated_at();

CREATE INDEX idx_team_members_team ON ag_team_members(team_id);
CREATE INDEX idx_teams_enabled     ON ag_teams(enabled);
```

#### schemas.py（TeamCreate）

```python
class TeamMemberInput(BaseModel):
    member_id: UUID
    member_type: str = "agent"   # agent / team
    role: str | None = None
    member_order: int = 0

class TeamCreate(BaseModel):
    name: str
    model_id: UUID | None = None
    mode: str = "route"
    instructions: str | None = None
    # 创建时直接指定成员和绑定
    members:       list[TeamMemberInput] = []   → ag_team_members
    tool_ids:      list[UUID] = []              → ag_bindings
    knowledge_ids: list[UUID] = []              → ag_bindings
    mcp_ids:       list[UUID] = []              → ag_bindings
    enabled: bool = True
```

#### service.py（TeamService.create）

```python
from sqlalchemy.ext.asyncio import AsyncSession
from core.registry import RuntimeRegistry
from .schemas import TeamCreate
from .repo import TeamRepo, TeamMemberRepo
from modules.bindings.repo import AsyncBindingRepo


class TeamService:
    def __init__(self, db: AsyncSession, registry: RuntimeRegistry):
        self.db = db
        self.repo = TeamRepo(db)
        self.member_repo = TeamMemberRepo(db)
        self.binding_repo = AsyncBindingRepo(db)
        self.reg = registry

async def create(self, body: TeamCreate):
    data = body.model_dump()
    members_data   = data.pop("members")
    tool_ids       = data.pop("tool_ids")
    knowledge_ids  = data.pop("knowledge_ids")
    mcp_ids        = data.pop("mcp_ids")

    async with self.db.begin():
        # 1. 创建 team 行
        row = await self.team_repo.create(data)

        # 2. 写成员（ag_team_members）
        for m in members_data:
            await self.member_repo.create({
                "team_id": row.id, **m
            })

        # 3. 写绑定（ag_bindings，与 agent 共用同一张表）
        bindings = []
        for rid in tool_ids:
            bindings.append({"owner_type": "team", "owner_id": str(row.id),
                             "resource_type": "toolkit", "resource_id": str(rid), "priority": 0})
        for rid in knowledge_ids:
            bindings.append({"owner_type": "team", "owner_id": str(row.id),
                             "resource_type": "knowledge", "resource_id": str(rid), "priority": 0})
        for rid in mcp_ids:
            bindings.append({"owner_type": "team", "owner_id": str(row.id),
                             "resource_type": "mcp", "resource_id": str(rid), "priority": 0})
        if bindings:
            await self.binding_repo.bulk_create(bindings)

    # 4. 注册到 runtime
    await self.reg.create_team(row)
    return row
```

#### registry.create_team（核心）

```python
async def create_team(self, row) -> object:
    from agno.team import Team
    from modules.teams.repo import SyncTeamMemberRepo

    team_id = str(row.id)

    # 1. 从 _agents_map / _teams_map 解析成员列表
    member_rows = SyncTeamMemberRepo.get_active(team_id)
    members = []
    for m in sorted(member_rows, key=lambda x: x.member_order):
        if m.member_type == "agent":
            agent = self._agents_map.get(str(m.member_id))
            if agent:
                if m.role:
                    agent.role = m.role
                members.append(agent)
        elif m.member_type == "team":
            sub_team = self._teams_map.get(str(m.member_id))
            if sub_team:
                members.append(sub_team)

    # 2. 子管理器
    agno_db = self._agno_db
    memory_manager = (
        self.build_memory_manager(self._memory_manager_rows[str(row.memory_manager_id)], agno_db)
        if row.memory_manager_id else None
    )

    # 3. 构建 Team（tools/knowledge 也用 callable factory，热插拔）
    team = Team(
        id=team_id,
        name=row.name,
        description=row.description,
        model=self._model_cache.get(str(row.model_id)) if row.model_id else None,
        members=members,
        mode=row.mode,
        instructions=row.instructions,
        expected_output=row.expected_output,
        # callable factory（与 agent 相同模式）
        tools=lambda tid=team_id: self.resolve_tools(tid),
        knowledge=lambda tid=team_id: self.resolve_knowledge(tid),
        cache_callables=False,
        memory=memory_manager,
        respond_directly=row.respond_directly,
        delegate_to_all_members=row.delegate_to_all_members,
        determine_input_for_members=row.determine_input_for_members,
        max_iterations=row.max_iterations,
        add_team_history_to_members=row.add_team_history_to_members,
        num_team_history_runs=row.num_team_history_runs,
        search_knowledge=row.search_knowledge,
        enable_agentic_memory=row.enable_agentic_memory,
        tool_call_limit=row.tool_call_limit,
        stream=row.stream,
        debug_mode=row.debug_mode,
        store_events=True,
    )

    self._teams_map[team_id] = team
    self.teams.append(team)
    return team
```

> **注意**：Team 依赖已注册的 Agent，所以预热顺序必须是 agents → teams。

#### CRUD 差异（相对 5.1 Models 模式）

> router.py / repo.py 结构同 5.1 Models。

```python
# app/teams/router.py（关键差异：members 子资源）
@router.post("", response_model=TeamResponse, status_code=201)
async def create_team(body: TeamCreate, s=Depends(svc)):
    return await s.create(body)   # 事务内写 ag_teams + ag_team_members

@router.patch("/{team_id}/members/{agent_id}")
async def update_member(team_id: UUID, agent_id: UUID, body: MemberUpdate, s=Depends(svc)):
    """调整成员角色/优先级；需 rebuild_team(team_id) 重建 Team 实例"""
    return await s.update_member(str(team_id), str(agent_id), body)
```

**TeamService.delete registry 清理：**

```python
async def delete(self, team_id: str):
    await self.repo.delete(team_id)   # enabled=false
    self.reg.teams[:] = [t for t in self.reg.teams if (t.team_id or t.id) != team_id]
    self.reg._teams_map.pop(team_id, None)
```

**rebuild_team**（成员变更时调用）：

```python
async def rebuild_team(self, team_id: str) -> None:
    """重建 Team 实例并替换 teams[] 中的引用（pattern 同 rebuild_agent）"""
    old = self._teams_map.get(team_id)
    if old is None:
        return
    from modules.teams.repo import TeamRepo, TeamMemberRepo
    from core.db import AsyncSessionLocal
    async with AsyncSessionLocal() as db:
        row = await TeamRepo(db).get(team_id)
        member_rows = await TeamMemberRepo(db).get_by_team(team_id)
    if not row:
        return
    # 先从列表移除旧实例（create_team 内部会 append）
    self.teams[:] = [t for t in self.teams if (t.team_id or t.id) != team_id]
    new_team = await self.create_team(row, member_rows)
    # create_team 已执行 append + _teams_map 更新
```

---

### 5.16 Workflows

#### 表设计

```sql
CREATE TABLE ag_workflows (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name        VARCHAR(255) NOT NULL,
    description TEXT,

    -- Agno: Workflow.stream
    stream                        BOOLEAN NOT NULL DEFAULT false,
    stream_events                 BOOLEAN NOT NULL DEFAULT false,
    stream_executor_events        BOOLEAN NOT NULL DEFAULT true,
    store_events                  BOOLEAN NOT NULL DEFAULT false,
    store_executor_outputs        BOOLEAN NOT NULL DEFAULT true,
    add_workflow_history_to_steps BOOLEAN NOT NULL DEFAULT false,
    num_history_runs              INT     NOT NULL DEFAULT 3,
    add_session_state_to_context  BOOLEAN NOT NULL DEFAULT false,
    debug_mode                    BOOLEAN NOT NULL DEFAULT false,

    -- Agno: Workflow.input_schema（Pydantic schema JSON）
    input_schema JSONB,
    metadata_config     JSONB NOT NULL DEFAULT '{}',
    enabled      BOOLEAN NOT NULL DEFAULT true,
    created_at   TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at   TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- 统一节点表（step/condition/loop/parallel/router）
CREATE TABLE ag_workflow_nodes (
    id             UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workflow_id    UUID NOT NULL REFERENCES ag_workflows(id) ON DELETE CASCADE,
    -- 父节点 ID（NULL 表示顶层）
    parent_node_id UUID REFERENCES ag_workflow_nodes(id),
    node_order     INT NOT NULL,
    -- step/condition/loop/parallel/router
    node_type      VARCHAR(20) NOT NULL,
    name           VARCHAR(255),
    description    TEXT,

    -- ── step ────────────────────────────────────────────────
    -- Agno: Step.executor（agent/team/custom）
    executor_type  VARCHAR(20),
    agent_id       UUID REFERENCES ag_agents(id),
    team_id        UUID REFERENCES ag_teams(id),
    executor_module VARCHAR(500),
    add_workflow_history     BOOLEAN,
    num_history_runs         INT DEFAULT 3,
    strict_input_validation  BOOLEAN NOT NULL DEFAULT false,
    max_retries              INT     NOT NULL DEFAULT 3,
    skip_on_failure          BOOLEAN NOT NULL DEFAULT false,

    -- ── condition ───────────────────────────────────────────
    -- Agno: Condition.evaluator（bool/cel/function_ref）
    evaluator_type  VARCHAR(20),
    evaluator_value TEXT,
    -- if/else（子节点用）
    branch          VARCHAR(10),

    -- ── loop ────────────────────────────────────────────────
    -- Agno: Loop.max_iterations
    max_iterations           INT DEFAULT 3,
    end_condition_type       VARCHAR(20),
    end_condition_value      TEXT,
    forward_iteration_output BOOLEAN NOT NULL DEFAULT false,

    -- ── router ──────────────────────────────────────────────
    -- Agno: Router.selector
    selector_type            VARCHAR(20),
    selector_value           TEXT,
    allow_multiple_selections BOOLEAN NOT NULL DEFAULT false,

    -- ── HITL（所有节点共用）────────────────────────────────
    -- Agno: Step.requires_confirmation
    requires_confirmation BOOLEAN NOT NULL DEFAULT false,
    confirmation_message  TEXT,
    requires_user_input   BOOLEAN NOT NULL DEFAULT false,
    user_input_message    TEXT,
    user_input_schema     JSONB,
    on_reject             VARCHAR(20) NOT NULL DEFAULT 'skip',
    on_error              VARCHAR(20) NOT NULL DEFAULT 'skip',

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TRIGGER trg_workflows_updated_at
    BEFORE UPDATE ON ag_workflows
    FOR EACH ROW EXECUTE FUNCTION fn_update_updated_at();

CREATE TRIGGER trg_workflow_nodes_updated_at
    BEFORE UPDATE ON ag_workflow_nodes
    FOR EACH ROW EXECUTE FUNCTION fn_update_updated_at();

CREATE INDEX idx_workflow_nodes_workflow ON ag_workflow_nodes(workflow_id);
CREATE INDEX idx_workflow_nodes_parent   ON ag_workflow_nodes(parent_node_id);
```

#### registry.create_workflow（核心）

```python
async def create_workflow(self, row, node_rows: list) -> object:
    """
    从 ag_workflow_nodes 树构建 Agno Workflow。
    node_rows: 该 workflow 所有节点行，已按 node_order 排序。
    """
    from agno.workflow import Workflow
    from agno.workflow.steps import Steps

    workflow_id = str(row.id)

    # 递归构建节点树
    def build_nodes(parent_id=None) -> list:
        children = [n for n in node_rows if str(n.parent_node_id) == str(parent_id or "")]
        result = []
        for node in sorted(children, key=lambda x: x.node_order):
            built = build_node(node)
            if built is not None:
                result.append(built)
        return result

    def build_node(node):
        ntype = node.node_type

        if ntype == "step":
            from agno.workflow.step import Step
            agent = self._agents_map.get(str(node.agent_id)) if node.agent_id else None
            team = self._teams_map.get(str(node.team_id)) if node.team_id else None
            executor = None
            if node.executor_module:
                import importlib
                parts = node.executor_module.rsplit(".", 1)
                mod = importlib.import_module(parts[0])
                executor = getattr(mod, parts[1])
            return Step(
                name=node.name,
                agent=agent,
                team=team,
                executor=executor,
                max_retries=node.max_retries,
                skip_on_failure=node.skip_on_failure,
                requires_confirmation=node.requires_confirmation,
                requires_user_input=node.requires_user_input,
            )

        elif ntype == "condition":
            from agno.workflow.condition import Condition
            child_nodes = build_nodes(parent_id=node.id)
            if_steps  = [n for n in child_nodes if getattr(n, "_branch", None) != "else"]
            else_steps = [n for n in child_nodes if getattr(n, "_branch", None) == "else"]
            evaluator = _build_evaluator(node.evaluator_type, node.evaluator_value)
            return Condition(
                evaluator=evaluator,
                steps=if_steps,
                else_steps=else_steps or None,
                requires_confirmation=node.requires_confirmation,
            )

        elif ntype == "loop":
            from agno.workflow.loop import Loop
            inner = build_nodes(parent_id=node.id)
            end_cond = _build_evaluator(node.end_condition_type, node.end_condition_value)
            return Loop(
                steps=inner,
                max_iterations=node.max_iterations or 3,
                end_condition=end_cond,
            )

        elif ntype == "parallel":
            from agno.workflow.parallel import Parallel
            inner = build_nodes(parent_id=node.id)
            return Parallel(*inner)

        elif ntype == "router":
            from agno.workflow.router import Router
            routes = build_nodes(parent_id=node.id)
            selector = _build_evaluator(node.selector_type, node.selector_value)
            return Router(
                routes=routes,
                selector=selector,
                allow_multiple_selections=node.allow_multiple_selections,
            )

        return None

    def _build_evaluator(etype, evalue):
        """构建 condition/loop/router 的 evaluator/selector"""
        if not etype or not evalue:
            return True  # 默认始终为真
        if etype == "bool":
            return evalue.lower() == "true"
        if etype == "cel":
            return evalue  # CEL 字符串，Agno 自动识别
        if etype == "function":
            import importlib
            parts = evalue.rsplit(".", 1)
            mod = importlib.import_module(parts[0])
            return getattr(mod, parts[1])
        return True

    top_level_nodes = build_nodes(parent_id=None)
    steps = Steps(top_level_nodes) if top_level_nodes else None

    workflow = Workflow(
        id=workflow_id,
        name=row.name,
        description=row.description,
        steps=steps,
        stream=row.stream,
        stream_events=row.stream_events,
        add_workflow_history_to_steps=row.add_workflow_history_to_steps,
        num_history_runs=row.num_history_runs,
        debug_mode=row.debug_mode,
        store_events=True,
    )

    self._workflows_map[workflow_id] = workflow
    self.workflows.append(workflow)
    return workflow
```

#### CRUD 差异（相对 5.1 Models 模式）

> router.py / service.py / repo.py 结构同 5.1 Models。Workflow 的特殊性在于节点树的 CRUD。

```python
# app/workflows/router.py（关键差异）
@router.post("", response_model=WorkflowResponse, status_code=201)
async def create_workflow(body: WorkflowCreate, s=Depends(svc)):
    """事务内写 ag_workflows + ag_workflow_nodes（递归插入节点树）"""
    return await s.create(body)

@router.patch("/{workflow_id}/nodes/{node_id}")
async def update_node(workflow_id: UUID, node_id: UUID,
                      body: NodeUpdate, s=Depends(svc)):
    """节点属性变更；需 rebuild_workflow(workflow_id) 重建 Workflow 实例"""
    return await s.update_node(str(workflow_id), str(node_id), body)
```

**WorkflowService.delete registry 清理：**

```python
async def delete(self, workflow_id: str):
    await self.repo.delete(workflow_id)
    self.reg.workflows[:] = [w for w in self.reg.workflows
                              if (w.workflow_id or w.id) != workflow_id]
    self.reg._workflows_map.pop(workflow_id, None)
```

**WorkflowCreate schema（核心字段）：**

```python
class WorkflowNodeInput(BaseModel):
    node_type: str            # step / condition / loop / parallel / router
    name: str
    config: dict = {}
    children: list["WorkflowNodeInput"] = []

class WorkflowCreate(BaseModel):
    name: str
    description: str | None = None
    agent_id: UUID | None = None   # 驱动 Workflow 的主 Agent
    nodes: list[WorkflowNodeInput]
```

---

### 5.17 Integrations（渠道）

#### 表设计

```sql
CREATE TABLE ag_integrations (
    id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name         VARCHAR(255) NOT NULL,
    -- Agno: AgentOS interfaces 类型
    -- slack/telegram/whatsapp/agui → AgentOS interfaces 参数
    -- discord → 独立 DiscordClient 进程
    type         VARCHAR(20)  NOT NULL,
    -- 绑定目标（三选一）
    agent_id     UUID REFERENCES ag_agents(id),
    team_id      UUID REFERENCES ag_teams(id),
    workflow_id  UUID REFERENCES ag_workflows(id),
    -- Agno: Slack.token / Telegram.token
    token               TEXT,
    -- Agno: Slack.signing_secret
    signing_secret      TEXT,
    -- Agno: interface prefix（默认 /slack /telegram 等）
    prefix       VARCHAR(100),
    -- Agno: Slack(streaming=, reply_to_mentions_only=, ...)
    config       JSONB NOT NULL DEFAULT '{}',
    enabled      BOOLEAN NOT NULL DEFAULT true,
    created_at   TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at   TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TRIGGER trg_integrations_updated_at
    BEFORE UPDATE ON ag_integrations
    FOR EACH ROW EXECUTE FUNCTION fn_update_updated_at();

CREATE INDEX idx_integrations_agent_id    ON ag_integrations(agent_id);
CREATE INDEX idx_integrations_team_id     ON ag_integrations(team_id);
CREATE INDEX idx_integrations_workflow_id ON ag_integrations(workflow_id);
```

#### 与 AgentOS 的集成方式

Integrations **不走 registry**，而是在 `lifespan` 中动态构建 interface 列表，传给 `AgentOS(interfaces=[...])`。AgentOS 自动将路由挂载到 FastAPI app。

```python
# main.py lifespan 中（startup 阶段）

async def build_interfaces(db, registry) -> list:
    from agno.os.interfaces.slack import Slack
    from agno.os.interfaces.telegram import Telegram
    from agno.os.interfaces.whatsapp import WhatsApp
    from agno.os.interfaces.agui import AgUI
    from modules.integrations.repo import IntegrationRepo

    interfaces = []
    for row in await IntegrationRepo(db).get_all_enabled():
        config = row.config or {}
        # 解析绑定目标
        target_agent = registry._agents_map.get(str(row.agent_id)) if row.agent_id else None
        target_team  = registry._teams_map.get(str(row.team_id))   if row.team_id  else None

        if row.type == "slack":
            interfaces.append(Slack(
                agent=target_agent, team=target_team,
                token=row.token,
                signing_secret=row.signing_secret,
                prefix=row.prefix or "/slack",
                streaming=config.get("streaming", True),
            ))
        elif row.type == "telegram":
            interfaces.append(Telegram(
                agent=target_agent, team=target_team,
                token=row.token,
                prefix=row.prefix or "/telegram",
            ))
        elif row.type == "whatsapp":
            interfaces.append(WhatsApp(
                agent=target_agent, team=target_team,
                token=row.token,
                prefix=row.prefix or "/whatsapp",
            ))
        elif row.type == "agui":
            interfaces.append(AgUI(
                agent=target_agent, team=target_team,
                prefix=row.prefix or "/agui",
            ))

    return interfaces
```

> `main.py` lifespan 中在 `create_team` 之后调用 `build_interfaces`，然后传给 `AgentOS(interfaces=interfaces)`。
> 动态添加/删除渠道需要重启（接口路由在启动时挂载），这是 AgentOS 的限制。

#### service.py（核心）

```python
class IntegrationService:
    async def create(self, body: IntegrationCreate):
        row = await self.repo.create(body.model_dump())
        return row

    async def toggle(self, integration_id: UUID, enabled: bool):
        """启用/禁用渠道（下次重启生效）"""
        return await self.repo.update(integration_id, {"enabled": enabled})
```

#### CRUD 差异

> router.py / repo.py 结构同 5.1 Models。

- **Integrations 的 interface 在 AgentOS 启动时挂载**，运行期间无法热插拔。变更（新增/删除渠道）需要重启服务。`toggle()` 只改 DB，下次重启时 `build_interfaces()` 读 `enabled=true` 的行重新挂载。
- router.py 提供 list / get / create / toggle 端点即可，无 delete（推荐软删 enabled=false）。

```python
# app/integrations/router.py
@router.get("", response_model=list[IntegrationResponse])
async def list_integrations(s=Depends(svc)):
    return await s.list()

@router.post("", response_model=IntegrationResponse, status_code=201)
async def create_integration(body: IntegrationCreate, s=Depends(svc)):
    return await s.create(body)

@router.patch("/{integration_id}/toggle")
async def toggle_integration(integration_id: UUID, body: ToggleRequest, s=Depends(svc)):
    """变更后需重启服务才生效"""
    return await s.toggle(integration_id, body.enabled)
```

---

### 5.18 Schedules（定时任务）

#### 表设计

```sql
-- 管理层视图（对应 Agno agno_schedules 原生表的 UI 层）
CREATE TABLE ag_schedules (
    id               UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name             VARCHAR(255) NOT NULL,
    description      TEXT,
    -- 触发目标
    agent_id         UUID REFERENCES ag_agents(id),
    team_id          UUID REFERENCES ag_teams(id),
    -- 触发时传入的消息/参数
    payload          JSONB NOT NULL DEFAULT '{}',
    -- Agno: ScheduleManager.create(cron=)
    cron_expr        VARCHAR(100) NOT NULL,
    timezone         VARCHAR(100) NOT NULL DEFAULT 'UTC',
    timeout_seconds  INT NOT NULL DEFAULT 3600,
    max_retries      INT NOT NULL DEFAULT 0,
    retry_delay_seconds INT NOT NULL DEFAULT 60,
    enabled          BOOLEAN NOT NULL DEFAULT true,
    created_at       TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at       TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TRIGGER trg_schedules_updated_at
    BEFORE UPDATE ON ag_schedules
    FOR EACH ROW EXECUTE FUNCTION fn_update_updated_at();

CREATE INDEX idx_schedules_agent_id ON ag_schedules(agent_id);
CREATE INDEX idx_schedules_team_id  ON ag_schedules(team_id);
```

#### service.py（核心）

```python
from agno.scheduler.manager import ScheduleManager

class ScheduleService:
    def __init__(self, db, agno_db):
        self.repo = ScheduleRepo(db)
        self.agno_mgr = ScheduleManager(db=agno_db)

    async def create(self, body: ScheduleCreate):
        row = await self.repo.create(body.model_dump())
        await self._sync_to_agno(row)
        return row

    async def update(self, schedule_id: UUID, body: ScheduleUpdate):
        data = body.model_dump(exclude_none=True)
        row = await self.repo.update(schedule_id, data)
        if row:
            await self._sync_to_agno(row)
        return row

    async def delete(self, schedule_id: UUID):
        row = await self.repo.get_by_id(schedule_id)
        if not row:
            return False
        # 从 Agno 调度器删除
        self.agno_mgr.delete(row.name)
        await self.repo.delete(schedule_id)
        return True

    async def toggle(self, schedule_id: UUID, enabled: bool):
        row = await self.repo.update(schedule_id, {"enabled": enabled})
        if row:
            if enabled:
                await self._sync_to_agno(row)
            else:
                self.agno_mgr.delete(row.name)
        return row

    def _sync_to_agno(self, row):
        """写入/更新 Agno 原生调度器"""
        if not row.enabled:
            return
        target_id = str(row.agent_id or row.team_id)
        resource = "agents" if row.agent_id else "teams"
        self.agno_mgr.create(
            name=row.name,
            cron=row.cron_expr,
            endpoint=f"/{resource}/{target_id}/runs",
            method="POST",
            payload=row.payload or {},
            timezone=row.timezone,
            timeout_seconds=row.timeout_seconds,
            max_retries=row.max_retries,
            if_exists="update",  # 同名则更新
        )
```

#### router.py

```python
@router.post("", status_code=201)
async def create_schedule(body: ScheduleCreate, s=Depends(svc)):
    return await s.create(body)

@router.patch("/{schedule_id}")
async def update_schedule(schedule_id: UUID, body: ScheduleUpdate, s=Depends(svc)):
    return await s.update(schedule_id, body)

@router.patch("/{schedule_id}/toggle")
async def toggle_schedule(schedule_id: UUID, body: ToggleRequest, s=Depends(svc)):
    return await s.toggle(schedule_id, body.enabled)

@router.delete("/{schedule_id}", status_code=204)
async def delete_schedule(schedule_id: UUID, s=Depends(svc)):
    await s.delete(schedule_id)
```

#### schemas（补充缺失部分）

```python
# app/schedules/schemas.py
from pydantic import BaseModel
from uuid import UUID

class ScheduleCreate(BaseModel):
    name: str
    agent_id: UUID | None = None
    team_id: UUID | None = None
    cron_expr: str             # e.g. "0 9 * * 1-5"
    message: str               # 定时发给 Agent 的消息内容
    session_id: str | None = None
    enabled: bool = True

class ScheduleUpdate(BaseModel):
    cron_expr: str | None = None
    message: str | None = None
    enabled: bool | None = None

class ToggleRequest(BaseModel):
    enabled: bool
```

---

### 5.19 RBAC

#### 表设计

```sql
CREATE TABLE ag_roles (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name        VARCHAR(100) UNIQUE NOT NULL,  -- admin/operator/viewer
    -- Agno AgentOS scopes: ["agents:*:run","sessions:read",...]
    scopes      JSONB NOT NULL,
    description TEXT,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TRIGGER trg_roles_updated_at
    BEFORE UPDATE ON ag_roles
    FOR EACH ROW EXECUTE FUNCTION fn_update_updated_at();

CREATE TABLE ag_user_roles (
    user_id    VARCHAR(255) NOT NULL,
    role_id    UUID NOT NULL REFERENCES ag_roles(id) ON DELETE CASCADE,
    granted_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    PRIMARY KEY (user_id, role_id)
);

CREATE INDEX idx_user_roles_user ON ag_user_roles(user_id);
```

**JWT 签发流程：**
```python
# 你的 Auth 服务签发 JWT 时
async def issue_token(user_id: str, db) -> str:
    # 查用户所有角色的 scopes
    roles = await get_user_roles(user_id, db)
    scopes = []
    for role in roles:
        scopes.extend(role.scopes)

    payload = {
        "sub": user_id,
        "aud": AGENTIOS_ID,          # 对应 AgentOS id 参数
        "scopes": list(set(scopes)),  # 去重
        "exp": ...,
    }
    return jwt.encode(payload, PRIVATE_KEY, algorithm="RS256")
```

**AgentOS 预置 scope 列表：**

| Scope | 含义 |
|-------|------|
| `agent_os:admin` | 全量权限 |
| `agents:read` / `agents:write` / `agents:delete` | Agent 管理 |
| `agents:<id>:run` | 运行指定 Agent |
| `agents:*:run` | 运行任意 Agent |
| `sessions:read/write/delete` | 会话管理 |
| `memories:read/write/delete` | 记忆管理 |
| `knowledge:read/write/delete` | 知识库管理 |
| `schedules:read/write/delete` | 定时任务 |
| `approvals:read/write` | 审批队列 |

#### service.py（核心）

```python
class RBACService:
    def __init__(self, db: AsyncSession):
        self.role_repo = RoleRepo(db)
        self.user_role_repo = UserRoleRepo(db)

    async def create_role(self, body: RoleCreate):
        return await self.role_repo.create(body.model_dump())

    async def assign_role(self, user_id: str, role_id: UUID):
        return await self.user_role_repo.create({"user_id": user_id, "role_id": role_id})

    async def revoke_role(self, user_id: str, role_id: UUID):
        await self.user_role_repo.delete(user_id, role_id)

    async def get_user_scopes(self, user_id: str) -> list[str]:
        """JWT 签发时调用，返回该用户所有角色合并后的 scopes"""
        roles = await self.user_role_repo.get_user_roles(user_id)
        scopes = set()
        for role in roles:
            scopes.update(role.scopes)
        return list(scopes)
```

#### JWT 签发（与 AgentOS 对接）

```python
# auth/jwt.py
async def issue_token(user_id: str, db: AsyncSession) -> str:
    scopes = await RBACService(db).get_user_scopes(user_id)
    payload = {
        "sub": user_id,
        "scopes": scopes,
        "exp": datetime.utcnow() + timedelta(hours=24),
    }
    return jwt.encode(payload, PRIVATE_KEY, algorithm="RS256")

# AgentOS 配置（main.py）
AuthorizationConfig(
    verification_keys=[PUBLIC_KEY],
    algorithm="RS256",
)
# AgentOS 自动验证 JWT 并按 scopes 鉴权，无需额外中间件
```

#### router.py

```python
# app/rbac/router.py
from fastapi import APIRouter, Depends
from core.deps import get_db
from .schemas import RoleCreate, AssignRoleRequest
from .service import RBACService

router = APIRouter(prefix="/rbac", tags=["RBAC"])


def svc(db=Depends(get_db)):
    return RBACService(db)


@router.get("/roles")
async def list_roles(s=Depends(svc)):
    return await s.list_roles()


@router.post("/roles", status_code=201)
async def create_role(body: RoleCreate, s=Depends(svc)):
    return await s.create_role(body)


@router.delete("/roles/{role_id}", status_code=204)
async def delete_role(role_id: str, s=Depends(svc)):
    await s.delete_role(role_id)


@router.post("/users/{user_id}/roles")
async def assign_role(user_id: str, body: AssignRoleRequest, s=Depends(svc)):
    return await s.assign_role(user_id, body.role_id)


@router.delete("/users/{user_id}/roles/{role_id}", status_code=204)
async def revoke_role(user_id: str, role_id: str, s=Depends(svc)):
    await s.revoke_role(user_id, role_id)


@router.post("/token")
async def issue_token(user_id: str, s=Depends(svc)):
    """签发 JWT，scopes 由用户角色决定"""
    scopes = await s.get_user_scopes(user_id)
    return {"token": s.sign_jwt(user_id, scopes)}
```

#### schemas

```python
# app/rbac/schemas.py
from pydantic import BaseModel

class RoleCreate(BaseModel):
    name: str
    scopes: list[str]   # e.g. ["agents:read", "agents:write", "admin"]

class AssignRoleRequest(BaseModel):
    role_id: str
```

---

### 5.20 Secrets（密钥管理）

> **设计决策**：密钥（api_key、token 等）直接以明文存储在各自的资源表字段中（如 `ag_models.api_key`、`ag_integrations.token`），无独立 secrets 表。依赖数据库访问控制和传输层 HTTPS 保障安全。如需加密，后期可对字段单独加密，不影响表结构。

---

### 5.21 Usage Logs & Audit Logs

#### 表设计

```sql
-- 用量日志（追加写，用 BIGSERIAL 避免 UUID 索引碎片）
CREATE TABLE ag_usage_logs (
    id            BIGSERIAL PRIMARY KEY,
    agent_id      UUID,
    user_id       VARCHAR(255),
    session_id    VARCHAR(255),
    model_id      UUID,
    input_tokens  BIGINT NOT NULL DEFAULT 0,
    output_tokens BIGINT NOT NULL DEFAULT 0,
    cost_usd      DECIMAL(12, 6),
    latency_ms    INT,
    created_at    TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_usage_logs_user  ON ag_usage_logs(user_id,  created_at DESC);
CREATE INDEX idx_usage_logs_agent ON ag_usage_logs(agent_id, created_at DESC);
CREATE INDEX idx_usage_logs_time  ON ag_usage_logs(created_at DESC);

-- 审计日志
CREATE TABLE ag_audit_logs (
    id            BIGSERIAL PRIMARY KEY,
    actor_id      VARCHAR(255),
    action        VARCHAR(20) NOT NULL,  -- CREATE/UPDATE/DELETE/RUN
    resource_type VARCHAR(50) NOT NULL,
    resource_id   UUID,
    diff          JSONB,
    ip            VARCHAR(50),
    created_at    TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_audit_logs_resource ON ag_audit_logs(resource_type, resource_id);
CREATE INDEX idx_audit_logs_actor    ON ag_audit_logs(actor_id, created_at DESC);
```

#### 写入方式

**Usage Logs**：通过 post_hook 自动采集，无需业务层手动调用。

```python
# hooks/usage_logger.py（注册为全局 post_hook）
from agno.hooks.decorator import hook

@hook(run_in_background=True)  # 后台写入，不阻塞响应
async def usage_log_hook(agent, run_context, **kwargs):
    """从 run_context 提取 token 用量，写入 ag_usage_logs"""
    metrics = getattr(run_context, "metrics", None)
    if not metrics:
        return
    from core.sync_db import SyncSession
    from sqlalchemy import text
    with SyncSession() as db:
        db.execute(text("""
            INSERT INTO ag_usage_logs
              (agent_id, user_id, session_id, model_id, input_tokens, output_tokens, latency_ms)
            VALUES
              (:agent_id, :user_id, :session_id, :model_id, :input_tokens, :output_tokens, :latency_ms)
        """), {
            "agent_id": agent.agent_id,
            "user_id": run_context.user_id,
            "session_id": run_context.session_id,
            "model_id": None,  # 可从 agent.model.id 获取
            "input_tokens": getattr(metrics, "input_tokens", 0),
            "output_tokens": getattr(metrics, "output_tokens", 0),
            "latency_ms": getattr(metrics, "time_to_first_token_ms", None),
        })
        db.commit()
```

**Audit Logs**：通过 FastAPI 中间件拦截管理层写操作。

```python
# core/audit.py
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

class AuditMiddleware(BaseHTTPMiddleware):
    """拦截 /management/* 的 POST/PATCH/DELETE，写审计日志"""
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        method = request.method
        path = request.url.path
        if path.startswith("/management/") and method in ("POST", "PATCH", "DELETE"):
            action = {"POST": "CREATE", "PATCH": "UPDATE", "DELETE": "DELETE"}.get(method)
            actor_id = request.state.user_id if hasattr(request.state, "user_id") else None
            # 异步写审计日志（fire-and-forget）
            asyncio.create_task(_write_audit(actor_id, action, path, request.client.host))
        return response

# main.py 中注册
app.add_middleware(AuditMiddleware)
```

#### 读取端点（router.py）

```python
# app/logs/router.py
from fastapi import APIRouter, Depends, Query
from core.deps import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

router = APIRouter(prefix="/logs", tags=["Logs"])


@router.get("/usage")
async def get_usage_logs(
    agent_id: str | None = None,
    user_id: str | None = None,
    limit: int = Query(50, le=500),
    offset: int = 0,
    db: AsyncSession = Depends(get_db),
):
    filters, params = ["1=1"], {}
    if agent_id:
        filters.append("agent_id=:agent_id")
        params["agent_id"] = agent_id
    if user_id:
        filters.append("user_id=:user_id")
        params["user_id"] = user_id
    params.update({"limit": limit, "offset": offset})
    result = await db.execute(
        text(f"SELECT * FROM ag_usage_logs WHERE {' AND '.join(filters)} "
             "ORDER BY created_at DESC LIMIT :limit OFFSET :offset"),
        params,
    )
    return result.fetchall()


@router.get("/audit")
async def get_audit_logs(
    resource_type: str | None = None,
    actor_id: str | None = None,
    limit: int = Query(50, le=500),
    offset: int = 0,
    db: AsyncSession = Depends(get_db),
):
    filters, params = ["1=1"], {}
    if resource_type:
        filters.append("resource_type=:resource_type")
        params["resource_type"] = resource_type
    if actor_id:
        filters.append("actor_id=:actor_id")
        params["actor_id"] = actor_id
    params.update({"limit": limit, "offset": offset})
    result = await db.execute(
        text(f"SELECT * FROM ag_audit_logs WHERE {' AND '.join(filters)} "
             "ORDER BY created_at DESC LIMIT :limit OFFSET :offset"),
        params,
    )
    return result.fetchall()
```

---

## 六、Agno 原生表（只读）

| 表名 | 用途 | 谁写 |
|------|------|------|
| `agno_sessions` | 会话历史 | Agno |
| `agno_user_memory` | 用户记忆 | Agno |
| `agno_traces` / `agno_spans` | OTel 链路追踪 | Agno |
| `agno_approvals` | HITL 审批记录 | Agno |
| `agno_schedules` | 定时任务运行记录 | Agno |
| `agno_knowledge` | LearningMachine 知识 | Agno |
| `agno_eval` | 评测结果 | Agno |
| `agno_metrics` | 运行指标 | Agno |
| `agno_cultural_knowledge` | CultureManager 知识 | Agno |

---

## 七、索引汇总

```sql
-- bindings（热路径，每次 run 查询）
CREATE INDEX idx_bindings_owner      ON ag_bindings(owner_type, owner_id);
CREATE INDEX idx_bindings_owner_type ON ag_bindings(owner_type, owner_id, resource_type);
CREATE INDEX idx_bindings_enabled    ON ag_bindings(owner_id, enabled);

-- documents
CREATE INDEX idx_documents_kb_id    ON ag_documents(kb_id);
CREATE INDEX idx_documents_status   ON ag_documents(kb_id, status);

-- workflow 节点树
CREATE INDEX idx_workflow_nodes_workflow ON ag_workflow_nodes(workflow_id);
CREATE INDEX idx_workflow_nodes_parent   ON ag_workflow_nodes(parent_node_id);

-- team 成员
CREATE INDEX idx_team_members_team  ON ag_team_members(team_id);

-- 日志
CREATE INDEX idx_usage_logs_user    ON ag_usage_logs(user_id,  created_at DESC);
CREATE INDEX idx_usage_logs_agent   ON ag_usage_logs(agent_id, created_at DESC);
CREATE INDEX idx_audit_logs_resource ON ag_audit_logs(resource_type, resource_id);

-- 基础过滤
CREATE INDEX idx_agents_enabled     ON ag_agents(enabled);
CREATE INDEX idx_models_enabled     ON ag_models(enabled);
CREATE INDEX idx_vectordbs_enabled  ON ag_vectordbs(enabled);
CREATE INDEX idx_user_roles_user    ON ag_user_roles(user_id);

-- schedules
CREATE INDEX idx_schedules_agent_id ON ag_schedules(agent_id);
CREATE INDEX idx_schedules_team_id  ON ag_schedules(team_id);

-- integrations FK
CREATE INDEX idx_integrations_agent_id    ON ag_integrations(agent_id);
CREATE INDEX idx_integrations_team_id     ON ag_integrations(team_id);
CREATE INDEX idx_integrations_workflow_id ON ag_integrations(workflow_id);
```
