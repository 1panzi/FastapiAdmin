"""
AzureEmbedderBuilder — Azure OpenAI Embedding 模型 Builder
"""

from typing import Any

from app.plugin.module_agno_manage_v2.builders.embedders.base import BaseEmbedderBuilder


class AzureEmbedderBuilder(BaseEmbedderBuilder):
    type = "azure"
    label = "Azure OpenAI Embedder"
    agno_class = None  # 延迟导入

    extra_fields = [
        {"name": "model_id", "type": "str", "required": True, "order": 1},
        {"name": "api_key", "type": "password", "required": False, "order": 2},
        # Azure Endpoint 必填
        {"name": "base_url", "type": "str", "required": True, "order": 3},
        {"name": "dimensions", "type": "int", "required": False, "order": 4},
        {"name": "azure_deployment", "type": "str", "required": False, "order": 5},
        {"name": "api_version", "type": "str", "required": False, "default": "2024-02-01", "order": 6},
    ]
    field_meta = {
        **BaseEmbedderBuilder.field_meta,
        "model_id": {
            "label": "模型ID",
            "group": "基础配置",
            "span": 12,
            "placeholder": "如 text-embedding-3-small",
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
    }

    def build(self, config: dict, resolver) -> Any:
        from agno.knowledge.embedder.azure_openai import AzureOpenAIEmbedder

        kwargs: dict = {
            "id": config.get("model_id") or config.get("model"),
            "azure_endpoint": config.get("azure_endpoint") or config.get("base_url"),
        }
        if config.get("api_key"):
            kwargs["api_key"] = config["api_key"]
        if config.get("azure_deployment"):
            kwargs["azure_deployment"] = config["azure_deployment"]
        if config.get("api_version"):
            kwargs["api_version"] = config["api_version"]
        if config.get("dimensions"):
            kwargs["dimensions"] = config["dimensions"]
        return AzureOpenAIEmbedder(**kwargs)
