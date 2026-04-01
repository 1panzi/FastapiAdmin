# -*- coding: utf-8 -*-

from pydantic import BaseModel, ConfigDict, Field
from fastapi import Query
from datetime import datetime
from app.core.validator import DateTimeStr
from app.common.enums import QueueEnum
from app.core.base_schema import BaseSchema, UserBySchema

class ModelCreateSchema(BaseModel):
    """
    模型管理新增模型
    """
    name: str = Field(default=..., description='')
    model_id: str = Field(default=..., description='')
    provider: str = Field(default=..., description='')
    api_key: str = Field(default=..., description='')
    base_url: str = Field(default=..., description='')
    config: dict = Field(default=..., description='')
    status: str = Field(default="0", description='')
    description: str | None = Field(default=None, max_length=255, description='')


class ModelUpdateSchema(ModelCreateSchema):
    """
    模型管理更新模型
    """
    ...


class ModelOutSchema(ModelCreateSchema, BaseSchema, UserBySchema):
    """
    模型管理响应模型
    """
    model_config = ConfigDict(from_attributes=True)


class ModelQueryParam:
    """模型管理查询参数"""

    def __init__(
        self,
        name: str | None = Query(None, description=""),
        uuid: str | None = Query(None, description=""),
        model_id: str | None = Query(None, description=""),
        provider: str | None = Query(None, description=""),
        api_key: str | None = Query(None, description=""),
        base_url: str | None = Query(None, description=""),
        status: str | None = Query(None, description=""),
        created_id: int | None = Query(None, description=""),
        updated_id: int | None = Query(None, description=""),
        created_time: list[DateTimeStr] | None = Query(None, description="创建时间范围", examples=["2025-01-01 00:00:00", "2025-12-31 23:59:59"]),
        updated_time: list[DateTimeStr] | None = Query(None, description="更新时间范围", examples=["2025-01-01 00:00:00", "2025-12-31 23:59:59"]),
    ) -> None:
        # 精确查询字段
        if uuid:
            self.uuid = (QueueEnum.eq.value, uuid)
        # 模糊查询字段
        self.name = (QueueEnum.like.value, name)
        # 精确查询字段
        if model_id:
            self.model_id = (QueueEnum.eq.value, model_id)
        # 精确查询字段
        if provider:
            self.provider = (QueueEnum.eq.value, provider)
        # 精确查询字段
        if api_key:
            self.api_key = (QueueEnum.eq.value, api_key)
        # 精确查询字段
        if base_url:
            self.base_url = (QueueEnum.eq.value, base_url)
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
