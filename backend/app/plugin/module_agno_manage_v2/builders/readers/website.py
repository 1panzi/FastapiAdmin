"""
WebsiteReaderBuilder — 网站 URL Reader Builder
"""

from typing import Any

from app.plugin.module_agno_manage_v2.builders.readers.base import BaseReaderBuilder


class WebsiteReaderBuilder(BaseReaderBuilder):
    type = "website"
    label = "Website Reader"
    agno_class = None  # 延迟导入

    extra_fields = [
        *BaseReaderBuilder.extra_fields,
        {"name": "max_links", "type": "int", "required": False, "default": 10, "order": 20},
        {"name": "max_depth", "type": "int", "required": False, "default": 1, "order": 21},
    ]
    field_meta = {
        **BaseReaderBuilder.field_meta,
        "max_links": {
            "label": "最大链接数",
            "group": "爬取配置",
            "span": 12,
            "min": 1,
            "max": 1000,
            "tooltip": "最多抓取的链接数量",
        },
        "max_depth": {
            "label": "最大深度",
            "group": "爬取配置",
            "span": 12,
            "min": 1,
            "max": 10,
            "tooltip": "从起始 URL 向下爬取的最大层数",
        },
    }

    def build(self, config: dict, resolver) -> Any:
        from agno.document.reader.website import WebsiteReader

        kwargs = self._get_chunker_kwargs(config)
        if config.get("max_links") is not None:
            kwargs["max_links"] = config["max_links"]
        if config.get("max_depth") is not None:
            kwargs["max_depth"] = config["max_depth"]
        return WebsiteReader(**kwargs)
