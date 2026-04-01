# -*- coding: utf-8 -*-

from pydantic import BaseModel, ConfigDict, Field
from fastapi import Query
from datetime import datetime
from app.core.validator import DateTimeStr
from app.core.validator import DateTimeStr
from app.common.enums import QueueEnum
from app.core.base_schema import BaseSchema, UserBySchema

class AgWorkflowNodeCreateSchema(BaseModel):
    """
    工作流节点新增模型
    """
    workflow_id: int = Field(default=..., description='所属工作流ID')
    parent_node_id: int | None = Field(default=None, description='父节点ID（NULL为顶层节点）')
    node_order: int | None = Field(default=None, description='节点顺序')
    node_type: str | None = Field(default=None, description='节点类型(step/condition/loop/parallel/router)')
    name: str = Field(default=..., description='节点名称')
    executor_type: str | None = Field(default=None, description='执行器类型(agent/team/custom)')
    agent_id: int | None = Field(default=None, description='联AgentID（executor_type=agent时）')
    team_id: int | None = Field(default=None, description='关联TeamID（executor_type=team时）')
    executor_module: str | None = Field(default=None, description='自定义执行器模块路径（executor_type=custom时）')
    add_workflow_history: bool | None = Field(default=None, description='是否传入工作流历史')
    num_history_runs: int | None = Field(default=None, description='传入历史运行次数')
    strict_input_validation: bool | None = Field(default=None, description='是否严格校验输入')
    max_retries: int | None = Field(default=None, description='最大重试次数')
    skip_on_failure: bool | None = Field(default=None, description='失败时是否跳过')
    evaluator_type: str | None = Field(default=None, description='条件评估器类型(bool/cel/function)')
    evaluator_value: str | None = Field(default=None, description='条件评估器值')
    branch: str | None = Field(default=None, description='分支标记(if/else)')
    max_iterations: int | None = Field(default=None, description='循环最大迭代次数')
    end_condition_type: str | None = Field(default=None, description='循环终止条件类型')
    end_condition_value: str | None = Field(default=None, description='循环终止条件值')
    forward_iteration_output: bool | None = Field(default=None, description='是否传递迭代输出')
    selector_type: str | None = Field(default=None, description='路由选择器类型')
    selector_value: str | None = Field(default=None, description='路由选择器值')
    allow_multiple_selections: bool | None = Field(default=None, description='是否允许多路由选择')
    requires_confirmation: bool | None = Field(default=None, description='是否需要用户确认（HITL）')
    confirmation_message: str | None = Field(default=None, description='确认提示消息')
    requires_user_input: bool | None = Field(default=None, description='是否需要用户输入（HITL）')
    user_input_message: str | None = Field(default=None, description='用户输入提示消息')
    user_input_schema: dict | None = Field(default=None, description='用户输入结构体Schema')
    on_reject: str | None = Field(default=None, description='用户拒绝时处理策略(skip/abort)')
    on_error: str | None = Field(default=None, description='节点出错时处理策略(skip/abort)')
    status: str = Field(default="0", description='')
    description: str | None = Field(default=None, max_length=255, description='')


class AgWorkflowNodeUpdateSchema(AgWorkflowNodeCreateSchema):
    """
    工作流节点更新模型
    """
    ...


class AgWorkflowNodeOutSchema(AgWorkflowNodeCreateSchema, BaseSchema, UserBySchema):
    """
    工作流节点响应模型
    """
    model_config = ConfigDict(from_attributes=True)


