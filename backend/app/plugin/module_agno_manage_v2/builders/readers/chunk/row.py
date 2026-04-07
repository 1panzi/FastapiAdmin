from typing import Any
from app.plugin.module_agno_manage_v2.builders.readers.chunk.base import BaseChunkerBuilder


class RowChunkerBuilder(BaseChunkerBuilder):
    type = "RowChunker"
    label = "行分块"
    extra_fields = [
        {
            "name": "skip_header", "type": "bool", "default": False, "required": False,
            "label": "跳过表头", "group": "分块参数", "span": 12,
            "tooltip": "CSV/Excel 专用，跳过第一行表头",
        },
        {
            "name": "clean_rows", "type": "bool", "default": True, "required": False,
            "label": "清理空行", "group": "分块参数", "span": 12,
        },
    ]

    def build(self, config: dict, resolver) -> Any:
        from agno.knowledge.chunking.row import RowChunking
        return RowChunking(
            skip_header=config.get("skip_header", False),
            clean_rows=config.get("clean_rows", True),
        )
