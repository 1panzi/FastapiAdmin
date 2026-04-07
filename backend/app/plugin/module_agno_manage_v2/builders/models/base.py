"""
BaseModelBuilder — 所有 Model Builder 的基类
"""

from app.plugin.module_agno_manage_v2.core.builder_base import BaseBuilder


class BaseModelBuilder(BaseBuilder):
    category = "model"
    agno_class = None  # Model 基类不直接实例化，agno_class 由子类按需设置

    # 所有 model 共有的字段（手动定义，因为 agno Model 基类参数复杂）
    extra_fields = [
        {"name": "model_id", "type": "str", "required": True, "order": 1},
        {"name": "api_key", "type": "password", "required": False, "order": 2},
        {"name": "base_url", "type": "str", "required": False, "order": 3},
    ]
    field_meta = {
        "model_id": {
            "label": "模型ID",
            "group": "基础配置",
            "span": 12,
            "placeholder": "如 gpt-4o / claude-3-5-sonnet-20241022",
        },
        "api_key": {
            "label": "API Key",
            "group": "认证",
            "span": 24,
            "tooltip": "留空则从环境变量读取",
        },
        "base_url": {
            "label": "Base URL",
            "group": "认证",
            "span": 24,
            "placeholder": "留空使用默认地址",
        },
    }

    def build(self, config: dict, resolver):
        raise NotImplementedError("BaseModelBuilder 不可直接实例化，请使用具体 provider 的 Builder")
