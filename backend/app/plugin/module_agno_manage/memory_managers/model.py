# -*- coding: utf-8 -*-

from datetime import datetime
from sqlalchemy import Integer, String, DateTime, Boolean, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.base_model import ModelMixin, UserMixin


class AgMemoryManagerModel(ModelMixin, UserMixin):
    """
    记忆管理表
    """
    __tablename__: str = 'ag_memory_managers'
    __table_args__: dict[str, str] = {'comment': '记忆管理'}
    __loader_options__: list[str] = ["created_by", "updated_by"]

    name: Mapped[str | None] = mapped_column(String(255), nullable=True, comment='记忆管理器名称')
    model_id: Mapped[int | None] = mapped_column(Integer, nullable=True, comment='关联模型ID（用于记忆处理）')
    delete_memories: Mapped[bool | None] = mapped_column(Boolean, nullable=True, comment='是否允许删除记忆')
    update_memories: Mapped[bool | None] = mapped_column(Boolean, nullable=True, comment='是否允许更新记忆')
    add_memories: Mapped[bool | None] = mapped_column(Boolean, nullable=True, comment='是否允许新增记忆')
    clear_memories: Mapped[bool | None] = mapped_column(Boolean, nullable=True, comment='是否允许清空记忆')
    memory_capture_instructions: Mapped[str | None] = mapped_column(Text, nullable=True, comment='记忆捕获指令')
    additional_instructions: Mapped[str | None] = mapped_column(Text, nullable=True, comment='附加指令')

