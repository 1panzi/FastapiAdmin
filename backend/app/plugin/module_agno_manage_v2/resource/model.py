
from sqlalchemy import JSON, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.base_model import ModelMixin, UserMixin


class AgResourceModel(ModelMixin, UserMixin):
    """
    AI资源统一管理表（v2）
    一张表管所有资源类型：model/embedder/reader/toolkit/knowledge/agent/team
    """
    __tablename__: str = 'ag_resources'
    __table_args__: dict[str, str] = {'comment': 'AI资源统一管理表（v2）'}
    __loader_options__: list[str] = ["created_by", "updated_by"]

    name: Mapped[str] = mapped_column(
        String(255), nullable=False, comment='资源名称'
    )
    category: Mapped[str] = mapped_column(
        String(50), nullable=False,
        comment='资源大类(model/embedder/reader/toolkit/knowledge/agent/team)'
    )
    type: Mapped[str] = mapped_column(
        String(50), nullable=False,
        comment='具体类型(openai/pdf/duckduckgo/base等)'
    )
    config: Mapped[dict] = mapped_column(
        JSON, nullable=False, default=dict,
        comment='资源配置（支持ref引用或inline内联）'
    )
    # status 字段继承自 ModelMixin（"0":启用 "1":禁用）
    # description 字段继承自 ModelMixin
