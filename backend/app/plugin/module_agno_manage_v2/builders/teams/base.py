"""
TeamBuilder — Agno Team Builder

build 为 async，通过 resolver 异步 resolve 所有依赖资源：
- model / members / knowledge（核心）
- tools（Team 也支持直接挂工具）
- memory_manager / session_summary_manager（记忆）
- learning / compression_manager（学习/压缩）
- reasoning_model + reasoning 相关参数
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
            "options": [
                {"value": "coordinate", "label": "协调模式（coordinate）"},
                {"value": "route", "label": "路由模式（route）"},
                {"value": "collaborate", "label": "协作模式（collaborate）"},
            ],
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
        {
            "name": "tools",
            "type": "ref_or_inline_array",
            "required": False,
            "order": 7,
            "source": "toolkit",
        },
        {
            "name": "knowledge",
            "type": "ref_or_inline",
            "required": False,
            "order": 8,
            "source": "knowledge",
        },
        {"name": "show_members_responses", "type": "bool", "required": False, "default": False, "order": 9},
        {"name": "max_iterations", "type": "int", "required": False, "default": 10, "order": 10},
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
        {
            "name": "session_summary_manager",
            "type": "ref_or_inline",
            "required": False,
            "order": 24,
            "source": "session_summary",
        },
        {
            "name": "add_session_summary_to_context",
            "type": "bool",
            "required": False,
            "default": False,
            "order": 25,
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
        # ── 推理 ──────────────────────────────────────────────────────────────
        {
            "name": "reasoning_config",
            "type": "ref_or_inline",
            "required": False,
            "order": 50,
            "source": "reasoning",
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
        "name": {"label": "Team 名称", "group": "基础配置", "span": 12},
        "mode": {"label": "协作模式", "group": "基础配置", "span": 12},
        "model": {"label": "协调模型", "group": "模型配置", "span": 24},
        "members": {"label": "成员", "group": "成员配置", "span": 24},
        "instructions": {"label": "指令", "group": "基础配置", "span": 24},
        "markdown": {"label": "Markdown输出", "group": "输出配置", "span": 12},
        "show_members_responses": {"label": "显示成员响应", "group": "输出配置", "span": 12},
        "tools": {"label": "工具", "group": "能力配置", "span": 24},
        "knowledge": {"label": "知识库", "group": "能力配置", "span": 24},
        "max_iterations": {
            "label": "最大迭代次数",
            "group": "基础配置",
            "span": 12,
            "min": 1,
            "max": 100,
            "tooltip": "Team 协作的最大轮次",
        },
        # 记忆
        "memory_manager": {"label": "记忆管理器", "group": "记忆配置", "span": 24},
        "enable_agentic_memory": {"label": "启用自主记忆", "group": "记忆配置", "span": 12},
        "update_memory_on_run": {"label": "每次运行后更新记忆", "group": "记忆配置", "span": 12},
        "add_memories_to_context": {"label": "将记忆注入上下文", "group": "记忆配置", "span": 12},
        "session_summary_manager": {"label": "会话摘要管理器", "group": "记忆配置", "span": 24},
        "add_session_summary_to_context": {"label": "将会话摘要注入上下文", "group": "记忆配置", "span": 12},
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
        # 推理
        "reasoning_config": {
            "label": "推理配置",
            "group": "推理配置",
            "span": 24,
            "tooltip": "配置推理模型及推理步骤参数",
        },
        # 存储
        "db": {
            "label": "会话存储",
            "group": "存储配置",
            "span": 24,
            "tooltip": "持久化 Team 的会话、记忆等数据；留空则使用内存存储",
        },
    }

    async def build(self, config: dict, resolver) -> Any:
        from agno.team import Team

        model = await resolver.resolve(config.get("model"))
        members = await resolver.resolve_list(config.get("members", []))
        tools = await resolver.resolve_list(config.get("tools", []))
        knowledge = await resolver.resolve(config.get("knowledge"))
        memory_manager = await resolver.resolve(config.get("memory_manager"))
        session_summary_manager = await resolver.resolve(config.get("session_summary_manager"))
        learning = await resolver.resolve(config.get("learning"))
        compression_manager = await resolver.resolve(config.get("compression_manager"))
        reasoning_cfg = await resolver.resolve(config.get("reasoning_config"))
        db = await resolver.resolve(config.get("db"))

        # 推理参数
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
            "members": members,
            "mode": config.get("mode", "coordinate"),
            "markdown": config.get("markdown", True),
            "show_members_responses": config.get("show_members_responses", False),
        }

        if config.get("name"):
            kwargs["name"] = config["name"]
        if config.get("instructions"):
            kwargs["instructions"] = config["instructions"]
        if tools:
            kwargs["tools"] = tools
        if knowledge is not None:
            kwargs["knowledge"] = knowledge
        if config.get("max_iterations") is not None:
            kwargs["max_iterations"] = config["max_iterations"]

        # 记忆
        if memory_manager is not None:
            kwargs["memory_manager"] = memory_manager
        if config.get("enable_agentic_memory"):
            kwargs["enable_agentic_memory"] = config["enable_agentic_memory"]
        if not config.get("update_memory_on_run", True):
            kwargs["update_memory_on_run"] = False
        if not config.get("add_memories_to_context", True):
            kwargs["add_memories_to_context"] = False
        if session_summary_manager is not None:
            kwargs["session_summary_manager"] = session_summary_manager
        if config.get("add_session_summary_to_context"):
            kwargs["add_session_summary_to_context"] = config["add_session_summary_to_context"]

        # 学习
        if learning is not None:
            kwargs["learning"] = learning
        if not config.get("add_learnings_to_context", True):
            kwargs["add_learnings_to_context"] = False

        # 压缩
        if compression_manager is not None:
            kwargs["compression_manager"] = compression_manager

        # 推理
        if reasoning_enabled:
            kwargs["reasoning"] = True
            if reasoning_model is not None:
                kwargs["reasoning_model"] = reasoning_model
            kwargs["reasoning_min_steps"] = reasoning_min_steps
            kwargs["reasoning_max_steps"] = reasoning_max_steps

        # 存储
        if db is not None:
            kwargs["db"] = db

        return Team(**kwargs)
