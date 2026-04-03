
from sqlalchemy import JSON, Integer, String, Boolean
from sqlalchemy.orm import Mapped, mapped_column

from app.core.base_model import ModelMixin, UserMixin


class AgKnowledgeBaseModel(ModelMixin, UserMixin):
    """
    知识库表
    """
    __tablename__: str = 'ag_knowledge_bases'
    __table_args__: dict[str, str] = {'comment': '知识库'}
    __loader_options__: list[str] = ["created_by", "updated_by"]

    name: Mapped[str | None] = mapped_column(String(255), nullable=True, comment='知识库名称')
    vectordb_id: Mapped[int | None] = mapped_column(Integer, nullable=True, comment='关联向量数据库ID')
    max_results: Mapped[int | None] = mapped_column(Integer, nullable=True, comment='最大检索结果数')
    isolate_vector_search: Mapped[bool | None] = mapped_column(Boolean, nullable=False, comment='是否启用向量搜索隔离（多知识库共享同一向量库时按name隔离）')
    reader_type: Mapped[str | None] = mapped_column(String(50), nullable=True, comment='文档读取器类型(pdf/web/docx/csv/json/text)')
    reader_config: Mapped[dict | None] = mapped_column(JSON, nullable=True, comment='读取器配置参数')
