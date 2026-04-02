
from sqlalchemy import JSON, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.base_model import ModelMixin, UserMixin


class AgGuardrailModel(ModelMixin, UserMixin):
    """
    护栏表
    """
    __tablename__: str = 'ag_guardrails'
    __table_args__: dict[str, str] = {'comment': '护栏'}
    __loader_options__: list[str] = ["created_by", "updated_by"]

    name: Mapped[str | None] = mapped_column(String(255), nullable=True, comment='护栏名称')
    type: Mapped[str | None] = mapped_column(String(50), nullable=True, comment='护栏类型(openai_moderation/pii/prompt_injection/custom)')
    hook_type: Mapped[str | None] = mapped_column(String(20), nullable=True, comment='作用阶段(pre/post)')
    config: Mapped[dict | None] = mapped_column(JSON, nullable=True, comment='护栏配置参数')
    module_path: Mapped[str | None] = mapped_column(String(500), nullable=True, comment='自定义护栏模块路径（type=custom时使用）')
    class_name: Mapped[str | None] = mapped_column(String(255), nullable=True, comment='自定义护栏类名（type=custom时使用）')
