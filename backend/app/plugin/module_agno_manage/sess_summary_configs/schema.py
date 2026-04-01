# -*- coding: utf-8 -*-

from pydantic import BaseModel, ConfigDict, Field
from fastapi import Query
from datetime import datetime
from app.core.validator import DateTimeStr
from app.core.validator import DateTimeStr
from app.common.enums import QueueEnum
from app.core.base_schema import BaseSchema, UserBySchema

class AgSessSummaryConfigCreateSchema(BaseModel):
    """
    会话摘要配置新增模型
    """
    name: str = Field(default=..., description='会话摘要配置名称')
    model_id: int | None = Field(default=None, description='关联摘要模型ID')
    session_summary_prompt: str | None = Field(default=None, description='摘要生成提示词')
    summary_request_message: str | None = Field(default=None, description='摘要请求消息')
    status: str = Field(default="0", description='')
    description: str | None = Field(default=None, max_length=255, description='')


class AgSessSummaryConfigUpdateSchema(AgSessSummaryConfigCreateSchema):
    """
    会话摘要配置更新模型
    """
    ...


class AgSessSummaryConfigOutSchema(AgSessSummaryConfigCreateSchema, BaseSchema, UserBySchema):
    """
    会话摘要配置响应模型
    """
    model_config = ConfigDict(from_attributes=True)


class AgSessSummaryConfigQueryParam:
    """会话摘要配置查询参数"""

    def __init__(
        self,
        name: str | None = Query(None, description="会话摘要配置名称"),
        model_id: int | None = Query(None, description="关联摘要模型ID"),
        session_summary_prompt: str | None = Query(None, description="摘要生成提示词"),
        summary_request_message: str | None = Query(None, description="摘要请求消息"),
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
        if session_summary_prompt:
            self.session_summary_prompt = (QueueEnum.eq.value, session_summary_prompt)
        # 精确查询字段
        if summary_request_message:
            self.summary_request_message = (QueueEnum.eq.value, summary_request_message)
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
