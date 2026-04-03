"""Agno 支持的知识库 Reader 类型元数据。"""
from typing import TypedDict


class ReaderTypeInfo(TypedDict):
    reader_type: str
    label: str
    agno_class: str
    description: str
    config_example: dict


# 对齐 agno.knowledge.reader.reader_factory.ReaderFactory.READER_METADATA
_READER_TYPES: list[ReaderTypeInfo] = [
    {
        "reader_type": "pdf",
        "label": "PDF 文档",
        "agno_class": "PDFReader",
        "description": "支持 OCR 的 PDF 文档文本提取",
        "config_example": {},
    },
    {
        "reader_type": "csv",
        "label": "CSV 文件",
        "agno_class": "CSVReader",
        "description": "支持自定义分隔符的 CSV 文件解析",
        "config_example": {},
    },
    {
        "reader_type": "excel",
        "label": "Excel 文件",
        "agno_class": "ExcelReader",
        "description": "处理 .xlsx/.xls 工作簿，支持工作表筛选和按行分块",
        "config_example": {},
    },
    {
        "reader_type": "field_labeled_csv",
        "label": "字段标注 CSV",
        "agno_class": "FieldLabeledCSVReader",
        "description": "将 CSV 行转换为字段标注文本，提升可读性和上下文",
        "config_example": {},
    },
    {
        "reader_type": "docx",
        "label": "Word 文档",
        "agno_class": "DocxReader",
        "description": "从 .docx/.doc 文件提取文本内容",
        "config_example": {},
    },
    {
        "reader_type": "pptx",
        "label": "PowerPoint 演示文稿",
        "agno_class": "PPTXReader",
        "description": "从 .pptx 演示文稿提取文本内容",
        "config_example": {},
    },
    {
        "reader_type": "json",
        "label": "JSON / JSONL",
        "agno_class": "JSONReader",
        "description": "处理 JSON 数据结构和 API 响应，支持嵌套对象",
        "config_example": {},
    },
    {
        "reader_type": "markdown",
        "label": "Markdown 文档",
        "agno_class": "MarkdownReader",
        "description": "处理 Markdown 文档，支持标题感知分块和格式保留",
        "config_example": {},
    },
    {
        "reader_type": "text",
        "label": "纯文本文件",
        "agno_class": "TextReader",
        "description": "处理纯文本文件，支持自定义分块策略和编码检测",
        "config_example": {},
    },
    {
        "reader_type": "website",
        "label": "网页",
        "agno_class": "WebsiteReader",
        "description": "抓取网页内容，支持 HTML 解析和文本清洗",
        "config_example": {},
    },
    {
        "reader_type": "firecrawl",
        "label": "Firecrawl 爬虫",
        "agno_class": "FirecrawlReader",
        "description": "高级网页抓取与爬取，支持 JavaScript 渲染和结构化数据提取",
        "config_example": {"api_key": ""},
    },
    {
        "reader_type": "tavily",
        "label": "Tavily 提取",
        "agno_class": "TavilyReader",
        "description": "使用 Tavily Extract API 从 URL 提取内容",
        "config_example": {"api_key": ""},
    },
    {
        "reader_type": "youtube",
        "label": "YouTube 视频",
        "agno_class": "YouTubeReader",
        "description": "从 YouTube 视频和播放列表提取字幕和元数据",
        "config_example": {},
    },
    {
        "reader_type": "arxiv",
        "label": "ArXiv 论文",
        "agno_class": "ArxivReader",
        "description": "从 ArXiv 下载并处理学术论文",
        "config_example": {},
    },
    {
        "reader_type": "wikipedia",
        "label": "Wikipedia 文章",
        "agno_class": "WikipediaReader",
        "description": "获取并处理 Wikipedia 文章，支持章节感知分块",
        "config_example": {},
    },
    {
        "reader_type": "web_search",
        "label": "网络搜索",
        "agno_class": "WebSearchReader",
        "description": "执行网络搜索并处理结果，支持相关性排序和内容提取",
        "config_example": {},
    },
]

# 保留旧名称兼容性
KnowledgeTypeInfo = ReaderTypeInfo


def list_knowledge_types() -> list[ReaderTypeInfo]:
    """返回所有支持的 Reader 类型（供 /agno/reader_types 使用）。"""
    return _READER_TYPES


def list_reader_types() -> list[ReaderTypeInfo]:
    return _READER_TYPES


def get_reader_type_names() -> list[str]:
    return [t["reader_type"] for t in _READER_TYPES]
