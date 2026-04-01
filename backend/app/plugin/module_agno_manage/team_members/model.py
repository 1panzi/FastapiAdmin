# -*- coding: utf-8 -*-

from datetime import datetime
from sqlalchemy import Integer, Text, DateTime, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.base_model import ModelMixin, UserMixin


class AgTeamMemberModel(ModelMixin, UserMixin):
    """
    Team成员关系表
    """
    __tablename__: str = 'ag_team_members'
    __table_args__: dict[str, str] = {'comment': 'Team成员关系'}
    __loader_options__: list[str] = ["created_by", "updated_by"]

    team_id: Mapped[int | None] = mapped_column(Integer, nullable=True, comment='所属TeamID')
    member_type: Mapped[str | None] = mapped_column(String(20), nullable=True, comment='成员类型(agent/team)')
    member_id: Mapped[int | None] = mapped_column(Integer, nullable=True, comment='成员ID（agent或嵌套team）')
    role: Mapped[str | None] = mapped_column(String(255), nullable=True, comment='成员角色描述')
    member_order: Mapped[int | None] = mapped_column(Integer, nullable=True, comment='成员排序（数字小优先）')

