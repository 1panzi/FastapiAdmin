from typing import Any
from app.plugin.module_agno_manage_v2.builders.readers.base import BaseReaderBuilder


class ArxivReaderBuilder(BaseReaderBuilder):
    type = "arxiv"
    label = "ArXiv 论文"

    try:
        from agno.knowledge.reader.arxiv_reader import ArxivReader
        agno_class = ArxivReader
    except ImportError:
        agno_class = None

    extra_fields = [
        {
            "name": "sort_by",
            "type": "select",
            "default": "Relevance",
            "required": False,
            "label": "排序方式",
            "group": "ArXiv 配置",
            "span": 12,
            "order": 1,
            "options": [
                {"value": "Relevance",       "label": "相关性"},
                {"value": "LastUpdatedDate", "label": "最近更新"},
                {"value": "SubmittedDate",   "label": "提交日期"},
            ],
        },
    ]

    def build(self, config: dict, resolver) -> Any:
        from agno.knowledge.reader.arxiv_reader import ArxivReader
        chunker = self._build_chunker(config, resolver)
        kwargs: dict = {
            "chunk": config.get("chunk", True),
            "chunk_size": config.get("chunk_size", 5000),
        }
        if chunker is not None:
            kwargs["chunking_strategy"] = chunker
        if config.get("sort_by"):
            import arxiv
            sort_map = {
                "Relevance":       arxiv.SortCriterion.Relevance,
                "LastUpdatedDate": arxiv.SortCriterion.LastUpdatedDate,
                "SubmittedDate":   arxiv.SortCriterion.SubmittedDate,
            }
            sort_val = sort_map.get(config["sort_by"])
            if sort_val is not None:
                kwargs["sort_by"] = sort_val
        return ArxivReader(**kwargs)
