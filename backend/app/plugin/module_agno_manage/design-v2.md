# AI 管理平台设计文档 v2

基于 Agno 框架，用 FastAPI + PostgreSQL 构建的 AI 资源管理平台 v2。
v2 是独立的新版本，v1 保留不动。

---

## 一、核心设计原则

v2 相对 v1 的根本变化：

| 方面 | v1 | v2 |
|------|----|----|
| 表数量 | 20+ 张 | 1 张 `ag_resources` |
| 模块数量 | 28 个 | 1 个 `resource/` |
| 资源关系 | 外键 + `ag_bindings` | config 内联 dict |
| 外键 | 大量 | 无 |
| Registry | 884 行，复杂 resolve 链 | ~50 行，只管列表 |
| 新增资源类型 | 加表 + 加模块 | 加一个 Builder 文件 |
| 前端表单 | 硬编码字段 | 由后端 schema API 驱动 |

---

## 二、统一资源表

所有资源（model/embedder/reader/toolkit/knowledge/agent/team 等）统一存一张表：

```sql
CREATE TABLE ag_resources (
    id           SERIAL PRIMARY KEY,
    uuid         VARCHAR(64)  NOT NULL UNIQUE,
    name         VARCHAR(255) NOT NULL,
    category     VARCHAR(50)  NOT NULL,   -- model/embedder/reader/toolkit/knowledge/agent/team
    type         VARCHAR(50)  NOT NULL,   -- openai/pdf/duckduckgo/base...
    config       JSONB        NOT NULL DEFAULT '{}',
    status       VARCHAR(10)  NOT NULL DEFAULT '0',  -- 0:启用 1:禁用
    description  TEXT,
    created_time TIMESTAMP    NOT NULL,
    updated_time TIMESTAMP    NOT NULL,
    created_id   INTEGER,
    updated_id   INTEGER
);

CREATE INDEX ix_ag_resources_category ON ag_resources(category);
CREATE INDEX ix_ag_resources_type     ON ag_resources(type);
CREATE INDEX ix_ag_resources_status   ON ag_resources(status);
```

### category 与 type 的关系

- **category**：资源的大类，决定它能被谁用、显示在哪里
- **type**：具体实现，决定用哪个 Builder 实例化

```
category=model,     type=openai / anthropic / ollama / groq ...
category=embedder,  type=openai / azure / ollama / cohere ...
category=reader,    type=pdf / website / csv / docx / youtube ...
category=toolkit,   type=duckduckgo / python / shell / custom ...
category=knowledge, type=base
category=agent,     type=base
category=team,      type=base
```

---

## 三、config 结构：ref 与 inline 两种模式

资源的 config 中，引用其他资源时支持两种模式：

### 3.1 ref 模式（活链接）

```json
{
  "model": { "ref": "model-uuid-xxx" }
}
```

模板更新后，下次实例化时自动使用最新配置。

### 3.2 ref + override（活链接 + 参数覆盖）

```json
{
  "model": {
    "ref": "model-uuid-xxx",
    "override": {
      "temperature": 0.9,
      "max_tokens": 2048
    }
  }
}
```

以模板 config 为基础，override 字段优先。

### 3.3 inline 模式（独立副本）

```json
{
  "model": {
    "category": "model",
    "type": "openai",
    "model_id": "gpt-4o",
    "api_key": "sk-xxx",
    "temperature": 0.7
  }
}
```

与任何模板无关，独立存储。

### 3.4 数组支持

tools/members 等字段支持数组，每个元素均可为 ref 或 inline：

```json
{
  "tools": [
    { "ref": "toolkit-uuid-1" },
    { "ref": "toolkit-uuid-2", "override": {} },
    { "category": "toolkit", "type": "duckduckgo" }
  ]
}
```

### 3.5 前端交互

用户选择一个模板后，出现开关：

```
[从模板选 ▼]  gpt-4o

使用方式：[引用模板 ●]  [独立副本 ○]

（引用模板时可选填覆盖参数）
▶ 覆盖参数
```

