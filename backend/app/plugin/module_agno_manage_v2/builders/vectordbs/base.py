"""
BaseVectordbBuilder — 所有 VectorDB Builder 的基类。

每个子类对应一种向量数据库，声明：
- type: 类型字符串（如 "pgvector"）
- label: 前端显示名称
- agno_class: 对应 agno vectordb 类，供 BaseBuilder.schema 自动反射字段
- extra_fields: 手写字段（覆盖或追加）
- build(config, resolver): 构建并返回 VectorDB 实例

注意：所有 vectordb 子类的 config 中必须包含 embedder（ref 或 inline），
embedder 由 build() 通过 resolver.resolve() 解析。
"""

from app.plugin.module_agno_manage_v2.core.builder_base import BaseBuilder


class BaseVectordbBuilder(BaseBuilder):
    category = "vectordb"
    agno_class = None
    extra_fields: list[dict] = []
    field_meta: dict[str, dict] = {}

    # 所有 vectordb 共有的 embedder 字段
    _embedder_field: dict = {
        "name": "embedder",
        "type": "ref_or_inline",
        "required": True,
        "label": "向量模型（Embedder）",
        "group": "基础配置",
        "span": 24,
        "order": 0,
        "source": "embedder",
        "tooltip": "用于将文档向量化的 Embedding 模型",
    }

    @property
    def schema(self) -> list[dict]:
        # embedder 字段排在最前面，后接子类 extra_fields
        fields: dict[str, dict] = {"embedder": self._embedder_field.copy()}
        fm = type(self).field_meta or {}
        for i, f in enumerate(type(self).extra_fields):
            merged = {**f, **fm.get(f["name"], {})}
            merged.setdefault("order", i + 1)
            fields[f["name"]] = merged
        return sorted(fields.values(), key=lambda x: x.get("order", 99))

    def build(self, config: dict, resolver):
        raise NotImplementedError
