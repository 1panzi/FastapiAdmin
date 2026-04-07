"""
DuckDuckGoBuilder — DuckDuckGo 搜索工具 Builder
"""

from typing import Any

from app.plugin.module_agno_manage_v2.builders.toolkits.base import BaseToolkitBuilder


class DuckDuckGoBuilder(BaseToolkitBuilder):
    type = "duckduckgo"
    label = "DuckDuckGo 搜索"

    extra_fields = [
        {"name": "fixed_max_results", "type": "int", "required": False, "default": 5, "order": 1},
        {
            "name": "search_type",
            "type": "select",
            "required": False,
            "options": ["text", "news"],
            "default": "text",
            "order": 2,
        },
    ]
    field_meta = {
        "fixed_max_results": {"label": "最大结果数", "group": "基础配置", "span": 12},
        "search_type": {"label": "搜索类型", "group": "基础配置", "span": 12},
    }

    def build(self, config: dict, resolver) -> Any:
        from agno.tools.duckduckgo import DuckDuckGoTools

        return DuckDuckGoTools(
            fixed_max_results=config.get("fixed_max_results", 5),
        )
