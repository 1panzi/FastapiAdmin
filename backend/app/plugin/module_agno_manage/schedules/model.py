
from sqlalchemy import JSON, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.base_model import ModelMixin, UserMixin


class AgScheduleModel(ModelMixin, UserMixin):
    """
    定时任务管理表
    """
    __tablename__: str = 'ag_schedules'
    __table_args__: dict[str, str] = {'comment': '定时任务管理'}
    __loader_options__: list[str] = ["created_by", "updated_by"]

    name: Mapped[str | None] = mapped_column(String(255), nullable=True, comment='定时任务名称')
    agent_id: Mapped[int | None] = mapped_column(Integer, nullable=True, comment='触发目标AgentID')
    team_id: Mapped[int | None] = mapped_column(Integer, nullable=True, comment='触发目标TeamID')
    payload: Mapped[dict | None] = mapped_column(JSON, nullable=True, comment='触发时传入的消息/参数')
    cron_expr: Mapped[str | None] = mapped_column(String(100), nullable=True, comment='Cron表达式（如0 9 * * 1-5）')
    timezone: Mapped[str | None] = mapped_column(String(100), nullable=True, comment='时区（如Asia/Shanghai）')
    timeout_seconds: Mapped[int | None] = mapped_column(Integer, nullable=True, comment='任务超时秒数')
    max_retries: Mapped[int | None] = mapped_column(Integer, nullable=True, comment='失败最大重试次数')
    retry_delay_seconds: Mapped[int | None] = mapped_column(Integer, nullable=True, comment='重试间隔秒数')
