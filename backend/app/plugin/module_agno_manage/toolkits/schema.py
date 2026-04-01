# -*- coding: utf-8 -*-

from pydantic import BaseModel, ConfigDict, Field
from fastapi import Query
from datetime import datetime
from app.core.validator import DateTimeStr
from app.common.enums import QueueEnum
from app.core.base_schema import BaseSchema, UserBySchema

class AgToolkitCreateSchema(BaseModel):
    """
    工具管理新增模型
    """
    name: str = Field(default=..., description='工具包名称')
    type: str = Field(default=..., description='类型(toolkit:整个类 function:单个函数)')
    module_path: str = Field(default=..., description='Python模块路径')
    class_name: str = Field(default=..., description='类名（type=toolkit时使用）')
    func_name: str = Field(default=..., description='函数名（type=function时使用）')
    config: dict = Field(default=..., description='初始化参数')
    instructions: str = Field(default=..., description='工具使用说明')
    requires_confirmation: bool = Field(default=..., description='是否需要确认')
    approval_type: str = Field(default=..., description='审批类型(NULL/required/audit)')
    stop_after_call: bool = Field(default=..., description='调用后是否停止')
    show_result: bool = Field(default=..., description='是否展示结果')
    cache_results: bool = Field(default=..., description='是否缓存结果')
    cache_ttl: int = Field(default=..., description='缓存TTL秒数')
    status: str = Field(default="0", description='')
    description: str | None = Field(default=None, max_length=255, description='')


class AgToolkitUpdateSchema(AgToolkitCreateSchema):
    """
    工具管理更新模型
    """
    ...


class AgToolkitOutSchema(AgToolkitCreateSchema, BaseSchema, UserBySchema):
    """
    工具管理响应模型
    """
    model_config = ConfigDict(from_attributes=True)


class AgToolkitQueryParam:
    """工具管理查询参数"""

    def __init__(
        self,
        name: str | None = Query(None, description="工具包名称"),
        class_name: str | None = Query(None, description="类名（type=toolkit时使用）"),
        func_name: str | None = Query(None, description="函数名（type=function时使用）"),
        type: str | None = Query(None, description="类型(toolkit:整个类 function:单个函数)"),
        module_path: str | None = Query(None, description="Python模块路径"),
        # config: dict | None = Query(None, description="初始化参数"),
        instructions: str | None = Query(None, description="工具使用说明"),
        requires_confirmation: bool | None = Query(None, description="是否需要确认"),
        approval_type: str | None = Query(None, description="审批类型(NULL/required/audit)"),
        stop_after_call: bool | None = Query(None, description="调用后是否停止"),
        show_result: bool | None = Query(None, description="是否展示结果"),
        cache_results: bool | None = Query(None, description="是否缓存结果"),
        cache_ttl: int | None = Query(None, description="缓存TTL秒数"),
        status: str | None = Query(None, description=""),
        created_id: int | None = Query(None, description=""),
        updated_id: int | None = Query(None, description=""),
        created_time: list[DateTimeStr] | None = Query(None, description="创建时间范围", examples=["2025-01-01 00:00:00", "2025-12-31 23:59:59"]),
        updated_time: list[DateTimeStr] | None = Query(None, description="更新时间范围", examples=["2025-01-01 00:00:00", "2025-12-31 23:59:59"]),
    ) -> None:
        # 模糊查询字段
        self.name = (QueueEnum.like.value, name)
        # 精确查询字段
        if type:
            self.type = (QueueEnum.eq.value, type)
        # 精确查询字段
        if module_path:
            self.module_path = (QueueEnum.eq.value, module_path)
        # 模糊查询字段
        self.class_name = (QueueEnum.like.value, class_name)
        # 模糊查询字段
        self.func_name = (QueueEnum.like.value, func_name)
        # 精确查询字段
        # if config:
        #     self.config = (QueueEnum.eq.value, config)
        # 精确查询字段
        if instructions:
            self.instructions = (QueueEnum.eq.value, instructions)
        # 精确查询字段
        if requires_confirmation:
            self.requires_confirmation = (QueueEnum.eq.value, requires_confirmation)
        # 精确查询字段
        if approval_type:
            self.approval_type = (QueueEnum.eq.value, approval_type)
        # 精确查询字段
        if stop_after_call:
            self.stop_after_call = (QueueEnum.eq.value, stop_after_call)
        # 精确查询字段
        if show_result:
            self.show_result = (QueueEnum.eq.value, show_result)
        # 精确查询字段
        if cache_results:
            self.cache_results = (QueueEnum.eq.value, cache_results)
        # 精确查询字段
        if cache_ttl:
            self.cache_ttl = (QueueEnum.eq.value, cache_ttl)
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
