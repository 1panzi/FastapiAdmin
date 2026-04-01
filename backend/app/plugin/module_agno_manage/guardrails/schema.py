# -*- coding: utf-8 -*-

from pydantic import BaseModel, ConfigDict, Field
from fastapi import Query
from datetime import datetime
from app.core.validator import DateTimeStr
from app.core.validator import DateTimeStr
from app.common.enums import QueueEnum
from app.core.base_schema import BaseSchema, UserBySchema

class AgGuardrailCreateSchema(BaseModel):
    """
    护栏新增模型
    """
    name: str = Field(default=..., description='护栏名称')
    type: str = Field(default=..., description='护栏类型(openai_moderation/pii/prompt_injection/custom)')
    hook_type: str = Field(default=..., description='作用阶段(pre/post)')
    config: dict | None = Field(default=None, description='护栏配置参数')
    module_path: str | None = Field(default=None, description='自定义护栏模块路径（type=custom时使用）')
    class_name: str | None = Field(default=None, description='自定义护栏类名（type=custom时使用）')
    status: str = Field(default="0", description='')
    description: str | None = Field(default=None, max_length=255, description='')


class AgGuardrailUpdateSchema(AgGuardrailCreateSchema):
    """
    护栏更新模型
    """
    ...


class AgGuardrailOutSchema(AgGuardrailCreateSchema, BaseSchema, UserBySchema):
    """
    护栏响应模型
    """
    model_config = ConfigDict(from_attributes=True)


class AgGuardrailQueryParam:
    """护栏查询参数"""

    def __init__(
        self,
        name: str | None = Query(None, description="护栏名称"),
        class_name: str | None = Query(None, description="自定义护栏类名（type=custom时使用）"),
        type: str | None = Query(None, description="护栏类型(openai_moderation/pii/prompt_injection/custom)"),
        hook_type: str | None = Query(None, description="作用阶段(pre/post)"),
        # config: dict | None = Query(None, description="护栏配置参数"),
        module_path: str | None = Query(None, description="自定义护栏模块路径（type=custom时使用）"),
        status: str | None = Query(None, description=""),
        created_id: int | None = Query(None, description=""),
        updated_id: int | None = Query(None, description=""),
        created_time: list[DateTimeStr] | None = Query(None, description="创建时间范围", examples=["2025-01-01 00:00:00", "2025-12-31 23:59:59"]),
        updated_time: list[DateTimeStr] | None = Query(None, description="更新时间范围", examples=["2025-01-01 00:00:00", "2025-12-31 23:59:59"]),
    ) -> None:
        # 模糊查询字段
        self.name = (QueueEnum.like.value, name)
        # 精确查询字段
        if type:
            self.type = (QueueEnum.eq.value, type)
        # 精确查询字段
        if hook_type:
            self.hook_type = (QueueEnum.eq.value, hook_type)
        # 精确查询字段
        # if config:
        #     self.config = (QueueEnum.eq.value, config)
        # 精确查询字段
        if module_path:
            self.module_path = (QueueEnum.eq.value, module_path)
        # 模糊查询字段
        self.class_name = (QueueEnum.like.value, class_name)
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
