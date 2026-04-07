"""
CohereModelBuilder — Cohere 模型 Builder
"""

from typing import Any

from app.plugin.module_agno_manage_v2.builders.models.base import BaseModelBuilder


class CohereModelBuilder(BaseModelBuilder):
    type = "cohere"
    label = "Cohere"
    agno_class = None  # 延迟导入

    extra_fields = [
        {"name": "model_id", "type": "str", "required": True, "order": 1},
        {"name": "api_key", "type": "password", "required": False, "order": 2},
        # Cohere 无 base_url，隐藏
        {"name": "base_url", "type": "str", "required": False, "order": 3, "hidden": True},
        {"name": "temperature", "type": "float", "required": False, "default": 0.7, "order": 10},
        {"name": "max_tokens", "type": "int", "required": False, "order": 11},
    ]
    field_meta = {
        **BaseModelBuilder.field_meta,
        "model_id": {
            "label": "模型ID",
            "group": "基础配置",
            "span": 12,
            "placeholder": "如 command-r-plus",
        },
        "base_url": {
            "label": "Base URL",
            "group": "认证",
            "span": 24,
            "hidden": True,
        },
        "temperature": {
            "label": "温度",
            "group": "生成参数",
            "span": 12,
            "min": 0.0,
            "max": 1.0,
            "step": 0.1,
            "omit_if_default": True,
        },
        "max_tokens": {
            "label": "最大Token",
            "group": "生成参数",
            "span": 12,
            "min": 1,
        },
    }

    def build(self, config: dict, resolver) -> Any:
        from agno.models.cohere import CohereChat

        return CohereChat(
            id=config.get("model_id"),
            api_key=config.get("api_key") or None,
            temperature=config.get("temperature"),
            max_tokens=config.get("max_tokens"),
        )
