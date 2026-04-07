from typing import Any
from app.plugin.module_agno_manage_v2.builders.vectordbs.base import BaseVectordbBuilder


class MongodbBuilder(BaseVectordbBuilder):
    type = "mongodb"
    label = "MongoDB Atlas"

    extra_fields = [
        {
            "name": "collection", "type": "str", "required": True,
            "label": "集合名", "group": "连接配置", "span": 12, "order": 1,
        },
        {
            "name": "connection_string", "type": "password", "required": True,
            "label": "连接串", "group": "连接配置", "span": 24, "order": 2,
            "placeholder": "mongodb+srv://user:pass@cluster.mongodb.net",
        },
        {
            "name": "database", "type": "str", "required": False,
            "label": "数据库名", "group": "连接配置", "span": 12, "order": 3,
        },
    ]

    def build(self, config: dict, resolver) -> Any:
        from agno.vectordb.mongodb import MongoDb
        embedder = resolver.resolve(config.get("embedder"))
        kwargs: dict = {
            "collection": config["collection"],
            "connection_string": config["connection_string"],
            "embedder": embedder,
        }
        if config.get("database"):
            kwargs["database"] = config["database"]
        return MongoDb(**kwargs)
