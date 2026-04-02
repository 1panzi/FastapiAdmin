
from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.base_model import ModelMixin, UserMixin


class AgUserRoleModel(ModelMixin, UserMixin):
    """
    用户角色关联表
    """
    __tablename__: str = 'ag_user_roles'
    __table_args__: dict[str, str] = {'comment': '用户角色关联'}
    __loader_options__: list[str] = ["created_by", "updated_by"]

    user_id: Mapped[str | None] = mapped_column(String(255), nullable=True, comment='用户ID（来自外部Auth系统）')
    role_id: Mapped[int | None] = mapped_column(Integer, nullable=True, comment='角色ID')
