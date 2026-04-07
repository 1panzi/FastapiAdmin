"""
OllamaEmbedderBuilder — Ollama 本地 Embedding 模型 Builder
"""

from typing import Any

from app.plugin.module_agno_manage_v2.builders.embedders.base import BaseEmbedderBuilder


class OllamaEmbedderBuilder(BaseEmbedderBuilder):
    type = "ollama"
    label = "Ollama Embedder"
    agno_class = None  # 延迟导入

    extra_fields = [
        {"name": "model_id", "type": "str", "required": True, "order": 1},
        # Ollama 不需要 api_key，隐藏
        {"name": "api_key", "type": "password", "required": False, "order": 2, "hidden": True},
        {"name": "base_url", "type": "str", "required": False, "order": 3},
        {"name": "dimensions", "type": "int", "required": False, "order": 4},
    ]
    field_meta = {
        **BaseEmbedderBuilder.field_meta,
        "model_id": {
            "label": "模型ID",
            "group": "基础配置",
            "span": 12,
            "placeholder": "如 nomic-embed-text / mxbai-embed-large",
        },
        "api_key": {
            "label": "API Key",
            "group": "认证",
            "span": 24,
            "hidden": True,
        },
        "base_url": {
            "label": "Host",
            "group": "认证",
            "span": 24,
            "placeholder": "http://localhost:11434",
        },
    }

    def build(self, config: dict, resolver) -> Any:
        from agno.embedder.ollama import OllamaEmbedder

        kwargs: dict = {
            "id": config.get("model_id"),
        }
        if config.get("base_url"):
            kwargs["host"] = config["base_url"]
        if config.get("dimensions"):
            kwargs["dimensions"] = config["dimensions"]
        return OllamaEmbedder(**kwargs)
