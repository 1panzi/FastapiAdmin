"""
PythonToolsBuilder — Python 执行工具 Builder
"""

from typing import Any

from app.plugin.module_agno_manage_v2.builders.toolkits.base import BaseToolkitBuilder


class PythonToolsBuilder(BaseToolkitBuilder):
    type = "python"
    label = "Python 执行"

    extra_fields = [
        {"name": "base_dir", "type": "str", "required": False, "order": 1},
        {"name": "safe_globals", "type": "bool", "required": False, "default": True, "order": 2},
    ]
    field_meta = {
        "base_dir": {"label": "工作目录", "group": "基础配置", "span": 24},
        "safe_globals": {"label": "安全模式", "group": "基础配置", "span": 12},
    }

    def build(self, config: dict, resolver) -> Any:
        from agno.tools.python import PythonTools

        return PythonTools(
            base_dir=config.get("base_dir"),
            safe_globals=config.get("safe_globals", True),
        )
