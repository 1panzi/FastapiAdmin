"""
BaseChunkerBuilder — 所有 Chunker Builder 的基类。

每个子类对应一种 ChunkingStrategyType，声明：
- category = "chunker"（固定）
- type: ChunkingStrategyType 的 value 字符串（如 "FixedSizeChunker"）
- label: 前端显示名称
- agno_class: 对应 agno chunking 类，供 BaseBuilder.schema 自动反射字段
- extra_fields: 手写字段（覆盖或追加反射字段）
- build(config, resolver): 构建并返回 ChunkingStrategy 实例
"""

from app.plugin.module_agno_manage_v2.core.builder_base import BaseBuilder


class BaseChunkerBuilder(BaseBuilder):
    category = "chunker"
    type: str = ""
    label: str = ""

    # agno_class 指向对应的 agno chunking 类，BaseBuilder.schema 会自动反射字段
    agno_class = None

    # extra_fields 用于手写字段（当 agno_class 反射不足时覆盖或追加）
    extra_fields: list[dict] = []
    field_meta: dict[str, dict] = {}

    def build(self, config: dict, resolver):
        raise NotImplementedError


# Chunker 注册表（在各子类导入后填充）
CHUNKER_REGISTRY: dict[str, "BaseChunkerBuilder"] = {}
