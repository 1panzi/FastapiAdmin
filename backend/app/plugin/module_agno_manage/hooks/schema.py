# -*- coding: utf-8 -*-

from pydantic import BaseModel, ConfigDict, Field
from fastapi import Query
from app.core.validator import DateTimeStr
from datetime import datetime
from app.core.validator import DateTimeStr
from app.common.enums import QueueEnum
from app.core.base_schema import BaseSchema, UserBySchema

class AgHookCreateSchema(BaseModel):
    """
    hook新增模型
    """
    name: str = Field(default=..., description='Hook名称')
    hook_type: str = Field(default=..., description='Hook类型(pre/post/tool)')
    module_path: str = Field(default=..., description='Python模块路径')
    func_name: str = Field(default=..., description='函数名')
    config: dict | None = Field(default=None, description='额外配置参数')
    run_in_background: bool | None = Field(default=None, description='是否后台运行（不阻塞响应）')
    status: str = Field(default="0", description='')
    description: str | None = Field(default=None, max_length=255, description='')


class AgHookUpdateSchema(AgHookCreateSchema):
    """
    hook更新模型
    """
    ...


class AgHookOutSchema(AgHookCreateSchema, BaseSchema, UserBySchema):
    """
    hook响应模型
    """
    model_config = ConfigDict(from_attributes=True)


class AgHookQueryParam:
    """hook查询参数"""

    def __init__(
        self,
        name: str | None = Query(None, description="Hook名称"),
        func_name: str | None = Query(None, description="函数名"),
        hook_type: str | None = Query(None, description="Hook类型(pre/post/tool)"),
        module_path: str | None = Query(None, description="Python模块路径"),
        # config: dict | None = Query(None, description="额外配置参数"),
        run_in_background: bool | None = Query(None, description="是否后台运行（不阻塞响应）"),
        status: str | None = Query(None, description=""),
        created_id: int | None = Query(None, description=""),
        updated_id: int | None = Query(None, description=""),
        created_time: list[DateTimeStr] | None = Query(None, description="创建时间范围", examples=["2025-01-01 00:00:00", "2025-12-31 23:59:59"]),
        updated_time: list[DateTimeStr] | None = Query(None, description="更新时间范围", examples=["2025-01-01 00:00:00", "2025-12-31 23:59:59"]),
    ) -> None:
        # 模糊查询字段
        self.name = (QueueEnum.like.value, name)
        # 精确查询字段
        if hook_type:
            self.hook_type = (QueueEnum.eq.value, hook_type)
        # 精确查询字段
        if module_path:
            self.module_path = (QueueEnum.eq.value, module_path)
        # 模糊查询字段
        self.func_name = (QueueEnum.like.value, func_name)
        # 精确查询字段
        # if config:
        #     self.config = (QueueEnum.eq.value, config)
        # 精确查询字段
        if run_in_background:
            self.run_in_background = (QueueEnum.eq.value, run_in_background)
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
