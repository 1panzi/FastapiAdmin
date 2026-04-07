"""
Agno Reader & Chunking 策略元数据目录。

提供：
- READER_CATALOG：每种 reader_type 的标签、默认 chunking 策略、支持的 chunking 策略列表、
  reader 专属参数 schema（供前端动态渲染表单）
- CHUNKING_STRATEGY_CATALOG：每种 chunking 策略的参数 schema
- list_reader_types() / get_reader_info() / list_chunking_strategies()：对外接口
"""

from typing import Any, TypedDict

# ── 类型定义 ────────────────────────────────────────────────────────────────


class ParamSchema(TypedDict):
    name: str           # 参数名（对应 reader_config 的 key）
    type: str           # 类型：str / int / float / bool / list / dict / enum
    default: Any        # 默认值（None 表示无默认/必填）
    required: bool      # 是否必填
    label: str          # 前端展示名
    description: str    # 说明
    options: list       # type=enum 时的可选值列表


class ReaderInfo(TypedDict):
    reader_type: str
    label: str
    description: str
    default_chunking_strategy: str          # 与 Agno 默认保持一致
    supported_chunking_strategies: list[str]
    reader_config_schema: list[ParamSchema]  # reader 专属参数
    needs_encoding: bool                     # 是否展示 encoding 字段（文本类）


class ChunkingStrategyInfo(TypedDict):
    strategy: str   # 对应 ChunkingStrategyType 的 value，如 "FixedSizeChunker"
    label: str
    description: str
    param_schema: list[ParamSchema]  # 该策略自身的参数（chunk_size/overlap 等）


# ── Chunking 策略目录 ────────────────────────────────────────────────────────

# 注：chunk_size / chunk_overlap 是通用字段，直接存在 ag_readers 表列上；
#     此处 param_schema 只描述策略自身的"额外"参数。
_CHUNKING_STRATEGIES: list[ChunkingStrategyInfo] = [
    {
        "strategy": "FixedSizeChunker",
        "label": "固定大小分块",
        "description": "按字符数固定分块，支持重叠。适合均匀文本。",
        "param_schema": [],  # chunk_size + chunk_overlap 已在表列，无额外参数
    },
    {
        "strategy": "RecursiveChunker",
        "label": "递归分块",
        "description": "按自然断点递归分割，支持重叠。比固定分块更智能。",
        "param_schema": [],  # chunk_size + chunk_overlap 已在表列，无额外参数
    },
    {
        "strategy": "DocumentChunker",
        "label": "文档分块",
        "description": "按文档结构（段落/章节）分块，支持重叠。适合 PDF/Word。",
        "param_schema": [],
    },
    {
        "strategy": "MarkdownChunker",
        "label": "Markdown 分块",
        "description": "按 Markdown 标题层级分块，支持重叠。适合 .md 文档。",
        "param_schema": [],
    },
    {
        "strategy": "RowChunker",
        "label": "行分块",
        "description": "每行/每条记录作为独立 chunk。专为 CSV/Excel 设计，无 chunk_size 概念。",
        "param_schema": [],
    },
    {
        "strategy": "CodeChunker",
        "label": "代码分块",
        "description": "按代码语义单元（函数/类）分块。适合源代码文件。",
        "param_schema": [],  # chunk_size 有效，无 overlap
    },
    {
        "strategy": "SemanticChunker",
        "label": "语义分块",
        "description": "基于语义相似度动态分块，需要 Embedder。效果最好但成本最高。",
        "param_schema": [
            # chunk_size 有效；embedder_id 在表列上；以下为策略自身额外参数
            {
                "name": "similarity_threshold",
                "type": "float",
                "default": 0.5,
                "required": False,
                "label": "相似度阈值",
                "description": "低于此值时触发分块，越小分块越细",
                "options": [],
            },
            {
                "name": "similarity_window",
                "type": "int",
                "default": 3,
                "required": False,
                "label": "相似度窗口",
                "description": "计算相似度时前后参考的句子数",
                "options": [],
            },
            {
                "name": "min_sentences_per_chunk",
                "type": "int",
                "default": 1,
                "required": False,
                "label": "最少句子数/块",
                "description": "每个 chunk 至少包含的句子数",
                "options": [],
            },
        ],
    },
    {
        "strategy": "AgenticChunker",
        "label": "智能分块（LLM）",
        "description": "调用 LLM 判断语义断点，需要 Model。质量最高，但速度慢、费用高。",
        "param_schema": [
            # model_id 在表列上；max_chunk_size 用 chunk_size 字段存储
        ],
    },
]

_CHUNKING_STRATEGY_MAP: dict[str, ChunkingStrategyInfo] = {
    s["strategy"]: s for s in _CHUNKING_STRATEGIES
}


