

from fastapi import Query
from pydantic import BaseModel, ConfigDict, Field

from app.common.enums import QueueEnum
from app.core.base_schema import BaseSchema, UserBySchema
from app.core.validator import DateTimeStr


class AgLearningConfigCreateSchema(BaseModel):
    """
    学习管理新增模型
    """
    name: str = Field(default=..., description='学习机配置名称')
    model_id: int | None = Field(default=None, description='关联模型ID')
    namespace: str | None = Field(default=None, description='命名空间（用于隔离不同租户/场景的学习数据）')
    user_profile: dict | None = Field(default=None, description='用户画像配置（UserProfileConfig JSON）')
    user_memory: dict | None = Field(default=None, description='用户记忆配置（UserMemoryConfig JSON）')
    session_context: dict | None = Field(default=None, description='会话上下文配置（SessionContextConfig JSON）')
    entity_memory: dict | None = Field(default=None, description='实体记忆配置（EntityMemoryConfig JSON）')
    learned_knowledge: dict | None = Field(default=None, description='学习知识配置（LearnedKnowledgeConfig JSON）')
    decision_log: dict | None = Field(default=None, description='决策日志配置（DecisionLogConfig JSON）')
    status: str = Field(default="0", description='')
    description: str | None = Field(default=None, max_length=255, description='')


class AgLearningConfigUpdateSchema(AgLearningConfigCreateSchema):
    """
    学习管理更新模型
    """
    ...


class AgLearningConfigOutSchema(AgLearningConfigCreateSchema, BaseSchema, UserBySchema):
    """
    学习管理响应模型
    """
    model_config = ConfigDict(from_attributes=True)


class AgLearningConfigQueryParam:
    """学习管理查询参数"""

    def __init__(
        self,
        name: str | None = Query(None, description="学习机配置名称"),
        model_id: int | None = Query(None, description="关联模型ID"),
        namespace: str | None = Query(None, description="命名空间（用于隔离不同租户/场景的学习数据）"),
        # user_profile: dict | None = Query(None, description="用户画像配置（UserProfileConfig JSON）"),
        # user_memory: dict | None = Query(None, description="用户记忆配置（UserMemoryConfig JSON）"),
        # session_context: dict | None = Query(None, description="会话上下文配置（SessionContextConfig JSON）"),
        # entity_memory: dict | None = Query(None, description="实体记忆配置（EntityMemoryConfig JSON）"),
        # learned_knowledge: dict | None = Query(None, description="学习知识配置（LearnedKnowledgeConfig JSON）"),
        # decision_log: dict | None = Query(None, description="决策日志配置（DecisionLogConfig JSON）"),
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
        if namespace:
            self.namespace = (QueueEnum.eq.value, namespace)
        # 精确查询字段
        # if user_profile:
        #     self.user_profile = (QueueEnum.eq.value, user_profile)
        # # 精确查询字段
        # if user_memory:
        #     self.user_memory = (QueueEnum.eq.value, user_memory)
        # # 精确查询字段
        # if session_context:
        #     self.session_context = (QueueEnum.eq.value, session_context)
        # # 精确查询字段
        # if entity_memory:
        #     self.entity_memory = (QueueEnum.eq.value, entity_memory)
        # # 精确查询字段
        # if learned_knowledge:
        #     self.learned_knowledge = (QueueEnum.eq.value, learned_knowledge)
        # # 精确查询字段
        # if decision_log:
        #     self.decision_log = (QueueEnum.eq.value, decision_log)
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
