from app.plugin.module_agno_manage_v2.builders.readers.chunk.base import BaseChunkerBuilder, CHUNKER_REGISTRY
from app.plugin.module_agno_manage_v2.builders.readers.chunk.fixed import FixedSizeChunkerBuilder
from app.plugin.module_agno_manage_v2.builders.readers.chunk.recursive import RecursiveChunkerBuilder
from app.plugin.module_agno_manage_v2.builders.readers.chunk.document import DocumentChunkerBuilder
from app.plugin.module_agno_manage_v2.builders.readers.chunk.markdown import MarkdownChunkerBuilder
from app.plugin.module_agno_manage_v2.builders.readers.chunk.row import RowChunkerBuilder
from app.plugin.module_agno_manage_v2.builders.readers.chunk.code import CodeChunkerBuilder
from app.plugin.module_agno_manage_v2.builders.readers.chunk.semantic import SemanticChunkerBuilder
from app.plugin.module_agno_manage_v2.builders.readers.chunk.agentic import AgenticChunkerBuilder

# 填充注册表
CHUNKER_REGISTRY.update({
    "FixedSizeChunker": FixedSizeChunkerBuilder(),
    "RecursiveChunker": RecursiveChunkerBuilder(),
    "DocumentChunker":  DocumentChunkerBuilder(),
    "MarkdownChunker":  MarkdownChunkerBuilder(),
    "RowChunker":       RowChunkerBuilder(),
    "CodeChunker":      CodeChunkerBuilder(),
    "SemanticChunker":  SemanticChunkerBuilder(),
    "AgenticChunker":   AgenticChunkerBuilder(),
})

__all__ = ["BaseChunkerBuilder", "CHUNKER_REGISTRY"]
