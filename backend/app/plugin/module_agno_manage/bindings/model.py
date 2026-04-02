
from sqlalchemy import JSON, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.base_model import ModelMixin, UserMixin


class AgBindingModel(ModelMixin, UserMixin):
    """
    资源绑定关系表
    """
    __tablename__: str = 'ag_bindings'
    __table_args__: dict[str, str] = {'comment': '资源绑定关系'}
    __loader_options__: list[str] = ["created_by", "updated_by"]

    owner_type: Mapped[str | None] = mapped_column(String(50), nullable=True, comment='拥有者类型(agent/team)')
    owner_id: Mapped[int | None] = mapped_column(Integer, nullable=True, comment='拥有者ID')
    resource_type: Mapped[str | None] = mapped_column(String(50), nullable=True, comment='资源类型(toolkit/skill/mcp/knowledge/hook/guardrail)')
    resource_id: Mapped[int | None] = mapped_column(Integer, nullable=True, comment='资源ID')
    priority: Mapped[int | None] = mapped_column(Integer, nullable=True, comment='优先级（数字小优先）')
    config_override: Mapped[dict | None] = mapped_column(JSON, nullable=True, comment='覆盖资源默认配置（如特定Agent使用不同API Key）')
