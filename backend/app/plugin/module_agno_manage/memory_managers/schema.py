# -*- coding: utf-8 -*-

from pydantic import BaseModel, ConfigDict, Field
from fastapi import Query
from datetime import datetime
from app.core.validator import DateTimeStr
from app.core.validator import DateTimeStr
from app.common.enums import QueueEnum
from app.core.base_schema import BaseSchema, UserBySchema

class AgMemoryManagerCreateSchema(BaseModel):
    """
    记忆管理新增模型
    """
    name: str = Field(default=..., description='记忆管理器名称')
    model_id: int = Field(default=..., description='关联模型ID（用于记忆处理）')
    delete_memories: bool = Field(default=..., description='是否允许删除记忆')
    update_memories: bool = Field(default=..., description='是否允许更新记忆')
    add_memories: bool = Field(default=..., description='是否允许新增记忆')
    clear_memories: bool = Field(default=..., description='是否允许清空记忆')
    memory_capture_instructions: str = Field(default=..., description='记忆捕获指令')
    additional_instructions: str = Field(default=..., description='附加指令')
    status: str = Field(default="0", description='')
    description: str | None = Field(default=None, max_length=255, description='')


class AgMemoryManagerUpdateSchema(AgMemoryManagerCreateSchema):
    """
    记忆管理更新模型
    """
    ...


class AgMemoryManagerOutSchema(AgMemoryManagerCreateSchema, BaseSchema, UserBySchema):
    """
    记忆管理响应模型
    """
    model_config = ConfigDict(from_attributes=True)


class AgMemoryManagerQueryParam:
    """记忆管理查询参数"""

    def __init__(
        self,
        name: str | None = Query(None, description="记忆管理器名称"),
        model_id: int | None = Query(None, description="关联模型ID（用于记忆处理）"),
        delete_memories: bool | None = Query(None, description="是否允许删除记忆"),
        update_memories: bool | None = Query(None, description="是否允许更新记忆"),
        add_memories: bool | None = Query(None, description="是否允许新增记忆"),
        clear_memories: bool | None = Query(None, description="是否允许清空记忆"),
        memory_capture_instructions: str | None = Query(None, description="记忆捕获指令"),
        additional_instructions: str | None = Query(None, description="附加指令"),
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
        if delete_memories:
            self.delete_memories = (QueueEnum.eq.value, delete_memories)
        # 精确查询字段
        if update_memories:
            self.update_memories = (QueueEnum.eq.value, update_memories)
        # 精确查询字段
        if add_memories:
            self.add_memories = (QueueEnum.eq.value, add_memories)
        # 精确查询字段
        if clear_memories:
            self.clear_memories = (QueueEnum.eq.value, clear_memories)
        # 精确查询字段
        if memory_capture_instructions:
            self.memory_capture_instructions = (QueueEnum.eq.value, memory_capture_instructions)
        # 精确查询字段
        if additional_instructions:
            self.additional_instructions = (QueueEnum.eq.value, additional_instructions)
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
