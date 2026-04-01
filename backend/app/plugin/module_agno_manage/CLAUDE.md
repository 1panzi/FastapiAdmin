# module_agno_manage — CLAUDE.md

## 项目概述

基于 Agno 框架的 AI 资源管理平台插件，集成到 FastapiAdmin 后端。
通过 FastAPI CRUD API 管理 `ag_*` 数据库表，同时维护内存中的 RuntimeRegistry，将 DB 配置翻译成活的 Agno 对象。

---

## 架构分层

```
管理层  (controller → service → crud → ag_* 表)
   ↕  启动/CRUD 时 Hydrate
RuntimeRegistry（内存单例）
   ↕  base_app 共享同一 FastAPI 实例
AgentOS（直接复用，不重写）
   ↕  持久化运行时数据
Agno 原生表（agno_sessions / agno_user_memory / agno_traces）
```

**层次职责：**
- `controller.py` — 只管 HTTP 路由（参数/响应/状态码），调 service，不直接碰 DB 或 registry
- `service.py` — 业务逻辑，唯一调 crud（DB）+ registry（运行时）的层
- `crud.py` — 只管 SQL，零 Agno 知识
- `core/registry.py` — RuntimeRegistry 单例，只管运行时对象，零 DB 知识

---

## 代码约定

### 目录结构
每个模块遵循：`<module>/model.py` | `schema.py` | `crud.py` | `service.py` | `controller.py`

### 命名规范
- ORM 类：`Ag<ModuleName>Model`（如 `AgModelModel`）
- CRUD 类：`Ag<ModuleName>CRUD`
- Service 类：`Ag<ModuleName>Service`
- Schema 类：`AgModel{Create/Update/Out/QueryParam}Schema`

### registry key
使用 `str(obj.uuid)` 作为 registry 中所有对象的 key（非 int id）。

### status 字段
- `"0"` = 启用，`"1"` = 禁用
- 创建时默认 `"0"`

---

## 核心组件

### `core/registry.py` — RuntimeRegistry
- **全局单例**：`_registry: RuntimeRegistry | None = None`，通过 `get_registry()` 访问
- `register_model(uuid: str, row)` — 根据 provider 构建 Agno Model 实例
- `unregister_model(uuid: str)` — 从缓存移除
- `get_model(uuid: str)` — 取模型实例（Agent 创建时使用）
- `resolve_tools(agent_id)` / `resolve_knowledge(agent_id)` — callable factory 同步调用
- LRUCache 用于 knowledge（maxsize=50）和 mcp（maxsize=20）

### `core/sync_db.py` — SyncBindingRepo
- Agno callable factory 在 `run()` 时**同步**调用，不能 await
- 使用独立同步连接池（`settings.DB_URI`，psycopg），与主 asyncpg 隔离
- `SyncBindingRepo.get_active(owner_id, owner_type, resource_type)` — 查 ag_bindings

### `core/startup.py` — 预热逻辑
- `warm_up()` — 按依赖顺序加载所有启用资源到 registry（asyncio.Lock 保证幂等）
- 由 `core/controller.py` 中的 `CoreRouter.add_event_handler("startup", ...)` 触发
- **无需修改任何上层配置文件**，完全自包含

### `core/controller.py` — 生命周期控制器
- 定义 `CoreRouter`，无路由端点，仅挂载 startup/shutdown 事件
- 被 `get_dynamic_router()` 自动发现（匹配 `module_*/core/controller.py`）
- FastAPI `include_router` 时将事件逐层传递到 app

---

## 模块开发进度

