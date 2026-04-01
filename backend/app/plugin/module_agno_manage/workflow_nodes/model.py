# -*- coding: utf-8 -*-

from datetime import datetime
from sqlalchemy import String, Integer, Text, JSON, DateTime, Boolean
from sqlalchemy.orm import Mapped, mapped_column

from app.core.base_model import ModelMixin, UserMixin


class AgWorkflowNodeModel(ModelMixin, UserMixin):
    """
    工作流节点表
    """
    __tablename__: str = 'ag_workflow_nodes'
    __table_args__: dict[str, str] = {'comment': '工作流节点'}
    __loader_options__: list[str] = ["created_by", "updated_by"]

    workflow_id: Mapped[int | None] = mapped_column(Integer, nullable=True, comment='所属工作流ID')
    parent_node_id: Mapped[int | None] = mapped_column(Integer, nullable=True, comment='父节点ID（NULL为顶层节点）')
    node_order: Mapped[int | None] = mapped_column(Integer, nullable=True, comment='节点顺序')
    node_type: Mapped[str | None] = mapped_column(String(20), nullable=True, comment='节点类型(step/condition/loop/parallel/router)')
    name: Mapped[str | None] = mapped_column(String(255), nullable=True, comment='节点名称')
    executor_type: Mapped[str | None] = mapped_column(String(20), nullable=True, comment='执行器类型(agent/team/custom)')
    agent_id: Mapped[int | None] = mapped_column(Integer, nullable=True, comment='联AgentID（executor_type=agent时）')
    team_id: Mapped[int | None] = mapped_column(Integer, nullable=True, comment='关联TeamID（executor_type=team时）')
    executor_module: Mapped[str | None] = mapped_column(String(500), nullable=True, comment='自定义执行器模块路径（executor_type=custom时）')
    add_workflow_history: Mapped[bool | None] = mapped_column(Boolean, nullable=True, comment='是否传入工作流历史')
    num_history_runs: Mapped[int | None] = mapped_column(Integer, nullable=True, comment='传入历史运行次数')
    strict_input_validation: Mapped[bool | None] = mapped_column(Boolean, nullable=True, comment='是否严格校验输入')
    max_retries: Mapped[int | None] = mapped_column(Integer, nullable=True, comment='最大重试次数')
    skip_on_failure: Mapped[bool | None] = mapped_column(Boolean, nullable=True, comment='失败时是否跳过')
    evaluator_type: Mapped[str | None] = mapped_column(String(20), nullable=True, comment='条件评估器类型(bool/cel/function)')
    evaluator_value: Mapped[str | None] = mapped_column(Text, nullable=True, comment='条件评估器值')
    branch: Mapped[str | None] = mapped_column(String(10), nullable=True, comment='分支标记(if/else)')
    max_iterations: Mapped[int | None] = mapped_column(Integer, nullable=True, comment='循环最大迭代次数')
    end_condition_type: Mapped[str | None] = mapped_column(String(20), nullable=True, comment='循环终止条件类型')
    end_condition_value: Mapped[str | None] = mapped_column(Text, nullable=True, comment='循环终止条件值')
    forward_iteration_output: Mapped[bool | None] = mapped_column(Boolean, nullable=True, comment='是否传递迭代输出')
    selector_type: Mapped[str | None] = mapped_column(String(20), nullable=True, comment='路由选择器类型')
    selector_value: Mapped[str | None] = mapped_column(Text, nullable=True, comment='路由选择器值')
    allow_multiple_selections: Mapped[bool | None] = mapped_column(Boolean, nullable=True, comment='是否允许多路由选择')
    requires_confirmation: Mapped[bool | None] = mapped_column(Boolean, nullable=True, comment='是否需要用户确认（HITL）')
    confirmation_message: Mapped[str | None] = mapped_column(Text, nullable=True, comment='确认提示消息')
    requires_user_input: Mapped[bool | None] = mapped_column(Boolean, nullable=True, comment='是否需要用户输入（HITL）')
    user_input_message: Mapped[str | None] = mapped_column(Text, nullable=True, comment='用户输入提示消息')
    user_input_schema: Mapped[dict | None] = mapped_column(JSON, nullable=True, comment='用户输入结构体Schema')
    on_reject: Mapped[str | None] = mapped_column(String(20), nullable=True, comment='用户拒绝时处理策略(skip/abort)')
    on_error: Mapped[str | None] = mapped_column(String(20), nullable=True, comment='节点出错时处理策略(skip/abort)')

