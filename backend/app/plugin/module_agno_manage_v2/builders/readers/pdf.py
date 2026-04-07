from typing import Any

from app.plugin.module_agno_manage_v2.builders.readers.base import BaseReaderBuilder


class PdfReaderBuilder(BaseReaderBuilder):
    type = "pdf"
    label = "PDF 文档"

    try:
        from agno.knowledge.reader.pdf_reader import PDFReader
        agno_class = PDFReader
    except ImportError:
        agno_class = None

    extra_fields = [
        {
            "name": "split_on_pages", "type": "bool", "default": True, "required": False,
            "label": "按页分割", "group": "PDF 配置", "span": 12, "order": 1,
            "tooltip": "每页作为独立文档单元",
        },
        {
            "name": "sanitize_content", "type": "bool", "default": True, "required": False,
            "label": "内容清洗", "group": "PDF 配置", "span": 12, "order": 2,
            "tooltip": "去除多余空白和特殊字符",
        },
        {
            "name": "password", "type": "password", "default": None, "required": False,
            "label": "PDF 密码", "group": "PDF 配置", "span": 12, "order": 3,
            "tooltip": "加密 PDF 的解密密码",
        },
    ]

    async def build(self, config: dict, resolver) -> Any:
        from agno.knowledge.reader.pdf_reader import PDFReader
        chunker = await self._build_chunker(config, resolver)
        kwargs: dict = {
            "chunk": config.get("chunk", True),
            "chunk_size": config.get("chunk_size", 5000),
        }
        if chunker is not None:
            kwargs["chunking_strategy"] = chunker
        for k in ("split_on_pages", "sanitize_content", "password"):
            if config.get(k) is not None:
                kwargs[k] = config[k]
        return PDFReader(**kwargs)
