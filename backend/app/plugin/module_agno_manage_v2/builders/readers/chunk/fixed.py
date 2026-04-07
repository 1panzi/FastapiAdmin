from typing import Any

from app.plugin.module_agno_manage_v2.builders.readers.chunk.base import BaseChunkerBuilder


class FixedSizeChunkerBuilder(BaseChunkerBuilder):
    type = "FixedSizeChunker"
    label = "固定大小分块"
    extra_fields = [
        {
            "name": "chunk_size", "type": "int", "default": 5000, "required": False,
            "label": "分块大小", "group": "分块参数", "span": 12, "min": 100,
            "tooltip": "每个 chunk 的最大字符数",
        },
        {
            "name": "overlap", "type": "int", "default": 0, "required": False,
            "label": "重叠大小", "group": "分块参数", "span": 12, "min": 0,
            "tooltip": "相邻 chunk 的重叠字符数",
        },
    ]

    async def build(self, config: dict, resolver) -> Any:
        from agno.knowledge.chunking.fixed import FixedSizeChunking
        return FixedSizeChunking(
            chunk_size=config.get("chunk_size", 5000),
            overlap=config.get("overlap", 0),
        )
