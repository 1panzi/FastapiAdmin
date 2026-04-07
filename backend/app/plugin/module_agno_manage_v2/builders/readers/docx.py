"""
DocxReaderBuilder — Word DOCX 文件 Reader Builder
"""

from typing import Any

from app.plugin.module_agno_manage_v2.builders.readers.base import BaseReaderBuilder


class DocxReaderBuilder(BaseReaderBuilder):
    type = "docx"
    label = "DOCX Reader"
    agno_class = None  # 延迟导入

    field_meta = {
        **BaseReaderBuilder.field_meta,
    }

    def build(self, config: dict, resolver) -> Any:
        from agno.document.reader.docx import DocxReader

        kwargs = self._get_chunker_kwargs(config)
        return DocxReader(**kwargs)
