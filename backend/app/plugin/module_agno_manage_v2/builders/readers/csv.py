from typing import Any
from app.plugin.module_agno_manage_v2.builders.readers.base import BaseReaderBuilder


class CsvReaderBuilder(BaseReaderBuilder):
    type = "csv"
    label = "CSV 文件"

    try:
        from agno.knowledge.reader.csv_reader import CSVReader
        agno_class = CSVReader
    except ImportError:
        agno_class = None

    extra_fields = [
        {
            "name": "encoding", "type": "str", "default": "utf-8", "required": False,
            "label": "文本编码", "group": "基础配置", "span": 12, "order": 1,
            "placeholder": "utf-8 / gbk / auto",
            "tooltip": "文本编码，留空自动检测",
        },
    ]

    async def build(self, config: dict, resolver) -> Any:
        from agno.knowledge.reader.csv_reader import CSVReader
        chunker = await self._build_chunker(config, resolver)
        kwargs: dict = {
            "chunk": config.get("chunk", True),
            "chunk_size": config.get("chunk_size", 5000),
        }
        if chunker is not None:
            kwargs["chunking_strategy"] = chunker
        if config.get("encoding"):
            kwargs["encoding"] = config["encoding"]
        return CSVReader(**kwargs)
