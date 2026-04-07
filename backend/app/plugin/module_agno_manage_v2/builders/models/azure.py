"""
AzureModelBuilder — Azure OpenAI 模型 Builder
"""

from typing import Any

from app.plugin.module_agno_manage_v2.builders.models.base import BaseModelBuilder


class AzureModelBuilder(BaseModelBuilder):
    type = "azure"
    label = "Azure OpenAI"
    agno_class = None  # 延迟导入

    extra_fields = [
        {"name": "model_id", "type": "str", "required": True, "order": 1},
        {"name": "api_key", "type": "password", "required": False, "order": 2},
        # Azure 的 base_url 实为 Endpoint，必填
        {"name": "base_url", "type": "str", "required": True, "order": 3},
        {"name": "azure_deployment", "type": "str", "required": False, "order": 4},
        {"name": "api_version", "type": "str", "required": False, "default": "2024-02-01", "order": 5},
        {"name": "temperature", "type": "float", "required": False, "default": 0.7, "order": 10},
        {"name": "max_tokens", "type": "int", "required": False, "order": 11},
    ]
    field_meta = {
        **BaseModelBuilder.field_meta,
        "model_id": {
            "label": "模型ID",
            "group": "基础配置",
            "span": 12,
            "placeholder": "如 gpt-4o",
        },
        "base_url": {
            "label": "Azure Endpoint",
            "group": "认证",
            "span": 24,
            "placeholder": "https://<resource>.openai.azure.com/",
            "required": True,
        },
        "azure_deployment": {
            "label": "部署名称",
            "group": "认证",
            "span": 12,
            "tooltip": "Azure 部署名称，留空则与模型ID相同",
        },
        "api_version": {
            "label": "API版本",
            "group": "认证",
            "span": 12,
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
        from agno.models.azure import AzureOpenAI

        return AzureOpenAI(
            id=config.get("model_id"),
            api_key=config.get("api_key") or None,
            azure_endpoint=config.get("base_url"),
            azure_deployment=config.get("azure_deployment") or None,
            api_version=config.get("api_version") or "2024-02-01",
            temperature=config.get("temperature"),
            max_tokens=config.get("max_tokens"),
        )
