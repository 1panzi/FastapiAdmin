"""
KnowledgeBuilder — 知识库 Builder

Knowledge 依赖 embedder/vectordb/readers，build 为 async，
通过 resolver.resolve / resolve_list 异步 resolve 依赖资源。
"""

from typing import Any

from app.plugin.module_agno_manage_v2.core.builder_base import BaseBuilder


class KnowledgeBuilder(BaseBuilder):
    category = "knowledge"
    type = "base"
    label = "知识库"
    agno_class = None

    extra_fields = [
        {"name": "name", "type": "str", "required": True, "order": 1},
        {
            "name": "vectordb",
            "type": "ref_or_inline",
            "required": True,
            "order": 2,
            "source": "vectordb",
        },
        {
            "name": "readers",
            "type": "ref_or_inline_array",
            "required": False,
            "order": 3,
            "source": "reader",
        },
        {"name": "max_results", "type": "int", "required": False, "default": 10, "order": 4},
    ]
    field_meta = {
        "name": {"label": "知识库名称", "group": "基础配置", "span": 12},
        "vectordb": {"label": "向量数据库", "group": "存储配置", "span": 24},
        "readers": {"label": "文档读取器", "group": "读取配置", "span": 24},
        "max_results": {"label": "最大检索结果", "group": "基础配置", "span": 12, "min": 1},
    }

    async def build(self, config: dict, resolver) -> Any:
        from agno.knowledge.base import Knowledge

        vectordb = await resolver.resolve(config.get("vectordb"))
        readers = await resolver.resolve_list(config.get("readers", []))

        return Knowledge(
            name=config.get("name", ""),
            vector_db=vectordb,
            reader=readers[0] if len(readers) == 1 else (readers if readers else None),
            max_results=config.get("max_results", 10),
        )
