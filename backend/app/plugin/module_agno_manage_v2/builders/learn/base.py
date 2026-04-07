"""
LearningMachineBuilder — LearningMachine Builder。

LearningMachine 是 agno 统一学习系统，协调多种学习存储：
- user_profile：用户档案（结构化长期信息）
- user_memory：用户记忆（非结构化观察）
- session_context：会话上下文（会话摘要/状态）
- entity_memory：实体记忆（关于第三方实体的知识）
- learned_knowledge：学到的知识（可复用洞察，需要 knowledge 支持）

build() 为 async，通过 resolver.resolve() 解析 model / knowledge 依赖。
"""

from typing import Any

from app.plugin.module_agno_manage_v2.core.builder_base import BaseBuilder


class LearningMachineBuilder(BaseBuilder):
    category = "learn"
    type = "base"
    label = "学习机器"
    agno_class = None

    extra_fields = [
        {
            "name": "model",
            "type": "ref_or_inline",
            "required": False,
            "order": 1,
            "source": "model",
        },
        {
            "name": "enable_user_profile",
            "type": "bool",
            "required": False,
            "default": False,
            "order": 10,
        },
        {
            "name": "enable_user_memory",
            "type": "bool",
            "required": False,
            "default": False,
            "order": 11,
        },
        {
            "name": "enable_session_context",
            "type": "bool",
            "required": False,
            "default": False,
            "order": 12,
        },
        {
            "name": "enable_entity_memory",
            "type": "bool",
            "required": False,
            "default": False,
            "order": 13,
        },
        {
            "name": "enable_learned_knowledge",
            "type": "bool",
            "required": False,
            "default": False,
            "order": 14,
        },
        {
            "name": "knowledge",
            "type": "ref_or_inline",
            "required": False,
            "order": 15,
            "source": "knowledge",
        },
        {
            "name": "namespace",
            "type": "str",
            "required": False,
            "default": "global",
            "order": 20,
        },
        {
            "name": "debug_mode",
            "type": "bool",
            "required": False,
            "default": False,
            "order": 30,
        },
    ]

    field_meta = {
        "model": {
            "label": "学习模型",
            "group": "基础配置",
            "span": 24,
            "tooltip": "用于学习提取的模型",
        },
        "enable_user_profile": {
            "label": "启用用户档案",
            "group": "学习类型",
            "span": 12,
            "tooltip": "记录用户的结构化长期信息（姓名、偏好等）",
        },
        "enable_user_memory": {
            "label": "启用用户记忆",
            "group": "学习类型",
            "span": 12,
            "tooltip": "记录关于用户的非结构化观察",
        },
        "enable_session_context": {
            "label": "启用会话上下文",
            "group": "学习类型",
            "span": 12,
            "tooltip": "捕获当前会话的状态和摘要",
        },
        "enable_entity_memory": {
            "label": "启用实体记忆",
            "group": "学习类型",
            "span": 12,
            "tooltip": "记录关于第三方实体（公司、项目等）的知识",
        },
        "enable_learned_knowledge": {
            "label": "启用学到的知识",
            "group": "学习类型",
            "span": 12,
            "tooltip": "捕获可复用的洞察和规律（需要配置知识库）",
        },
        "knowledge": {
            "label": "关联知识库",
            "group": "学习类型",
            "span": 24,
            "tooltip": "启用「学到的知识」时必须配置",
            "depends_on": {"enable_learned_knowledge": True},
        },
        "namespace": {
            "label": "命名空间",
            "group": "高级配置",
            "span": 12,
            "placeholder": "global",
            "tooltip": "实体记忆和学到的知识的共享边界（user/global/自定义）",
        },
        "debug_mode": {"label": "调试模式", "group": "高级配置", "span": 12},
    }

    async def build(self, config: dict, resolver) -> Any:
        from agno.learn.machine import LearningMachine

        model = await resolver.resolve(config.get("model"))
        knowledge = await resolver.resolve(config.get("knowledge")) if config.get("enable_learned_knowledge") else None

        return LearningMachine(
            model=model,
            knowledge=knowledge,
            user_profile=config.get("enable_user_profile", False),
            user_memory=config.get("enable_user_memory", False),
            session_context=config.get("enable_session_context", False),
            entity_memory=config.get("enable_entity_memory", False),
            learned_knowledge=config.get("enable_learned_knowledge", False),
            namespace=config.get("namespace", "global"),
            debug_mode=config.get("debug_mode", False),
        )
