"""
TextReaderBuilder — 纯文本文件 Reader Builder
"""

from typing import Any

from app.plugin.module_agno_manage_v2.builders.readers.base import BaseReaderBuilder


class TextReaderBuilder(BaseReaderBuilder):
    type = "text"
    label = "Text Reader"
    agno_class = None  # 延迟导入

    field_meta = {
        **BaseReaderBuilder.field_meta,
        "encoding": {
            "label": "文本编码",
            "group": "基础配置",
            "span": 12,
            "hidden": False,  # 文本文件编码比较重要，展示出来
        },
    }

    def build(self, config: dict, resolver) -> Any:
        from agno.document.reader.text import TextReader

        kwargs = self._get_chunker_kwargs(config)
        if config.get("encoding"):
            kwargs["encoding"] = config["encoding"]
        return TextReader(**kwargs)