# ── Reader 目录 ──────────────────────────────────────────────────────────────

_FILE_STRATEGIES = [
    "FixedSizeChunker", "RecursiveChunker", "DocumentChunker",
    "SemanticChunker", "AgenticChunker", "CodeChunker",
]

_READER_CATALOG: list[ReaderInfo] = [
    # ── 文件类 ────────────────────────────────────────────────────────────────
    {
        "reader_type": "pdf",
        "label": "PDF 文档",
        "description": "支持 OCR 的 PDF 文档文本提取",
        "default_chunking_strategy": "DocumentChunker",
        "supported_chunking_strategies": _FILE_STRATEGIES,
        "needs_encoding": False,
        "reader_config_schema": [
            {
                "name": "split_on_pages",
                "type": "bool",
                "default": True,
                "required": False,
                "label": "按页分割",
                "description": "每页作为独立文档单元",
                "options": [],
            },
            {
                "name": "sanitize_content",
                "type": "bool",
                "default": True,
                "required": False,
                "label": "内容清洗",
                "description": "去除多余空白和特殊字符",
                "options": [],
            },
            {
                "name": "password",
                "type": "str",
                "default": None,
                "required": False,
                "label": "PDF 密码",
                "description": "加密 PDF 的解密密码",
                "options": [],
            },
        ],
    },
    {
        "reader_type": "docx",
        "label": "Word 文档",
        "description": "从 .docx/.doc 文件提取文本内容",
        "default_chunking_strategy": "DocumentChunker",
        "supported_chunking_strategies": [
            "DocumentChunker", "FixedSizeChunker", "RecursiveChunker",
            "SemanticChunker", "AgenticChunker", "CodeChunker",
        ],
        "needs_encoding": False,
        "reader_config_schema": [],
    },
    {
        "reader_type": "pptx",
        "label": "PowerPoint 演示文稿",
        "description": "从 .pptx 提取文本内容",
        "default_chunking_strategy": "DocumentChunker",
        "supported_chunking_strategies": [
            "DocumentChunker", "FixedSizeChunker", "RecursiveChunker",
            "SemanticChunker", "AgenticChunker", "CodeChunker",
        ],
        "needs_encoding": False,
        "reader_config_schema": [],
    },
    {
        "reader_type": "csv",
        "label": "CSV 文件",
        "description": "支持自定义分隔符的 CSV 文件解析",
        "default_chunking_strategy": "RowChunker",
        "supported_chunking_strategies": [
            "RowChunker", "FixedSizeChunker", "RecursiveChunker",
            "DocumentChunker", "AgenticChunker", "CodeChunker",
        ],
        "needs_encoding": True,
        "reader_config_schema": [],
    },
    {
        "reader_type": "field_labeled_csv",
        "label": "字段标注 CSV",
        "description": "将 CSV 行转换为字段标注文本，提升可读性",
        "default_chunking_strategy": "RowChunker",
        "supported_chunking_strategies": [],  # 不支持分块，每行即一个 chunk
        "needs_encoding": True,
        "reader_config_schema": [
            {
                "name": "chunk_title",
                "type": "str",
                "default": None,
                "required": False,
                "label": "块标题字段",
                "description": "用哪个字段的值作为文档标题，可为字段名列表",
                "options": [],
            },
            {
                "name": "field_names",
                "type": "list",
                "default": [],
                "required": False,
                "label": "字段白名单",
                "description": "只处理这些字段，为空则处理全部",
                "options": [],
            },
            {
                "name": "format_headers",
                "type": "bool",
                "default": True,
                "required": False,
                "label": "格式化表头",
                "description": "将表头转换为可读格式（下划线→空格，首字母大写）",
                "options": [],
            },
            {
                "name": "skip_empty_fields",
                "type": "bool",
                "default": True,
                "required": False,
                "label": "跳过空字段",
                "description": "忽略值为空的字段",
                "options": [],
            },
        ],
    },
    {
        "reader_type": "excel",
        "label": "Excel 文件",
        "description": "处理 .xlsx/.xls 工作簿，支持工作表筛选",
        "default_chunking_strategy": "RowChunker",
        "supported_chunking_strategies": [
            "RowChunker", "FixedSizeChunker", "RecursiveChunker",
            "DocumentChunker", "AgenticChunker", "CodeChunker",
        ],
        "needs_encoding": False,
        "reader_config_schema": [
            {
                "name": "sheets",
                "type": "list",
                "default": None,
                "required": False,
                "label": "工作表筛选",
                "description": "指定要读取的工作表名或索引列表，为空则读取全部",
                "options": [],
            },
        ],
    },
    {
        "reader_type": "json",
        "label": "JSON / JSONL",
        "description": "处理 JSON 数据结构和 API 响应",
        "default_chunking_strategy": "FixedSizeChunker",
        "supported_chunking_strategies": [
            "FixedSizeChunker", "RecursiveChunker", "DocumentChunker",
            "SemanticChunker", "AgenticChunker", "CodeChunker",
        ],
        "needs_encoding": True,
        "reader_config_schema": [],
    },
    {
        "reader_type": "markdown",
        "label": "Markdown 文档",
        "description": "按标题层级感知分块，保留格式",
        "default_chunking_strategy": "MarkdownChunker",
        "supported_chunking_strategies": [
            "MarkdownChunker", "FixedSizeChunker", "RecursiveChunker",
            "DocumentChunker", "SemanticChunker", "AgenticChunker",
        ],
        "needs_encoding": True,
        "reader_config_schema": [],
    },
    {
        "reader_type": "text",
        "label": "纯文本文件",
        "description": "处理 .txt 等纯文本文件，支持编码检测",
        "default_chunking_strategy": "FixedSizeChunker",
        "supported_chunking_strategies": [
            "FixedSizeChunker", "RecursiveChunker", "DocumentChunker",
            "SemanticChunker", "AgenticChunker", "CodeChunker",
        ],
        "needs_encoding": True,
        "reader_config_schema": [],
    },
    # ── 网络类 ────────────────────────────────────────────────────────────────
    {
        "reader_type": "website",
        "label": "网页",
        "description": "抓取网页内容，支持递归爬取",
        "default_chunking_strategy": "FixedSizeChunker",
        "supported_chunking_strategies": [
            "FixedSizeChunker", "RecursiveChunker", "DocumentChunker",
            "SemanticChunker", "AgenticChunker",
        ],
        "needs_encoding": False,
        "reader_config_schema": [
            {
                "name": "max_depth",
                "type": "int",
                "default": 3,
                "required": False,
                "label": "最大爬取深度",
                "description": "从起始 URL 递归爬取的最大层数",
                "options": [],
            },
            {
                "name": "max_links",
                "type": "int",
                "default": 10,
                "required": False,
                "label": "最大链接数",
                "description": "每次爬取最多处理的链接数量",
                "options": [],
            },
            {
                "name": "timeout",
                "type": "int",
                "default": 10,
                "required": False,
                "label": "超时时间（秒）",
                "description": "单个页面请求超时时间",
                "options": [],
            },
            {
                "name": "proxy",
                "type": "str",
                "default": None,
                "required": False,
                "label": "代理地址",
                "description": "HTTP 代理，如 http://127.0.0.1:7890",
                "options": [],
            },
        ],
    },
    {
        "reader_type": "firecrawl",
        "label": "Firecrawl 爬虫",
        "description": "高级网页抓取，支持 JavaScript 渲染（需 API Key）",
        "default_chunking_strategy": "SemanticChunker",
        "supported_chunking_strategies": [
            "SemanticChunker", "FixedSizeChunker", "RecursiveChunker",
            "DocumentChunker", "AgenticChunker",
        ],
        "needs_encoding": False,
        "reader_config_schema": [
            {
                "name": "api_key",
                "type": "str",
                "default": None,
                "required": True,
                "label": "API Key",
                "description": "Firecrawl API Key，也可通过环境变量 FIRECRAWL_API_KEY 设置",
                "options": [],
            },
            {
                "name": "mode",
                "type": "enum",
                "default": "scrape",
                "required": False,
                "label": "模式",
                "description": "scrape: 单页抓取；crawl: 递归爬取整站",
                "options": ["scrape", "crawl"],
            },
            {
                "name": "params",
                "type": "dict",
                "default": None,
                "required": False,
                "label": "附加参数",
                "description": "透传给 Firecrawl API 的额外参数",
                "options": [],
            },
        ],
    },
    {
        "reader_type": "tavily",
        "label": "Tavily 内容提取",
        "description": "使用 Tavily Extract API 从 URL 提取内容（需 API Key）",
        "default_chunking_strategy": "SemanticChunker",
        "supported_chunking_strategies": [
            "SemanticChunker", "FixedSizeChunker", "RecursiveChunker",
            "DocumentChunker", "AgenticChunker",
        ],
        "needs_encoding": False,
        "reader_config_schema": [
            {
                "name": "api_key",
                "type": "str",
                "default": None,
                "required": True,
                "label": "API Key",
                "description": "Tavily API Key，也可通过环境变量 TAVILY_API_KEY 设置",
                "options": [],
            },
            {
                "name": "extract_format",
                "type": "enum",
                "default": "markdown",
                "required": False,
                "label": "输出格式",
                "description": "markdown 或 text",
                "options": ["markdown", "text"],
            },
            {
                "name": "extract_depth",
                "type": "enum",
                "default": "basic",
                "required": False,
                "label": "提取深度",
                "description": "basic: 1 credit/5 URLs；advanced: 2 credits/5 URLs",
                "options": ["basic", "advanced"],
            },
            {
                "name": "params",
                "type": "dict",
                "default": None,
                "required": False,
                "label": "附加参数",
                "description": "透传给 Tavily Extract API 的额外参数",
                "options": [],
            },
        ],
    },
    {
        "reader_type": "web_search",
        "label": "网络搜索",
        "description": "执行网络搜索并将结果作为文档处理（DuckDuckGo）",
        "default_chunking_strategy": "FixedSizeChunker",
        "supported_chunking_strategies": [
            "FixedSizeChunker", "RecursiveChunker", "DocumentChunker",
            "SemanticChunker", "AgenticChunker",
        ],
        "needs_encoding": False,
        "reader_config_schema": [],
    },
    # ── 知识源类 ──────────────────────────────────────────────────────────────
    {
        "reader_type": "youtube",
        "label": "YouTube 视频",
        "description": "从 YouTube 视频和播放列表提取字幕和元数据",
        "default_chunking_strategy": "RecursiveChunker",
        "supported_chunking_strategies": [
            "RecursiveChunker", "FixedSizeChunker", "DocumentChunker",
            "SemanticChunker", "AgenticChunker", "CodeChunker",
        ],
        "needs_encoding": False,
        "reader_config_schema": [],
    },
    {
        "reader_type": "arxiv",
        "label": "ArXiv 论文",
        "description": "从 ArXiv 下载并处理学术论文",
        "default_chunking_strategy": "FixedSizeChunker",
        "supported_chunking_strategies": [
            "FixedSizeChunker", "RecursiveChunker", "DocumentChunker",
            "SemanticChunker", "AgenticChunker",
        ],
        "needs_encoding": False,
        "reader_config_schema": [
            {
                "name": "sort_by",
                "type": "enum",
                "default": "Relevance",
                "required": False,
                "label": "排序方式",
                "description": "论文搜索结果排序方式",
                "options": ["Relevance", "LastUpdatedDate", "SubmittedDate"],
            },
        ],
    },
    {
        "reader_type": "wikipedia",
        "label": "Wikipedia 文章",
        "description": "获取并处理 Wikipedia 文章，支持章节感知分块",
        "default_chunking_strategy": "FixedSizeChunker",
        "supported_chunking_strategies": [
            "FixedSizeChunker", "RecursiveChunker", "DocumentChunker",
            "SemanticChunker", "AgenticChunker", "CodeChunker",
        ],
        "needs_encoding": False,
        "reader_config_schema": [
            {
                "name": "auto_suggest",
                "type": "bool",
                "default": True,
                "required": False,
                "label": "自动建议",
                "description": "查询词不精确时自动匹配最近似的词条",
                "options": [],
            },
        ],
    },
]

