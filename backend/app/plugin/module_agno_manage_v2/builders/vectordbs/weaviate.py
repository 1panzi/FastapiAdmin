from typing import Any

from app.plugin.module_agno_manage_v2.builders.vectordbs.base import BaseVectordbBuilder


class WeaviateBuilder(BaseVectordbBuilder):
    type = "weaviate"
    label = "Weaviate"

    extra_fields = [
        {
            "name": "collection", "type": "str", "required": True,
            "label": "集合名", "group": "连接配置", "span": 12, "order": 1,
        },
        {
            "name": "url", "type": "str", "required": False,
            "label": "服务地址", "group": "连接配置", "span": 12, "order": 2,
            "placeholder": "http://localhost:8080",
        },
        {
            "name": "api_key", "type": "password", "required": False,
            "label": "API Key", "group": "连接配置", "span": 24, "order": 3,
            "tooltip": "Weaviate Cloud 需要填写",
        },
    ]

    def build(self, config: dict, resolver) -> Any:
        from agno.vectordb.weaviate import Weaviate
        embedder = resolver.resolve(config.get("embedder"))
        kwargs: dict = {"collection": config["collection"], "embedder": embedder}
        if config.get("url"):
            kwargs["url"] = config["url"]
        if config.get("api_key"):
            kwargs["api_key"] = config["api_key"]
        return Weaviate(**kwargs)
