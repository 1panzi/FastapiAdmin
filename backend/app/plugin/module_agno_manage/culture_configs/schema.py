# -*- coding: utf-8 -*-

from pydantic import BaseModel, ConfigDict, Field
from fastapi import Query
from datetime import datetime
from app.core.validator import DateTimeStr
from app.core.validator import DateTimeStr
from app.common.enums import QueueEnum
from app.core.base_schema import BaseSchema, UserBySchema

class AgCultureConfigCreateSchema(BaseModel):
    """
    文化配置新增模型
    """
    name: str = Field(default=..., description='文化配置名称')
    model_id: int = Field(default=..., description='关联模型ID')
    add_knowledge: bool = Field(default=..., description='是否允许新增知识')
    update_knowledge: bool = Field(default=..., description='是否允许更新知识')
    delete_knowledge: bool = Field(default=..., description='是否允许删除知识')
    clear_knowledge: bool = Field(default=..., description='是否允许清空知识')
    culture_capture_instructions: str = Field(default=..., description='文化捕获指令')
    additional_instructions: str = Field(default=..., description='附加指令')
    debug_mode: bool = Field(default=..., description='是否开启调试模式')
    status: str = Field(default="0", description='')
    description: str | None = Field(default=None, max_length=255, description='')


class AgCultureConfigUpdateSchema(AgCultureConfigCreateSchema):
    """
    文化配置更新模型
    """
    ...


class AgCultureConfigOutSchema(AgCultureConfigCreateSchema, BaseSchema, UserBySchema):
    """
    文化配置响应模型
    """
    model_config = ConfigDict(from_attributes=True)


class AgCultureConfigQueryParam:
    """文化配置查询参数"""

    def __init__(
        self,
        name: str | None = Query(None, description="文化配置名称"),
        model_id: int | None = Query(None, description="关联模型ID"),
        add_knowledge: bool | None = Query(None, description="是否允许新增知识"),
        update_knowledge: bool | None = Query(None, description="是否允许更新知识"),
        delete_knowledge: bool | None = Query(None, description="是否允许删除知识"),
        clear_knowledge: bool | None = Query(None, description="是否允许清空知识"),
        culture_capture_instructions: str | None = Query(None, description="文化捕获指令"),
        additional_instructions: str | None = Query(None, description="附加指令"),
        debug_mode: bool | None = Query(None, description="是否开启调试模式"),
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
        if add_knowledge:
            self.add_knowledge = (QueueEnum.eq.value, add_knowledge)
        # 精确查询字段
        if update_knowledge:
            self.update_knowledge = (QueueEnum.eq.value, update_knowledge)
        # 精确查询字段
        if delete_knowledge:
            self.delete_knowledge = (QueueEnum.eq.value, delete_knowledge)
        # 精确查询字段
        if clear_knowledge:
            self.clear_knowledge = (QueueEnum.eq.value, clear_knowledge)
        # 精确查询字段
        if culture_capture_instructions:
            self.culture_capture_instructions = (QueueEnum.eq.value, culture_capture_instructions)
        # 精确查询字段
        if additional_instructions:
            self.additional_instructions = (QueueEnum.eq.value, additional_instructions)
        # 精确查询字段
        if debug_mode:
            self.debug_mode = (QueueEnum.eq.value, debug_mode)
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
