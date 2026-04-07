from typing import Any

from app.plugin.module_agno_manage_v2.builders.vectordbs.base import BaseVectordbBuilder


class PineconeBuilder(BaseVectordbBuilder):
    type = "pinecone"
    label = "Pinecone"

    extra_fields = [
        {
            "name": "index_name", "type": "str", "required": True,
            "label": "索引名", "group": "连接配置", "span": 12, "order": 1,
        },
        {
            "name": "api_key", "type": "password", "required": True,
            "label": "API Key", "group": "连接配置", "span": 12, "order": 2,
        },
        {
            "name": "namespace", "type": "str", "required": False,
            "label": "命名空间", "group": "连接配置", "span": 12, "order": 3,
        },
    ]

    def build(self, config: dict, resolver) -> Any:
        from agno.vectordb.pineconedb import PineconeDb
        embedder = resolver.resolve(config.get("embedder"))
        kwargs: dict = {
            "index_name": config["index_name"],
            "api_key": config["api_key"],
            "embedder": embedder,
        }
        if config.get("namespace"):
            kwargs["namespace"] = config["namespace"]
        return PineconeDb(**kwargs)
