

from fastapi import Query
from pydantic import BaseModel, ConfigDict, Field

from app.common.enums import QueueEnum
from app.core.base_schema import BaseSchema, UserBySchema
from app.core.validator import DateTimeStr


class AgDocumentCreateSchema(BaseModel):
    """
    知识库文档新增模型
    """
    kb_id: int = Field(default=..., description='所属知识库ID')
    name: str = Field(default=..., description='文档名称')
    storage_type: str | None = Field(default=None, description='存储类型(local/s3/gcs/url)')
    storage_path: str | None = Field(default=None, description='存储路径或URL')
    doc_status: str | None = Field(default=None, description='处理状态(pending/processing/indexed/failed)')
    error_msg: str | None = Field(default=None, description='处理失败错误信息')
    content_id: str | None = Field(default=None, description='Agno contents_db 记录ID')
    metadata_config: dict | None = Field(default=None, description='文档元数据')
    reader_id: int | None = Field(default=None, description='处理该文档所用的 Reader ID')
    status: str = Field(default="0", description='')
    description: str | None = Field(default=None, max_length=255, description='')


class AgDocumentUpdateSchema(AgDocumentCreateSchema):
    """
    知识库文档更新模型
    """
    ...


class AgDocumentOutSchema(AgDocumentCreateSchema, BaseSchema, UserBySchema):
    """
    知识库文档响应模型
    """
    model_config = ConfigDict(from_attributes=True)


class AgDocumentQueryParam:
    """知识库文档查询参数"""

    def __init__(
        self,
        name: str | None = Query(None, description="文档名称"),
        kb_id: int | None = Query(None, description="所属知识库ID"),
        storage_type: str | None = Query(None, description="存储类型(local/s3/gcs/url)"),
        storage_path: str | None = Query(None, description="存储路径或URL"),
        doc_status: str | None = Query(None, description="处理状态(pending/processing/indexed/failed)"),
        error_msg: str | None = Query(None, description="处理失败错误信息"),
        # metadata_config: dict | None = Query(None, description="文档元数据"),
        status: str | None = Query(None, description=""),
        created_id: int | None = Query(None, description=""),
        updated_id: int | None = Query(None, description=""),
        created_time: list[DateTimeStr] | None = Query(None, description="创建时间范围", examples=["2025-01-01 00:00:00", "2025-12-31 23:59:59"]),
        updated_time: list[DateTimeStr] | None = Query(None, description="更新时间范围", examples=["2025-01-01 00:00:00", "2025-12-31 23:59:59"]),
    ) -> None:
        # 精确查询字段
        if kb_id:
            self.kb_id = (QueueEnum.eq.value, kb_id)
        # 模糊查询字段
        self.name = (QueueEnum.like.value, name)
        # 精确查询字段
        if storage_type:
            self.storage_type = (QueueEnum.eq.value, storage_type)
        # 精确查询字段
        if storage_path:
            self.storage_path = (QueueEnum.eq.value, storage_path)
        # 精确查询字段
        if doc_status:
            self.doc_status = (QueueEnum.eq.value, doc_status)
        # 精确查询字段
        if error_msg:
            self.error_msg = (QueueEnum.eq.value, error_msg)
        # 精确查询字段
        # if metadata_config:
            # self.metadata_config = (QueueEnum.eq.value, metadata_config)
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


class AgDocumentStatusUpdateSchema(BaseModel):
    """内部状态回写，不走 auth 的更新模型"""
    doc_status: str
    error_msg: str | None = None
    content_id: str | None = None


class AgDocumentSubQueryParam:
    """知识库子路由文档查询参数（不含 kb_id，避免与路径参数冲突）"""

    def __init__(
        self,
        name: str | None = Query(None, description="文档名称"),
        storage_type: str | None = Query(None, description="存储类型"),
        doc_status: str | None = Query(None, description="处理状态"),
        status: str | None = Query(None, description="记录状态"),
    ) -> None:
        self.name = (QueueEnum.like.value, name)
        if storage_type:
            self.storage_type = (QueueEnum.eq.value, storage_type)
        if doc_status:
            self.doc_status = (QueueEnum.eq.value, doc_status)
        if status:
            self.status = (QueueEnum.eq.value, status)
