from typing import Any

from app.plugin.module_agno_manage_v2.builders.readers.chunk.base import BaseChunkerBuilder


class AgenticChunkerBuilder(BaseChunkerBuilder):
    type = "AgenticChunker"
    label = "智能分块（LLM）"
    extra_fields = [
        {
            "name": "max_chunk_size", "type": "int", "default": 5000, "required": False,
            "label": "最大分块大小", "group": "分块参数", "span": 12, "min": 100,
            "tooltip": "LLM 判断语义断点，成本较高",
        },
        {
            "name": "model", "type": "ref_or_inline", "required": False,
            "label": "语言模型（Model）", "group": "分块参数", "span": 24,
            "source": "model",
            "tooltip": "调用 LLM 判断语义断点，不填则使用默认模型",
        },
    ]

    async def build(self, config: dict, resolver) -> Any:
        from agno.knowledge.chunking.agentic import AgenticChunking
        model = await resolver.resolve(config.get("model")) if config.get("model") else None
        kwargs: dict = {}
        if model is not None:
            kwargs["model"] = model
        if config.get("max_chunk_size"):
            kwargs["max_chunk_size"] = config["max_chunk_size"]
        return AgenticChunking(**kwargs)
