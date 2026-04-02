
from sqlalchemy import JSON, Boolean, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.base_model import ModelMixin, UserMixin


class AgAgentModel(ModelMixin, UserMixin):
    """
    Agent管理表
    """
    __tablename__: str = 'ag_agents'
    __table_args__: dict[str, str] = {'comment': 'Agent管理'}
    __loader_options__: list[str] = ["created_by", "updated_by"]

    name: Mapped[str | None] = mapped_column(String(255), nullable=True, comment='Agent名称')
    model_id: Mapped[int | None] = mapped_column(Integer, nullable=True, comment='主模型ID')
    reasoning_model_id: Mapped[int | None] = mapped_column(Integer, nullable=True, comment='推理模型ID')
    output_model_id: Mapped[int | None] = mapped_column(Integer, nullable=True, comment='输出模型ID（response_model）')
    parser_model_id: Mapped[int | None] = mapped_column(Integer, nullable=True, comment='解析模型ID')
    memory_manager_id: Mapped[int | None] = mapped_column(Integer, nullable=True, comment='记忆管理器ID')
    learning_config_id: Mapped[int | None] = mapped_column(Integer, nullable=True, comment='学习机配置ID')
    reasoning_config_id: Mapped[int | None] = mapped_column(Integer, nullable=True, comment='推理配置ID')
    compression_config_id: Mapped[int | None] = mapped_column(Integer, nullable=True, comment='压缩管理器配置ID')
    session_summary_config_id: Mapped[int | None] = mapped_column(Integer, nullable=True, comment='会话摘要配置ID')
    culture_config_id: Mapped[int | None] = mapped_column(Integer, nullable=True, comment='文化管理器配置ID')
    instructions: Mapped[str | None] = mapped_column(Text, nullable=True, comment='Agent指令（system prompt）')
    expected_output: Mapped[str | None] = mapped_column(Text, nullable=True, comment='期望输出格式说明')
    additional_context: Mapped[str | None] = mapped_column(Text, nullable=True, comment='附加上下文')
    reasoning: Mapped[bool | None] = mapped_column(Boolean, nullable=True, comment='是否开启推理')
    reasoning_min_steps: Mapped[int | None] = mapped_column(Integer, nullable=True, comment='最少推理步数')
    reasoning_max_steps: Mapped[int | None] = mapped_column(Integer, nullable=True, comment='最多推理步数')
    learning: Mapped[bool | None] = mapped_column(Boolean, nullable=True, comment='是否开启学习')
    search_knowledge: Mapped[bool | None] = mapped_column(Boolean, nullable=True, comment='是否搜索知识库')
    update_knowledge: Mapped[bool | None] = mapped_column(Boolean, nullable=True, comment='是否允许更新知识库')
    add_knowledge_to_context: Mapped[bool | None] = mapped_column(Boolean, nullable=True, comment='是否将知识库内容加入上下文')
    enable_agentic_knowledge_filters: Mapped[bool | None] = mapped_column(Boolean, nullable=True, comment='是否开启智能知识过滤')
    enable_agentic_state: Mapped[bool | None] = mapped_column(Boolean, nullable=True, comment='是否开启智能状态')
    enable_agentic_memory: Mapped[bool | None] = mapped_column(Boolean, nullable=True, comment='是否开启智能记忆')
    update_memory_on_run: Mapped[bool | None] = mapped_column(Boolean, nullable=True, comment='是否每次运行后更新记忆')
    add_memories_to_context: Mapped[bool | None] = mapped_column(Boolean, nullable=True, comment='是否将记忆加入上下文')
    add_history_to_context: Mapped[bool | None] = mapped_column(Boolean, nullable=True, comment='是否将历史记录加入上下文')
    num_history_runs: Mapped[int | None] = mapped_column(Integer, nullable=True, comment='加入上下文的历史运行次数')
    num_history_messages: Mapped[int | None] = mapped_column(Integer, nullable=True, comment='加入上下文的历史消息数')
    search_past_sessions: Mapped[bool | None] = mapped_column(Boolean, nullable=True, comment='是否搜索历史会话')
    num_past_sessions_to_search: Mapped[int | None] = mapped_column(Integer, nullable=True, comment='搜索历史会话数量')
    enable_session_summaries: Mapped[bool | None] = mapped_column(Boolean, nullable=True, comment='是否开启会话摘要')
    add_session_summary_to_context: Mapped[bool | None] = mapped_column(Boolean, nullable=True, comment='是否将会话摘要加入上下文')
    tool_call_limit: Mapped[int | None] = mapped_column(Integer, nullable=True, comment='工具调用次数上限')
    tool_choice: Mapped[str | None] = mapped_column(String(50), nullable=True, comment='工具选择策略(none/auto/specific)')
    output_schema: Mapped[dict | None] = mapped_column(JSON, nullable=True, comment='输出结构体JSON Schema')
    input_schema: Mapped[dict | None] = mapped_column(JSON, nullable=True, comment='输入结构体JSON Schema')
    use_json_mode: Mapped[bool | None] = mapped_column(Boolean, nullable=True, comment='是否使用JSON输出模式')
    structured_outputs: Mapped[bool | None] = mapped_column(Boolean, nullable=True, comment='是否使用结构化输出')
    parse_response: Mapped[bool | None] = mapped_column(Boolean, nullable=True, comment='是否解析响应')
    retries: Mapped[int | None] = mapped_column(Integer, nullable=True, comment='失败重试次数')
    delay_between_retries: Mapped[int | None] = mapped_column(Integer, nullable=True, comment='重试间隔秒数')
    exponential_backoff: Mapped[bool | None] = mapped_column(Boolean, nullable=True, comment='是否指数退避重试')
    add_datetime_to_context: Mapped[bool | None] = mapped_column(Boolean, nullable=True, comment='是否将当前时间加入上下文')
    add_name_to_context: Mapped[bool | None] = mapped_column(Boolean, nullable=True, comment='是否将Agent名称加入上下文')
    compress_tool_results: Mapped[bool | None] = mapped_column(Boolean, nullable=True, comment='是否压缩工具结果')
    stream: Mapped[bool | None] = mapped_column(Boolean, nullable=True, comment='是否开启流式输出')
    stream_events: Mapped[bool | None] = mapped_column(Boolean, nullable=True, comment='是否流式推送事件')
    store_events: Mapped[bool | None] = mapped_column(Boolean, nullable=True, comment='是否存储事件')
    markdown: Mapped[bool | None] = mapped_column(Boolean, nullable=True, comment='是否输出Markdown格式')
    followups: Mapped[bool | None] = mapped_column(Boolean, nullable=True, comment='是否生成追问')
    num_followups: Mapped[int | None] = mapped_column(Integer, nullable=True, comment='追问数量')
    debug_mode: Mapped[bool | None] = mapped_column(Boolean, nullable=True, comment='是否开启调试模式')
    debug_level: Mapped[int | None] = mapped_column(Integer, nullable=True, comment='调试级别')
    a2a_enabled: Mapped[bool | None] = mapped_column(Boolean, nullable=True, comment='是否对外暴露A2A接口')
    is_remote: Mapped[bool | None] = mapped_column(Boolean, nullable=True, comment='是否为远程Agent')
    remote_url: Mapped[str | None] = mapped_column(String(500), nullable=True, comment='远程Agent地址')
    remote_agent_id: Mapped[str | None] = mapped_column(String(255), nullable=True, comment='远程Agent标识符')
    metadata_config: Mapped[dict | None] = mapped_column(JSON, nullable=True, comment='元数据')
