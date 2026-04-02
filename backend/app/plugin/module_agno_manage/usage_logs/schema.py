
from decimal import Decimal

from fastapi import Query
from pydantic import BaseModel, ConfigDict, Field

from app.common.enums import QueueEnum
from app.core.base_schema import BaseSchema, UserBySchema
from app.core.validator import DateTimeStr


class AgUsageLogCreateSchema(BaseModel):
    """
    用量日志新增模型
    """
    agent_id: int = Field(default=..., description='关联AgentID')
    user_id: str = Field(default=..., description='用户ID')
    session_id: str = Field(default=..., description='会话ID')
    model_id: int = Field(default=..., description='关联模型ID')
    input_tokens: int = Field(default=..., description='输入Token数')
    output_tokens: int = Field(default=..., description='输出Token数')
    cost_usd: Decimal = Field(default=..., description='本次调用费用（美元）')
    latency_ms: int = Field(default=..., description='首Token延迟毫秒数')


class AgUsageLogUpdateSchema(AgUsageLogCreateSchema):
    """
    用量日志更新模型
    """
    ...


class AgUsageLogOutSchema(AgUsageLogCreateSchema, BaseSchema, UserBySchema):
    """
    用量日志响应模型
    """
    model_config = ConfigDict(from_attributes=True)


class AgUsageLogQueryParam:
    """用量日志查询参数"""

    def __init__(
        self,
        agent_id: int | None = Query(None, description="关联AgentID"),
        user_id: str | None = Query(None, description="用户ID"),
        session_id: str | None = Query(None, description="会话ID"),
        model_id: int | None = Query(None, description="关联模型ID"),
        input_tokens: int | None = Query(None, description="输入Token数"),
        output_tokens: int | None = Query(None, description="输出Token数"),
        cost_usd: Decimal | None = Query(None, description="本次调用费用（美元）"),
        latency_ms: int | None = Query(None, description="首Token延迟毫秒数"),
        created_time: list[DateTimeStr] | None = Query(None, description="创建时间范围", examples=["2025-01-01 00:00:00", "2025-12-31 23:59:59"]),
        updated_time: list[DateTimeStr] | None = Query(None, description="更新时间范围", examples=["2025-01-01 00:00:00", "2025-12-31 23:59:59"]),
    ) -> None:
        # 精确查询字段
        if agent_id:
            self.agent_id = (QueueEnum.eq.value, agent_id)
        # 精确查询字段
        if user_id:
            self.user_id = (QueueEnum.eq.value, user_id)
        # 精确查询字段
        if session_id:
            self.session_id = (QueueEnum.eq.value, session_id)
        # 精确查询字段
        if model_id:
            self.model_id = (QueueEnum.eq.value, model_id)
        # 精确查询字段
        if input_tokens:
            self.input_tokens = (QueueEnum.eq.value, input_tokens)
        # 精确查询字段
        if output_tokens:
            self.output_tokens = (QueueEnum.eq.value, output_tokens)
        # 精确查询字段
        if cost_usd:
            self.cost_usd = (QueueEnum.eq.value, cost_usd)
        # 精确查询字段
        if latency_ms:
            self.latency_ms = (QueueEnum.eq.value, latency_ms)
        # 时间范围查询
        if created_time and len(created_time) == 2:
            self.created_time = (QueueEnum.between.value, (created_time[0], created_time[1]))
        if updated_time and len(updated_time) == 2:
            self.updated_time = (QueueEnum.between.value, (updated_time[0], updated_time[1]))
