# -*- coding: utf-8 -*-

from datetime import datetime
from sqlalchemy import DateTime, Integer, String, Boolean, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.base_model import ModelMixin, UserMixin


class AgCultureConfigModel(ModelMixin, UserMixin):
    """
    文化配置表
    """
    __tablename__: str = 'ag_culture_configs'
    __table_args__: dict[str, str] = {'comment': '文化配置'}
    __loader_options__: list[str] = ["created_by", "updated_by"]

    name: Mapped[str | None] = mapped_column(String(255), nullable=True, comment='文化配置名称')
    model_id: Mapped[int | None] = mapped_column(Integer, nullable=True, comment='关联模型ID')
    add_knowledge: Mapped[bool | None] = mapped_column(Boolean, nullable=True, comment='是否允许新增知识')
    update_knowledge: Mapped[bool | None] = mapped_column(Boolean, nullable=True, comment='是否允许更新知识')
    delete_knowledge: Mapped[bool | None] = mapped_column(Boolean, nullable=True, comment='是否允许删除知识')
    clear_knowledge: Mapped[bool | None] = mapped_column(Boolean, nullable=True, comment='是否允许清空知识')
    culture_capture_instructions: Mapped[str | None] = mapped_column(Text, nullable=True, comment='文化捕获指令')
    additional_instructions: Mapped[str | None] = mapped_column(Text, nullable=True, comment='附加指令')
    debug_mode: Mapped[bool | None] = mapped_column(Boolean, nullable=True, comment='是否开启调试模式')

