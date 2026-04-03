

from fastapi import Query
from pydantic import BaseModel, ConfigDict, Field

from app.common.enums import QueueEnum
from app.core.base_schema import BaseSchema, UserBySchema
from app.core.validator import DateTimeStr


class AgKnowledgeBaseCreateSchema(BaseModel):
    """
    知识库新增模型

    readers 通过 ag_bindings (owner_type='knowledge', resource_type='reader') 关联，不在此处配置
    """
    name: str = Field(default=..., description='知识库名称')
    vectordb_id: int | None = Field(default=None, description='关联向量数据库ID')
    max_results: int | None = Field(default=10, description='检索返回最大条数')
    isolate_vector_search: bool = Field(default=False, description='向量搜索隔离：多知识库共享同一向量库时按name字段过滤，避免内容混淆')
    status: str = Field(default="0", description='状态(0:启用 1:禁用)')
    description: str | None = Field(default=None, max_length=255, description='备注')


class AgKnowledgeBaseUpdateSchema(AgKnowledgeBaseCreateSchema):
    """
    知识库更新模型
    """
    ...


class AgKnowledgeBaseOutSchema(AgKnowledgeBaseCreateSchema, BaseSchema, UserBySchema):
    """
    知识库响应模型
    """
    model_config = ConfigDict(from_attributes=True)


class AgKnowledgeBaseQueryParam:
    """知识库查询参数"""

    def __init__(
        self,
        name: str | None = Query(None, description="知识库名称"),
        vectordb_id: int | None = Query(None, description="关联向量数据库ID"),
        isolate_vector_search: bool | None = Query(None, description="是否启用向量搜索隔离"),
        status: str | None = Query(None, description="状态(0:启用 1:禁用)"),
        created_id: int | None = Query(None, description="创建人ID"),
        updated_id: int | None = Query(None, description="更新人ID"),
        created_time: list[DateTimeStr] | None = Query(None, description="创建时间范围", examples=["2025-01-01 00:00:00", "2025-12-31 23:59:59"]),
        updated_time: list[DateTimeStr] | None = Query(None, description="更新时间范围", examples=["2025-01-01 00:00:00", "2025-12-31 23:59:59"]),
    ) -> None:
        self.name = (QueueEnum.like.value, name)
        if vectordb_id:
            self.vectordb_id = (QueueEnum.eq.value, vectordb_id)
        if isolate_vector_search is not None:
            self.isolate_vector_search = (QueueEnum.eq.value, isolate_vector_search)
        if status:
            self.status = (QueueEnum.eq.value, status)
        if created_id:
            self.created_id = (QueueEnum.eq.value, created_id)
        if updated_id:
            self.updated_id = (QueueEnum.eq.value, updated_id)
        if created_time and len(created_time) == 2:
            self.created_time = (QueueEnum.between.value, (created_time[0], created_time[1]))
        if updated_time and len(updated_time) == 2:
            self.updated_time = (QueueEnum.between.value, (updated_time[0], updated_time[1]))
