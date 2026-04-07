"""
OllamaModelBuilder — Ollama 本地模型 Builder
"""

from typing import Any

from app.plugin.module_agno_manage_v2.builders.models.base import BaseModelBuilder


class OllamaModelBuilder(BaseModelBuilder):
    type = "ollama"
    label = "Ollama"
    agno_class = None  # 延迟导入

    extra_fields = [
        {"name": "model_id", "type": "str", "required": True, "order": 1},
        # Ollama 不需要 api_key，隐藏
        {"name": "api_key", "type": "password", "required": False, "order": 2, "hidden": True},
        {"name": "base_url", "type": "str", "required": False, "order": 3},
    ]
    field_meta = {
        **BaseModelBuilder.field_meta,
        "model_id": {
            "label": "模型ID",
            "group": "基础配置",
            "span": 12,
            "placeholder": "如 llama3.2 / qwen2.5",
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
        from agno.models.ollama import Ollama

        return Ollama(
            id=config.get("model_id"),
            host=config.get("base_url") or None,
        )
