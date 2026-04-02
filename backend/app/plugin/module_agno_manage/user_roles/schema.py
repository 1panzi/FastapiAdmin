

from fastapi import Query
from pydantic import BaseModel, ConfigDict, Field

from app.common.enums import QueueEnum
from app.core.base_schema import BaseSchema, UserBySchema
from app.core.validator import DateTimeStr


class AgUserRoleCreateSchema(BaseModel):
    """
    用户角色关联新增模型
    """
    user_id: str = Field(default=..., description='用户ID（来自外部Auth系统）')
    role_id: int = Field(default=..., description='角色ID')


class AgUserRoleUpdateSchema(AgUserRoleCreateSchema):
    """
    用户角色关联更新模型
    """
    ...


class AgUserRoleOutSchema(AgUserRoleCreateSchema, BaseSchema, UserBySchema):
    """
    用户角色关联响应模型
    """
    model_config = ConfigDict(from_attributes=True)


class AgUserRoleQueryParam:
    """用户角色关联查询参数"""

    def __init__(
        self,
        user_id: str | None = Query(None, description="用户ID（来自外部Auth系统）"),
        role_id: int | None = Query(None, description="角色ID"),
        created_id: int | None = Query(None, description=""),
        updated_id: int | None = Query(None, description=""),
        created_time: list[DateTimeStr] | None = Query(None, description="创建时间范围", examples=["2025-01-01 00:00:00", "2025-12-31 23:59:59"]),
        updated_time: list[DateTimeStr] | None = Query(None, description="更新时间范围", examples=["2025-01-01 00:00:00", "2025-12-31 23:59:59"]),
    ) -> None:
        # 精确查询字段
        if user_id:
            self.user_id = (QueueEnum.eq.value, user_id)
        # 精确查询字段
        if role_id:
            self.role_id = (QueueEnum.eq.value, role_id)
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
