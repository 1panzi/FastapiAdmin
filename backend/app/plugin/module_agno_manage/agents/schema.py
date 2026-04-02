

from fastapi import Query
from pydantic import BaseModel, ConfigDict, Field

from app.common.enums import QueueEnum
from app.core.base_schema import BaseSchema, UserBySchema
from app.core.validator import DateTimeStr


class AgAgentCreateSchema(BaseModel):
    """
    Agent管理新增模型
    """
    name: str = Field(default=..., description='Agent名称')
    model_id: int = Field(default=..., description='主模型ID')
    reasoning_model_id: int | None = Field(default=None, description='推理模型ID')
    output_model_id: int | None = Field(default=None, description='输出模型ID（response_model）')
    parser_model_id: int | None = Field(default=None, description='解析模型ID')
    memory_manager_id: int | None = Field(default=None, description='记忆管理器ID')
    learning_config_id: int | None = Field(default=None, description='学习机配置ID')
    reasoning_config_id: int | None = Field(default=None, description='推理配置ID')
    compression_config_id: int | None = Field(default=None, description='压缩管理器配置ID')
    session_summary_config_id: int | None = Field(default=None, description='会话摘要配置ID')
    culture_config_id: int | None = Field(default=None, description='文化管理器配置ID')
    instructions: str | None = Field(default=None, description='Agent指令（system prompt）')
    expected_output: str | None = Field(default=None, description='期望输出格式说明')
    additional_context: str | None = Field(default=None, description='附加上下文')
    reasoning: bool | None = Field(default=None, description='是否开启推理')
    reasoning_min_steps: int | None = Field(default=None, description='最少推理步数')
    reasoning_max_steps: int | None = Field(default=None, description='最多推理步数')
    learning: bool | None = Field(default=None, description='是否开启学习')
    search_knowledge: bool | None = Field(default=None, description='是否搜索知识库')
    update_knowledge: bool | None = Field(default=None, description='是否允许更新知识库')
    add_knowledge_to_context: bool | None = Field(default=None, description='是否将知识库内容加入上下文')
    enable_agentic_knowledge_filters: bool | None = Field(default=None, description='是否开启智能知识过滤')
    enable_agentic_state: bool | None = Field(default=None, description='是否开启智能状态')
    enable_agentic_memory: bool | None = Field(default=None, description='是否开启智能记忆')
    update_memory_on_run: bool | None = Field(default=None, description='是否每次运行后更新记忆')
    add_memories_to_context: bool | None = Field(default=None, description='是否将记忆加入上下文')
    add_history_to_context: bool | None = Field(default=None, description='是否将历史记录加入上下文')
    num_history_runs: int | None = Field(default=None, description='加入上下文的历史运行次数')
    num_history_messages: int | None = Field(default=None, description='加入上下文的历史消息数')
    search_past_sessions: bool | None = Field(default=None, description='是否搜索历史会话')
    num_past_sessions_to_search: int | None = Field(default=None, description='搜索历史会话数量')
    enable_session_summaries: bool | None = Field(default=None, description='是否开启会话摘要')
    add_session_summary_to_context: bool | None = Field(default=None, description='是否将会话摘要加入上下文')
    tool_call_limit: int | None = Field(default=None, description='工具调用次数上限')
    tool_choice: str | None = Field(default=None, description='工具选择策略(none/auto/specific)')
    output_schema: dict | None = Field(default=None, description='输出结构体JSON Schema')
    input_schema: dict | None = Field(default=None, description='输入结构体JSON Schema')
    use_json_mode: bool | None = Field(default=None, description='是否使用JSON输出模式')
    structured_outputs: bool | None = Field(default=None, description='是否使用结构化输出')
    parse_response: bool | None = Field(default=None, description='是否解析响应')
    retries: int | None = Field(default=None, description='失败重试次数')
    delay_between_retries: int | None = Field(default=None, description='重试间隔秒数')
    exponential_backoff: bool | None = Field(default=None, description='是否指数退避重试')
    add_datetime_to_context: bool | None = Field(default=None, description='是否将当前时间加入上下文')
    add_name_to_context: bool | None = Field(default=None, description='是否将Agent名称加入上下文')
    compress_tool_results: bool | None = Field(default=None, description='是否压缩工具结果')
    stream: bool | None = Field(default=None, description='是否开启流式输出')
    stream_events: bool | None = Field(default=None, description='是否流式推送事件')
    store_events: bool | None = Field(default=None, description='是否存储事件')
    markdown: bool | None = Field(default=None, description='是否输出Markdown格式')
    followups: bool | None = Field(default=None, description='是否生成追问')
    num_followups: int | None = Field(default=None, description='追问数量')
    debug_mode: bool | None = Field(default=None, description='是否开启调试模式')
    debug_level: int | None = Field(default=None, description='调试级别')
    a2a_enabled: bool | None = Field(default=None, description='是否对外暴露A2A接口')
    is_remote: bool | None = Field(default=None, description='是否为远程Agent')
    remote_url: str | None = Field(default=None, description='远程Agent地址')
    remote_agent_id: str | None = Field(default=None, description='远程Agent标识符')
    metadata_config: dict | None = Field(default=None, description='元数据')
    status: str = Field(default="0", description='')
    description: str | None = Field(default=None, max_length=255, description='')


