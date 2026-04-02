
from sqlalchemy import JSON, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.base_model import ModelMixin, UserMixin


class AgAuditLogModel(ModelMixin, UserMixin):
    """
    审计日志表
    """
    __tablename__: str = 'ag_audit_logs'
    __table_args__: dict[str, str] = {'comment': '审计日志'}
    __loader_options__: list[str] = ["created_by", "updated_by"]

    actor_id: Mapped[str | None] = mapped_column(String(255), nullable=True, comment='操作人ID')
    action: Mapped[str | None] = mapped_column(String(20), nullable=True, comment='操作类型(CREATE/UPDATE/DELETE/RUN)')
    resource_type: Mapped[str | None] = mapped_column(String(50), nullable=True, comment='资源类型')
    resource_id: Mapped[int | None] = mapped_column(Integer, nullable=True, comment='资源ID')
    diff: Mapped[dict | None] = mapped_column(JSON, nullable=True, comment='变更前后数据对比（JSON）')
    ip: Mapped[str | None] = mapped_column(String(50), nullable=True, comment='操作来源IP')
