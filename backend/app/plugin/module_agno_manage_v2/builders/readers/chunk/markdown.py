from typing import Any
from app.plugin.module_agno_manage_v2.builders.readers.chunk.base import BaseChunkerBuilder


class MarkdownChunkerBuilder(BaseChunkerBuilder):
    type = "MarkdownChunker"
    label = "Markdown 分块"
    extra_fields = [
        {
            "name": "chunk_size", "type": "int", "default": 5000, "required": False,
            "label": "分块大小", "group": "分块参数", "span": 12, "min": 100,
            "tooltip": "按 Markdown 标题层级分块，适合 .md 文档",
        },
        {
            "name": "overlap", "type": "int", "default": 0, "required": False,
            "label": "重叠大小", "group": "分块参数", "span": 12, "min": 0,
        },
    ]

    def build(self, config: dict, resolver) -> Any:
        from agno.knowledge.chunking.markdown import MarkdownChunking
        return MarkdownChunking(
            chunk_size=config.get("chunk_size", 5000),
            overlap=config.get("overlap", 0),
        )
