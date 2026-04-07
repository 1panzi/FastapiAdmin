from typing import Any
from app.plugin.module_agno_manage_v2.builders.readers.chunk.base import BaseChunkerBuilder


class DocumentChunkerBuilder(BaseChunkerBuilder):
    type = "DocumentChunker"
    label = "文档分块"
    extra_fields = [
        {
            "name": "chunk_size", "type": "int", "default": 5000, "required": False,
            "label": "分块大小", "group": "分块参数", "span": 12, "min": 100,
            "tooltip": "按文档结构（段落/章节）分块，适合 PDF/Word",
        },
        {
            "name": "overlap", "type": "int", "default": 0, "required": False,
            "label": "重叠大小", "group": "分块参数", "span": 12, "min": 0,
        },
    ]

    def build(self, config: dict, resolver) -> Any:
        from agno.knowledge.chunking.document import DocumentChunking
        return DocumentChunking(
            chunk_size=config.get("chunk_size", 5000),
            overlap=config.get("overlap", 0),
        )
