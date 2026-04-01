# -*- coding: utf-8 -*-

from datetime import datetime
from sqlalchemy import Integer, DateTime, Text, Boolean, String, JSON
from sqlalchemy.orm import Mapped, mapped_column

from app.core.base_model import ModelMixin, UserMixin


class AgWorkflowModel(ModelMixin, UserMixin):
    """
    workflow管理表
    """
    __tablename__: str = 'ag_workflows'
    __table_args__: dict[str, str] = {'comment': 'workflow管理'}
    __loader_options__: list[str] = ["created_by", "updated_by"]

    name: Mapped[str | None] = mapped_column(String(255), nullable=True, comment='工作流名称')
    stream: Mapped[bool | None] = mapped_column(Boolean, nullable=True, comment='是否开启流式输出')
    stream_events: Mapped[bool | None] = mapped_column(Boolean, nullable=True, comment='是否流式推送事件')
    stream_executor_events: Mapped[bool | None] = mapped_column(Boolean, nullable=True, comment='是否流式推送执行器事件')
    store_events: Mapped[bool | None] = mapped_column(Boolean, nullable=True, comment='是否存储事件')
    store_executor_outputs: Mapped[bool | None] = mapped_column(Boolean, nullable=True, comment='是否存储执行器输出')
    add_workflow_history_to_steps: Mapped[bool | None] = mapped_column(Boolean, nullable=True, comment='是否将工作流历史传给步骤')
    num_history_runs: Mapped[int | None] = mapped_column(Integer, nullable=True, comment='传给步骤的历史运行次数')
    add_session_state_to_context: Mapped[bool | None] = mapped_column(Boolean, nullable=True, comment='是否将会话状态加入上下文')
    debug_mode: Mapped[bool | None] = mapped_column(Boolean, nullable=True, comment='是否开启调试模式')
    input_schema: Mapped[dict | None] = mapped_column(JSON, nullable=True, comment='输入结构体JSON Schema')
    metadata_config: Mapped[dict | None] = mapped_column(JSON, nullable=True, comment='元数据')

