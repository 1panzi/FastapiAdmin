from typing import Any
from app.plugin.module_agno_manage_v2.builders.vectordbs.base import BaseVectordbBuilder


class ChromaBuilder(BaseVectordbBuilder):
    type = "chroma"
    label = "Chroma"

    extra_fields = [
        {
            "name": "collection", "type": "str", "required": True,
            "label": "集合名", "group": "连接配置", "span": 12, "order": 1,
        },
        {
            "name": "path", "type": "str", "required": False, "default": "tmp/chromadb",
            "label": "本地路径", "group": "连接配置", "span": 12, "order": 2,
            "tooltip": "本地持久化路径，使用远程服务时忽略",
        },
        {
            "name": "host", "type": "str", "required": False,
            "label": "服务地址", "group": "连接配置", "span": 12, "order": 3,
            "placeholder": "localhost",
        },
        {
            "name": "port", "type": "int", "required": False, "default": 8000,
            "label": "端口", "group": "连接配置", "span": 12, "order": 4,
        },
    ]

    def build(self, config: dict, resolver) -> Any:
        from agno.vectordb.chroma import ChromaDb
        embedder = resolver.resolve(config.get("embedder"))
        kwargs: dict = {"collection": config["collection"], "embedder": embedder}
        if config.get("host"):
            kwargs["host"] = config["host"]
            kwargs["port"] = config.get("port", 8000)
        else:
            kwargs["path"] = config.get("path", "tmp/chromadb")
        return ChromaDb(**kwargs)
