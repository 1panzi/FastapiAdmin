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
- LRUCache 用于 mcp（maxsize=20）；knowledge 改用普通 dict `_knowledge_map`（全量常驻，启动时预构建）
- `update_kb_row(kid, row)` / `remove_kb_row(kid)` — 知识库行数据同步，同步更新 `_knowledge_map`
- `update_reader_row(rid, row)` / `remove_reader_row(rid)` — reader 行数据同步（同时通过 `_invalidate_kb_cache_by_reader` 级联重建所有绑定该 reader 的知识库实例）
- `_build_reader(reader_row, config_override)` — 构建 Agno Reader 实例，处理 chunking 策略（含 SemanticChunker/AgenticChunker 特殊依赖）
- `_build_knowledge(kb_id, row)` — 构建 Agno Knowledge 实例，通过 SyncBindingRepo 查 reader 绑定，**必须传 `contents_db=self._agno_db`**
- `get_knowledge(kb_id)` — 从 `_knowledge_map` 取已构建的 Knowledge 实例（供 documents 路由使用）

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
- reader 行数据更新时，会级联重建所有绑定该 reader 的知识库实例（`_invalidate_kb_cache_by_reader`，名称保留但逻辑改为重建而非失效 LRU）
- knowledge_bases 表已移除 reader_type/reader_config/default_filters 字段，reader 配置改由独立 ag_readers 表管理，通过 ag_bindings 绑定到知识库
- bindings 的 config_override 字段支持在绑定层覆盖 reader/其他资源的参数配置
- 同一知识库下每种 `reader_type` 只允许绑定一个 reader（在 `bindings/service.py` 的 `_check_knowledge_reader_type_unique` 中校验，创建和更新时触发，仅限 `owner_type="knowledge"` + `resource_type="reader"` 的绑定）
- `bindings/controller.py` 维护静态 `BINDING_META` 字典，定义 owner 类型（agent/team/knowledge）→ 可绑资源类型及其前端 api_path 映射，通过 `GET /agno_manage/bindings/meta` 暴露给前端；前端 bindings 页面根据此元数据动态渲染下拉选项并发起列表请求，新增 owner/resource 类型只需修改 `BINDING_META`
- team 的成员关系走独立的 `ag_team_members` 表（非 `ag_bindings`），有 `member_order`/`role` 字段；`ag_bindings` 只管 toolkit/skill/knowledge 等能力资源挂载
- `ag_documents` 是文件注册表 + 向量化状态追踪，字段职责见下方「documents 模块设计」；**不使用** Agno 内置的 `/knowledge/content` 路由（其 `knowledge_id` 为哈希值，与我们的整数 ID 不兼容，auth 也不走我们的权限体系）
- `_build_knowledge()` 必须传 `contents_db=self._agno_db`，否则 Agno 无法追踪文档处理状态
- knowledge 实例从 LRU 改为普通 dict `_knowledge_map`，启动时全量预构建，CRUD 时同步更新

---

## documents 模块设计

### 定位

`ag_documents` = **文件注册表 + 向量化状态追踪**，独立于 Agno 的 `contents_db`。

| 字段 | 职责 |
|------|------|
| `kb_id` | 属于哪个知识库 |
| `name` | 文件名/来源名称 |
| `storage_type` | `local` / `s3` / `url` |
| `storage_path` | 文件本地路径、S3 Key 或 URL |
| `doc_status` | `pending` → `processing` → `indexed` / `failed` |
| `error_msg` | 向量化失败原因 |
| `metadata_config` | 文件自身的业务元数据（标签、来源、分类等），独立于 Agno |
| `content_id` | 对应 Agno `contents_db` 的记录 ID（外键引用，可为空） |

### 为什么保留 `ag_documents`

- **重新向量化**：更换 embedder 或 chunking 策略后，可从 `storage_path` 重新读取原始文件触发向量化，无需用户重传
- **自己的状态查询**：管理界面展示文档状态、筛选失败记录，直接查自己的表，无需调 Agno 内部方法
- **业务元数据独立**：`metadata_config` 存业务侧标签/分类/来源等，与 Agno `contents_db` 的 metadata 字段互相独立，宁可两边重复也不依赖 Agno 内部结构
- Agno `contents_db` 是 Agno 内部追踪层，`ag_documents` 是我们的业务层，两者通过 `content_id` 关联，但各自独立，不强依赖

### 文档路由（挂载在 `knowledge_bases/controller.py`）

```
POST   /knowledge_bases/{id}/docs/upload        上传文件 → 后台向量化
POST   /knowledge_bases/{id}/docs               插入 URL / 文本
GET    /knowledge_bases/{id}/docs               列出文档（分页，查 ag_documents）
GET    /knowledge_bases/{id}/docs/{doc_id}      文档详情
DELETE /knowledge_bases/{id}/docs/{doc_id}      删除文档（同时删 VectorDB chunks）
POST   /knowledge_bases/{id}/docs/{doc_id}/reprocess  重新向量化（读 storage_path）
GET    /knowledge_bases/{id}/search             向量检索
```

### 后台向量化任务模式

```python
async def _vectorize_document(kb, doc_id, content, auth):
    await update_doc_status(doc_id, "processing", auth)
    try:
        await kb._aload_content(content, upsert=False, skip_if_exists=True)
        await update_doc_status(doc_id, "indexed", auth, content_id=content.id)
    except Exception as e:
        await update_doc_status(doc_id, "failed", auth, error_msg=str(e))
```
