from typing import Any

from app.plugin.module_agno_manage_v2.builders.vectordbs.base import BaseVectordbBuilder


class MilvusBuilder(BaseVectordbBuilder):
    type = "milvus"
    label = "Milvus"

    extra_fields = [
        {
            "name": "collection", "type": "str", "required": True,
            "label": "集合名", "group": "连接配置", "span": 12, "order": 1,
        },
        {
            "name": "uri", "type": "str", "required": False,
            "label": "连接地址", "group": "连接配置", "span": 12, "order": 2,
            "placeholder": "http://localhost:19530",
        },
        {
            "name": "token", "type": "password", "required": False,
            "label": "Token", "group": "连接配置", "span": 24, "order": 3,
        },
    ]

    def build(self, config: dict, resolver) -> Any:
        from agno.vectordb.milvus import Milvus
        embedder = resolver.resolve(config.get("embedder"))
        kwargs: dict = {"collection": config["collection"], "embedder": embedder}
        if config.get("uri"):
            kwargs["uri"] = config["uri"]
        if config.get("token"):
            kwargs["token"] = config["token"]
        return Milvus(**kwargs)
