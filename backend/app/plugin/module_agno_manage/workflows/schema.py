

from fastapi import Query
from pydantic import BaseModel, ConfigDict, Field

from app.common.enums import QueueEnum
from app.core.base_schema import BaseSchema, UserBySchema
from app.core.validator import DateTimeStr


class AgWorkflowCreateSchema(BaseModel):
    """
    workflow管理新增模型
    """
    name: str = Field(default=..., description='工作流名称')
    stream: bool | None = Field(default=None, description='是否开启流式输出')
    stream_events: bool | None = Field(default=None, description='是否流式推送事件')
    stream_executor_events: bool | None = Field(default=None, description='是否流式推送执行器事件')
    store_events: bool | None = Field(default=None, description='是否存储事件')
    store_executor_outputs: bool | None = Field(default=None, description='是否存储执行器输出')
    add_workflow_history_to_steps: bool | None = Field(default=None, description='是否将工作流历史传给步骤')
    num_history_runs: int | None = Field(default=None, description='传给步骤的历史运行次数')
    add_session_state_to_context: bool | None = Field(default=None, description='是否将会话状态加入上下文')
    debug_mode: bool | None = Field(default=None, description='是否开启调试模式')
    input_schema: dict | None = Field(default=None, description='输入结构体JSON Schema')
    metadata_config: dict | None = Field(default=None, description='元数据')
    status: str = Field(default="0", description='')
    description: str | None = Field(default=None, max_length=255, description='')


class AgWorkflowUpdateSchema(AgWorkflowCreateSchema):
    """
    workflow管理更新模型
    """
    ...


class AgWorkflowOutSchema(AgWorkflowCreateSchema, BaseSchema, UserBySchema):
    """
    workflow管理响应模型
    """
    model_config = ConfigDict(from_attributes=True)


class AgWorkflowQueryParam:
    """workflow管理查询参数"""

    def __init__(
        self,
        name: str | None = Query(None, description="工作流名称'"),
        stream: bool | None = Query(None, description="是否开启流式输出"),
        stream_events: bool | None = Query(None, description="是否流式推送事件"),
        stream_executor_events: bool | None = Query(None, description="是否流式推送执行器事件"),
        store_events: bool | None = Query(None, description="是否存储事件"),
        store_executor_outputs: bool | None = Query(None, description="是否存储执行器输出"),
        add_workflow_history_to_steps: bool | None = Query(None, description="是否将工作流历史传给步骤"),
        num_history_runs: int | None = Query(None, description="传给步骤的历史运行次数"),
        add_session_state_to_context: bool | None = Query(None, description="是否将会话状态加入上下文"),
        debug_mode: bool | None = Query(None, description="是否开启调试模式"),
        # input_schema: dict | None = Query(None, description="输入结构体JSON Schema"),
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
        if stream:
            self.stream = (QueueEnum.eq.value, stream)
        # 精确查询字段
        if stream_events:
            self.stream_events = (QueueEnum.eq.value, stream_events)
        # 精确查询字段
        if stream_executor_events:
            self.stream_executor_events = (QueueEnum.eq.value, stream_executor_events)
        # 精确查询字段
        if store_events:
            self.store_events = (QueueEnum.eq.value, store_events)
        # 精确查询字段
        if store_executor_outputs:
            self.store_executor_outputs = (QueueEnum.eq.value, store_executor_outputs)
        # 精确查询字段
        if add_workflow_history_to_steps:
            self.add_workflow_history_to_steps = (QueueEnum.eq.value, add_workflow_history_to_steps)
        # 精确查询字段
        if num_history_runs:
            self.num_history_runs = (QueueEnum.eq.value, num_history_runs)
        # 精确查询字段
        if add_session_state_to_context:
            self.add_session_state_to_context = (QueueEnum.eq.value, add_session_state_to_context)
        # 精确查询字段
        if debug_mode:
            self.debug_mode = (QueueEnum.eq.value, debug_mode)
        # 精确查询字段
        # if input_schema:
        #     self.input_schema = (QueueEnum.eq.value, input_schema)
        # # 精确查询字段
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
