# -*- coding: utf-8 -*-

from pydantic import BaseModel, ConfigDict, Field
from fastapi import Query
from app.core.validator import DateTimeStr
from datetime import datetime
from app.core.validator import DateTimeStr
from app.common.enums import QueueEnum
from app.core.base_schema import BaseSchema, UserBySchema

class AgReasoningConfigCreateSchema(BaseModel):
    """
    推理配置新增模型
    """
    name: str = Field(default=..., description='推理配置名称')
    model_id: int = Field(default=..., description='关联推理模型ID')
    min_steps: int = Field(default=..., description='最少推理步数')
    max_steps: int = Field(default=..., description='最多推理步数')
    use_json_mode: bool = Field(default=..., description='是否使用JSON模式')
    tool_call_limit: int = Field(default=..., description='工具调用次数上限')
    debug_mode: bool = Field(default=..., description='是否开启调试模式')
    status: str = Field(default="0", description='')
    description: str | None = Field(default=None, max_length=255, description='')


class AgReasoningConfigUpdateSchema(AgReasoningConfigCreateSchema):
    """
    推理配置更新模型
    """
    ...


class AgReasoningConfigOutSchema(AgReasoningConfigCreateSchema, BaseSchema, UserBySchema):
    """
    推理配置响应模型
    """
    model_config = ConfigDict(from_attributes=True)


class AgReasoningConfigQueryParam:
    """推理配置查询参数"""

    def __init__(
        self,
        name: str | None = Query(None, description="推理配置名称"),
        model_id: int | None = Query(None, description="关联推理模型ID"),
        min_steps: int | None = Query(None, description="最少推理步数"),
        max_steps: int | None = Query(None, description="最多推理步数"),
        use_json_mode: bool | None = Query(None, description="是否使用JSON模式"),
        tool_call_limit: int | None = Query(None, description="工具调用次数上限"),
        debug_mode: bool | None = Query(None, description="是否开启调试模式"),
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
        if min_steps:
            self.min_steps = (QueueEnum.eq.value, min_steps)
        # 精确查询字段
        if max_steps:
            self.max_steps = (QueueEnum.eq.value, max_steps)
        # 精确查询字段
        if use_json_mode:
            self.use_json_mode = (QueueEnum.eq.value, use_json_mode)
        # 精确查询字段
        if tool_call_limit:
            self.tool_call_limit = (QueueEnum.eq.value, tool_call_limit)
        # 精确查询字段
        if debug_mode:
            self.debug_mode = (QueueEnum.eq.value, debug_mode)
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
