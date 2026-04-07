"""
SkillBuilder — Agno Skill Builder

Skill 是 agno 的技能单元，提供结构化指令、参考文档供 Agent 按需调用。

两种管理模式，通过 source 字段区分：

1. inline 模式（source="inline"，默认）：
   内容全部存入 ag_resources.config，无需文件系统。
   适合在前端直接创建/编辑 SKILL.md 内容。

2. path 模式（source="path"）：
   指定服务器上已有的 Skill 目录路径（含 SKILL.md），
   或上传文件后服务端保存的路径。
   使用 agno 原生 LocalSkills 加载，支持 scripts/ references/ 子目录。

config 示例（inline）：
{
  "source": "inline",
  "name": "sql_expert",
  "description": "SQL 查询优化专家",
  "instructions": "# SQL Expert\\n\\n当用户询问 SQL 相关问题时...",
  "allowed_tools": "sql, postgres"
}

config 示例（path）：
{
  "source": "path",
  "skill_path": "/data/skills/sql_expert/"
}
"""

from typing import Any

from app.plugin.module_agno_manage_v2.core.builder_base import BaseBuilder


class _InlineSkillLoader:
    """从 config dict 构造 Skill 的内存 Loader。"""

    def __init__(self, skill_data: dict):
        self._data = skill_data

    def load(self):
        from agno.skills.skill import Skill

        allowed_tools = self._data.get("allowed_tools")
        if isinstance(allowed_tools, str):
            allowed_tools = [t.strip() for t in allowed_tools.split(",") if t.strip()] or None

        return [
            Skill(
                name=self._data["name"],
                description=self._data.get("description", ""),
                instructions=self._data.get("instructions", ""),
                source_path="",
                allowed_tools=allowed_tools,
            )
        ]


class SkillBuilder(BaseBuilder):
    category = "skill"
    type = "base"
    label = "技能（Skill）"
    agno_class = None

    extra_fields = [
        # ── 模式选择 ───────────────────────────────────────────────────────────
        {
            "name": "source",
            "type": "select",
            "required": False,
            "default": "inline",
            "order": 0,
            "options": [
                {"value": "inline", "label": "内联编辑（直接填写内容）"},
                {"value": "path", "label": "路径加载（上传/指定目录）"},
            ],
        },
        # ── inline 模式字段 ────────────────────────────────────────────────────
        {
            "name": "name",
            "type": "str",
            "required": False,       # path 模式时由文件读取，故非全局必填
            "order": 1,
        },
        {
            "name": "description",
            "type": "str",
            "required": False,
            "order": 2,
        },
        {
            "name": "instructions",
            "type": "str",
            "required": False,
            "order": 3,
        },
        {
            "name": "allowed_tools",
            "type": "str",
            "required": False,
            "order": 4,
        },
        # ── path 模式字段 ──────────────────────────────────────────────────────
        {
            "name": "skill_path",
            "type": "str",
            "required": False,
            "order": 10,
        },
    ]

    field_meta = {
        "source": {
            "label": "技能来源",
            "group": "基础配置",
            "span": 24,
            "tooltip": "选择内联编辑或指定已有 Skill 目录路径",
        },
        # inline
        "name": {
            "label": "技能名称",
            "group": "内联内容",
            "span": 12,
            "placeholder": "sql_expert",
            "tooltip": "唯一标识，Agent 通过此名称调用技能",
            "depends_on": {"source": "inline"},
        },
        "description": {
            "label": "技能描述",
            "group": "内联内容",
            "span": 12,
            "placeholder": "简短描述该技能的用途",
            "tooltip": "Agent 浏览技能列表时看到的摘要",
            "depends_on": {"source": "inline"},
        },
        "instructions": {
            "label": "技能指令（SKILL.md 正文）",
            "group": "内联内容",
            "span": 24,
            "placeholder": "# 技能名称\n\n## 何时使用\n\n...\n\n## 如何使用\n\n...",
            "tooltip": "Agent 调用 get_skill_instructions() 时获取的完整指令，支持 Markdown",
            "depends_on": {"source": "inline"},
        },
        "allowed_tools": {
            "label": "允许使用的工具",
            "group": "内联内容",
            "span": 24,
            "placeholder": "sql, postgres, python（逗号分隔）",
            "tooltip": "该技能允许使用的工具列表，留空表示不限制",
            "depends_on": {"source": "inline"},
        },
        # path
        "skill_path": {
            "label": "Skill 目录路径",
            "group": "路径配置",
            "span": 24,
            "placeholder": "/data/skills/sql_expert/",
            "tooltip": "服务器上包含 SKILL.md 的目录路径，或包含多个 Skill 子目录的父目录",
            "depends_on": {"source": "path"},
        },
    }

    async def build(self, config: dict, resolver) -> Any:
        from agno.skills import Skills

        source = config.get("source", "inline")

        if source == "path":
            skill_path = config.get("skill_path", "").strip()
            if not skill_path:
                raise ValueError("Skill path 模式下 skill_path 不能为空")
            from agno.skills.loaders import LocalSkills
            loader = LocalSkills(skill_path)
        else:
            # inline 模式
            if not config.get("name"):
                raise ValueError("Skill inline 模式下 name 不能为空")
            loader = _InlineSkillLoader(config)

        return Skills(loaders=[loader])
