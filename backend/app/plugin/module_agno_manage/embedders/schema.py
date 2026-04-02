

from fastapi import Query
from pydantic import BaseModel, ConfigDict, Field

from app.common.enums import QueueEnum
from app.core.base_schema import BaseSchema, UserBySchema
from app.core.validator import DateTimeStr


class AgEmbedderCreateSchema(BaseModel):
    """
    嵌入模型新增模型
    """
    name: str = Field(default=..., description='嵌入器名称')
    provider: str = Field(default=..., description='提供商')
    model_id: str = Field(default=..., description='嵌入模型标识')
    api_key: str | None = Field(default=None, description='API密钥')
    base_url: str | None = Field(default=None, description='自定义端点地址')
    dimensions: int | None = Field(default=None, description='向量维度')
    config: dict | None = Field(default=None, description='其他构造参数')
    status: str = Field(default="0", description='是否启用')
    description: str | None = Field(default=None, max_length=255, description='备注/描述')


class AgEmbedderUpdateSchema(AgEmbedderCreateSchema):
    """
    嵌入模型更新模型
    """
    ...


class AgEmbedderOutSchema(AgEmbedderCreateSchema, BaseSchema, UserBySchema):
    """
    嵌入模型响应模型
    """
    model_config = ConfigDict(from_attributes=True)


class AgEmbedderQueryParam:
    """嵌入模型查询参数"""

    def __init__(
        self,
        name: str | None = Query(None, description="嵌入器名称"),
        provider: str | None = Query(None, description="提供商"),
        model_id: str | None = Query(None, description="嵌入模型标识"),
        api_key: str | None = Query(None, description="API密钥"),
        base_url: str | None = Query(None, description="自定义端点地址"),
        dimensions: int | None = Query(None, description="向量维度"),
        # config: dict | None = Query(None, description="其他构造参数"),
        status: str | None = Query(None, description="是否启用"),
        created_id: int | None = Query(None, description=""),
        updated_id: int | None = Query(None, description=""),
        created_time: list[DateTimeStr] | None = Query(None, description="创建时间范围", examples=["2025-01-01 00:00:00", "2025-12-31 23:59:59"]),
        updated_time: list[DateTimeStr] | None = Query(None, description="更新时间范围", examples=["2025-01-01 00:00:00", "2025-12-31 23:59:59"]),
    ) -> None:
        # 模糊查询字段
        self.name = (QueueEnum.like.value, name)
        # 精确查询字段
        if provider:
            self.provider = (QueueEnum.eq.value, provider)
        # 精确查询字段
        if model_id:
            self.model_id = (QueueEnum.eq.value, model_id)
        # 精确查询字段
        if api_key:
            self.api_key = (QueueEnum.eq.value, api_key)
        # 精确查询字段
        if base_url:
            self.base_url = (QueueEnum.eq.value, base_url)
        # 精确查询字段
        if dimensions:
            self.dimensions = (QueueEnum.eq.value, dimensions)
        # 精确查询字段
        # if config:
        #     self.config = (QueueEnum.eq.value, config)
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
