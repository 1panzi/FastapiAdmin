"""
DbBuilder 基类 — 公共表名字段。

所有 db builder 共享这些可选的表名配置字段（留空则 agno 使用默认表名）。
"""

from app.plugin.module_agno_manage_v2.core.builder_base import BaseBuilder

_TABLE_FIELDS = [
    {"name": "session_table",    "type": "str", "required": False, "order": 50},
    {"name": "memory_table",     "type": "str", "required": False, "order": 51},
    {"name": "metrics_table",    "type": "str", "required": False, "order": 52},
    {"name": "knowledge_table",  "type": "str", "required": False, "order": 53},
    {"name": "traces_table",     "type": "str", "required": False, "order": 54},
    {"name": "spans_table",      "type": "str", "required": False, "order": 55},
]

_TABLE_FIELD_META = {
    "session_table":   {"label": "会话表名",   "group": "表名配置（高级）", "span": 12, "placeholder": "留空使用默认"},
    "memory_table":    {"label": "记忆表名",   "group": "表名配置（高级）", "span": 12, "placeholder": "留空使用默认"},
    "metrics_table":   {"label": "指标表名",   "group": "表名配置（高级）", "span": 12, "placeholder": "留空使用默认"},
    "knowledge_table": {"label": "知识库表名", "group": "表名配置（高级）", "span": 12, "placeholder": "留空使用默认"},
    "traces_table":    {"label": "追踪表名",   "group": "表名配置（高级）", "span": 12, "placeholder": "留空使用默认"},
    "spans_table":     {"label": "Span表名",   "group": "表名配置（高级）", "span": 12, "placeholder": "留空使用默认"},
}


def _table_kwargs(config: dict) -> dict:
    """从 config 提取非空的表名参数，供 build() 使用。"""
    table_keys = [f["name"] for f in _TABLE_FIELDS]
    return {k: config[k] for k in table_keys if config.get(k)}


class DbBuilder(BaseBuilder):
    """db builder 基类，提供公共表名字段。子类不直接实例化。"""

    category = "db"
    type = ""
    label = ""
    agno_class = None

    extra_fields = list(_TABLE_FIELDS)
    field_meta = dict(_TABLE_FIELD_META)
