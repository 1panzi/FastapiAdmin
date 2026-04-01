# -*- coding: utf-8 -*-

from datetime import datetime
from sqlalchemy import JSON, String, Integer, Text, DateTime
from sqlalchemy.orm import Mapped, mapped_column

from app.core.base_model import ModelMixin, UserMixin


class AgRoleModel(ModelMixin, UserMixin):
    """
    agno角色管理表
    """
    __tablename__: str = 'ag_roles'
    __table_args__: dict[str, str] = {'comment': 'agno角色管理'}
    __loader_options__: list[str] = ["created_by", "updated_by"]

    name: Mapped[str | None] = mapped_column(String(100), nullable=True, comment='角色名称（唯一，如admin/operator/viewer）')
    scopes: Mapped[dict | None] = mapped_column(JSON, nullable=True, comment='gentOS权限范围列表（JSON数组）')

