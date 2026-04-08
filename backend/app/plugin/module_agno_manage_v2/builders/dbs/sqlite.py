"""
SqliteDbBuilder — SQLite 存储后端。

支持通过 db_url（优先）或 db_file 指定数据库路径。
"""

from typing import Any

from app.plugin.module_agno_manage_v2.builders.dbs.base import DbBuilder, _table_kwargs


class SqliteDbBuilder(DbBuilder):
    category = "db"
    type = "sqlite"
    label = "SQLite"

    extra_fields = [
        {
            "name": "db_url",
            "type": "str",
            "required": False,
            "order": 1,
            "placeholder": "sqlite:///path/to/agno.db",
        },
        {
            "name": "db_file",
            "type": "str",
            "required": False,
            "order": 2,
            "placeholder": "/path/to/agno.db（db_url 优先）",
        },
        *DbBuilder.extra_fields,
    ]

    field_meta = {
        "db_url":  {"label": "数据库 URL", "group": "连接配置", "span": 24,
                    "tooltip": "形如 sqlite:///./agno.db，优先于 db_file"},
        "db_file": {"label": "数据库文件路径", "group": "连接配置", "span": 24,
                    "tooltip": "当 db_url 为空时使用，如 ./agno.db"},
        **DbBuilder.field_meta,
    }

    async def build(self, config: dict, resolver) -> Any:
        from agno.db.sqlite.sqlite import SqliteDb

        kwargs = _table_kwargs(config)
        if config.get("db_url"):
            kwargs["db_url"] = config["db_url"]
        elif config.get("db_file"):
            kwargs["db_file"] = config["db_file"]

        return SqliteDb(**kwargs)
