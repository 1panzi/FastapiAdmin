# -*- coding: utf-8 -*-

from pydantic import BaseModel, ConfigDict, Field
from fastapi import Query
from datetime import datetime
from app.core.validator import DateTimeStr
from app.core.validator import DateTimeStr
from app.common.enums import QueueEnum
from app.core.base_schema import BaseSchema, UserBySchema

class AgSkillCreateSchema(BaseModel):
    """
    技能管理新增模型
    """
    name: str = Field(default=..., description='技能名称')
    instructions: str | None = Field(default=None, description='注入Agent system prompt的技能指令')
    source_path: str | None = Field(default=None, description='本地磁盘路径（可选）')
    scripts: dict | None = Field(default=None, description='脚本文件名列表')
    references: dict | None = Field(default=None, description='参考文件名列表')
    allowed_tools: dict | None = Field(default=None, description='允许使用的工具列表')
    metadata_config: dict | None = Field(default=None, description='元数据')
    status: str = Field(default="0", description='')
    description: str | None = Field(default=None, max_length=255, description='')


class AgSkillUpdateSchema(AgSkillCreateSchema):
    """
    技能管理更新模型
    """
    ...


class AgSkillOutSchema(AgSkillCreateSchema, BaseSchema, UserBySchema):
    """
    技能管理响应模型
    """
    model_config = ConfigDict(from_attributes=True)


class AgSkillQueryParam:
    """技能管理查询参数"""

    def __init__(
        self,
        name: str | None = Query(None, description="技能名称"),
        instructions: str | None = Query(None, description="注入Agent system prompt的技能指令"),
        source_path: str | None = Query(None, description="本地磁盘路径（可选）"),
        # scripts: dict | None = Query(None, description="脚本文件名列表"),
        # references: dict | None = Query(None, description="参考文件名列表"),
        # allowed_tools: dict | None = Query(None, description="允许使用的工具列表"),
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
        if instructions:
            self.instructions = (QueueEnum.eq.value, instructions)
        # 精确查询字段
        if source_path:
            self.source_path = (QueueEnum.eq.value, source_path)
        # 精确查询字段
        # if scripts:
        #     self.scripts = (QueueEnum.eq.value, scripts)
        # # 精确查询字段
        # if references:
        #     self.references = (QueueEnum.eq.value, references)
        # # 精确查询字段
        # if allowed_tools:
        #     self.allowed_tools = (QueueEnum.eq.value, allowed_tools)
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
