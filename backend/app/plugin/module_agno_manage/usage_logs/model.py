# -*- coding: utf-8 -*-

from datetime import datetime
from decimal import Decimal
from sqlalchemy import Integer, Numeric, DateTime, BigInteger, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.base_model import ModelMixin, UserMixin


class AgUsageLogModel(ModelMixin, UserMixin):
    """
    用量日志表
    """
    __tablename__: str = 'ag_usage_logs'
    __table_args__: dict[str, str] = {'comment': '用量日志'}
    __loader_options__: list[str] = ["created_by", "updated_by"]

    agent_id: Mapped[int | None] = mapped_column(Integer, nullable=True, comment='关联AgentID')
    user_id: Mapped[str | None] = mapped_column(String(255), nullable=True, comment='用户ID')
    session_id: Mapped[str | None] = mapped_column(String(255), nullable=True, comment='会话ID')
    model_id: Mapped[int | None] = mapped_column(Integer, nullable=True, comment='关联模型ID')
    input_tokens: Mapped[int | None] = mapped_column(BigInteger, nullable=True, comment='输入Token数')
    output_tokens: Mapped[int | None] = mapped_column(BigInteger, nullable=True, comment='输出Token数')
    cost_usd: Mapped[Decimal | None] = mapped_column(String(255), nullable=True, comment='本次调用费用（美元）')
    latency_ms: Mapped[int | None] = mapped_column(Integer, nullable=True, comment='首Token延迟毫秒数')

