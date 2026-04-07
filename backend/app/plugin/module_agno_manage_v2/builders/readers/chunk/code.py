from typing import Any
from app.plugin.module_agno_manage_v2.builders.readers.chunk.base import BaseChunkerBuilder


class CodeChunkerBuilder(BaseChunkerBuilder):
    type = "CodeChunker"
    label = "代码分块"
    extra_fields = [
        {
            "name": "chunk_size", "type": "int", "default": 5000, "required": False,
            "label": "分块大小", "group": "分块参数", "span": 12, "min": 100,
            "tooltip": "按代码语义单元（函数/类）分块，不支持重叠",
        },
    ]

    async def build(self, config: dict, resolver) -> Any:
        from agno.knowledge.chunking.code import CodeChunking
        return CodeChunking(chunk_size=config.get("chunk_size", 5000))
