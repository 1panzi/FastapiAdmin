# -*- coding: utf-8 -*-

from datetime import datetime
from sqlalchemy import DateTime, Integer, Boolean, Text, String, JSON
from sqlalchemy.orm import Mapped, mapped_column

from app.core.base_model import ModelMixin, UserMixin


class AgTeamModel(ModelMixin, UserMixin):
    """
    Team管理表
    """
    __tablename__: str = 'ag_teams'
    __table_args__: dict[str, str] = {'comment': 'Team管理'}
    __loader_options__: list[str] = ["created_by", "updated_by"]

    name: Mapped[str | None] = mapped_column(String(255), nullable=True, comment='Team名称')
    model_id: Mapped[int | None] = mapped_column(Integer, nullable=True, comment='主模型ID')
    memory_manager_id: Mapped[int | None] = mapped_column(Integer, nullable=True, comment='记忆管理器ID')
    mode: Mapped[str | None] = mapped_column(String(20), nullable=True, comment='协作模式(route/coordinate/collaborate/tasks)')
    respond_directly: Mapped[bool | None] = mapped_column(Boolean, nullable=True, comment='是否直接响应（不经过协调）')
    delegate_to_all_members: Mapped[bool | None] = mapped_column(Boolean, nullable=True, comment='是否分发给所有成员')
    determine_input_for_members: Mapped[bool | None] = mapped_column(Boolean, nullable=True, comment='是否为成员决定输入内容')
    max_iterations: Mapped[int | None] = mapped_column(Integer, nullable=True, comment='最大迭代次数')
    instructions: Mapped[str | None] = mapped_column(Text, nullable=True, comment='Team指令')
    expected_output: Mapped[str | None] = mapped_column(Text, nullable=True, comment='期望输出格式说明')
    markdown: Mapped[bool | None] = mapped_column(Boolean, nullable=True, comment='是否输出Markdown格式')
    add_team_history_to_members: Mapped[bool | None] = mapped_column(Boolean, nullable=True, comment='是否将Team历史传给成员')
    num_team_history_runs: Mapped[int | None] = mapped_column(Integer, nullable=True, comment='传给成员的历史运行次数')
    share_member_interactions: Mapped[bool | None] = mapped_column(Boolean, nullable=True, comment='是否共享成员交互记录')
    add_member_tools_to_context: Mapped[bool | None] = mapped_column(Boolean, nullable=True, comment='是否将成员工具加入上下文')
    read_chat_history: Mapped[bool | None] = mapped_column(Boolean, nullable=True, comment='是否读取聊天历史')
    search_past_sessions: Mapped[bool | None] = mapped_column(Boolean, nullable=True, comment='是否搜索历史会话')
    num_past_sessions_to_search: Mapped[int | None] = mapped_column(Integer, nullable=True, comment='搜索历史会话数量')
    search_knowledge: Mapped[bool | None] = mapped_column(Boolean, nullable=True, comment='是否搜索知识库')
    update_knowledge: Mapped[bool | None] = mapped_column(Boolean, nullable=True, comment='是否允许更新知识库')
    enable_agentic_knowledge_filters: Mapped[bool | None] = mapped_column(Boolean, nullable=True, comment='是否开启智能知识过滤')
    enable_agentic_state: Mapped[bool | None] = mapped_column(Boolean, nullable=True, comment='是否开启智能状态')
    enable_agentic_memory: Mapped[bool | None] = mapped_column(Boolean, nullable=True, comment='是否开启智能记忆')
    update_memory_on_run: Mapped[bool | None] = mapped_column(Boolean, nullable=True, comment='是否每次运行后更新记忆')
    enable_session_summaries: Mapped[bool | None] = mapped_column(Boolean, nullable=True, comment='是否开启会话摘要')
    add_session_summary_to_context: Mapped[bool | None] = mapped_column(Boolean, nullable=True, comment='是否将会话摘要加入上下文')
    tool_call_limit: Mapped[int | None] = mapped_column(Integer, nullable=True, comment='工具调用次数上限')
    stream: Mapped[bool | None] = mapped_column(Boolean, nullable=True, comment='是否开启流式输出')
    stream_events: Mapped[bool | None] = mapped_column(Boolean, nullable=True, comment='是否流式推送事件')
    debug_mode: Mapped[bool | None] = mapped_column(Boolean, nullable=True, comment='是否开启调试模式')
    metadata_config: Mapped[dict | None] = mapped_column(JSON, nullable=True, comment='元数据')

