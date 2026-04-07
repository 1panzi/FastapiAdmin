from typing import Any

from app.plugin.module_agno_manage_v2.builders.vectordbs.base import BaseVectordbBuilder


class LanceDbBuilder(BaseVectordbBuilder):
    type = "lancedb"
    label = "LanceDB"

    extra_fields = [
        {
            "name": "table_name", "type": "str", "required": True,
            "label": "表名", "group": "连接配置", "span": 12, "order": 1,
        },
        {
            "name": "uri", "type": "str", "required": False, "default": "tmp/lancedb",
            "label": "存储路径", "group": "连接配置", "span": 12, "order": 2,
            "tooltip": "本地路径或 S3/GCS URI",
        },
    ]

    def build(self, config: dict, resolver) -> Any:
        from agno.vectordb.lancedb import LanceDb
        embedder = resolver.resolve(config.get("embedder"))
        return LanceDb(
            table_name=config["table_name"],
            uri=config.get("uri", "tmp/lancedb"),
            embedder=embedder,
        )
