"""
BaseEmbedderBuilder — 所有 Embedder Builder 的基类
"""

from app.plugin.module_agno_manage_v2.core.builder_base import BaseBuilder


class BaseEmbedderBuilder(BaseBuilder):
    category = "embedder"
    agno_class = None  # 延迟导入，由子类设置

    extra_fields = [
        {"name": "model_id", "type": "str", "required": True, "order": 1},
        {"name": "api_key", "type": "password", "required": False, "order": 2},
        {"name": "base_url", "type": "str", "required": False, "order": 3},
        {"name": "dimensions", "type": "int", "required": False, "order": 4},
    ]
    field_meta = {
        "model_id": {
            "label": "模型ID",
            "group": "基础配置",
            "span": 12,
        },
        "api_key": {
            "label": "API Key",
            "group": "认证",
            "span": 24,
        },
        "base_url": {
            "label": "Base URL",
            "group": "认证",
            "span": 24,
        },
        "dimensions": {
            "label": "向量维度",
            "group": "基础配置",
            "span": 12,
            "min": 1,
        },
    }

    def build(self, config: dict, resolver):
        raise NotImplementedError("BaseEmbedderBuilder 不可直接实例化，请使用具体 provider 的 Builder")
