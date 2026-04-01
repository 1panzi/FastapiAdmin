# -*- coding: utf-8 -*-

from pydantic import BaseModel, ConfigDict, Field
from fastapi import Query
from app.core.validator import DateTimeStr
from datetime import datetime
from app.core.validator import DateTimeStr
from app.common.enums import QueueEnum
from app.core.base_schema import BaseSchema, UserBySchema

class AgTeamCreateSchema(BaseModel):
    """
    Team管理新增模型
    """
    name: str = Field(default=..., description='Team名称')
    model_id: int = Field(default=..., description='主模型ID')
    memory_manager_id: int = Field(default=..., description='记忆管理器ID')
    mode: str = Field(default=..., description='协作模式(route/coordinate/collaborate/tasks)')
    respond_directly: bool = Field(default=..., description='是否直接响应（不经过协调）')
    delegate_to_all_members: bool = Field(default=..., description='是否分发给所有成员')
    determine_input_for_members: bool = Field(default=..., description='是否为成员决定输入内容')
    max_iterations: int = Field(default=..., description='最大迭代次数')
    instructions: str = Field(default=..., description='Team指令')
    expected_output: str = Field(default=..., description='期望输出格式说明')
    markdown: bool = Field(default=..., description='是否输出Markdown格式')
    add_team_history_to_members: bool = Field(default=..., description='是否将Team历史传给成员')
    num_team_history_runs: int = Field(default=..., description='传给成员的历史运行次数')
    share_member_interactions: bool = Field(default=..., description='是否共享成员交互记录')
    add_member_tools_to_context: bool = Field(default=..., description='是否将成员工具加入上下文')
    read_chat_history: bool = Field(default=..., description='是否读取聊天历史')
    search_past_sessions: bool = Field(default=..., description='是否搜索历史会话')
    num_past_sessions_to_search: int = Field(default=..., description='搜索历史会话数量')
    search_knowledge: bool = Field(default=..., description='是否搜索知识库')
    update_knowledge: bool = Field(default=..., description='是否允许更新知识库')
    enable_agentic_knowledge_filters: bool = Field(default=..., description='是否开启智能知识过滤')
    enable_agentic_state: bool = Field(default=..., description='是否开启智能状态')
    enable_agentic_memory: bool = Field(default=..., description='是否开启智能记忆')
    update_memory_on_run: bool = Field(default=..., description='是否每次运行后更新记忆')
    enable_session_summaries: bool = Field(default=..., description='是否开启会话摘要')
    add_session_summary_to_context: bool = Field(default=..., description='是否将会话摘要加入上下文')
    tool_call_limit: int = Field(default=..., description='工具调用次数上限')
    stream: bool = Field(default=..., description='是否开启流式输出')
    stream_events: bool = Field(default=..., description='是否流式推送事件')
    debug_mode: bool = Field(default=..., description='是否开启调试模式')
    metadata_config: dict = Field(default=..., description='元数据')
    status: str = Field(default="0", description='')
    description: str | None = Field(default=None, max_length=255, description='')


class AgTeamUpdateSchema(AgTeamCreateSchema):
    """
    Team管理更新模型
    """
    ...


class AgTeamOutSchema(AgTeamCreateSchema, BaseSchema, UserBySchema):
    """
    Team管理响应模型
    """
    model_config = ConfigDict(from_attributes=True)


