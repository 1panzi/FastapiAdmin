
from sqlalchemy import Integer, String, Boolean
from sqlalchemy.orm import Mapped, mapped_column

from app.core.base_model import ModelMixin, UserMixin


class AgKnowledgeBaseModel(ModelMixin, UserMixin):
    """
    知识库表

    readers 通过 ag_bindings (owner_type='knowledge', resource_type='reader') 关联
    """
    __tablename__: str = 'ag_knowledge_bases'
    __table_args__: dict[str, str] = {'comment': '知识库'}
    __loader_options__: list[str] = ["created_by", "updated_by"]

    name: Mapped[str | None] = mapped_column(String(255), nullable=True, comment='知识库名称')
    vectordb_id: Mapped[int | None] = mapped_column(Integer, nullable=True, comment='关联向量数据库ID')
    max_results: Mapped[int | None] = mapped_column(Integer, nullable=True, default=10, comment='检索返回最大条数')
    isolate_vector_search: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, comment='向量搜索隔离：多知识库共享同一向量库时按name字段过滤，避免内容混淆')
