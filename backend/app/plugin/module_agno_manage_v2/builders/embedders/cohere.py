"""
CohereEmbedderBuilder — Cohere Embedding 模型 Builder
"""

from typing import Any

from app.plugin.module_agno_manage_v2.builders.embedders.base import BaseEmbedderBuilder


class CohereEmbedderBuilder(BaseEmbedderBuilder):
    type = "cohere"
    label = "Cohere Embedder"
    agno_class = None  # 延迟导入

    extra_fields = [
        {"name": "model_id", "type": "str", "required": True, "order": 1},
        {"name": "api_key", "type": "password", "required": False, "order": 2},
        # Cohere 无 base_url，隐藏
        {"name": "base_url", "type": "str", "required": False, "order": 3, "hidden": True},
        {"name": "dimensions", "type": "int", "required": False, "order": 4},
    ]
    field_meta = {
        **BaseEmbedderBuilder.field_meta,
        "model_id": {
            "label": "模型ID",
            "group": "基础配置",
            "span": 12,
            "placeholder": "如 embed-multilingual-v3.0",
        },
        "base_url": {
            "label": "Base URL",
            "group": "认证",
            "span": 24,
            "hidden": True,
        },
    }

    def build(self, config: dict, resolver) -> Any:
        from agno.embedder.cohere import CohereEmbedder

        kwargs: dict = {
            "id": config.get("model_id"),
        }
        if config.get("api_key"):
            kwargs["api_key"] = config["api_key"]
        if config.get("dimensions"):
            kwargs["dimensions"] = config["dimensions"]
        return CohereEmbedder(**kwargs)
