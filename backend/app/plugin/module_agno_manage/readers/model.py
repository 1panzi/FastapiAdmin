# -*- coding: utf-8 -*-

from datetime import datetime
from sqlalchemy import Boolean, DateTime, Text, String, Integer, JSON
from sqlalchemy.orm import Mapped, mapped_column

from app.core.base_model import ModelMixin, UserMixin


class AgReaderModel(ModelMixin, UserMixin):
    """
    reader管理表
    """
    __tablename__: str = 'ag_readers'
    __table_args__: dict[str, str] = {'comment': 'reader管理'}
    __loader_options__: list[str] = ["created_by", "updated_by"]

    name: Mapped[str | None] = mapped_column(String(255), nullable=True, comment='Reader名称')
    reader_type: Mapped[str | None] = mapped_column(String(30), nullable=True, comment='Reader类型(pdf/csv/excel/docx/pptx/json/markdown/text/website/firecrawl/tavily/youtube/arxiv/wikipedia/web_search/field_labeled_csv)')
    chunk: Mapped[bool | None] = mapped_column(Boolean, nullable=True, comment='是否对内容分块')
    chunk_size: Mapped[int | None] = mapped_column(Integer, nullable=True, comment='分块大小（字符数）')
    encoding: Mapped[str | None] = mapped_column(String(30), nullable=True, comment='文本编码（utf-8/gbk等，文本类Reader使用）')
    chunking_strategy: Mapped[str | None] = mapped_column(String(30), nullable=True, comment='Chunking策略(FixedSizeChunker/RecursiveChunker/DocumentChunker/MarkdownChunker/RowChunker/SemanticChunker/AgenticChunker/CodeChunker)')
    chunk_overlap: Mapped[int | None] = mapped_column(Integer, nullable=True, comment='Chunk重叠字符数（FixedSize/Recursive/Document/Markdown策略支持）')
    reader_config: Mapped[dict | None] = mapped_column(JSON, nullable=True, comment='Reader专属参数（按reader_type不同，见表注释）')
    embedder_id: Mapped[int | None] = mapped_column(Integer, nullable=True, comment='关联Embedder ID（SemanticChunker使用）')
    model_id: Mapped[int | None] = mapped_column(Integer, nullable=True, comment='关联Model ID（AgenticChunker使用）')

