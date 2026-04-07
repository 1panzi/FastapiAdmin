"""
CustomToolkitBuilder — 通过 module_path + class_name 动态加载自定义工具包
"""

import importlib
import json
from typing import Any

from app.plugin.module_agno_manage_v2.builders.toolkits.base import BaseToolkitBuilder


class CustomToolkitBuilder(BaseToolkitBuilder):
    type = "custom"
    label = "自定义工具包"

    extra_fields = [
        {"name": "module_path", "type": "str", "required": True, "order": 1},
        {"name": "class_name", "type": "str", "required": True, "order": 2},
        {
            "name": "init_params",
            "type": "str",
            "required": False,
            "order": 3,
            "placeholder": '{"key": "value"}',
        },
    ]
    field_meta = {
        "module_path": {
            "label": "模块路径",
            "group": "基础配置",
            "span": 12,
            "placeholder": "agno.tools.duckduckgo",
        },
        "class_name": {"label": "类名", "group": "基础配置", "span": 12},
        "init_params": {"label": "初始化参数(JSON)", "group": "基础配置", "span": 24},
    }

    def build(self, config: dict, resolver) -> Any:
        mod = importlib.import_module(config["module_path"])
        cls = getattr(mod, config["class_name"])
        params_str = config.get("init_params", "{}")
        params = json.loads(params_str) if isinstance(params_str, str) else (params_str or {})
        return cls(**params)
