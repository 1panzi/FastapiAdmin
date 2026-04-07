"""
CsvReaderBuilder — CSV 文件 Reader Builder
"""

from typing import Any

from app.plugin.module_agno_manage_v2.builders.readers.base import BaseReaderBuilder


class CsvReaderBuilder(BaseReaderBuilder):
    type = "csv"
    label = "CSV Reader"
    agno_class = None  # 延迟导入

    extra_fields = [
        *BaseReaderBuilder.extra_fields,
        {"name": "delimiter", "type": "str", "required": False, "default": ",", "order": 20},
    ]
    field_meta = {
        **BaseReaderBuilder.field_meta,
        "delimiter": {
            "label": "分隔符",
            "group": "基础配置",
            "span": 12,
            "placeholder": "默认逗号 ,",
        },
    }

    def build(self, config: dict, resolver) -> Any:
        from agno.document.reader.csv_reader import CSVReader

        kwargs = self._get_chunker_kwargs(config)
        if config.get("delimiter"):
            kwargs["delimiter"] = config["delimiter"]
        return CSVReader(**kwargs)
