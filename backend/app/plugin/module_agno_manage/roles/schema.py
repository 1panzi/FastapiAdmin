

from fastapi import Query
from pydantic import BaseModel, ConfigDict, Field

from app.common.enums import QueueEnum
from app.core.base_schema import BaseSchema, UserBySchema
from app.core.validator import DateTimeStr


class AgRoleCreateSchema(BaseModel):
    """
    agno角色管理新增模型
    """
    name: str = Field(default=..., description='角色名称（唯一，如admin/operator/viewer）')
    scopes: dict | None = Field(default=None, description='gentOS权限范围列表（JSON数组）')
    status: str = Field(default="0", description='')
    description: str | None = Field(default=None, max_length=255, description='')


class AgRoleUpdateSchema(AgRoleCreateSchema):
    """
    agno角色管理更新模型
    """
    ...


class AgRoleOutSchema(AgRoleCreateSchema, BaseSchema, UserBySchema):
    """
    agno角色管理响应模型
    """
    model_config = ConfigDict(from_attributes=True)


class AgRoleQueryParam:
    """agno角色管理查询参数"""

    def __init__(
        self,
        name: str | None = Query(None, description="角色名称（唯一，如admin/operator/viewer）"),
        # scopes: dict | None = Query(None, description="gentOS权限范围列表（JSON数组）"),
        status: str | None = Query(None, description=""),
        created_id: int | None = Query(None, description=""),
        updated_id: int | None = Query(None, description=""),
        created_time: list[DateTimeStr] | None = Query(None, description="创建时间范围", examples=["2025-01-01 00:00:00", "2025-12-31 23:59:59"]),
        updated_time: list[DateTimeStr] | None = Query(None, description="更新时间范围", examples=["2025-01-01 00:00:00", "2025-12-31 23:59:59"]),
    ) -> None:
        # 模糊查询字段
        self.name = (QueueEnum.like.value, name)
        # 精确查询字段
        # if scopes:
        #     self.scopes = (QueueEnum.eq.value, scopes)
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
