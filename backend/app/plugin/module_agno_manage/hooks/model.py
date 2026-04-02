
from sqlalchemy import JSON, Boolean, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.base_model import ModelMixin, UserMixin


class AgHookModel(ModelMixin, UserMixin):
    """
    hook表
    """
    __tablename__: str = 'ag_hooks'
    __table_args__: dict[str, str] = {'comment': 'hook'}
    __loader_options__: list[str] = ["created_by", "updated_by"]

    name: Mapped[str | None] = mapped_column(String(255), nullable=True, comment='Hook名称')
    hook_type: Mapped[str | None] = mapped_column(String(20), nullable=True, comment='Hook类型(pre/post/tool)')
    module_path: Mapped[str | None] = mapped_column(String(500), nullable=True, comment='Python模块路径')
    func_name: Mapped[str | None] = mapped_column(String(255), nullable=True, comment='函数名')
    config: Mapped[dict | None] = mapped_column(JSON, nullable=True, comment='额外配置参数')
    run_in_background: Mapped[bool | None] = mapped_column(Boolean, nullable=True, comment='是否后台运行（不阻塞响应）')
