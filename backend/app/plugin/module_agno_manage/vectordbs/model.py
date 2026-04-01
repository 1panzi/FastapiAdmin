# -*- coding: utf-8 -*-

from datetime import datetime
from sqlalchemy import String, DateTime, JSON, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.base_model import ModelMixin, UserMixin


class AgVectordbModel(ModelMixin, UserMixin):
    """
    向量数据库表
    """
    __tablename__: str = 'ag_vectordbs'
    __table_args__: dict[str, str] = {'comment': '向量数据库'}
    __loader_options__: list[str] = ["created_by", "updated_by"]

    name: Mapped[str | None] = mapped_column(String(255), nullable=True, comment='向量库名称')
    provider: Mapped[str | None] = mapped_column(String(50), nullable=True, comment='向量库类型')
    embedder_id: Mapped[int | None] = mapped_column(Integer, nullable=True, comment='关联嵌入模型ID')
    config: Mapped[dict | None] = mapped_column(JSON, nullable=True, comment='连接配置')

