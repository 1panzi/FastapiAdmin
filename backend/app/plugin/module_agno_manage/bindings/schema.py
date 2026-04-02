

from fastapi import Query
from pydantic import BaseModel, ConfigDict, Field

from app.common.enums import QueueEnum
from app.core.base_schema import BaseSchema, UserBySchema
from app.core.validator import DateTimeStr


class AgBindingCreateSchema(BaseModel):
    """
    资源绑定关系新增模型
    """
    owner_type: str = Field(default=..., description='拥有者类型(agent/team)')
    owner_id: int = Field(default=..., description='拥有者ID')
    resource_type: str = Field(default=..., description='资源类型(toolkit/skill/mcp/knowledge/hook/guardrail)')
    resource_id: int = Field(default=..., description='资源ID')
    priority: int | None = Field(default=None, description='优先级（数字小优先）')
    config_override: dict | None = Field(default=None, description='覆盖资源默认配置（如特定Agent使用不同API Key）')
    status: str = Field(default="0", description='')
    description: str | None = Field(default=None, max_length=255, description='')


class AgBindingUpdateSchema(AgBindingCreateSchema):
    """
    资源绑定关系更新模型
    """
    ...


class AgBindingOutSchema(AgBindingCreateSchema, BaseSchema, UserBySchema):
    """
    资源绑定关系响应模型
    """
    model_config = ConfigDict(from_attributes=True)


class AgBindingQueryParam:
    """资源绑定关系查询参数"""

    def __init__(
        self,
        owner_type: str | None = Query(None, description="拥有者类型(agent/team)"),
        owner_id: int | None = Query(None, description="拥有者ID"),
        resource_type: str | None = Query(None, description="资源类型(toolkit/skill/mcp/knowledge/hook/guardrail)"),
        resource_id: int | None = Query(None, description="资源ID"),
        priority: int | None = Query(None, description="优先级（数字小优先）"),
        # config_override: dict | None = Query(None, description="覆盖资源默认配置（如特定Agent使用不同API Key）"),
        status: str | None = Query(None, description=""),
        created_id: int | None = Query(None, description=""),
        updated_id: int | None = Query(None, description=""),
        created_time: list[DateTimeStr] | None = Query(None, description="创建时间范围", examples=["2025-01-01 00:00:00", "2025-12-31 23:59:59"]),
        updated_time: list[DateTimeStr] | None = Query(None, description="更新时间范围", examples=["2025-01-01 00:00:00", "2025-12-31 23:59:59"]),
    ) -> None:
        # 精确查询字段
        if owner_type:
            self.owner_type = (QueueEnum.eq.value, owner_type)
        # 精确查询字段
        if owner_id:
            self.owner_id = (QueueEnum.eq.value, owner_id)
        # 精确查询字段
        if resource_type:
            self.resource_type = (QueueEnum.eq.value, resource_type)
        # 精确查询字段
        if resource_id:
            self.resource_id = (QueueEnum.eq.value, resource_id)
        # 精确查询字段
        if priority:
            self.priority = (QueueEnum.eq.value, priority)
        # 精确查询字段
        # if config_override:
        #     self.config_override = (QueueEnum.eq.value, config_override)
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
