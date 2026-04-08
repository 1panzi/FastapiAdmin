"""
InMemoryDbBuilder — 纯内存存储后端。

无需任何配置，适用于测试和无需持久化的场景。
"""

from typing import Any

from app.plugin.module_agno_manage_v2.core.builder_base import BaseBuilder


class InMemoryDbBuilder(BaseBuilder):
    category = "db"
    type = "in_memory"
    label = "内存（InMemory）"
    agno_class = None

    extra_fields = []
    field_meta = {}

    async def build(self, config: dict, resolver) -> Any:
        from agno.db.in_memory import InMemoryDb

        return InMemoryDb()