_READER_MAP: dict[str, ReaderInfo] = {r["reader_type"]: r for r in _READER_CATALOG}


# ── 对外接口 ─────────────────────────────────────────────────────────────────


def list_reader_types() -> list[ReaderInfo]:
    """返回所有支持的 Reader 类型列表。"""
    return _READER_CATALOG


def get_reader_info(reader_type: str) -> ReaderInfo | None:
    """按 reader_type 获取单个 Reader 元数据，不存在返回 None。"""
    return _READER_MAP.get(reader_type)


def list_chunking_strategies() -> list[ChunkingStrategyInfo]:
    """返回所有支持的 Chunking 策略列表。"""
    return _CHUNKING_STRATEGIES


def get_chunking_strategy_info(strategy: str) -> ChunkingStrategyInfo | None:
    """按策略名获取 Chunking 策略元数据，不存在返回 None。"""
    return _CHUNKING_STRATEGY_MAP.get(strategy)


def get_supported_strategies_for_reader(reader_type: str) -> list[str]:
    """
    返回指定 reader_type 支持的 chunking 策略名列表。

    优先从 Agno ReaderFactory 动态获取（永远与 Agno 版本同步），
    失败时回退到 catalog 静态数据。
    """
    try:
        from agno.knowledge.reader.reader_factory import ReaderFactory
        reader_cls = ReaderFactory.get_reader_class(reader_type)
        strategies = reader_cls.get_supported_chunking_strategies()
        return [s.value for s in strategies]
    except Exception:
        info = _READER_MAP.get(reader_type)
        return info["supported_chunking_strategies"] if info else []
