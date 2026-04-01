# -*- coding: utf-8 -*-

from datetime import datetime
from sqlalchemy import Integer, Text, JSON, String, DateTime
from sqlalchemy.orm import Mapped, mapped_column

from app.core.base_model import ModelMixin, UserMixin


class ModelModel(ModelMixin, UserMixin):
    """
    模型管理表
    """
    __tablename__: str = 'ag_models'
    __table_args__: dict[str, str] = {'comment': '模型管理'}
    __loader_options__: list[str] = ["created_by", "updated_by"]

    name: Mapped[str | None] = mapped_column(String(255), nullable=True, comment='')
    model_id: Mapped[str | None] = mapped_column(String(255), nullable=True, comment='')
    provider: Mapped[str | None] = mapped_column(String(50), nullable=True, comment='')
    api_key: Mapped[str | None] = mapped_column(Text, nullable=True, comment='')
    base_url: Mapped[str | None] = mapped_column(String(500), nullable=True, comment='')
    config: Mapped[dict | None] = mapped_column(JSON, nullable=True, comment='')

