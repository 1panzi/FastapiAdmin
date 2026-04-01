# -*- coding: utf-8 -*-

from pydantic import BaseModel, ConfigDict, Field
from fastapi import Query
from app.core.validator import DateTimeStr
from datetime import datetime
from app.core.validator import DateTimeStr
from app.common.enums import QueueEnum
from app.core.base_schema import BaseSchema, UserBySchema

class AgCompressionConfigCreateSchema(BaseModel):
    """
    压缩管理器新增模型
    """
    name: str = Field(default=..., description='压缩配置名称')
    model_id: int = Field(default=..., description='关联压缩模型ID')
    compress_tool_results_limit: int = Field(default=..., description='触发工具结果压缩的条数阈值')
    compress_token_limit: int = Field(default=..., description='触发压缩的Token数阈值')
    compress_tool_call_instructions: str = Field(default=..., description='工具调用压缩指令')
    status: str = Field(default="0", description='')
    description: str | None = Field(default=None, max_length=255, description='')


class AgCompressionConfigUpdateSchema(AgCompressionConfigCreateSchema):
    """
    压缩管理器更新模型
    """
    ...


class AgCompressionConfigOutSchema(AgCompressionConfigCreateSchema, BaseSchema, UserBySchema):
    """
    压缩管理器响应模型
    """
    model_config = ConfigDict(from_attributes=True)


class AgCompressionConfigQueryParam:
    """压缩管理器查询参数"""

    def __init__(
        self,
        name: str | None = Query(None, description="压缩配置名称"),
        model_id: int | None = Query(None, description="关联压缩模型ID"),
        compress_tool_results_limit: int | None = Query(None, description="触发工具结果压缩的条数阈值"),
        compress_token_limit: int | None = Query(None, description="触发压缩的Token数阈值"),
        compress_tool_call_instructions: str | None = Query(None, description="工具调用压缩指令"),
        status: str | None = Query(None, description=""),
        created_id: int | None = Query(None, description=""),
        updated_id: int | None = Query(None, description=""),
        created_time: list[DateTimeStr] | None = Query(None, description="创建时间范围", examples=["2025-01-01 00:00:00", "2025-12-31 23:59:59"]),
        updated_time: list[DateTimeStr] | None = Query(None, description="更新时间范围", examples=["2025-01-01 00:00:00", "2025-12-31 23:59:59"]),
    ) -> None:
        # 模糊查询字段
        self.name = (QueueEnum.like.value, name)
        # 精确查询字段
        if model_id:
            self.model_id = (QueueEnum.eq.value, model_id)
        # 精确查询字段
        if compress_tool_results_limit:
            self.compress_tool_results_limit = (QueueEnum.eq.value, compress_tool_results_limit)
        # 精确查询字段
        if compress_token_limit:
            self.compress_token_limit = (QueueEnum.eq.value, compress_token_limit)
        # 精确查询字段
        if compress_tool_call_instructions:
            self.compress_tool_call_instructions = (QueueEnum.eq.value, compress_tool_call_instructions)
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
