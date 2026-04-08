"""
AgentBuilder — Agno Agent Builder

build 为 async，通过 resolver 异步 resolve 所有依赖资源：
- model / tools / knowledge（核心）
- skills（技能列表，每个 ref → SkillBuilder 返回 Skills 对象，合并后传入）
- memory_manager / session_summary_manager / compression_manager / culture_manager（可选管理器）
- learning（LearningMachine）
- guardrails（护栏列表）
- reasoning_config + reasoning 相关参数
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
        {
            "name": "skills",
            "type": "ref_or_inline_array",
            "required": False,
            "order": 7,
            "source": "skill",
        },
        {"name": "markdown", "type": "bool", "required": False, "default": True, "order": 8},
        {
            "name": "show_tool_calls",
            "type": "bool",
            "required": False,
            "default": False,
            "order": 9,
        },
        # ── 会话摘要 ───────────────────────────────────────────────────────────
        {
            "name": "session_summary_manager",
            "type": "ref_or_inline",
            "required": False,
            "order": 18,
            "source": "session_summary",
        },
        {
            "name": "add_session_summary_to_context",
            "type": "bool",
            "required": False,
            "default": False,
            "order": 19,
        },
        # ── 记忆 ──────────────────────────────────────────────────────────────
        {
            "name": "memory_manager",
            "type": "ref_or_inline",
            "required": False,
            "order": 20,
            "source": "memory",
        },
        {
            "name": "enable_agentic_memory",
            "type": "bool",
            "required": False,
            "default": False,
            "order": 21,
        },
        {
            "name": "update_memory_on_run",
            "type": "bool",
            "required": False,
            "default": True,
            "order": 22,
        },
        {
            "name": "add_memories_to_context",
            "type": "bool",
            "required": False,
            "default": True,
            "order": 23,
        },
        # ── 学习 ──────────────────────────────────────────────────────────────
        {
            "name": "learning",
            "type": "ref_or_inline",
            "required": False,
            "order": 30,
            "source": "learn",
        },
        {
            "name": "add_learnings_to_context",
            "type": "bool",
            "required": False,
            "default": True,
            "order": 31,
        },
        # ── 压缩 ──────────────────────────────────────────────────────────────
        {
            "name": "compression_manager",
            "type": "ref_or_inline",
            "required": False,
            "order": 40,
            "source": "compress",
        },
        # ── 护栏 ──────────────────────────────────────────────────────────────
        {
            "name": "guardrails",
            "type": "ref_or_inline_array",
            "required": False,
            "order": 50,
            "source": "guardrail",
        },
        # ── 推理 ──────────────────────────────────────────────────────────────
        {
            "name": "reasoning_config",
            "type": "ref_or_inline",
            "required": False,
            "order": 60,
            "source": "reasoning",
        },
        # ── 文化（实验性） ────────────────────────────────────────────────────
        {
            "name": "culture_manager",
            "type": "ref_or_inline",
            "required": False,
            "order": 70,
            "source": "culture",
        },
        {
            "name": "enable_agentic_culture",
            "type": "bool",
            "required": False,
            "default": False,
            "order": 71,
        },
        {
            "name": "add_culture_to_context",
            "type": "bool",
            "required": False,
            "default": True,
            "order": 72,
        },
        # ── 存储 ──────────────────────────────────────────────────────────────
        {
            "name": "db",
            "type": "ref_or_inline",
            "required": False,
            "order": 90,
            "source": "db",
        },
    ]

    field_meta = {
        "agent_id": {"label": "Agent ID", "group": "基础配置", "span": 12, "tooltip": "留空则自动生成"},
        "name": {"label": "名称", "group": "基础配置", "span": 12},
        "instructions": {"label": "指令", "group": "基础配置", "span": 24, "placeholder": "你是一个助手..."},
        "model": {"label": "模型", "group": "模型配置", "span": 24},
        "tools": {"label": "工具", "group": "能力配置", "span": 24},
        "knowledge": {"label": "知识库", "group": "能力配置", "span": 24},
        "skills": {
            "label": "技能",
            "group": "能力配置",
            "span": 24,
            "tooltip": "选择已创建的 Skill 资源，Agent 可按需调用其中的指令和脚本",
        },
        "markdown": {"label": "Markdown输出", "group": "输出配置", "span": 12},
        "show_tool_calls": {"label": "显示工具调用", "group": "输出配置", "span": 12},
        # 会话摘要
        "session_summary_manager": {"label": "会话摘要管理器", "group": "记忆配置", "span": 24},
        "add_session_summary_to_context": {"label": "将会话摘要注入上下文", "group": "记忆配置", "span": 12},
        # 记忆
        "memory_manager": {"label": "记忆管理器", "group": "记忆配置", "span": 24},
        "enable_agentic_memory": {"label": "启用自主记忆", "group": "记忆配置", "span": 12},
        "update_memory_on_run": {"label": "每次运行后更新记忆", "group": "记忆配置", "span": 12},
        "add_memories_to_context": {"label": "将记忆注入上下文", "group": "记忆配置", "span": 12},
        # 学习
        "learning": {"label": "学习机器", "group": "学习配置", "span": 24},
        "add_learnings_to_context": {"label": "将学习内容注入上下文", "group": "学习配置", "span": 12},
        # 压缩
        "compression_manager": {
            "label": "压缩管理器",
            "group": "压缩配置",
            "span": 24,
            "tooltip": "启用工具调用结果压缩以节省 Token",
        },
        # 护栏
        "guardrails": {
            "label": "输入护栏",
            "group": "安全配置",
            "span": 24,
            "tooltip": "对用户输入进行安全检查（内容审核/PII/提示词注入等）",
        },
        # 推理
        "reasoning_config": {
            "label": "推理配置",
            "group": "推理配置",
            "span": 24,
            "tooltip": "配置推理模型及推理步骤参数",
        },
        # 文化
        "culture_manager": {
            "label": "文化管理器",
            "group": "文化配置（实验性）",
            "span": 24,
            "tooltip": "实验性功能：捕获和管理文化知识",
        },
        "enable_agentic_culture": {
            "label": "启用自主文化学习",
            "group": "文化配置（实验性）",
            "span": 12,
        },
        "add_culture_to_context": {
            "label": "将文化知识注入上下文",
            "group": "文化配置（实验性）",
            "span": 12,
        },
        # 存储
        "db": {
            "label": "会话存储",
            "group": "存储配置",
            "span": 24,
            "tooltip": "持久化 Agent 的会话、记忆等数据；留空则使用内存存储",
        },
    }

    async def build(self, config: dict, resolver) -> Any:
        from agno.agent import Agent

        model = await resolver.resolve(config.get("model"))
        tools = await resolver.resolve_list(config.get("tools", []))
        knowledge = await resolver.resolve(config.get("knowledge"))
        # 每个 skill ref → Skills 对象；将多个 Skills 合并为一个
        skill_objects = await resolver.resolve_list(config.get("skills", []))
        memory_manager = await resolver.resolve(config.get("memory_manager"))
        session_summary_manager = await resolver.resolve(config.get("session_summary_manager"))
        learning = await resolver.resolve(config.get("learning"))
        compression_manager = await resolver.resolve(config.get("compression_manager"))
        guardrails = await resolver.resolve_list(config.get("guardrails", []))
        reasoning_cfg = await resolver.resolve(config.get("reasoning_config"))
        culture_manager = await resolver.resolve(config.get("culture_manager"))
        db = await resolver.resolve(config.get("db"))

        # 多个 Skills 对象合并成一个（共享 loaders）
        merged_skills = None
        if skill_objects:
            from agno.skills import Skills
            all_loaders = []
            for s in skill_objects:
                if hasattr(s, "loaders"):
                    all_loaders.extend(s.loaders)
            if all_loaders:
                merged_skills = Skills(loaders=all_loaders)

        # 推理参数从 reasoning_config build() 返回的 dict 中提取
        reasoning_model = None
        reasoning_min_steps = 1
        reasoning_max_steps = 10
        reasoning_enabled = False
        if reasoning_cfg:
            reasoning_model = reasoning_cfg.get("reasoning_model")
            reasoning_min_steps = reasoning_cfg.get("min_steps", 1)
            reasoning_max_steps = reasoning_cfg.get("max_steps", 10)
            reasoning_enabled = True

        kwargs: dict = {
            "model": model,
            "tools": tools if tools else None,
            "knowledge": knowledge,
            "markdown": config.get("markdown", True),
            "cache_callables": False,
        }

        if config.get("agent_id"):
            kwargs["id"] = config["agent_id"]
        if config.get("name"):
            kwargs["name"] = config["name"]
        if config.get("instructions"):
            kwargs["instructions"] = config["instructions"]

        # Skills
        if merged_skills is not None:
            kwargs["skills"] = merged_skills

        # 会话摘要
        if session_summary_manager is not None:
            kwargs["session_summary_manager"] = session_summary_manager
        if config.get("add_session_summary_to_context"):
            kwargs["add_session_summary_to_context"] = config["add_session_summary_to_context"]

        # 记忆
        if memory_manager is not None:
            kwargs["memory_manager"] = memory_manager
        if config.get("enable_agentic_memory"):
            kwargs["enable_agentic_memory"] = config["enable_agentic_memory"]
        if not config.get("update_memory_on_run", True):
            kwargs["update_memory_on_run"] = False
        if not config.get("add_memories_to_context", True):
            kwargs["add_memories_to_context"] = False

        # 学习
        if learning is not None:
            kwargs["learning"] = learning
        if not config.get("add_learnings_to_context", True):
            kwargs["add_learnings_to_context"] = False

        # 压缩
        if compression_manager is not None:
            kwargs["compression_manager"] = compression_manager

        # 护栏（agno 当前版本 Agent 不直接接受 guardrails 参数，已移除）

        # 推理
        if reasoning_enabled:
            kwargs["reasoning"] = True
            if reasoning_model is not None:
                kwargs["reasoning_model"] = reasoning_model
            kwargs["reasoning_min_steps"] = reasoning_min_steps
            kwargs["reasoning_max_steps"] = reasoning_max_steps

        # 文化
        if culture_manager is not None:
            kwargs["culture_manager"] = culture_manager
        if config.get("enable_agentic_culture"):
            kwargs["enable_agentic_culture"] = config["enable_agentic_culture"]
        if not config.get("add_culture_to_context", True):
            kwargs["add_culture_to_context"] = False

        # 存储
        if db is not None:
            kwargs["db"] = db

        return Agent(**kwargs)
