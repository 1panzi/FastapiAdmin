# -*- coding: utf-8 -*-

from datetime import datetime
from sqlalchemy import Integer, DateTime, String, Text, JSON
from sqlalchemy.orm import Mapped, mapped_column

from app.core.base_model import ModelMixin, UserMixin


class AgSkillModel(ModelMixin, UserMixin):
    """
    技能管理表
    """
    __tablename__: str = 'ag_skills'
    __table_args__: dict[str, str] = {'comment': '技能管理'}
    __loader_options__: list[str] = ["created_by", "updated_by"]

    name: Mapped[str | None] = mapped_column(String(255), nullable=True, comment='技能名称')
    instructions: Mapped[str | None] = mapped_column(Text, nullable=True, comment='注入Agent system prompt的技能指令')
    source_path: Mapped[str | None] = mapped_column(String(500), nullable=True, comment='本地磁盘路径（可选）')
    scripts: Mapped[dict | None] = mapped_column(JSON, nullable=True, comment='脚本文件名列表')
    references: Mapped[dict | None] = mapped_column(JSON, nullable=True, comment='参考文件名列表')
    allowed_tools: Mapped[dict | None] = mapped_column(JSON, nullable=True, comment='允许使用的工具列表')
    skill_metadata: Mapped[dict | None] = mapped_column(JSON, nullable=True, comment='元数据')