class AgAgentUpdateSchema(AgAgentCreateSchema):
    """
    Agent管理更新模型
    """
    ...


class AgAgentOutSchema(AgAgentCreateSchema, BaseSchema, UserBySchema):
    """
    Agent管理响应模型
    """
    model_config = ConfigDict(from_attributes=True)


class AgAgentQueryParam:
    """Agent管理查询参数"""

    def __init__(
        self,
        name: str | None = Query(None, description="Agent名称"),
        model_id: int | None = Query(None, description="主模型ID"),
        reasoning_model_id: int | None = Query(None, description="推理模型ID"),
        output_model_id: int | None = Query(None, description="输出模型ID（response_model）"),
        parser_model_id: int | None = Query(None, description="解析模型ID"),
        memory_manager_id: int | None = Query(None, description="记忆管理器ID"),
        learning_config_id: int | None = Query(None, description="学习机配置ID"),
        reasoning_config_id: int | None = Query(None, description="推理配置ID"),
        compression_config_id: int | None = Query(None, description="压缩管理器配置ID"),
        session_summary_config_id: int | None = Query(None, description="会话摘要配置ID"),
        culture_config_id: int | None = Query(None, description="文化管理器配置ID"),
        instructions: str | None = Query(None, description="Agent指令（system prompt）"),
        expected_output: str | None = Query(None, description="期望输出格式说明"),
        additional_context: str | None = Query(None, description="附加上下文"),
        reasoning: bool | None = Query(None, description="是否开启推理"),
        reasoning_min_steps: int | None = Query(None, description="最少推理步数"),
        reasoning_max_steps: int | None = Query(None, description="最多推理步数"),
        learning: bool | None = Query(None, description="是否开启学习"),
        search_knowledge: bool | None = Query(None, description="是否搜索知识库"),
        update_knowledge: bool | None = Query(None, description="是否允许更新知识库"),
        add_knowledge_to_context: bool | None = Query(None, description="是否将知识库内容加入上下文"),
        enable_agentic_knowledge_filters: bool | None = Query(None, description="是否开启智能知识过滤"),
        enable_agentic_state: bool | None = Query(None, description="是否开启智能状态"),
        enable_agentic_memory: bool | None = Query(None, description="是否开启智能记忆"),
        update_memory_on_run: bool | None = Query(None, description="是否每次运行后更新记忆"),
        add_memories_to_context: bool | None = Query(None, description="是否将记忆加入上下文"),
        add_history_to_context: bool | None = Query(None, description="是否将历史记录加入上下文"),
        num_history_runs: int | None = Query(None, description="加入上下文的历史运行次数"),
        num_history_messages: int | None = Query(None, description="加入上下文的历史消息数"),
        search_past_sessions: bool | None = Query(None, description="是否搜索历史会话"),
        num_past_sessions_to_search: int | None = Query(None, description="搜索历史会话数量"),
        enable_session_summaries: bool | None = Query(None, description="是否开启会话摘要"),
        add_session_summary_to_context: bool | None = Query(None, description="是否将会话摘要加入上下文"),
        tool_call_limit: int | None = Query(None, description="工具调用次数上限"),
        tool_choice: str | None = Query(None, description="工具选择策略(none/auto/specific)"),
        # output_schema: dict | None = Query(None, description="输出结构体JSON Schema"),
        # input_schema: dict | None = Query(None, description="输入结构体JSON Schema"),
        use_json_mode: bool | None = Query(None, description="是否使用JSON输出模式"),
        structured_outputs: bool | None = Query(None, description="是否使用结构化输出"),
        parse_response: bool | None = Query(None, description="是否解析响应"),
        retries: int | None = Query(None, description="失败重试次数"),
        delay_between_retries: int | None = Query(None, description="重试间隔秒数"),
        exponential_backoff: bool | None = Query(None, description="是否指数退避重试"),
        add_datetime_to_context: bool | None = Query(None, description="是否将当前时间加入上下文"),
        add_name_to_context: bool | None = Query(None, description="是否将Agent名称加入上下文"),
        compress_tool_results: bool | None = Query(None, description="是否压缩工具结果"),
        stream: bool | None = Query(None, description="是否开启流式输出"),
        stream_events: bool | None = Query(None, description="是否流式推送事件"),
        store_events: bool | None = Query(None, description="是否存储事件"),
        markdown: bool | None = Query(None, description="是否输出Markdown格式"),
        followups: bool | None = Query(None, description="是否生成追问"),
        num_followups: int | None = Query(None, description="追问数量"),
        debug_mode: bool | None = Query(None, description="是否开启调试模式"),
        debug_level: int | None = Query(None, description="调试级别"),
        a2a_enabled: bool | None = Query(None, description="是否对外暴露A2A接口"),
        is_remote: bool | None = Query(None, description="是否为远程Agent"),
        remote_url: str | None = Query(None, description="远程Agent地址"),
        remote_agent_id: str | None = Query(None, description="远程Agent标识符"),
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
        if reasoning_model_id:
            self.reasoning_model_id = (QueueEnum.eq.value, reasoning_model_id)
        # 精确查询字段
        if output_model_id:
            self.output_model_id = (QueueEnum.eq.value, output_model_id)
        # 精确查询字段
        if parser_model_id:
            self.parser_model_id = (QueueEnum.eq.value, parser_model_id)
        # 精确查询字段
        if memory_manager_id:
            self.memory_manager_id = (QueueEnum.eq.value, memory_manager_id)
        # 精确查询字段
        if learning_config_id:
            self.learning_config_id = (QueueEnum.eq.value, learning_config_id)
        # 精确查询字段
        if reasoning_config_id:
            self.reasoning_config_id = (QueueEnum.eq.value, reasoning_config_id)
        # 精确查询字段
        if compression_config_id:
            self.compression_config_id = (QueueEnum.eq.value, compression_config_id)
        # 精确查询字段
        if session_summary_config_id:
            self.session_summary_config_id = (QueueEnum.eq.value, session_summary_config_id)
        # 精确查询字段
        if culture_config_id:
            self.culture_config_id = (QueueEnum.eq.value, culture_config_id)
        # 精确查询字段
        if instructions:
            self.instructions = (QueueEnum.eq.value, instructions)
        # 精确查询字段
        if expected_output:
            self.expected_output = (QueueEnum.eq.value, expected_output)
        # 精确查询字段
        if additional_context:
            self.additional_context = (QueueEnum.eq.value, additional_context)
        # 精确查询字段
        if reasoning:
            self.reasoning = (QueueEnum.eq.value, reasoning)
        # 精确查询字段
        if reasoning_min_steps:
            self.reasoning_min_steps = (QueueEnum.eq.value, reasoning_min_steps)
        # 精确查询字段
        if reasoning_max_steps:
            self.reasoning_max_steps = (QueueEnum.eq.value, reasoning_max_steps)
        # 精确查询字段
        if learning:
            self.learning = (QueueEnum.eq.value, learning)
        # 精确查询字段
        if search_knowledge:
            self.search_knowledge = (QueueEnum.eq.value, search_knowledge)
        # 精确查询字段
        if update_knowledge:
            self.update_knowledge = (QueueEnum.eq.value, update_knowledge)
        # 精确查询字段
        if add_knowledge_to_context:
            self.add_knowledge_to_context = (QueueEnum.eq.value, add_knowledge_to_context)
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
        if add_memories_to_context:
            self.add_memories_to_context = (QueueEnum.eq.value, add_memories_to_context)
        # 精确查询字段
        if add_history_to_context:
            self.add_history_to_context = (QueueEnum.eq.value, add_history_to_context)
        # 精确查询字段
        if num_history_runs:
            self.num_history_runs = (QueueEnum.eq.value, num_history_runs)
        # 精确查询字段
        if num_history_messages:
            self.num_history_messages = (QueueEnum.eq.value, num_history_messages)
        # 精确查询字段
        if search_past_sessions:
            self.search_past_sessions = (QueueEnum.eq.value, search_past_sessions)
        # 精确查询字段
        if num_past_sessions_to_search:
            self.num_past_sessions_to_search = (QueueEnum.eq.value, num_past_sessions_to_search)
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
        if tool_choice:
            self.tool_choice = (QueueEnum.eq.value, tool_choice)
        # 精确查询字段
        # if output_schema:
        #     self.output_schema = (QueueEnum.eq.value, output_schema)
        # # 精确查询字段
        # if input_schema:
        #     self.input_schema = (QueueEnum.eq.value, input_schema)
        # 精确查询字段
        if use_json_mode:
            self.use_json_mode = (QueueEnum.eq.value, use_json_mode)
        # 精确查询字段
        if structured_outputs:
            self.structured_outputs = (QueueEnum.eq.value, structured_outputs)
        # 精确查询字段
        if parse_response:
            self.parse_response = (QueueEnum.eq.value, parse_response)
        # 精确查询字段
        if retries:
            self.retries = (QueueEnum.eq.value, retries)
        # 精确查询字段
        if delay_between_retries:
            self.delay_between_retries = (QueueEnum.eq.value, delay_between_retries)
        # 精确查询字段
        if exponential_backoff:
            self.exponential_backoff = (QueueEnum.eq.value, exponential_backoff)
        # 精确查询字段
        if add_datetime_to_context:
            self.add_datetime_to_context = (QueueEnum.eq.value, add_datetime_to_context)
        # 精确查询字段
        if add_name_to_context:
            self.add_name_to_context = (QueueEnum.eq.value, add_name_to_context)
        # 精确查询字段
        if compress_tool_results:
            self.compress_tool_results = (QueueEnum.eq.value, compress_tool_results)
        # 精确查询字段
        if stream:
            self.stream = (QueueEnum.eq.value, stream)
        # 精确查询字段
        if stream_events:
            self.stream_events = (QueueEnum.eq.value, stream_events)
        # 精确查询字段
        if store_events:
            self.store_events = (QueueEnum.eq.value, store_events)
        # 精确查询字段
        if markdown:
            self.markdown = (QueueEnum.eq.value, markdown)
        # 精确查询字段
        if followups:
            self.followups = (QueueEnum.eq.value, followups)
        # 精确查询字段
        if num_followups:
            self.num_followups = (QueueEnum.eq.value, num_followups)
        # 精确查询字段
        if debug_mode:
            self.debug_mode = (QueueEnum.eq.value, debug_mode)
        # 精确查询字段
        if debug_level:
            self.debug_level = (QueueEnum.eq.value, debug_level)
        # 精确查询字段
        if a2a_enabled:
            self.a2a_enabled = (QueueEnum.eq.value, a2a_enabled)
        # 精确查询字段
        if is_remote:
            self.is_remote = (QueueEnum.eq.value, is_remote)
        # 精确查询字段
        if remote_url:
            self.remote_url = (QueueEnum.eq.value, remote_url)
        # 精确查询字段
        if remote_agent_id:
            self.remote_agent_id = (QueueEnum.eq.value, remote_agent_id)
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