- 选「引用模板」→ 前端提交 `{"ref": "uuid"}`
- 选「独立副本」→ 前端把模板 config 复制填入表单 → 提交完整 inline dict
- 「转为独立副本」按钮：把已有 ref 展开成 inline，断开链接

---

## 四、资源 config 结构示例

### Agent config

```json
{
  "model":        { "ref": "model-uuid" },
  "instructions": "你是一个搜索助手",
  "tools": [
    { "ref": "toolkit-uuid-1" },
    { "category": "toolkit", "type": "mcp", "url": "http://mcp:8080", "transport": "sse" }
  ],
  "knowledge":  { "ref": "kb-uuid" },
  "skills":     [{ "ref": "skill-uuid" }],
  "memory":     { "ref": "memory-uuid" },
  "reasoning":  { "ref": "reasoning-uuid" }
}
```

### Knowledge config

```json
{
  "embedder": { "ref": "embedder-uuid" },
  "vectordb": {
    "category": "vectordb",
    "type": "pgvector",
    "table_name": "kb_product_docs"
  },
  "readers": [
    { "ref": "reader-uuid-1" },
    { "ref": "reader-uuid-2", "override": { "chunk_size": 300 } }
  ],
  "max_results": 10
}
```

### Team config

```json
{
  "mode":  "coordinate",
  "model": { "ref": "model-uuid" },
  "members": [
    { "ref": "agent-uuid-1", "role": "leader" },
    { "ref": "agent-uuid-2" },
    {
      "ref": "agent-uuid-3",
      "override": { "instructions": "专注回答销售问题" }
    }
  ]
}
```

---

## 五、Builder 系统

### 5.1 目录结构

```
module_agno_manage_v2/
├── core/
│   ├── builder_base.py      # BaseBuilder 基类 + generate_schema_from_class
│   ├── ref_resolver.py      # ref/inline/override 统一处理
│   ├── builder_registry.py  # 全局 Builder 注册表
│   ├── registry.py          # RuntimeRegistry（极简，只管 agent/team 列表）
│   ├── startup.py           # 预热逻辑
│   └── controller.py        # 生命周期（startup/shutdown 事件）
│
├── builders/
│   ├── models/
│   │   ├── base.py          # BaseModelBuilder（反射 agno Model 基类）
│   │   ├── openai.py
│   │   ├── anthropic.py
│   │   ├── ollama.py
│   │   └── ...
│   ├── embedders/
│   │   ├── base.py          # BaseEmbedderBuilder
│   │   ├── openai.py
│   │   └── ...
│   ├── readers/
│   │   ├── base.py          # BaseReaderBuilder（schema = extra_fields + chunk 动态字段）
│   │   ├── pdf.py           # 各 reader 独立 Builder（声明 agno_class + extra_fields）
│   │   ├── csv.py
│   │   ├── docx.py
│   │   ├── text.py
│   │   ├── json_reader.py
│   │   ├── website.py
│   │   ├── youtube.py
│   │   ├── arxiv.py
│   │   └── chunk/           # Chunker Builder 子模块
│   │       ├── base.py      # BaseChunkerBuilder（继承 BaseBuilder）+ CHUNKER_REGISTRY
│   │       ├── fixed.py     # FixedSizeChunkerBuilder
│   │       ├── recursive.py
│   │       ├── document.py
│   │       ├── markdown.py
│   │       ├── row.py
│   │       ├── code.py
│   │       ├── semantic.py
│   │       └── agentic.py
│   ├── toolkits/
│   │   ├── catalog.py   # TOOLKIT_CATALOG（100+ agno 工具）
│   │   ├── base.py      # BaseToolkitBuilder
│   │   ├── generic.py   # GenericToolkitBuilder（懒加载 + 反射，替代所有独立 toolkit builder）
│   │   └── custom.py    # CustomToolkitBuilder（用户自定义 module_path/class_name）
│   ├── knowledge/
│   ├── agents/
│   └── teams/
│
├── resource/                # 单一模块，管所有资源
│   ├── model.py             # AgResourceModel ORM
│   ├── schema.py            # 通用 Create/Update/Out schema
│   ├── crud.py              # 通用 CRUD（按 category 过滤）
│   ├── service.py           # 按 category 路由到对应 Builder
│   └── controller.py        # 统一 API 入口
│
└── catalog/
    └── controller.py        # GET /schema?category=&type= 统一入口
```

