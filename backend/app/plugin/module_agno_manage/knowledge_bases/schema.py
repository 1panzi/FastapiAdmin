# -*- coding: utf-8 -*-

from pydantic import BaseModel, ConfigDict, Field
from fastapi import Query
from datetime import datetime
from app.core.validator import DateTimeStr
from app.core.validator import DateTimeStr
from app.common.enums import QueueEnum
from app.core.base_schema import BaseSchema, UserBySchema

class AgKnowledgeBaseCreateSchema(BaseModel):
    """
    知识库新增模型
    """
    name: str = Field(default=..., description='知识库名称')
    vectordb_id: int | None = Field(default=None, description='关联向量数据库ID')
    max_results: int | None = Field(default=None, description='最大检索结果数')
    reader_type: str | None = Field(default=None, description='文档读取器类型(pdf/web/docx/csv/json/text)')
    reader_config: dict | None = Field(default=None, description='读取器配置参数')
    default_filters: dict | None = Field(default=None, description='默认搜索过滤条件')
    status: str = Field(default="0", description='')
    description: str | None = Field(default=None, max_length=255, description='')


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
        max_results: int | None = Query(None, description="最大检索结果数"),
        reader_type: str | None = Query(None, description="文档读取器类型(pdf/web/docx/csv/json/text)"),
        # reader_config: dict | None = Query(None, description="读取器配置参数"),
        # default_filters: dict | None = Query(None, description="默认搜索过滤条件"),
        status: str | None = Query(None, description=""),
        created_id: int | None = Query(None, description=""),
        updated_id: int | None = Query(None, description=""),
        created_time: list[DateTimeStr] | None = Query(None, description="创建时间范围", examples=["2025-01-01 00:00:00", "2025-12-31 23:59:59"]),
        updated_time: list[DateTimeStr] | None = Query(None, description="更新时间范围", examples=["2025-01-01 00:00:00", "2025-12-31 23:59:59"]),
    ) -> None:
        # 模糊查询字段
        self.name = (QueueEnum.like.value, name)
        # 精确查询字段
        if vectordb_id:
            self.vectordb_id = (QueueEnum.eq.value, vectordb_id)
        # 精确查询字段
        if max_results:
            self.max_results = (QueueEnum.eq.value, max_results)
        # 精确查询字段
        if reader_type:
            self.reader_type = (QueueEnum.eq.value, reader_type)
        # 精确查询字段
        # if reader_config:
        #     self.reader_config = (QueueEnum.eq.value, reader_config)
        # # 精确查询字段
        # if default_filters:
        #     self.default_filters = (QueueEnum.eq.value, default_filters)
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
