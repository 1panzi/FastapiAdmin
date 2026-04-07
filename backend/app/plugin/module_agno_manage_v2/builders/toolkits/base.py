"""
BaseToolkitBuilder — 所有 Toolkit Builder 的基类
"""

from app.plugin.module_agno_manage_v2.core.builder_base import BaseBuilder


class BaseToolkitBuilder(BaseBuilder):
    category = "toolkit"
    agno_class = None
    extra_fields: list[dict] = []
    field_meta: dict[str, dict] = {}

    def build(self, config: dict, resolver):
        raise NotImplementedError("BaseToolkitBuilder 不可直接实例化，请使用具体类型的 Builder")
