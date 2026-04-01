# -*- coding: utf-8 -*-

from pydantic import BaseModel, ConfigDict, Field
from fastapi import Query
from app.core.validator import DateTimeStr
from datetime import datetime
from app.core.validator import DateTimeStr
from app.common.enums import QueueEnum
from app.core.base_schema import BaseSchema, UserBySchema

class AgIntegrationCreateSchema(BaseModel):
    """
    渠道集成管理新增模型
    """
    name: str = Field(default=..., description='渠道名称')
    type: str = Field(default=..., description='渠道类型(slack/telegram/whatsapp/agui/discord)')
    agent_id: int = Field(default=..., description='绑定AgentID（三选一）')
    team_id: int = Field(default=..., description='绑定TeamID（三选一）')
    workflow_id: int = Field(default=..., description='绑定WorkflowID（三选一）')
    token: str = Field(default=..., description='渠道访问Token（Slack/Telegram等）')
    signing_secret: str = Field(default=..., description='签名密钥（Slack校验用）')
    prefix: str = Field(default=..., description='路由前缀（如/slack /telegram）')
    config: dict = Field(default=..., description='渠道扩展配置（streaming/reply_to_mentions_only等）')
    status: str = Field(default="0", description='')
    description: str | None = Field(default=None, max_length=255, description='')


class AgIntegrationUpdateSchema(AgIntegrationCreateSchema):
    """
    渠道集成管理更新模型
    """
    ...


class AgIntegrationOutSchema(AgIntegrationCreateSchema, BaseSchema, UserBySchema):
    """
    渠道集成管理响应模型
    """
    model_config = ConfigDict(from_attributes=True)


class AgIntegrationQueryParam:
    """渠道集成管理查询参数"""

    def __init__(
        self,
        name: str | None = Query(None, description="渠道名称"),
        type: str | None = Query(None, description="渠道类型(slack/telegram/whatsapp/agui/discord)"),
        agent_id: int | None = Query(None, description="绑定AgentID（三选一）"),
        team_id: int | None = Query(None, description="绑定TeamID（三选一）"),
        workflow_id: int | None = Query(None, description="绑定WorkflowID（三选一）"),
        token: str | None = Query(None, description="渠道访问Token（Slack/Telegram等）"),
        signing_secret: str | None = Query(None, description="签名密钥（Slack校验用）"),
        prefix: str | None = Query(None, description="路由前缀（如/slack /telegram）"),
        # config: dict | None = Query(None, description="渠道扩展配置（streaming/reply_to_mentions_only等）"),
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
        if agent_id:
            self.agent_id = (QueueEnum.eq.value, agent_id)
        # 精确查询字段
        if team_id:
            self.team_id = (QueueEnum.eq.value, team_id)
        # 精确查询字段
        if workflow_id:
            self.workflow_id = (QueueEnum.eq.value, workflow_id)
        # 精确查询字段
        if token:
            self.token = (QueueEnum.eq.value, token)
        # 精确查询字段
        if signing_secret:
            self.signing_secret = (QueueEnum.eq.value, signing_secret)
        # 精确查询字段
        if prefix:
            self.prefix = (QueueEnum.eq.value, prefix)
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
