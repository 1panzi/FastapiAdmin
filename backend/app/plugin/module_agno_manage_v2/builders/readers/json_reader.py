"""
JsonReaderBuilder — JSON 文件 Reader Builder

文件名用 json_reader.py 避免与内置 json 模块冲突。
"""

from typing import Any

from app.plugin.module_agno_manage_v2.builders.readers.base import BaseReaderBuilder


class JsonReaderBuilder(BaseReaderBuilder):
    type = "json"
    label = "JSON Reader"
    agno_class = None  # 延迟导入

    field_meta = {
        **BaseReaderBuilder.field_meta,
    }

    def build(self, config: dict, resolver) -> Any:
        from agno.document.reader.json import JSONReader

        kwargs = self._get_chunker_kwargs(config)
        return JSONReader(**kwargs)