### 5.2 Builder 基类

```python
# core/builder_base.py
from abc import ABC, abstractmethod
import inspect
from typing import Any


def generate_schema_from_class(cls) -> list[dict]:
    """从 Agno 类的 __init__ 签名自动提取字段定义"""
    try:
        sig = inspect.signature(cls.__init__)
    except (ValueError, TypeError):
        return []

    fields = []
    for name, param in sig.parameters.items():
        if name == "self":
            continue
        if name.startswith("_"):          # 内部参数
            continue
        if name.startswith("model_"):     # Pydantic 内部
            continue

        field: dict = {"name": name}

        # 自动推断类型
        ann = param.annotation
        if ann == int:
            field["type"] = "int"
        elif ann == float:
            field["type"] = "float"
        elif ann == bool:
            field["type"] = "bool"
        elif ann == str:
            field["type"] = "str"
        else:
            field["type"] = "str"  # 兜底

        # 自动提取默认值
        if param.default != inspect.Parameter.empty:
            field["default"] = param.default
            field["required"] = False
        else:
            field["required"] = True

        fields.append(field)
    return fields


class BaseBuilder(ABC):
    category: str = ""
    type: str = ""
    label: str = ""

    agno_class = None      # 指向 Agno 类，自动反射字段

    # 子类专属字段（手动定义或覆盖已有字段）
    extra_fields: list[dict] = []

    # UI 元数据补充（label/group/span/tooltip/约束等）
    field_meta: dict[str, dict] = {}

    @property
    def schema(self) -> list[dict]:
        fields: dict[str, dict] = {}

        # 1. 沿 MRO 反射所有基类的 agno_class（父类先填，子类不覆盖已有）
        for parent in type(self).__mro__:
            if hasattr(parent, "agno_class") and parent.agno_class is not None:
                for f in generate_schema_from_class(parent.agno_class):
                    if f["name"] not in fields:
                        fields[f["name"]] = f

        # 2. extra_fields 覆盖/追加
        for f in self.extra_fields:
            fields[f["name"]] = {**fields.get(f["name"], {}), **f}

        # 3. 沿 MRO 合并所有层级的 field_meta（子类覆盖父类）
        for parent in reversed(type(self).__mro__):
            if hasattr(parent, "field_meta"):
                for name, meta in parent.field_meta.items():
                    if name in fields:
                        fields[name].update(meta)

        return sorted(fields.values(), key=lambda x: x.get("order", 99))

    @abstractmethod
    def build(self, config: dict, resolver) -> Any:
        """接收展开后的 config dict，返回 Agno 对象"""
        ...
```

### 5.3 Builder 示例

