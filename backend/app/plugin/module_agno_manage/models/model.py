# -*- coding: utf-8 -*-

from datetime import datetime
from sqlalchemy import String, DateTime, JSON, Text, Integer
from sqlalchemy.orm import Mapped, mapped_column

from app.core.base_model import ModelMixin, UserMixin


class AgModelModel(ModelMixin, UserMixin):
    """
    模型管理表
    """
    __tablename__: str = 'ag_models'
    __table_args__: dict[str, str] = {'comment': '模型管理'}
    __loader_options__: list[str] = ["created_by", "updated_by"]

    name: Mapped[str | None] = mapped_column(String(255), nullable=True, comment='模型名称')
    model_id: Mapped[str | None] = mapped_column(String(255), nullable=True, comment='模型标识符（传给Agno Model的id参数）')
    provider: Mapped[str | None] = mapped_column(String(50), nullable=True, comment='模型提供商(openai/anthropic/google/ollama/deepseek)')
    api_key: Mapped[str | None] = mapped_column(Text, nullable=True, comment='API密钥（明文存储）')
    base_url: Mapped[str | None] = mapped_column(String(500), nullable=True, comment='自定义API地址（用于ollama/vllm/lmstudio）')
    config: Mapped[dict | None] = mapped_column(JSON, nullable=True, comment='模型配置参数（temperature/max_tokens/top_p等）')

