"""
BaseReaderBuilder — 所有 Reader Builder 的基类

分块策略处理：
- build() 是同步方法，对于 SemanticChunker/AgenticChunker 这类需要 resolver 的情况，
  直接用默认初始化（不传 embedder/model 参数），后续可按需优化。
"""

from app.plugin.module_agno_manage_v2.core.builder_base import BaseBuilder


def _build_chunker(strategy: str):
    """根据策略名称构建 Agno Chunker 实例（同步）。"""
    if strategy == "FixedSizeChunker":
        from agno.document.chunking.fixed import FixedSizeChunker
        return FixedSizeChunker()
    elif strategy == "RecursiveChunker":
        from agno.document.chunking.recursive import RecursiveChunker
        return RecursiveChunker()
    elif strategy == "DocumentChunker":
        from agno.document.chunking.document import DocumentChunker
        return DocumentChunker()
    elif strategy == "MarkdownChunker":
        from agno.document.chunking.markdown import MarkdownChunker
        return MarkdownChunker()
    elif strategy == "RowChunker":
        from agno.document.chunking.row import RowChunker
        return RowChunker()
    elif strategy == "SemanticChunker":
        # SemanticChunker 理想情况下需要 embedder，但 build 是同步的
        # 用默认初始化，后续可通过配置优化
        from agno.document.chunking.semantic import SemanticChunker
        return SemanticChunker()
    elif strategy == "AgenticChunker":
        from agno.document.chunking.agentic import AgenticChunker
        return AgenticChunker()
    elif strategy == "CodeChunker":
        from agno.document.chunking.code import CodeChunker
        return CodeChunker()
    return None


class BaseReaderBuilder(BaseBuilder):
    category = "reader"
    agno_class = None  # 延迟导入，由子类设置

    extra_fields = [
        {"name": "chunk", "type": "bool", "required": False, "default": True, "order": 1},
        {"name": "chunk_size", "type": "int", "required": False, "default": 5000, "order": 2},
        {
            "name": "chunking_strategy",
            "type": "select",
            "required": False,
            "order": 3,
            "options": [
                "FixedSizeChunker",
                "RecursiveChunker",
                "DocumentChunker",
                "MarkdownChunker",
                "RowChunker",
                "SemanticChunker",
                "AgenticChunker",
                "CodeChunker",
            ],
            "default": "FixedSizeChunker",
        },
        {"name": "chunk_overlap", "type": "int", "required": False, "default": 0, "order": 4},
        {"name": "encoding", "type": "str", "required": False, "default": "utf-8", "order": 5},
    ]
    field_meta = {
        "chunk": {
            "label": "启用分块",
            "group": "分块配置",
            "span": 12,
        },
        "chunk_size": {
            "label": "分块大小",
            "group": "分块配置",
            "span": 12,
            "min": 100,
        },
        "chunking_strategy": {
            "label": "分块策略",
            "group": "分块配置",
            "span": 12,
        },
        "chunk_overlap": {
            "label": "分块重叠",
            "group": "分块配置",
            "span": 12,
        },
        "encoding": {
            "label": "文本编码",
            "group": "基础配置",
            "span": 12,
            "hidden": True,
        },
    }

    def _get_chunker_kwargs(self, config: dict) -> dict:
        """提取公共 chunking 参数，返回可传给 Reader 的 kwargs。"""
        kwargs: dict = {}
        chunk = config.get("chunk", True)
        kwargs["chunk"] = chunk

        if chunk:
            chunk_size = config.get("chunk_size", 5000)
            chunk_overlap = config.get("chunk_overlap", 0)
            kwargs["chunk_size"] = chunk_size
            kwargs["chunk_overlap"] = chunk_overlap

            strategy = config.get("chunking_strategy", "FixedSizeChunker")
            chunker = _build_chunker(strategy)
            if chunker is not None:
                kwargs["chunker"] = chunker

        return kwargs

    def build(self, config: dict, resolver):
        raise NotImplementedError("BaseReaderBuilder 不可直接实例化，请使用具体类型的 Builder")
