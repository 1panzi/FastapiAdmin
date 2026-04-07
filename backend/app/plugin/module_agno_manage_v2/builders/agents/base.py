"""
AgentBuilder — Agno Agent Builder

build 为 async，通过 resolver 异步 resolve model/tools/knowledge 依赖。
"""

from typing import Any

from app.plugin.module_agno_manage_v2.core.builder_base import BaseBuilder


class AgentBuilder(BaseBuilder):
    category = "agent"
    type = "base"
    label = "Agent"
    agno_class = None

    extra_fields = [
        {"name": "agent_id", "type": "str", "required": False, "order": 1},
        {"name": "name", "type": "str", "required": False, "order": 2},
        {"name": "instructions", "type": "str", "required": False, "order": 3},
        {
            "name": "model",
            "type": "ref_or_inline",
            "required": True,
            "order": 4,
            "source": "model",
        },
        {
            "name": "tools",
            "type": "ref_or_inline_array",
            "required": False,
            "order": 5,
            "source": "toolkit",
        },
        {
            "name": "knowledge",
            "type": "ref_or_inline",
            "required": False,
            "order": 6,
            "source": "knowledge",
        },
        {"name": "markdown", "type": "bool", "required": False, "default": True, "order": 7},
        {
            "name": "show_tool_calls",
            "type": "bool",
            "required": False,
            "default": False,
            "order": 8,
        },
    ]
    field_meta = {
        "agent_id": {
            "label": "Agent ID",
            "group": "基础配置",
            "span": 12,
            "tooltip": "留空则自动生成",
        },
        "name": {"label": "名称", "group": "基础配置", "span": 12},
        "instructions": {
            "label": "指令",
            "group": "基础配置",
            "span": 24,
            "placeholder": "你是一个助手...",
        },
        "model": {"label": "模型", "group": "模型配置", "span": 24},
        "tools": {"label": "工具", "group": "能力配置", "span": 24},
        "knowledge": {"label": "知识库", "group": "能力配置", "span": 24},
        "markdown": {"label": "Markdown输出", "group": "输出配置", "span": 12},
        "show_tool_calls": {"label": "显示工具调用", "group": "输出配置", "span": 12},
    }

    async def build(self, config: dict, resolver) -> Any:
        from agno.agent import Agent

        model = await resolver.resolve(config.get("model"))
        tools = await resolver.resolve_list(config.get("tools", []))
        knowledge = await resolver.resolve(config.get("knowledge"))

        return Agent(
            agent_id=config.get("agent_id") or None,
            name=config.get("name") or None,
            instructions=config.get("instructions") or None,
            model=model,
            tools=tools if tools else None,
            knowledge=knowledge,
            markdown=config.get("markdown", True),
            show_tool_calls=config.get("show_tool_calls", False),
            cache_callables=False,
        )
