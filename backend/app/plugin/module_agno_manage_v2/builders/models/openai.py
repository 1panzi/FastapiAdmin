"""
OpenAIModelBuilder — OpenAI 模型 Builder
"""

from typing import Any

from app.plugin.module_agno_manage_v2.builders.models.base import BaseModelBuilder


class OpenAIModelBuilder(BaseModelBuilder):
    type = "openai"
    label = "OpenAI"
    agno_class = None  # 延迟导入，避免启动时必须安装依赖

    extra_fields = [
        *BaseModelBuilder.extra_fields,
        {"name": "temperature", "type": "float", "required": False, "default": 0.7, "order": 10},
        {"name": "max_tokens", "type": "int", "required": False, "order": 11},
    ]
    field_meta = {
        **BaseModelBuilder.field_meta,
        "temperature": {
            "label": "温度",
            "group": "生成参数",
            "span": 12,
            "min": 0.0,
            "max": 2.0,
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
        from agno.models.openai import OpenAIChat

        return OpenAIChat(
            id=config.get("model_id"),
            api_key=config.get("api_key") or None,
            base_url=config.get("base_url") or None,
            temperature=config.get("temperature"),
            max_tokens=config.get("max_tokens"),
        )
