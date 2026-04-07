"""
OpenAIEmbedderBuilder — OpenAI Embedding 模型 Builder
"""

from typing import Any

from app.plugin.module_agno_manage_v2.builders.embedders.base import BaseEmbedderBuilder


class OpenAIEmbedderBuilder(BaseEmbedderBuilder):
    type = "openai"
    label = "OpenAI Embedder"
    agno_class = None  # 延迟导入

    extra_fields = [
        *BaseEmbedderBuilder.extra_fields,
    ]
    field_meta = {
        **BaseEmbedderBuilder.field_meta,
        "model_id": {
            "label": "模型ID",
            "group": "基础配置",
            "span": 12,
            "placeholder": "如 text-embedding-3-small / text-embedding-3-large",
        },
    }

    def build(self, config: dict, resolver) -> Any:
        from agno.knowledge.embedder.openai import OpenAIEmbedder

        kwargs: dict = {
            "id": config.get("model_id"),
        }
        if config.get("api_key"):
            kwargs["api_key"] = config["api_key"]
        if config.get("base_url"):
            kwargs["base_url"] = config["base_url"]
        if config.get("dimensions"):
            kwargs["dimensions"] = config["dimensions"]
        return OpenAIEmbedder(**kwargs)