```python
# builders/models/base.py
from agno.models.base import Model
from core.builder_base import BaseBuilder

class BaseModelBuilder(BaseBuilder):
    category = "model"
    agno_class = Model

    field_meta = {
        "api_key":  {"type": "password", "label": "API Key",  "group": "认证", "order": 1, "span": 24},
        "base_url": {"label": "Base URL", "group": "认证", "order": 2, "span": 24,
                     "placeholder": "留空使用默认地址", "required": False},
    }


# builders/models/openai.py
from agno.models.openai import OpenAIChat
from .base import BaseModelBuilder

class OpenAIModelBuilder(BaseModelBuilder):
    type = "openai"
    label = "OpenAI"
    agno_class = OpenAIChat

    field_meta = {
        **BaseModelBuilder.field_meta,
        "temperature": {"label": "温度", "group": "生成参数", "order": 10,
                        "span": 12, "min": 0.0, "max": 2.0, "step": 0.1},
        "max_tokens":  {"label": "最大 Token", "group": "生成参数", "order": 11,
                        "span": 12, "min": 1, "max": 128000},
    }

    def build(self, config: dict, resolver) -> OpenAIChat:
        return OpenAIChat(
            id=config.get("model_id", "gpt-4o"),
            api_key=config.get("api_key"),
            base_url=config.get("base_url"),
            temperature=config.get("temperature"),
            max_tokens=config.get("max_tokens"),
        )


# builders/models/ollama.py
from agno.models.ollama import Ollama
from .base import BaseModelBuilder

class OllamaModelBuilder(BaseModelBuilder):
    type = "ollama"
    label = "Ollama"
    agno_class = Ollama

    # Ollama 不需要 api_key，隐藏掉
    extra_fields = [
        {"name": "api_key", "hidden": True, "required": False},
    ]
    field_meta = {
        **BaseModelBuilder.field_meta,
        "base_url": {"label": "Host", "placeholder": "http://localhost:11434",
                     "required": True},
    }

    def build(self, config: dict, resolver) -> Ollama:
        return Ollama(id=config.get("model_id"), host=config.get("base_url"))
```

### 5.4 Builder 注册表

```python
# core/builder_registry.py
# readers 逐一手动注册（每种 reader 有独立 Builder 文件）
builder_registry: dict[tuple[str, str], BaseBuilder] = {
    ("model",   "openai"):     OpenAIModelBuilder(),
    ("model",   "anthropic"):  AnthropicModelBuilder(),
    ("model",   "ollama"):     OllamaModelBuilder(),
    ("embedder","openai"):     OpenAIEmbedderBuilder(),
    ("reader",  "pdf"):        PdfReaderBuilder(),
    ("reader",  "docx"):       DocxReaderBuilder(),
    ("reader",  "text"):       TextReaderBuilder(),
    ("reader",  "csv"):        CsvReaderBuilder(),
    ("reader",  "json"):       JsonReaderBuilder(),
    ("reader",  "website"):    WebsiteReaderBuilder(),
    ("reader",  "youtube"):    YoutubeReaderBuilder(),
    ("reader",  "arxiv"):      ArxivReaderBuilder(),
    ("agent",   "base"):       AgentBuilder(),
    ("team",    "base"):       TeamBuilder(),
    # ...
}

# toolkits：按 TOOLKIT_CATALOG 批量注册，custom 单独注册
for _type_key in TOOLKIT_CATALOG:
    builder_registry[("toolkit", _type_key)] = GenericToolkitBuilder(_type_key)
builder_registry[("toolkit", "custom")] = CustomToolkitBuilder()
```

### 5.5 Toolkit Catalog + GenericToolkitBuilder

agno 内置工具多达 100+，不能为每个工具写独立 Builder 文件。改为：

- **`catalog.py`**：维护 `TOOLKIT_CATALOG`，key 为 `type` 字符串，value 含 `module_path / class_name / name / category / description`
- **`generic.py`**：`GenericToolkitBuilder` 按 type 从 catalog 查找并懒加载目标类，自动反射 `__init__` 生成 schema
- **`builder_registry.py`**：一行循环注册所有 catalog 工具，`custom` 单独注册

```python
# builders/toolkits/generic.py（核心逻辑）
class GenericToolkitBuilder(BaseToolkitBuilder):
    def __init__(self, type_key: str):
        info = TOOLKIT_CATALOG[type_key]
        self.type = type_key
        self.label = info["name"]
        self._module_path = info["module_path"]
        self._class_name = info["class_name"]
        self._agno_cls = None  # 懒加载

    @property
    def schema(self) -> list[dict]:
        try:
            return generate_schema_from_class(self._load_class())
        except Exception:
            return []  # 对应包未安装时优雅降级

    def build(self, config: dict, resolver) -> Any:
        return self._load_class()(**config)
```

```python
# builder_registry.py 中 toolkit 注册
for _type_key in TOOLKIT_CATALOG:
    builder_registry[("toolkit", _type_key)] = GenericToolkitBuilder(_type_key)
builder_registry[("toolkit", "custom")] = CustomToolkitBuilder()
```

