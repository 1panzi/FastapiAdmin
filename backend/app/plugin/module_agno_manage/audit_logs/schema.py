# -*- coding: utf-8 -*-

from pydantic import BaseModel, ConfigDict, Field
from fastapi import Query
from datetime import datetime
from app.core.validator import DateTimeStr
from app.core.validator import DateTimeStr
from app.common.enums import QueueEnum
from app.core.base_schema import BaseSchema, UserBySchema

class AgAuditLogCreateSchema(BaseModel):
    """
    审计日志新增模型
    """
    actor_id: str = Field(default=..., description='操作人ID')
    action: str = Field(default=..., description='操作类型(CREATE/UPDATE/DELETE/RUN)')
    resource_type: str = Field(default=..., description='资源类型')
    resource_id: int = Field(default=..., description='资源ID')
    diff: dict = Field(default=..., description='变更前后数据对比（JSON）')
    ip: str = Field(default=..., description='操作来源IP')


class AgAuditLogUpdateSchema(AgAuditLogCreateSchema):
    """
    审计日志更新模型
    """
    ...


class AgAuditLogOutSchema(AgAuditLogCreateSchema, BaseSchema, UserBySchema):
    """
    审计日志响应模型
    """
    model_config = ConfigDict(from_attributes=True)


class AgAuditLogQueryParam:
    """审计日志查询参数"""

    def __init__(
        self,
        actor_id: str | None = Query(None, description="操作人ID"),
        action: str | None = Query(None, description="操作类型(CREATE/UPDATE/DELETE/RUN)"),
        resource_type: str | None = Query(None, description="资源类型"),
        resource_id: int | None = Query(None, description="资源ID"),
        # diff: dict | None = Query(None, description="变更前后数据对比（JSON）"),
        ip: str | None = Query(None, description="操作来源IP"),
        created_time: list[DateTimeStr] | None = Query(None, description="创建时间范围", examples=["2025-01-01 00:00:00", "2025-12-31 23:59:59"]),
        updated_time: list[DateTimeStr] | None = Query(None, description="更新时间范围", examples=["2025-01-01 00:00:00", "2025-12-31 23:59:59"]),
    ) -> None:
        # 精确查询字段
        if actor_id:
            self.actor_id = (QueueEnum.eq.value, actor_id)
        # 精确查询字段
        if action:
            self.action = (QueueEnum.eq.value, action)
        # 精确查询字段
        if resource_type:
            self.resource_type = (QueueEnum.eq.value, resource_type)
        # 精确查询字段
        if resource_id:
            self.resource_id = (QueueEnum.eq.value, resource_id)
        # 精确查询字段
        # if diff:
        #     self.diff = (QueueEnum.eq.value, diff)
        # 精确查询字段
        if ip:
            self.ip = (QueueEnum.eq.value, ip)
        # 时间范围查询
        if created_time and len(created_time) == 2:
            self.created_time = (QueueEnum.between.value, (created_time[0], created_time[1]))
        if updated_time and len(updated_time) == 2:
            self.updated_time = (QueueEnum.between.value, (updated_time[0], updated_time[1]))
