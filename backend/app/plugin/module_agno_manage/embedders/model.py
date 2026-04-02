
from sqlalchemy import JSON, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.base_model import ModelMixin, UserMixin


class AgEmbedderModel(ModelMixin, UserMixin):
    """
    嵌入模型表
    """
    __tablename__: str = 'ag_embedders'
    __table_args__: dict[str, str] = {'comment': '嵌入模型'}
    __loader_options__: list[str] = ["created_by", "updated_by"]

    name: Mapped[str | None] = mapped_column(String(255), nullable=True, comment='嵌入器名称')
    provider: Mapped[str | None] = mapped_column(String(50), nullable=True, comment='提供商')
    model_id: Mapped[str | None] = mapped_column(String(255), nullable=True, comment='嵌入模型标识')
    api_key: Mapped[str | None] = mapped_column(Text, nullable=True, comment='API密钥')
    base_url: Mapped[str | None] = mapped_column(String(500), nullable=True, comment='自定义端点地址')
    dimensions: Mapped[int | None] = mapped_column(Integer, nullable=True, comment='向量维度')
    config: Mapped[dict | None] = mapped_column(JSON, nullable=True, comment='其他构造参数')