### 5.6 Reader Builder + Chunker 子系统

Reader 每种类型有独立 Builder 文件（和 model/embedder 保持一致），chunking 逻辑抽到 `chunk/` 子模块。

#### 设计结构

**`BaseReaderBuilder`**（`readers/base.py`）：
- `schema` = reader 的 `extra_fields` + `_get_chunk_schema_fields()` 动态生成的分块字段
- `_get_chunk_schema_fields()` 调用 `agno_class.get_supported_chunking_strategies()` 获取该 reader 支持的策略，从 `CHUNKER_REGISTRY` 取各策略字段，带 `depends_on` 联动
- `_build_chunker()` 委托给 `CHUNKER_REGISTRY` 对应的 `ChunkerBuilder.build()`

**各 reader 子类**（如 `PdfReaderBuilder`）：
- 声明 `agno_class`（类体顶层 `try/except ImportError`，可选包安全降级）
- 声明 `extra_fields`（reader 专属参数，如 `split_on_pages`、`max_depth` 等）
- 实现 `build(config, resolver)`

**`BaseChunkerBuilder`**（`chunk/base.py`，继承 `BaseBuilder`）：
- `category = "chunker"`，`extra_fields` 手写参数字段（字段名与 agno 构造参数保持一致）
- 8 种策略对应 8 个子类，注册到 `CHUNKER_REGISTRY`

#### Chunker 字段与 agno 参数对齐原则

`extra_fields` 中的 `name` 与 agno 构造参数名保持一致，`build()` 中不做字段名映射：

```python
# chunk/fixed.py
class FixedSizeChunkerBuilder(BaseChunkerBuilder):
    type = "FixedSizeChunker"
    label = "固定大小分块"
    extra_fields = [
        {"name": "chunk_size", "type": "int", "default": 5000, ...},
        {"name": "overlap",    "type": "int", "default": 0, ...},   # 与 agno 参数名一致
    ]

    def build(self, config, resolver):
        from agno.knowledge.chunking.fixed import FixedSizeChunking
        return FixedSizeChunking(
            chunk_size=config.get("chunk_size", 5000),
            overlap=config.get("overlap", 0),   # 直接透传，无需映射
        )
```

#### _get_chunk_schema_fields() 生成的字段结构

| order | 字段 | 说明 |
|-------|------|------|
| 100 | `chunk`（bool） | 启用分块开关 |
| 101 | `chunking_strategy`（select） | 按 reader 支持的策略过滤选项，`depends_on: {chunk: true}` |
| 110+ | 各策略参数字段 | 带 `depends_on: {chunking_strategy: "策略名"}`，按策略分组 |

```python
# builder_registry.py 中 reader 注册（逐一手动）
(\"reader\", \"pdf\"):     PdfReaderBuilder(),
(\"reader\", \"docx\"):    DocxReaderBuilder(),
(\"reader\", \"text\"):    TextReaderBuilder(),
(\"reader\", \"csv\"):     CsvReaderBuilder(),
(\"reader\", \"json\"):    JsonReaderBuilder(),
(\"reader\", \"website\"): WebsiteReaderBuilder(),
(\"reader\", \"youtube\"): YoutubeReaderBuilder(),
(\"reader\", \"arxiv\"):   ArxivReaderBuilder(),
```

---

## 六、RefResolver

