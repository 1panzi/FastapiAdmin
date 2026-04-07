"""
BaseReaderBuilder — Reader Builder 基类。

核心设计：
- 每个子类声明 agno_class（对应 agno reader 类）和 extra_fields（reader 专属字段）
- schema 属性 = extra_fields 的字段 + _get_chunk_schema_fields()
- _get_chunk_schema_fields() 调用 agno reader 类的 get_supported_chunking_strategies()
  动态获取支持的策略，再从 CHUNKER_REGISTRY 取各策略字段（带 depends_on 联动）
- _build_chunker() 委托给 CHUNKER_REGISTRY 对应的 ChunkerBuilder
"""

from app.plugin.module_agno_manage_v2.core.builder_base import BaseBuilder
from app.plugin.module_agno_manage_v2.builders.readers.chunk import CHUNKER_REGISTRY


class BaseReaderBuilder(BaseBuilder):
    category = "reader"
    agno_class = None  # 各子类声明对应的 agno reader 类

    extra_fields: list[dict] = []
    field_meta: dict[str, dict] = {}

    def _get_supported_strategies(self) -> list[str]:
        """调用 agno reader 类的 get_supported_chunking_strategies() 获取策略列表。"""
        try:
            cls = type(self).agno_class
            if cls is None:
                return list(CHUNKER_REGISTRY.keys())
            return [s.value for s in cls.get_supported_chunking_strategies()]
        except Exception:
            return list(CHUNKER_REGISTRY.keys())

    def _get_chunk_schema_fields(self) -> list[dict]:
        """
        生成分块相关字段：
        1. chunk（开关）
        2. chunking_strategy（select，按该 reader 支持的策略过滤）
        3. 每种策略的参数字段（带 depends_on: {chunking_strategy: strategy_type}）
        """
        supported = self._get_supported_strategies()
        fields: list[dict] = []

        # 1. chunk 开关
        fields.append({
            "name": "chunk", "type": "bool", "required": False, "default": True,
            "label": "启用分块", "group": "分块配置", "span": 8, "order": 100,
        })

        # 2. chunking_strategy select
        strategy_options = [
            {"value": s, "label": CHUNKER_REGISTRY[s].label}
            for s in supported if s in CHUNKER_REGISTRY
        ]
        default_strategy = supported[0] if supported else "FixedSizeChunker"
        fields.append({
            "name": "chunking_strategy",
            "type": "select",
            "required": False,
            "default": default_strategy,
            "label": "分块策略",
            "group": "分块配置",
            "span": 16,
            "order": 101,
            "options": strategy_options,
            "depends_on": {"chunk": True},
        })

        # 3. 各策略的参数字段（带 depends_on）
        for strategy_type in supported:
            builder = CHUNKER_REGISTRY.get(strategy_type)
            if not builder:
                continue
            for i, f in enumerate(builder.schema):
                fields.append({
                    **f,
                    "depends_on": {"chunking_strategy": strategy_type},
                    "order": 110 + list(supported).index(strategy_type) * 10 + i,
                })

        return fields

    @property
    def schema(self) -> list[dict]:
        """Reader 专属字段 + 分块配置字段。"""
        fields: list[dict] = []

        # reader 专属字段（extra_fields + field_meta）
        fm = type(self).field_meta or {}
        for i, f in enumerate(type(self).extra_fields):
            merged = {**f, **fm.get(f["name"], {})}
            merged.setdefault("order", i)
            fields.append(merged)

        # 分块配置字段
        fields += self._get_chunk_schema_fields()

        return sorted(fields, key=lambda x: x.get("order", 99))

    def _build_chunker(self, config: dict, resolver):
        """从 config 中取 chunking_strategy，委托给对应的 ChunkerBuilder 构建。"""
        strategy = config.get("chunking_strategy")
        if not strategy or not config.get("chunk", True):
            return None
        builder = CHUNKER_REGISTRY.get(strategy)
        if builder:
            return builder.build(config, resolver)
        return None

    def build(self, config: dict, resolver):
        raise NotImplementedError
