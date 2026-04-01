# -*- coding: utf-8 -*-

from datetime import datetime
from sqlalchemy import DateTime, Text, Integer, JSON, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.base_model import ModelMixin, UserMixin


class AgLearningConfigModel(ModelMixin, UserMixin):
    """
    学习管理表
    """
    __tablename__: str = 'ag_learning_configs'
    __table_args__: dict[str, str] = {'comment': '学习管理'}
    __loader_options__: list[str] = ["created_by", "updated_by"]

    name: Mapped[str | None] = mapped_column(String(255), nullable=True, comment='学习机配置名称')
    model_id: Mapped[int | None] = mapped_column(Integer, nullable=True, comment='关联模型ID')
    namespace: Mapped[str | None] = mapped_column(String(255), nullable=True, comment='命名空间（用于隔离不同租户/场景的学习数据）')
    user_profile: Mapped[dict | None] = mapped_column(JSON, nullable=True, comment='用户画像配置（UserProfileConfig JSON）')
    user_memory: Mapped[dict | None] = mapped_column(JSON, nullable=True, comment='用户记忆配置（UserMemoryConfig JSON）')
    session_context: Mapped[dict | None] = mapped_column(JSON, nullable=True, comment='会话上下文配置（SessionContextConfig JSON）')
    entity_memory: Mapped[dict | None] = mapped_column(JSON, nullable=True, comment='实体记忆配置（EntityMemoryConfig JSON）')
    learned_knowledge: Mapped[dict | None] = mapped_column(JSON, nullable=True, comment='学习知识配置（LearnedKnowledgeConfig JSON）')
    decision_log: Mapped[dict | None] = mapped_column(JSON, nullable=True, comment='决策日志配置（DecisionLogConfig JSON）')

