# -*- coding: utf-8 -*-

from datetime import datetime
from sqlalchemy import Text, Boolean, DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.base_model import ModelMixin, UserMixin


class AgReasoningConfigModel(ModelMixin, UserMixin):
    """
    推理配置表
    """
    __tablename__: str = 'ag_reasoning_configs'
    __table_args__: dict[str, str] = {'comment': '推理配置'}
    __loader_options__: list[str] = ["created_by", "updated_by"]

    name: Mapped[str | None] = mapped_column(String(255), nullable=True, comment='推理配置名称')
    model_id: Mapped[int | None] = mapped_column(Integer, nullable=True, comment='关联推理模型ID')
    min_steps: Mapped[int | None] = mapped_column(Integer, nullable=True, comment='最少推理步数')
    max_steps: Mapped[int | None] = mapped_column(Integer, nullable=True, comment='最多推理步数')
    use_json_mode: Mapped[bool | None] = mapped_column(Boolean, nullable=True, comment='是否使用JSON模式')
    tool_call_limit: Mapped[int | None] = mapped_column(Integer, nullable=True, comment='工具调用次数上限')
    debug_mode: Mapped[bool | None] = mapped_column(Boolean, nullable=True, comment='是否开启调试模式')