| 模块 | DB Model | Schema | CRUD | Service | Controller | Registry 集成 |
|------|----------|--------|------|---------|-----------|--------------|
| models | ✅ | ✅ | ✅ | ✅+Registry | ✅ | ✅ |
| toolkits | ✅ | ✅ | ✅ | ✅+Registry+Catalog | ✅+Catalog | ✅ |
| agents | ✅ | ✅ | ✅ | ✅+Registry | ✅ | ✅ |
| embedders | ✅ | ✅ | ✅ | ⬜ 待集成 | ✅ | ⬜ |
| vectordbs | ✅ | ✅ | ✅ | ⬜ 待集成 | ✅ | ⬜ |
| knowledge_bases | ✅ | ✅ | ✅ | ⬜ 待集成 | ✅ | ⬜ |
| mcp_servers | ✅ | ✅ | ✅ | ⬜ 待集成 | ✅ | ⬜ |
| toolkits | ✅ | ✅ | ✅ | ✅+Registry+Catalog | ✅+Catalog | ✅ |
| skills | ✅ | ✅ | ✅ | ⬜ 待集成 | ✅ | ⬜ |
| hooks | ✅ | ✅ | ✅ | ⬜ 待集成 | ✅ | ⬜ |
| guardrails | ✅ | ✅ | ✅ | ⬜ 待集成 | ✅ | ⬜ |
| memory_managers | ✅ | ✅ | ✅ | ⬜ 待集成 | ✅ | ⬜ |
| learning_configs | ✅ | ✅ | ✅ | ⬜ 待集成 | ✅ | ⬜ |
| reasoning_configs | ✅ | ✅ | ✅ | ⬜ 待集成 | ✅ | ⬜ |
| compression_configs | ✅ | ✅ | ✅ | ⬜ 待集成 | ✅ | ⬜ |
| sess_summary_configs | ✅ | ✅ | ✅ | ⬜ 待集成 | ✅ | ⬜ |
| culture_configs | ✅ | ✅ | ✅ | ⬜ 待集成 | ✅ | ⬜ |
| agents | ✅ | ✅ | ✅ | ✅+Registry | ✅ | ✅ |
| teams | ✅ | ✅ | ✅ | ⬜ 待集成 | ✅ | ⬜ |
| workflows | ✅ | ✅ | ✅ | ⬜ 待集成 | ✅ | ⬜ |
| bindings | ✅ | ✅ | ✅ | ⬜ 待集成 | ✅ | ⬜ |
| schedules | ✅ | ✅ | ✅ | — 无 | ✅ | — |
| roles | ✅ | ✅ | ✅ | — 无 | ✅ | — |
| user_roles | ✅ | ✅ | ✅ | — 无 | ✅ | — |
| audit_logs | ✅ | ✅ | ✅ | — 无 | ✅ | — |
| usage_logs | ✅ | ✅ | ✅ | — 无 | ✅ | — |
| integrations | ✅ | ✅ | ✅ | ⬜ 待集成 | ✅ | ⬜ |

---

## 启动预热顺序（RuntimeRegistry）

```
models → embedders
→ vectordbs (行数据) → knowledge_bases (行数据)
→ toolkits → mcp_servers (行数据) → skills (行数据)
→ hooks → guardrails
→ memory_managers/learning/reasoning/compression/session_summary/culture (行数据)
→ agents (依赖上层全部) → teams → workflows
→ integrations
```

---

## 支持的 Model Provider

| provider | Agno 类 | 参数 |
|---------|---------|------|
| openai | OpenAIChat | id, api_key, base_url, **config |
| anthropic | Claude | id, api_key, **config |
| google | Gemini | id, api_key, **config |
| ollama | Ollama | id, host=base_url, **config |
| groq | Groq | id, api_key, **config |
| deepseek | DeepSeek | id, api_key, base_url, **config |
| mistral | MistralChat | id, api_key, **config |
| azure | AzureOpenAI | id, api_key, azure_endpoint=base_url, **config |
| cohere | CohereChat | id, api_key, **config |
| together | Together | id, api_key, **config |
| openai_like | OpenAIChat | id, api_key, base_url, **config |

---

## 已知注意事项

- Agno callable factory 必须**同步**调用（`cache_callables=False`），详见 `core/sync_db.py`
- `ag_*` 表为管理表，Agno 原生表（`agno_sessions` 等）由 Agno 自动管理，勿手动修改
- `api_key` 当前明文存储，生产环境应考虑加密
- registry 在应用启动时由 `core/controller.py` 中的 CoreRouter 自动触发预热，无需修改上层配置
