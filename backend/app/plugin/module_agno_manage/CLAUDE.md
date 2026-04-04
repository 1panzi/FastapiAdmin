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
- `update_kb_row(kid, row)` / `remove_kb_row(kid)` — 知识库行数据同步（自动失效 LRU 缓存）
- `update_reader_row(rid, row)` / `remove_reader_row(rid)` — reader 行数据同步（同时通过 `_invalidate_kb_cache_by_reader` 级联失效所有绑定该 reader 的知识库 LRU 缓存）
- `_build_reader(reader_row, config_override)` — 构建 Agno Reader 实例，处理 chunking 策略（含 SemanticChunker/AgenticChunker 特殊依赖）
- `_build_knowledge(kb_id, row)` — 构建 Agno Knowledge 实例，通过 SyncBindingRepo 查 reader 绑定

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

### `readers/agno_catalog.py` — Reader & Chunking 元数据目录
- `ReaderInfo` / `ChunkingStrategyInfo` / `ParamSchema` TypedDict 定义
- 16 种 reader 类型：pdf/docx/pptx/csv/field_labeled_csv/excel/json/markdown/text/website/firecrawl/tavily/web_search/youtube/arxiv/wikipedia
- 8 种 chunking 策略：FixedSizeChunker/RecursiveChunker/DocumentChunker/MarkdownChunker/RowChunker/SemanticChunker/AgenticChunker/CodeChunker
- `get_supported_strategies_for_reader(reader_type)` — 优先动态调用 Agno `ReaderFactory`，失败时回退静态目录

---

## 模块开发进度

| 模块 | DB Model | Schema | CRUD | Service | Controller | Registry 集成 |
|------|----------|--------|------|---------|-----------|--------------|\
| models | ✅ | ✅ | ✅ | ✅+Registry | ✅ | ✅ |
| toolkits | ✅ | ✅ | ✅ | ✅+Registry+Catalog | ✅+Catalog | ✅ |
| agents | ✅ | ✅ | ✅ | ✅+Registry | ✅ | ✅ |
| embedders | ✅ | ✅ | ✅ | ✅+Registry | ✅ | ✅ |
| vectordbs | ✅ | ✅ | ✅ | ✅+Registry | ✅ | ✅ |
| knowledge_bases | ✅ | ✅ | ✅ | ✅+Registry | ✅ | ✅ |
| readers | ✅ | ✅ | ✅ | ✅+Registry+Catalog | ✅+Catalog | ✅ |
| toolkits | ✅ | ✅ | ✅ | ✅+Registry+Catalog | ✅+Catalog | ✅ |
| mcp_servers | ✅ | ✅ | ✅ | ✅+Registry | ✅ | ✅ |
| skills | ✅ | ✅ | ✅ | ✅+Registry | ✅ | ✅ |
| hooks | ✅ | ✅ | ✅ | ✅+Registry | ✅ | ✅ |
| guardrails | ✅ | ✅ | ✅ | ✅+Registry | ✅ | ✅ |
| memory_managers | ✅ | ✅ | ✅ | ✅+Registry | ✅ | ✅ |
| learning_configs | ✅ | ✅ | ✅ | ✅+Registry | ✅ | ✅ |
| reasoning_configs | ✅ | ✅ | ✅ | ✅+Registry | ✅ | ✅ |
| compression_configs | ✅ | ✅ | ✅ | ✅+Registry | ✅ | ✅ |
| sess_summary_configs | ✅ | ✅ | ✅ | ✅+Registry | ✅ | ✅ |
| culture_configs | ✅ | ✅ | ✅ | ✅+Registry | ✅ | ✅ |
| agents | ✅ | ✅ | ✅ | ✅+Registry | ✅ | ✅ |
| teams | ✅ | ✅ | ✅ | ✅+Registry | ✅ | ✅ |
| workflows | ✅ | ✅ | ✅ | ✅+Registry | ✅ | ✅ |
| bindings | ✅ | ✅ | ✅ | ✅+Registry | ✅ | ✅ |
| integrations | ✅ | ✅ | ✅ | ✅+Registry | ✅ | ✅ |
| schedules | ✅ | ✅ | ✅ | — 无 | ✅ | — |
| roles | ✅ | ✅ | ✅ | — 无 | ✅ | — |
| user_roles | ✅ | ✅ | ✅ | — 无 | ✅ | — |
| audit_logs | ✅ | ✅ | ✅ | — 无 | ✅ | — |
| usage_logs | ✅ | ✅ | ✅ | — 无 | ✅ | — |

---

## 启动预热顺序（RuntimeRegistry）

```
models → embedders
→ vectordbs (行数据) → knowledge_bases (行数据) → readers (行数据)
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
- reader 行数据更新时，会级联失效所有绑定该 reader 的知识库 LRU 缓存（`_invalidate_kb_cache_by_reader`）
- knowledge_bases 表已移除 reader_type/reader_config/default_filters 字段，reader 配置改由独立 ag_readers 表管理，通过 ag_bindings 绑定到知识库
- bindings 的 config_override 字段支持在绑定层覆盖 reader/其他资源的参数配置
- 同一知识库下每种 `reader_type` 只允许绑定一个 reader（在 `bindings/service.py` 的 `_check_knowledge_reader_type_unique` 中校验，创建和更新时触发，仅限 `owner_type="knowledge"` + `resource_type="reader"` 的绑定）
