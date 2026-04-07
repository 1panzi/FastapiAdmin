
from fastapi import Query
from pydantic import BaseModel, ConfigDict, Field

from app.common.enums import QueueEnum
from app.core.base_schema import BaseSchema, UserBySchema
from app.core.validator import DateTimeStr


class AgResourceCreateSchema(BaseModel):
    """
    AI资源统一管理新增模型
    """
    name: str = Field(default=..., max_length=255, description='资源名称')
    category: str = Field(default=..., description='资源大类(model/embedder/reader/toolkit/knowledge/agent/team)')
    type: str = Field(default=..., description='具体类型(openai/pdf/duckduckgo/base等)')
    config: dict = Field(default_factory=dict, description='资源配置（支持ref引用或inline内联）')
    status: str = Field(default="0", description='状态(0:启用 1:禁用)')
    description: str | None = Field(default=None, max_length=255, description='描述')


class AgResourceUpdateSchema(AgResourceCreateSchema):
    """
    AI资源统一管理更新模型
    """
    ...


class AgResourceOutSchema(AgResourceCreateSchema, BaseSchema, UserBySchema):
    """
    AI资源统一管理响应模型
    """
    model_config = ConfigDict(from_attributes=True)


class AgResourceQueryParam:
    """AI资源统一管理查询参数"""

    def __init__(
        self,
        name: str | None = Query(None, description="资源名称（模糊匹配）"),
        category: str | None = Query(None, description="资源大类(model/embedder/reader/toolkit/knowledge/agent/team)"),
        type: str | None = Query(None, description="具体类型(openai/pdf/duckduckgo/base等)"),
        status: str | None = Query(None, description="状态(0:启用 1:禁用)"),
        uuid: str | None = Query(None, description="UUID"),
        created_time: list[DateTimeStr] | None = Query(
            None,
            description="创建时间范围",
            examples=["2025-01-01 00:00:00", "2025-12-31 23:59:59"]
        ),
        updated_time: list[DateTimeStr] | None = Query(
            None,
            description="更新时间范围",
            examples=["2025-01-01 00:00:00", "2025-12-31 23:59:59"]
        ),
    ) -> None:
        # 模糊查询字段
        self.name = (QueueEnum.like.value, name)
        # 精确查询字段
        if category:
            self.category = (QueueEnum.eq.value, category)
        if type:
            self.type = (QueueEnum.eq.value, type)
        if status:
            self.status = (QueueEnum.eq.value, status)
        if uuid:
            self.uuid = (QueueEnum.eq.value, uuid)
        # 时间范围查询
        if created_time and len(created_time) == 2:
            self.created_time = (QueueEnum.between.value, (created_time[0], created_time[1]))
        if updated_time and len(updated_time) == 2:
            self.updated_time = (QueueEnum.between.value, (updated_time[0], updated_time[1]))
