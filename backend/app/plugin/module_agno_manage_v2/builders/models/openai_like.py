"""
OpenAILikeModelBuilder — OpenAI 兼容接口模型 Builder（自定义 base_url 的 OpenAI 协议模型）
"""

from typing import Any

from app.plugin.module_agno_manage_v2.builders.models.base import BaseModelBuilder


class OpenAILikeModelBuilder(BaseModelBuilder):
    type = "openai_like"
    label = "OpenAI 兼容接口"
    agno_class = None  # 延迟导入

    extra_fields = [
        {"name": "model_id", "type": "str", "required": True, "order": 1},
        {"name": "api_key", "type": "password", "required": False, "order": 2},
        # base_url 必填，因为这类模型的地址不固定
        {"name": "base_url", "type": "str", "required": True, "order": 3},
        {"name": "temperature", "type": "float", "required": False, "default": 0.7, "order": 10},
        {"name": "max_tokens", "type": "int", "required": False, "order": 11},
    ]
    field_meta = {
        **BaseModelBuilder.field_meta,
        "model_id": {
            "label": "模型ID",
            "group": "基础配置",
            "span": 12,
            "placeholder": "如 qwen-plus / moonshot-v1-8k",
        },
        "base_url": {
            "label": "API Base URL",
            "group": "认证",
            "span": 24,
            "placeholder": "如 https://api.qwen.ai/v1",
            "required": True,
        },
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
        from agno.models.openai.like import OpenAILike

        return OpenAILike(
            id=config.get("model_id"),
            api_key=config.get("api_key") or None,
            base_url=config.get("base_url"),
            temperature=config.get("temperature"),
            max_tokens=config.get("max_tokens"),
        )