```python
# core/ref_resolver.py
from sqlalchemy.orm import Session
from core.builder_registry import builder_registry
from resource.model import AgResourceModel


class RefResolver:
    def __init__(self, db: Session):
        self.db = db
        self._cache: dict[str, object] = {}  # uuid → 已构建对象，避免重复构建

    def resolve(self, value: dict | None):
        """
        value 可能是：
        - None                    → 返回 None
        - {"ref": "uuid"}         → 查表，展开 config，递归 build
        - {"ref": "uuid", "override": {...}} → 查表，merge override，递归 build
        - {"category": ..., "type": ..., ...} → inline，直接 build
        """
        if value is None:
            return None

        if "ref" in value:
            uuid = value["ref"]
            override = value.get("override", {})

            # 有 override 时不能用缓存（不同 override 产生不同对象）
            cache_key = uuid if not override else f"{uuid}:{hash(str(override))}"
            if cache_key in self._cache:
                return self._cache[cache_key]

            row = self.db.query(AgResourceModel).filter_by(uuid=uuid, status="0").first()
            if row is None:
                raise ValueError(f"Resource {uuid} not found or disabled")

            config = {**row.config, **override}
            obj = builder_registry[(row.category, row.type)].build(config, self)
            self._cache[cache_key] = obj
            return obj

        # inline 模式：必须包含 category + type
        value = dict(value)
        category = value.pop("category")
        type_ = value.pop("type")
        return builder_registry[(category, type_)].build(value, self)

    def resolve_list(self, values: list | None) -> list:
        if not values:
            return []
        return [self.resolve(v) for v in values]
```

---

## 七、RuntimeRegistry（极简）

```python
# core/registry.py
class RuntimeRegistry:
    def __init__(self):
        self.agents: list = []
        self.teams: list = []
        self.workflows: list = []
        self._agents_map: dict[str, object] = {}
        self._teams_map:  dict[str, object] = {}

    def add_agent(self, uuid: str, agent):
        self._agents_map[uuid] = agent
        self.agents.append(agent)

    def remove_agent(self, uuid: str):
        agent = self._agents_map.pop(uuid, None)
        if agent:
            self.agents[:] = [a for a in self.agents if a is not agent]

    def replace_agent(self, uuid: str, new_agent):
        self.remove_agent(uuid)
        self.add_agent(uuid, new_agent)

    def add_team(self, uuid: str, team):
        self._teams_map[uuid] = team
        self.teams.append(team)

    def remove_team(self, uuid: str):
        team = self._teams_map.pop(uuid, None)
        if team:
            self.teams[:] = [t for t in self.teams if t is not team]

    def replace_team(self, uuid: str, new_team):
        self.remove_team(uuid)
        self.add_team(uuid, new_team)
```

---

## 八、启动预热

```python
# core/startup.py
async def warm_up(db: Session, registry: RuntimeRegistry):
    resolver = RefResolver(db)

    # 只需预热 agent 和 team（其他资源按需 resolve）
    agents = db.query(AgResourceModel).filter_by(category="agent", status="0").all()
    for row in agents:
        agent = builder_registry[("agent", row.type)].build(row.config, resolver)
        registry.add_agent(row.uuid, agent)

    teams = db.query(AgResourceModel).filter_by(category="team", status="0").all()
    for row in teams:
        team = builder_registry[("team", row.type)].build(row.config, resolver)
        registry.add_team(row.uuid, team)
```

---

## 九、统一 API

### 9.1 资源 CRUD

```
GET    /agno_manage/v2/resources?category=reader    列表（按 category 过滤）
POST   /agno_manage/v2/resources                    创建
GET    /agno_manage/v2/resources/{uuid}             详情（default 值补全）
PATCH  /agno_manage/v2/resources/{uuid}             更新
DELETE /agno_manage/v2/resources/{uuid}             删除
```

### 9.2 Schema API（前端表单驱动）

```
GET /agno_manage/v2/schema?category=reader
→ 返回该 category 支持的所有 type 列表

GET /agno_manage/v2/schema?category=reader&type=pdf
→ 返回 pdf 的完整字段定义
```

### 9.3 Schema 响应格式

```json
{
  "category": "reader",
  "type": "pdf",
  "label": "PDF Reader",
  "fields": [
    {
      "name": "chunk_size",
      "type": "int",
      "label": "分块大小",
      "group": "基础配置",
      "order": 1,
      "span": 12,
      "default": 500,
      "required": false,
      "min": 100,
      "max": 10000,
      "step": 100,
      "omit_if_default": true,
      "tooltip": "每个 chunk 的字符数上限"
    },
    {
      "name": "embedder",
      "type": "ref_or_inline",
      "label": "向量模型",
      "group": "高级配置",
      "order": 10,
      "span": 24,
      "source": "embedder",
      "required": false,
      "hidden": true,
      "overridable_fields": ["dimensions", "model_id"]
    }
  ]
}
```

