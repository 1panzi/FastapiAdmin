from typing import Any
from app.plugin.module_agno_manage_v2.builders.vectordbs.base import BaseVectordbBuilder


class PgVectorBuilder(BaseVectordbBuilder):
    type = "pgvector"
    label = "PgVector（PostgreSQL）"

    extra_fields = [
        {
            "name": "table_name", "type": "str", "required": True,
            "label": "表名", "group": "连接配置", "span": 12, "order": 1,
            "placeholder": "kb_documents",
            "tooltip": "向量数据存储的 PostgreSQL 表名，不同知识库建议使用不同表名",
        },
        {
            "name": "schema", "type": "str", "required": False, "default": "ai",
            "label": "Schema", "group": "连接配置", "span": 12, "order": 2,
            "placeholder": "ai",
        },
        {
            "name": "db_url", "type": "password", "required": False,
            "label": "数据库连接串", "group": "连接配置", "span": 24, "order": 3,
            "placeholder": "留空使用系统默认数据库",
            "tooltip": "postgresql+psycopg://user:pass@host/db，留空使用系统 VECTOR_DB_URL 环境变量",
        },
    ]

    def build(self, config: dict, resolver) -> Any:
        from agno.vectordb.pgvector import PgVector
        embedder = resolver.resolve(config.get("embedder"))
        return PgVector(
            table_name=config["table_name"],
            schema=config.get("schema", "ai"),
            db_url=config.get("db_url") or None,
            embedder=embedder,
        )
