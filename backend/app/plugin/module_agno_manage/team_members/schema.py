

from fastapi import Query
from pydantic import BaseModel, ConfigDict, Field

from app.common.enums import QueueEnum
from app.core.base_schema import BaseSchema, UserBySchema
from app.core.validator import DateTimeStr


class AgTeamMemberCreateSchema(BaseModel):
    """
    Team成员关系新增模型
    """
    team_id: int = Field(default=..., description='所属TeamID')
    member_type: str = Field(default=..., description='成员类型(agent/team)')
    member_id: int = Field(default=..., description='成员ID（agent或嵌套team）')
    role: str = Field(default=..., description='成员角色描述')
    member_order: int = Field(default=..., description='成员排序（数字小优先）')
    status: str = Field(default="0", description='')
    description: str | None = Field(default=None, max_length=255, description='')


class AgTeamMemberUpdateSchema(AgTeamMemberCreateSchema):
    """
    Team成员关系更新模型
    """
    ...


class AgTeamMemberOutSchema(AgTeamMemberCreateSchema, BaseSchema, UserBySchema):
    """
    Team成员关系响应模型
    """
    model_config = ConfigDict(from_attributes=True)


class AgTeamMemberQueryParam:
    """Team成员关系查询参数"""

    def __init__(
        self,
        team_id: int | None = Query(None, description="所属TeamID"),
        member_type: str | None = Query(None, description="成员类型(agent/team)"),
        member_id: int | None = Query(None, description="成员ID（agent或嵌套team）"),
        role: str | None = Query(None, description="成员角色描述"),
        member_order: int | None = Query(None, description="成员排序（数字小优先）"),
        status: str | None = Query(None, description=""),
        created_id: int | None = Query(None, description=""),
        updated_id: int | None = Query(None, description=""),
        created_time: list[DateTimeStr] | None = Query(None, description="创建时间范围", examples=["2025-01-01 00:00:00", "2025-12-31 23:59:59"]),
        updated_time: list[DateTimeStr] | None = Query(None, description="更新时间范围", examples=["2025-01-01 00:00:00", "2025-12-31 23:59:59"]),
    ) -> None:
        # 精确查询字段
        if team_id:
            self.team_id = (QueueEnum.eq.value, team_id)
        # 精确查询字段
        if member_type:
            self.member_type = (QueueEnum.eq.value, member_type)
        # 精确查询字段
        if member_id:
            self.member_id = (QueueEnum.eq.value, member_id)
        # 精确查询字段
        if role:
            self.role = (QueueEnum.eq.value, role)
        # 精确查询字段
        if member_order:
            self.member_order = (QueueEnum.eq.value, member_order)
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
