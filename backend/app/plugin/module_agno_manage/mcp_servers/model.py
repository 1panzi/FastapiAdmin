# -*- coding: utf-8 -*-

from datetime import datetime
from sqlalchemy import DateTime, Boolean, String, Integer, Text, JSON
from sqlalchemy.orm import Mapped, mapped_column

from app.core.base_model import ModelMixin, UserMixin


class AgMcpServerModel(ModelMixin, UserMixin):
    """
    MCP服务表
    """
    __tablename__: str = 'ag_mcp_servers'
    __table_args__: dict[str, str] = {'comment': 'MCP服务'}
    __loader_options__: list[str] = ["created_by", "updated_by"]

    name: Mapped[str | None] = mapped_column(String(255), nullable=True, comment='MCP服务名称')
    transport: Mapped[str | None] = mapped_column(String(20), nullable=True, comment='传输协议')
    command: Mapped[str | None] = mapped_column(Text, nullable=True, comment='stdio启动命令')
    url: Mapped[str | None] = mapped_column(String(500), nullable=True, comment='HTTP/SSE服务地址')
    env_config: Mapped[dict | None] = mapped_column(JSON, nullable=True, comment='环境变量配置')
    include_tools: Mapped[dict | None] = mapped_column(JSON, nullable=True, comment='仅包含的工具列表')
    exclude_tools: Mapped[dict | None] = mapped_column(JSON, nullable=True, comment='排除的工具列表')
    tool_name_prefix: Mapped[str | None] = mapped_column(String(100), nullable=True, comment='工具名称前缀')
    timeout_seconds: Mapped[int | None] = mapped_column(Integer, nullable=True, comment='连接超时秒数')
    refresh_connection: Mapped[bool | None] = mapped_column(Boolean, nullable=True, comment='是否刷新连接')

