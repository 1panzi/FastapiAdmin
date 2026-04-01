# -*- coding: utf-8 -*-

from datetime import datetime
from sqlalchemy import JSON, String, Text, DateTime, Integer
from sqlalchemy.orm import Mapped, mapped_column

from app.core.base_model import ModelMixin, UserMixin


class AgIntegrationModel(ModelMixin, UserMixin):
    """
    渠道集成管理表
    """
    __tablename__: str = 'ag_integrations'
    __table_args__: dict[str, str] = {'comment': '渠道集成管理'}
    __loader_options__: list[str] = ["created_by", "updated_by"]

    name: Mapped[str | None] = mapped_column(String(255), nullable=True, comment='渠道名称')
    type: Mapped[str | None] = mapped_column(String(20), nullable=True, comment='渠道类型(slack/telegram/whatsapp/agui/discord)')
    agent_id: Mapped[int | None] = mapped_column(Integer, nullable=True, comment='绑定AgentID（三选一）')
    team_id: Mapped[int | None] = mapped_column(Integer, nullable=True, comment='绑定TeamID（三选一）')
    workflow_id: Mapped[int | None] = mapped_column(Integer, nullable=True, comment='绑定WorkflowID（三选一）')
    token: Mapped[str | None] = mapped_column(Text, nullable=True, comment='渠道访问Token（Slack/Telegram等）')
    signing_secret: Mapped[str | None] = mapped_column(Text, nullable=True, comment='签名密钥（Slack校验用）')
    prefix: Mapped[str | None] = mapped_column(String(100), nullable=True, comment='路由前缀（如/slack /telegram）')
    config: Mapped[dict | None] = mapped_column(JSON, nullable=True, comment='渠道扩展配置（streaming/reply_to_mentions_only等）')

