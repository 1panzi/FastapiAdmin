# -*- coding: utf-8 -*-

from pydantic import BaseModel, ConfigDict, Field
from fastapi import Query
from app.core.validator import DateTimeStr
from datetime import datetime
from app.core.validator import DateTimeStr
from app.common.enums import QueueEnum
from app.core.base_schema import BaseSchema, UserBySchema

class AgVectordbCreateSchema(BaseModel):
    """
    向量数据库新增模型
    """
    name: str = Field(default=..., description='向量库名称')
    provider: str = Field(default=..., description='向量库类型')
    embedder_id: int | None = Field(default=None, description='关联嵌入模型ID')
    config: dict | None = Field(default=None, description='连接配置')
    status: str = Field(default="0", description='是否启用')
    description: str | None = Field(default=None, max_length=255, description='')


class AgVectordbUpdateSchema(AgVectordbCreateSchema):
    """
    向量数据库更新模型
    """
    ...


class AgVectordbOutSchema(AgVectordbCreateSchema, BaseSchema, UserBySchema):
    """
    向量数据库响应模型
    """
    model_config = ConfigDict(from_attributes=True)


class AgVectordbQueryParam:
    """向量数据库查询参数"""

    def __init__(
        self,
        name: str | None = Query(None, description="向量库名称"),
        provider: str | None = Query(None, description="向量库类型"),
        embedder_id: int | None = Query(None, description="关联嵌入模型ID"),
        # config: dict | None = Query(None, description="连接配置"),
        status: str | None = Query(None, description="是否启用"),
        created_id: int | None = Query(None, description=""),
        updated_id: int | None = Query(None, description=""),
        created_time: list[DateTimeStr] | None = Query(None, description="创建时间范围", examples=["2025-01-01 00:00:00", "2025-12-31 23:59:59"]),
        updated_time: list[DateTimeStr] | None = Query(None, description="更新时间范围", examples=["2025-01-01 00:00:00", "2025-12-31 23:59:59"]),
    ) -> None:
        # 模糊查询字段
        self.name = (QueueEnum.like.value, name)
        # 精确查询字段
        if provider:
            self.provider = (QueueEnum.eq.value, provider)
        # 精确查询字段
        if embedder_id:
            self.embedder_id = (QueueEnum.eq.value, embedder_id)
        # 精确查询字段
        # if config:
        #     self.config = (QueueEnum.eq.value, config)
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
