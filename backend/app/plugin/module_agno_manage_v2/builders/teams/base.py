"""
TeamBuilder — Agno Team Builder

build 为 async，通过 resolver 异步 resolve model/members 依赖。
"""

from typing import Any

from app.plugin.module_agno_manage_v2.core.builder_base import BaseBuilder


class TeamBuilder(BaseBuilder):
    category = "team"
    type = "base"
    label = "Team"
    agno_class = None

    extra_fields = [
        {"name": "name", "type": "str", "required": False, "order": 1},
        {
            "name": "mode",
            "type": "select",
            "required": False,
            "options": ["coordinate", "route", "collaborate"],
            "default": "coordinate",
            "order": 2,
        },
        {
            "name": "model",
            "type": "ref_or_inline",
            "required": True,
            "order": 3,
            "source": "model",
        },
        {
            "name": "members",
            "type": "ref_or_inline_array",
            "required": True,
            "order": 4,
            "source": "agent",
        },
        {"name": "instructions", "type": "str", "required": False, "order": 5},
        {"name": "markdown", "type": "bool", "required": False, "default": True, "order": 6},
    ]
    field_meta = {
        "name": {"label": "Team名称", "group": "基础配置", "span": 12},
        "mode": {"label": "协作模式", "group": "基础配置", "span": 12},
        "model": {"label": "协调模型", "group": "模型配置", "span": 24},
        "members": {"label": "成员", "group": "成员配置", "span": 24},
        "instructions": {"label": "指令", "group": "基础配置", "span": 24},
        "markdown": {"label": "Markdown输出", "group": "输出配置", "span": 12},
    }

    async def build(self, config: dict, resolver) -> Any:
        from agno.team import Team

        model = await resolver.resolve(config.get("model"))
        members = await resolver.resolve_list(config.get("members", []))

        return Team(
            name=config.get("name") or None,
            mode=config.get("mode", "coordinate"),
            model=model,
            members=members,
            instructions=config.get("instructions") or None,
            markdown=config.get("markdown", True),
        )
