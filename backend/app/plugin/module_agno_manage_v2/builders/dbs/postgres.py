"""
PostgresDbBuilder — PostgreSQL 存储后端。

db_url 为必填项（如 postgresql+psycopg://user:pass@host/db）。
"""

from typing import Any

from app.plugin.module_agno_manage_v2.builders.dbs.base import DbBuilder, _table_kwargs


class PostgresDbBuilder(DbBuilder):
    category = "db"
    type = "postgres"
    label = "PostgreSQL"

    extra_fields = [
        {
            "name": "db_url",
            "type": "str",
            "required": True,
            "order": 1,
            "placeholder": "postgresql+psycopg://user:pass@host:5432/dbname",
        },
        {
            "name": "db_schema",
            "type": "str",
            "required": False,
            "order": 2,
            "placeholder": "agno（留空使用默认 schema）",
        },
        {
            "name": "create_schema",
            "type": "bool",
            "required": False,
            "default": True,
            "order": 3,
        },
        *DbBuilder.extra_fields,
    ]

    field_meta = {
        "db_url":        {"label": "数据库 URL", "group": "连接配置", "span": 24},
        "db_schema":     {"label": "Schema 名", "group": "连接配置", "span": 12,
                          "tooltip": "PostgreSQL schema，留空使用 agno 默认"},
        "create_schema": {"label": "自动创建 Schema", "group": "连接配置", "span": 12},
        **DbBuilder.field_meta,
    }

    async def build(self, config: dict, resolver) -> Any:
        from agno.db.postgres.postgres import PostgresDb

        kwargs = _table_kwargs(config)
        if config.get("db_url"):
            kwargs["db_url"] = config["db_url"]
        if config.get("db_schema"):
            kwargs["db_schema"] = config["db_schema"]
        kwargs["create_schema"] = config.get("create_schema", True)

        return PostgresDb(**kwargs)