class AgTeamQueryParam:
    """Team管理查询参数"""

    def __init__(
        self,
        name: str | None = Query(None, description="Team名称"),
        model_id: int | None = Query(None, description="主模型ID"),
        memory_manager_id: int | None = Query(None, description="记忆管理器ID"),
        mode: str | None = Query(None, description="协作模式(route/coordinate/collaborate/tasks)"),
        respond_directly: bool | None = Query(None, description="是否直接响应（不经过协调）"),
        delegate_to_all_members: bool | None = Query(None, description="是否分发给所有成员"),
        determine_input_for_members: bool | None = Query(None, description="是否为成员决定输入内容"),
        max_iterations: int | None = Query(None, description="最大迭代次数"),
        instructions: str | None = Query(None, description="Team指令"),
        expected_output: str | None = Query(None, description="期望输出格式说明"),
        markdown: bool | None = Query(None, description="是否输出Markdown格式"),
        add_team_history_to_members: bool | None = Query(None, description="是否将Team历史传给成员"),
        num_team_history_runs: int | None = Query(None, description="传给成员的历史运行次数"),
        share_member_interactions: bool | None = Query(None, description="是否共享成员交互记录"),
        add_member_tools_to_context: bool | None = Query(None, description="是否将成员工具加入上下文"),
        read_chat_history: bool | None = Query(None, description="是否读取聊天历史"),
        search_past_sessions: bool | None = Query(None, description="是否搜索历史会话"),
        num_past_sessions_to_search: int | None = Query(None, description="搜索历史会话数量"),
        search_knowledge: bool | None = Query(None, description="是否搜索知识库"),
        update_knowledge: bool | None = Query(None, description="是否允许更新知识库"),
        enable_agentic_knowledge_filters: bool | None = Query(None, description="是否开启智能知识过滤"),
        enable_agentic_state: bool | None = Query(None, description="是否开启智能状态"),
        enable_agentic_memory: bool | None = Query(None, description="是否开启智能记忆"),
        update_memory_on_run: bool | None = Query(None, description="是否每次运行后更新记忆"),
        enable_session_summaries: bool | None = Query(None, description="是否开启会话摘要"),
        add_session_summary_to_context: bool | None = Query(None, description="是否将会话摘要加入上下文"),
        tool_call_limit: int | None = Query(None, description="工具调用次数上限"),
        stream: bool | None = Query(None, description="是否开启流式输出"),
        stream_events: bool | None = Query(None, description="是否流式推送事件"),
        debug_mode: bool | None = Query(None, description="是否开启调试模式"),
        # metadata_config: dict | None = Query(None, description="元数据"),
        status: str | None = Query(None, description=""),
        created_id: int | None = Query(None, description=""),
        updated_id: int | None = Query(None, description=""),
        created_time: list[DateTimeStr] | None = Query(None, description="创建时间范围", examples=["2025-01-01 00:00:00", "2025-12-31 23:59:59"]),
        updated_time: list[DateTimeStr] | None = Query(None, description="更新时间范围", examples=["2025-01-01 00:00:00", "2025-12-31 23:59:59"]),
    ) -> None:
        # 模糊查询字段
        self.name = (QueueEnum.like.value, name)
        # 精确查询字段
        if model_id:
            self.model_id = (QueueEnum.eq.value, model_id)
        # 精确查询字段
        if memory_manager_id:
            self.memory_manager_id = (QueueEnum.eq.value, memory_manager_id)
        # 精确查询字段
        if mode:
            self.mode = (QueueEnum.eq.value, mode)
        # 精确查询字段
        if respond_directly:
            self.respond_directly = (QueueEnum.eq.value, respond_directly)
        # 精确查询字段
        if delegate_to_all_members:
            self.delegate_to_all_members = (QueueEnum.eq.value, delegate_to_all_members)
        # 精确查询字段
        if determine_input_for_members:
            self.determine_input_for_members = (QueueEnum.eq.value, determine_input_for_members)
        # 精确查询字段
        if max_iterations:
            self.max_iterations = (QueueEnum.eq.value, max_iterations)
        # 精确查询字段
        if instructions:
            self.instructions = (QueueEnum.eq.value, instructions)
        # 精确查询字段
        if expected_output:
            self.expected_output = (QueueEnum.eq.value, expected_output)
        # 精确查询字段
        if markdown:
            self.markdown = (QueueEnum.eq.value, markdown)
        # 精确查询字段
        if add_team_history_to_members:
            self.add_team_history_to_members = (QueueEnum.eq.value, add_team_history_to_members)
        # 精确查询字段
        if num_team_history_runs:
            self.num_team_history_runs = (QueueEnum.eq.value, num_team_history_runs)
        # 精确查询字段
        if share_member_interactions:
            self.share_member_interactions = (QueueEnum.eq.value, share_member_interactions)
        # 精确查询字段
        if add_member_tools_to_context:
            self.add_member_tools_to_context = (QueueEnum.eq.value, add_member_tools_to_context)
        # 精确查询字段
        if read_chat_history:
            self.read_chat_history = (QueueEnum.eq.value, read_chat_history)
        # 精确查询字段
        if search_past_sessions:
            self.search_past_sessions = (QueueEnum.eq.value, search_past_sessions)
        # 精确查询字段
        if num_past_sessions_to_search:
            self.num_past_sessions_to_search = (QueueEnum.eq.value, num_past_sessions_to_search)
        # 精确查询字段
        if search_knowledge:
            self.search_knowledge = (QueueEnum.eq.value, search_knowledge)
        # 精确查询字段
        if update_knowledge:
            self.update_knowledge = (QueueEnum.eq.value, update_knowledge)
        # 精确查询字段
        if enable_agentic_knowledge_filters:
            self.enable_agentic_knowledge_filters = (QueueEnum.eq.value, enable_agentic_knowledge_filters)
        # 精确查询字段
        if enable_agentic_state:
            self.enable_agentic_state = (QueueEnum.eq.value, enable_agentic_state)
        # 精确查询字段
        if enable_agentic_memory:
            self.enable_agentic_memory = (QueueEnum.eq.value, enable_agentic_memory)
        # 精确查询字段
        if update_memory_on_run:
            self.update_memory_on_run = (QueueEnum.eq.value, update_memory_on_run)
        # 精确查询字段
        if enable_session_summaries:
            self.enable_session_summaries = (QueueEnum.eq.value, enable_session_summaries)
        # 精确查询字段
        if add_session_summary_to_context:
            self.add_session_summary_to_context = (QueueEnum.eq.value, add_session_summary_to_context)
        # 精确查询字段
        if tool_call_limit:
            self.tool_call_limit = (QueueEnum.eq.value, tool_call_limit)
        # 精确查询字段
        if stream:
            self.stream = (QueueEnum.eq.value, stream)
        # 精确查询字段
        if stream_events:
            self.stream_events = (QueueEnum.eq.value, stream_events)
        # 精确查询字段
        if debug_mode:
            self.debug_mode = (QueueEnum.eq.value, debug_mode)
        # 精确查询字段
        # if metadata_config:
        #     self.metadata_config = (QueueEnum.eq.value, metadata_config)
        # 精确查询字段
        if status:
            self.status = (QueueEnum.eq.value, status)
        # 精确查询字段
        if created_id:
            self.created_id = (QueueEnum.eq.value, created_id)
        # 精确查询字段
        if updated_id:
            self.updated_id = (QueueEnum.eq.value, updated_id)
        # 时间范围查询
        if created_time and len(created_time) == 2:
            self.created_time = (QueueEnum.between.value, (created_time[0], created_time[1]))
        if updated_time and len(updated_time) == 2:
            self.updated_time = (QueueEnum.between.value, (updated_time[0], updated_time[1]))