### 9.4 FieldSchema 完整定义

```python
class FieldSchema(TypedDict, total=False):
    # 基础（必填）
    name: str
    type: str        # int/float/str/bool/password/select/ref_or_inline/ref_or_inline_array

    # 显示
    label: str
    group: str       # 分组面板名称
    order: int       # 显示顺序
    span: int        # 栅格 1-24
    hidden: bool     # 默认折叠到「高级配置」
    placeholder: str
    tooltip: str

    # 值处理
    required: bool
    default: Any
    omit_if_default: bool  # 未填时不提交，后端用 default

    # 数值约束
    min: float
    max: float
    step: float

    # 字符串约束
    min_length: int
    max_length: int
    pattern: str
    error_msg: str

    # select 专用
    options: list

    # ref_or_inline / ref_or_inline_array 专用
    source: str               # category 名，前端去 ?category=xxx 拉列表
    overridable_fields: list  # 选择 ref 时允许 override 的字段名

    # 字段联动
    affects: dict    # {option_value: [显示的字段名]} select 选不同值显示不同字段
    depends_on: dict # {field_name: value} 满足条件才显示此字段
```

---

## 十、前端表单处理

### 10.1 渲染规则

| field.type | Vue 组件 |
|------------|----------|
| `int/float` | `el-input-number` |
| `str` | `el-input` |
| `bool` | `el-switch` |
| `password` | `el-input type=password` |
| `select` | `el-select` |
| `ref_or_inline` | 自定义 `RefOrInlineField` 组件 |
| `ref_or_inline_array` | 多个 `RefOrInlineField` + 增删按钮 |

### 10.2 提交时 config 处理

```javascript
function buildConfig(formData, schema) {
  const config = {}
  for (const field of schema.fields) {
    const value = formData[field.name]
    if (value !== null && value !== undefined && value !== '') {
      config[field.name] = value
    } else if (field.required) {
      throw new Error(`${field.label} 是必填项`)
    }
    // omit_if_default: 不填不提交，后端 build 时用 default 兜底
  }
  return config
}
```

### 10.3 编辑时 config 回填

后端详情接口自动把 default 值补全返回，前端直接初始化表单：

```python
# resource/service.py
async def get(uuid: str, db) -> dict:
    row = await crud.get(uuid, db)
    builder = builder_registry[(row.category, row.type)]

    full_config = {}
    for field in builder.schema:
        name = field["name"]
        if name in row.config:
            full_config[name] = row.config[name]   # 用户填的优先
        elif "default" in field:
            full_config[name] = field["default"]   # 用 default 补全

    return {**row.__dict__, "config": full_config}
```

---

## 十一、CRUD 热更新

```python
# resource/service.py
async def create(body, db, registry):
    row = await crud.create(body, db)
    if body.category in ("agent", "team"):
        resolver = RefResolver(db)
        obj = builder_registry[(body.category, body.type)].build(row.config, resolver)
        getattr(registry, f"add_{body.category}")(row.uuid, obj)
    return row

async def update(uuid, body, db, registry):
    row = await crud.update(uuid, body, db)
    if row.category in ("agent", "team"):
        resolver = RefResolver(db)
        obj = builder_registry[(row.category, row.type)].build(row.config, resolver)
        getattr(registry, f"replace_{row.category}")(uuid, obj)
    return row

async def delete(uuid, db, registry):
    row = await crud.get(uuid, db)
    await crud.delete(uuid, db)
    if row.category in ("agent", "team"):
        getattr(registry, f"remove_{row.category}")(uuid)
```

---

## 十二、暂不设计的部分

- **ag_documents**（文件注册表 + 向量化状态）：延续 v1 设计，暂不迁移
- **权限/审计**（roles/audit_logs/user_roles）：延续 v1 设计，暂不迁移
- **workflow**：结构待定，v2 暂不实现
