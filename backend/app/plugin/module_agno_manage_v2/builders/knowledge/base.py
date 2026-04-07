"""
KnowledgeBuilder — 知识库 Builder。

Knowledge 依赖：
- vectordb（ref 或 inline）：向量数据库，内部已包含 embedder
- max_results：最大检索结果数
- search_type：检索方式

Reader 由 agno Knowledge 内部根据文档类型自动选择，无需在此配置。
build() 为 async，通过 resolver.resolve() 解析 vectordb 依赖。
"""

from typing import Any

from app.plugin.module_agno_manage_v2.core.builder_base import BaseBuilder


class KnowledgeBuilder(BaseBuilder):
    category = "knowledge"
    type = "base"
    label = "知识库"
    agno_class = None

    extra_fields = [
        {
            "name": "vectordb",
            "type": "ref_or_inline",
            "required": True,
            "label": "向量数据库",
            "group": "存储配置",
            "span": 24,
            "order": 1,
            "source": "vectordb",
            "tooltip": "选择已创建的向量数据库资源",
        },
        {
            "name": "max_results",
            "type": "int",
            "required": False,
            "default": 10,
            "label": "最大检索结果数",
            "group": "检索配置",
            "span": 12,
            "order": 2,
            "min": 1,
            "max": 100,
        },
        {
            "name": "search_type",
            "type": "select",
            "required": False,
            "default": "vector",
            "label": "检索方式",
            "group": "检索配置",
            "span": 12,
            "order": 3,
            "options": [
                {"value": "vector", "label": "向量检索"},
                {"value": "keyword", "label": "关键词检索"},
                {"value": "hybrid", "label": "混合检索"},
            ],
        },
    ]

    async def build(self, config: dict, resolver) -> Any:
        from agno.knowledge.base import Knowledge

        vectordb = await resolver.resolve(config.get("vectordb"))

        kwargs: dict = {
            "vector_db": vectordb,
            "max_results": config.get("max_results", 10),
        }
        if config.get("search_type"):
            kwargs["search_type"] = config["search_type"]

        return Knowledge(**kwargs)
