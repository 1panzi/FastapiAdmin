# -*- coding: utf-8 -*-

from pydantic import BaseModel, ConfigDict, Field
from fastapi import Query
from app.core.validator import DateTimeStr
from datetime import datetime
from app.core.validator import DateTimeStr
from app.common.enums import QueueEnum
from app.core.base_schema import BaseSchema, UserBySchema

class AgReaderCreateSchema(BaseModel):
    """
    reader管理新增模型

    chunking_strategy 参数说明：
      FixedSizeChunker / RecursiveChunker / DocumentChunker / MarkdownChunker
        → chunk_size + chunk_overlap 生效
      RowChunker
        → chunk_size / chunk_overlap 无效（每行即一个 chunk）
      CodeChunker
        → chunk_size 生效，chunk_overlap 无效
      SemanticChunker
        → chunk_size 生效，chunk_overlap 无效，需要 embedder_id
          reader_config 可含: similarity_threshold / similarity_window / min_sentences_per_chunk
      AgenticChunker
        → chunk_size 作为 max_chunk_size，chunk_overlap 无效，需要 model_id
    """
    name: str = Field(default=..., description='Reader名称')
    reader_type: str = Field(default=..., description='Reader类型(pdf/csv/excel/docx/pptx/json/markdown/text/website/firecrawl/tavily/youtube/arxiv/wikipedia/web_search/field_labeled_csv)')
    chunk: bool = Field(default=True, description='是否对内容分块')
    chunk_size: int = Field(default=5000, description='分块大小（字符数）')
    encoding: str | None = Field(default=None, description='文本编码（utf-8/gbk等，文本类Reader使用，为空时自动检测）')
    chunking_strategy: str | None = Field(default=None, description='Chunking策略，为空时使用该reader_type的默认策略')
    chunk_overlap: int = Field(default=0, description='Chunk重叠字符数（FixedSize/Recursive/Document/Markdown策略支持）')
    reader_config: dict | None = Field(default=None, description='Reader专属参数，按reader_type不同（参考 agno_catalog）')
    embedder_id: int | None = Field(default=None, description='关联Embedder ID（SemanticChunker使用）')
    model_id: int | None = Field(default=None, description='关联Model ID（AgenticChunker使用）')
    status: str = Field(default="0", description='状态(0:启用 1:禁用)')
    description: str | None = Field(default=None, max_length=255, description='备注/描述')


class AgReaderUpdateSchema(AgReaderCreateSchema):
    """
    reader管理更新模型
    """
    ...


class AgReaderOutSchema(AgReaderCreateSchema, BaseSchema, UserBySchema):
    """
    reader管理响应模型
    """
    model_config = ConfigDict(from_attributes=True)


class AgReaderQueryParam:
    """reader管理查询参数"""

    def __init__(
        self,
        name: str | None = Query(None, description="Reader名称"),
        description: str | None = Query(None, description="备注/描述"),
        reader_type: str | None = Query(None, description="Reader类型(pdf/csv/excel/docx/pptx/json/markdown/text/website/firecrawl/tavily/youtube/arxiv/wikipedia/web_search/field_labeled_csv)"),
        chunk: bool | None = Query(None, description="是否对内容分块"),
        chunk_size: int | None = Query(None, description="分块大小（字符数）"),
        encoding: str | None = Query(None, description="文本编码（utf-8/gbk等，文本类Reader使用）"),
        chunking_strategy: str | None = Query(None, description="Chunking策略(FixedSizeChunker/RecursiveChunker/DocumentChunker/MarkdownChunker/RowChunker/SemanticChunker/AgenticChunker/CodeChunker)"),
        chunk_overlap: int | None = Query(None, description="Chunk重叠字符数（FixedSize/Recursive/Document/Markdown策略支持）"),
        reader_config: dict | None = Query(None, description="Reader专属参数（按reader_type不同，见表注释）"),
        embedder_id: int | None = Query(None, description="关联Embedder ID（SemanticChunker使用）"),
        model_id: int | None = Query(None, description="关联Model ID（AgenticChunker使用）"),
        status: str | None = Query(None, description="是否启用(0:启用 1:禁用)"),
        created_id: int | None = Query(None, description=""),
        updated_id: int | None = Query(None, description=""),
        created_time: list[DateTimeStr] | None = Query(None, description="创建时间范围", examples=["2025-01-01 00:00:00", "2025-12-31 23:59:59"]),
        updated_time: list[DateTimeStr] | None = Query(None, description="更新时间范围", examples=["2025-01-01 00:00:00", "2025-12-31 23:59:59"]),
    ) -> None:
        # 模糊查询字段
        self.name = (QueueEnum.like.value, name)
        # 精确查询字段
        if reader_type:
            self.reader_type = (QueueEnum.eq.value, reader_type)
        # 精确查询字段
        if chunk:
            self.chunk = (QueueEnum.eq.value, chunk)
        # 精确查询字段
        if chunk_size:
            self.chunk_size = (QueueEnum.eq.value, chunk_size)
        # 精确查询字段
        if encoding:
            self.encoding = (QueueEnum.eq.value, encoding)
        # 精确查询字段
        if chunking_strategy:
            self.chunking_strategy = (QueueEnum.eq.value, chunking_strategy)
        # 精确查询字段
        if chunk_overlap:
            self.chunk_overlap = (QueueEnum.eq.value, chunk_overlap)
        # 精确查询字段
        if reader_config:
            self.reader_config = (QueueEnum.eq.value, reader_config)
        # 精确查询字段
        if embedder_id:
            self.embedder_id = (QueueEnum.eq.value, embedder_id)
        # 精确查询字段
        if model_id:
            self.model_id = (QueueEnum.eq.value, model_id)
        # 精确查询字段
        if status:
            self.status = (QueueEnum.eq.value, status)
        # 模糊查询字段
        self.description = (QueueEnum.like.value, description)
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
