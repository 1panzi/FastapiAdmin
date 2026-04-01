# -*- coding: utf-8 -*-

from pydantic import BaseModel, ConfigDict, Field
from fastapi import Query
from datetime import datetime
from app.core.validator import DateTimeStr
from app.core.validator import DateTimeStr
from app.common.enums import QueueEnum
from app.core.base_schema import BaseSchema, UserBySchema

class AgMcpServerCreateSchema(BaseModel):
    """
    MCP服务新增模型
    """
    name: str = Field(default=..., description='MCP服务名称')
    transport: str = Field(default=..., description='传输协议')
    command: str = Field(default=..., description='stdio启动命令')
    url: str = Field(default=..., description='HTTP/SSE服务地址')
    env_config: dict = Field(default=..., description='环境变量配置')
    include_tools: dict = Field(default=..., description='仅包含的工具列表')
    exclude_tools: dict = Field(default=..., description='排除的工具列表')
    tool_name_prefix: str = Field(default=..., description='工具名称前缀')
    timeout_seconds: int = Field(default=..., description='连接超时秒数')
    refresh_connection: bool = Field(default=..., description='是否刷新连接')
    status: str = Field(default="0", description='是否启用')
    description: str | None = Field(default=None, max_length=255, description='')


class AgMcpServerUpdateSchema(AgMcpServerCreateSchema):
    """
    MCP服务更新模型
    """
    ...


class AgMcpServerOutSchema(AgMcpServerCreateSchema, BaseSchema, UserBySchema):
    """
    MCP服务响应模型
    """
    model_config = ConfigDict(from_attributes=True)


class AgMcpServerQueryParam:
    """MCP服务查询参数"""

    def __init__(
        self,
        name: str | None = Query(None, description="MCP服务名称"),
        transport: str | None = Query(None, description="传输协议"),
        command: str | None = Query(None, description="stdio启动命令"),
        url: str | None = Query(None, description="HTTP/SSE服务地址"),
        # env_config: dict | None = Query(None, description="环境变量配置"),
        # include_tools: dict | None = Query(None, description="仅包含的工具列表"),
        # exclude_tools: dict | None = Query(None, description="排除的工具列表"),
        tool_name_prefix: str | None = Query(None, description="工具名称前缀"),
        timeout_seconds: int | None = Query(None, description="连接超时秒数"),
        refresh_connection: bool | None = Query(None, description="是否刷新连接"),
        status: str | None = Query(None, description="是否启用"),
        created_id: int | None = Query(None, description=""),
        updated_id: int | None = Query(None, description=""),
        created_time: list[DateTimeStr] | None = Query(None, description="创建时间范围", examples=["2025-01-01 00:00:00", "2025-12-31 23:59:59"]),
        updated_time: list[DateTimeStr] | None = Query(None, description="更新时间范围", examples=["2025-01-01 00:00:00", "2025-12-31 23:59:59"]),
    ) -> None:
        # 模糊查询字段
        self.name = (QueueEnum.like.value, name)
        # 精确查询字段
        if transport:
            self.transport = (QueueEnum.eq.value, transport)
        # 精确查询字段
        if command:
            self.command = (QueueEnum.eq.value, command)
        # 精确查询字段
        if url:
            self.url = (QueueEnum.eq.value, url)
        # 精确查询字段
        # if env_config:
        #     self.env_config = (QueueEnum.eq.value, env_config)
        # # 精确查询字段
        # if include_tools:
        #     self.include_tools = (QueueEnum.eq.value, include_tools)
        # # 精确查询字段
        # if exclude_tools:
        #     self.exclude_tools = (QueueEnum.eq.value, exclude_tools)
        # 精确查询字段
        if tool_name_prefix:
            self.tool_name_prefix = (QueueEnum.eq.value, tool_name_prefix)
        # 精确查询字段
        if timeout_seconds:
            self.timeout_seconds = (QueueEnum.eq.value, timeout_seconds)
        # 精确查询字段
        if refresh_connection:
            self.refresh_connection = (QueueEnum.eq.value, refresh_connection)
        # 精确查询字段
        if status:
            self.status = (QueueEnum.eq.value, status)
        # 精确查询字段
        if created_id:
            self.created_id = (QueueEnum.eq.value, created_id)
        # 精确查询字段
        if updated_id:
            self.updated_id = (QueueEnum.eq.value, updated_id)
        # 时间范围查询
        if created_time and len(created_time) == 2:
            self.created_time = (QueueEnum.between.value, (created_time[0], created_time[1]))
        if updated_time and len(updated_time) == 2:
            self.updated_time = (QueueEnum.between.value, (updated_time[0], updated_time[1]))
