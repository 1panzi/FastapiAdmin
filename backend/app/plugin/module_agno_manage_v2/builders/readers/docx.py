from typing import Any
from app.plugin.module_agno_manage_v2.builders.readers.base import BaseReaderBuilder


class DocxReaderBuilder(BaseReaderBuilder):
    type = "docx"
    label = "Word 文档"

    try:
        from agno.knowledge.reader.docx_reader import DocxReader
        agno_class = DocxReader
    except ImportError:
        agno_class = None

    async def build(self, config: dict, resolver) -> Any:
        from agno.knowledge.reader.docx_reader import DocxReader
        chunker = await self._build_chunker(config, resolver)
        kwargs: dict = {
            "chunk": config.get("chunk", True),
            "chunk_size": config.get("chunk_size", 5000),
        }
        if chunker is not None:
            kwargs["chunking_strategy"] = chunker
        return DocxReader(**kwargs)
