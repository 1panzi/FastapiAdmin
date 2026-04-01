# -*- coding: utf-8 -*-

from datetime import datetime
from sqlalchemy import DateTime, Integer, Text, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.base_model import ModelMixin, UserMixin


class AgSessSummaryConfigModel(ModelMixin, UserMixin):
    """
    会话摘要配置表
    """
    __tablename__: str = 'ag_sess_summary_configs'
    __table_args__: dict[str, str] = {'comment': '会话摘要配置'}
    __loader_options__: list[str] = ["created_by", "updated_by"]

    name: Mapped[str | None] = mapped_column(String(255), nullable=True, comment='会话摘要配置名称')
    model_id: Mapped[int | None] = mapped_column(Integer, nullable=True, comment='关联摘要模型ID')
    session_summary_prompt: Mapped[str | None] = mapped_column(Text, nullable=True, comment='摘要生成提示词')
    summary_request_message: Mapped[str | None] = mapped_column(Text, nullable=True, comment='摘要请求消息')

