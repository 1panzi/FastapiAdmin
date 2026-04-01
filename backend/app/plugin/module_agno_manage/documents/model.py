# -*- coding: utf-8 -*-

from datetime import datetime
from sqlalchemy import Integer, DateTime, Text, JSON, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.base_model import ModelMixin, UserMixin


class AgDocumentModel(ModelMixin, UserMixin):
    """
    知识库文档表
    """
    __tablename__: str = 'ag_documents'
    __table_args__: dict[str, str] = {'comment': '知识库文档'}
    __loader_options__: list[str] = ["created_by", "updated_by"]

    kb_id: Mapped[int | None] = mapped_column(Integer, nullable=True, comment='所属知识库ID')
    name: Mapped[str | None] = mapped_column(String(500), nullable=True, comment='文档名称')
    storage_type: Mapped[str | None] = mapped_column(String(20), nullable=True, comment='存储类型(local/s3/gcs/url)')
    storage_path: Mapped[str | None] = mapped_column(Text, nullable=True, comment='存储路径或URL')
    doc_status: Mapped[str | None] = mapped_column(String(20), nullable=True, comment='处理状态(pending/processing/indexed/failed)')
    error_msg: Mapped[str | None] = mapped_column(Text, nullable=True, comment='处理失败错误信息')
    metadata_config: Mapped[dict | None] = mapped_column(JSON, nullable=True, comment='文档元数据')