class AgWorkflowNodeQueryParam:
    """工作流节点查询参数"""

    def __init__(
        self,
        name: str | None = Query(None, description="节点名称"),
        workflow_id: int | None = Query(None, description="所属工作流ID"),
        parent_node_id: int | None = Query(None, description="父节点ID（NULL为顶层节点）"),
        node_order: int | None = Query(None, description="节点顺序"),
        node_type: str | None = Query(None, description="节点类型(step/condition/loop/parallel/router)"),
        executor_type: str | None = Query(None, description="执行器类型(agent/team/custom)"),
        agent_id: int | None = Query(None, description="联AgentID（executor_type=agent时）"),
        team_id: int | None = Query(None, description="关联TeamID（executor_type=team时）"),
        executor_module: str | None = Query(None, description="自定义执行器模块路径（executor_type=custom时）"),
        add_workflow_history: bool | None = Query(None, description="是否传入工作流历史"),
        num_history_runs: int | None = Query(None, description="传入历史运行次数"),
        strict_input_validation: bool | None = Query(None, description="是否严格校验输入"),
        max_retries: int | None = Query(None, description="最大重试次数"),
        skip_on_failure: bool | None = Query(None, description="失败时是否跳过"),
        evaluator_type: str | None = Query(None, description="条件评估器类型(bool/cel/function)"),
        evaluator_value: str | None = Query(None, description="条件评估器值"),
        branch: str | None = Query(None, description="分支标记(if/else)"),
        max_iterations: int | None = Query(None, description="循环最大迭代次数"),
        end_condition_type: str | None = Query(None, description="循环终止条件类型"),
        end_condition_value: str | None = Query(None, description="循环终止条件值"),
        forward_iteration_output: bool | None = Query(None, description="是否传递迭代输出"),
        selector_type: str | None = Query(None, description="路由选择器类型"),
        selector_value: str | None = Query(None, description="路由选择器值"),
        allow_multiple_selections: bool | None = Query(None, description="是否允许多路由选择"),
        requires_confirmation: bool | None = Query(None, description="是否需要用户确认（HITL）"),
        confirmation_message: str | None = Query(None, description="确认提示消息"),
        requires_user_input: bool | None = Query(None, description="是否需要用户输入（HITL）"),
        user_input_message: str | None = Query(None, description="用户输入提示消息"),
        # user_input_schema: dict | None = Query(None, description="用户输入结构体Schema"),
        on_reject: str | None = Query(None, description="用户拒绝时处理策略(skip/abort)"),
        on_error: str | None = Query(None, description="节点出错时处理策略(skip/abort)"),
        status: str | None = Query(None, description=""),
        created_id: int | None = Query(None, description=""),
        updated_id: int | None = Query(None, description=""),
        created_time: list[DateTimeStr] | None = Query(None, description="创建时间范围", examples=["2025-01-01 00:00:00", "2025-12-31 23:59:59"]),
        updated_time: list[DateTimeStr] | None = Query(None, description="更新时间范围", examples=["2025-01-01 00:00:00", "2025-12-31 23:59:59"]),
    ) -> None:
        # 精确查询字段
        if workflow_id:
            self.workflow_id = (QueueEnum.eq.value, workflow_id)
        # 精确查询字段
        if parent_node_id:
            self.parent_node_id = (QueueEnum.eq.value, parent_node_id)
        # 精确查询字段
        if node_order:
            self.node_order = (QueueEnum.eq.value, node_order)
        # 精确查询字段
        if node_type:
            self.node_type = (QueueEnum.eq.value, node_type)
        # 模糊查询字段
        self.name = (QueueEnum.like.value, name)
        # 精确查询字段
        if executor_type:
            self.executor_type = (QueueEnum.eq.value, executor_type)
        # 精确查询字段
        if agent_id:
            self.agent_id = (QueueEnum.eq.value, agent_id)
        # 精确查询字段
        if team_id:
            self.team_id = (QueueEnum.eq.value, team_id)
        # 精确查询字段
        if executor_module:
            self.executor_module = (QueueEnum.eq.value, executor_module)
        # 精确查询字段
        if add_workflow_history:
            self.add_workflow_history = (QueueEnum.eq.value, add_workflow_history)
        # 精确查询字段
        if num_history_runs:
            self.num_history_runs = (QueueEnum.eq.value, num_history_runs)
        # 精确查询字段
        if strict_input_validation:
            self.strict_input_validation = (QueueEnum.eq.value, strict_input_validation)
        # 精确查询字段
        if max_retries:
            self.max_retries = (QueueEnum.eq.value, max_retries)
        # 精确查询字段
        if skip_on_failure:
            self.skip_on_failure = (QueueEnum.eq.value, skip_on_failure)
        # 精确查询字段
        if evaluator_type:
            self.evaluator_type = (QueueEnum.eq.value, evaluator_type)
        # 精确查询字段
        if evaluator_value:
            self.evaluator_value = (QueueEnum.eq.value, evaluator_value)
        # 精确查询字段
        if branch:
            self.branch = (QueueEnum.eq.value, branch)
        # 精确查询字段
        if max_iterations:
            self.max_iterations = (QueueEnum.eq.value, max_iterations)
        # 精确查询字段
        if end_condition_type:
            self.end_condition_type = (QueueEnum.eq.value, end_condition_type)
        # 精确查询字段
        if end_condition_value:
            self.end_condition_value = (QueueEnum.eq.value, end_condition_value)
        # 精确查询字段
        if forward_iteration_output:
            self.forward_iteration_output = (QueueEnum.eq.value, forward_iteration_output)
        # 精确查询字段
        if selector_type:
            self.selector_type = (QueueEnum.eq.value, selector_type)
        # 精确查询字段
        if selector_value:
            self.selector_value = (QueueEnum.eq.value, selector_value)
        # 精确查询字段
        if allow_multiple_selections:
            self.allow_multiple_selections = (QueueEnum.eq.value, allow_multiple_selections)
        # 精确查询字段
        if requires_confirmation:
            self.requires_confirmation = (QueueEnum.eq.value, requires_confirmation)
        # 精确查询字段
        if confirmation_message:
            self.confirmation_message = (QueueEnum.eq.value, confirmation_message)
        # 精确查询字段
        if requires_user_input:
            self.requires_user_input = (QueueEnum.eq.value, requires_user_input)
        # 精确查询字段
        if user_input_message:
            self.user_input_message = (QueueEnum.eq.value, user_input_message)
        # 精确查询字段
        # if user_input_schema:
        #     self.user_input_schema = (QueueEnum.eq.value, user_input_schema)
        # 精确查询字段
        if on_reject:
            self.on_reject = (QueueEnum.eq.value, on_reject)
        # 精确查询字段
        if on_error:
            self.on_error = (QueueEnum.eq.value, on_error)
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
