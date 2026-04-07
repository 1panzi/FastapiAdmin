from typing import Any
from app.plugin.module_agno_manage_v2.builders.readers.base import BaseReaderBuilder


class WebsiteReaderBuilder(BaseReaderBuilder):
    type = "website"
    label = "网页"

    try:
        from agno.knowledge.reader.website_reader import WebsiteReader
        agno_class = WebsiteReader
    except ImportError:
        agno_class = None

    extra_fields = [
        {
            "name": "max_depth", "type": "int", "default": 3, "required": False,
            "label": "最大爬取深度", "group": "爬取配置", "span": 8, "order": 1,
            "min": 1, "max": 10, "tooltip": "从起始 URL 递归爬取的最大层数",
        },
        {
            "name": "max_links", "type": "int", "default": 10, "required": False,
            "label": "最大链接数", "group": "爬取配置", "span": 8, "order": 2,
            "min": 1, "max": 1000,
        },
        {
            "name": "timeout", "type": "int", "default": 10, "required": False,
            "label": "超时（秒）", "group": "爬取配置", "span": 8, "order": 3,
            "min": 1, "max": 300,
        },
        {
            "name": "proxy", "type": "str", "default": None, "required": False,
            "label": "代理", "group": "爬取配置", "span": 12, "order": 4,
            "placeholder": "http://proxy:port",
            "tooltip": "HTTP 代理地址",
        },
    ]

    def build(self, config: dict, resolver) -> Any:
        from agno.knowledge.reader.website_reader import WebsiteReader
        chunker = self._build_chunker(config, resolver)
        kwargs: dict = {
            "chunk": config.get("chunk", True),
            "chunk_size": config.get("chunk_size", 5000),
        }
        if chunker is not None:
            kwargs["chunking_strategy"] = chunker
        for k in ("max_depth", "max_links", "timeout", "proxy"):
            if config.get(k) is not None:
                kwargs[k] = config[k]
        return WebsiteReader(**kwargs)
