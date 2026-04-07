"""
ArxivReaderBuilder — arXiv 论文 Reader Builder
"""

from typing import Any

from app.plugin.module_agno_manage_v2.builders.readers.base import BaseReaderBuilder


class ArxivReaderBuilder(BaseReaderBuilder):
    type = "arxiv"
    label = "Arxiv Reader"
    agno_class = None  # 延迟导入

    extra_fields = [
        *BaseReaderBuilder.extra_fields,
        {"name": "max_results", "type": "int", "required": False, "default": 5, "order": 20},
    ]
    field_meta = {
        **BaseReaderBuilder.field_meta,
        "max_results": {
            "label": "最大结果数",
            "group": "基础配置",
            "span": 12,
            "min": 1,
            "max": 100,
            "tooltip": "单次查询最多返回的论文数量",
        },
    }

    def build(self, config: dict, resolver) -> Any:
        from agno.document.reader.arxiv import ArxivReader

        kwargs = self._get_chunker_kwargs(config)
        if config.get("max_results") is not None:
            kwargs["max_results"] = config["max_results"]
        return ArxivReader(**kwargs)
