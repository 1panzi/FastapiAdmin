# -*- coding: utf-8 -*-

from pydantic import BaseModel, ConfigDict, Field
from fastapi import Query
from app.core.validator import DateTimeStr
from datetime import datetime
from app.core.validator import DateTimeStr
from app.common.enums import QueueEnum
from app.core.base_schema import BaseSchema, UserBySchema

class AgScheduleCreateSchema(BaseModel):
    """
    定时任务管理新增模型
    """
    name: str = Field(default=..., description='定时任务名称')
    agent_id: int | None = Field(default=None, description='触发目标AgentID')
    team_id: int | None = Field(default=None, description='触发目标TeamID')
    payload: dict | None = Field(default=None, description='触发时传入的消息/参数')
    cron_expr: str | None = Field(default=None, description='Cron表达式（如0 9 * * 1-5）')
    timezone: str | None = Field(default=None, description='时区（如Asia/Shanghai）')
    timeout_seconds: int | None = Field(default=None, description='任务超时秒数')
    max_retries: int | None = Field(default=None, description='失败最大重试次数')
    retry_delay_seconds: int | None = Field(default=None, description='重试间隔秒数')
    status: str = Field(default="0", description='')
    description: str | None = Field(default=None, max_length=255, description='')


class AgScheduleUpdateSchema(AgScheduleCreateSchema):
    """
    定时任务管理更新模型
    """
    ...


class AgScheduleOutSchema(AgScheduleCreateSchema, BaseSchema, UserBySchema):
    """
    定时任务管理响应模型
    """
    model_config = ConfigDict(from_attributes=True)


class AgScheduleQueryParam:
    """定时任务管理查询参数"""

    def __init__(
        self,
        name: str | None = Query(None, description="定时任务名称"),
        agent_id: int | None = Query(None, description="触发目标AgentID"),
        team_id: int | None = Query(None, description="触发目标TeamID"),
        # payload: dict | None = Query(None, description="触发时传入的消息/参数"),
        cron_expr: str | None = Query(None, description="Cron表达式（如0 9 * * 1-5）"),
        timezone: str | None = Query(None, description="时区（如Asia/Shanghai）"),
        timeout_seconds: int | None = Query(None, description="任务超时秒数"),
        max_retries: int | None = Query(None, description="失败最大重试次数"),
        retry_delay_seconds: int | None = Query(None, description="重试间隔秒数"),
        status: str | None = Query(None, description=""),
        created_id: int | None = Query(None, description=""),
        updated_id: int | None = Query(None, description=""),
        created_time: list[DateTimeStr] | None = Query(None, description="创建时间范围", examples=["2025-01-01 00:00:00", "2025-12-31 23:59:59"]),
        updated_time: list[DateTimeStr] | None = Query(None, description="更新时间范围", examples=["2025-01-01 00:00:00", "2025-12-31 23:59:59"]),
    ) -> None:
        # 模糊查询字段
        self.name = (QueueEnum.like.value, name)
        # 精确查询字段
        if agent_id:
            self.agent_id = (QueueEnum.eq.value, agent_id)
        # 精确查询字段
        if team_id:
            self.team_id = (QueueEnum.eq.value, team_id)
        # 精确查询字段
        # if payload:
        #     self.payload = (QueueEnum.eq.value, payload)
        # 精确查询字段
        if cron_expr:
            self.cron_expr = (QueueEnum.eq.value, cron_expr)
        # 精确查询字段
        if timezone:
            self.timezone = (QueueEnum.eq.value, timezone)
        # 精确查询字段
        if timeout_seconds:
            self.timeout_seconds = (QueueEnum.eq.value, timeout_seconds)
        # 精确查询字段
        if max_retries:
            self.max_retries = (QueueEnum.eq.value, max_retries)
        # 精确查询字段
        if retry_delay_seconds:
            self.retry_delay_seconds = (QueueEnum.eq.value, retry_delay_seconds)
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
