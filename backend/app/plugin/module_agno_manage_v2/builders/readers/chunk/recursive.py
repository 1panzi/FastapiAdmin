from typing import Any
from app.plugin.module_agno_manage_v2.builders.readers.chunk.base import BaseChunkerBuilder


class RecursiveChunkerBuilder(BaseChunkerBuilder):
    type = "RecursiveChunker"
    label = "递归分块"
    extra_fields = [
        {
            "name": "chunk_size", "type": "int", "default": 5000, "required": False,
            "label": "分块大小", "group": "分块参数", "span": 12, "min": 100,
        },
        {
            "name": "overlap", "type": "int", "default": 0, "required": False,
            "label": "重叠大小", "group": "分块参数", "span": 12, "min": 0,
        },
    ]

    async def build(self, config: dict, resolver) -> Any:
        from agno.knowledge.chunking.recursive import RecursiveChunking
        return RecursiveChunking(
            chunk_size=config.get("chunk_size", 5000),
            overlap=config.get("overlap", 0),
        )
