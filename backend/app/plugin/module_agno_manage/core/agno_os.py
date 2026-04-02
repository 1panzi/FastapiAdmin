# -*- coding: utf-8 -*-
"""
AgentOS 初始化模块。

在 warm_up() 完成后由 init_app.py 中注册的 startup 事件触发。
使用 base_app 模式将 AgentOS 路由注入现有 FastAPI 实例，复用其中间件和路由体系。
"""

from fastapi import FastAPI

from app.core.logger import log


async def init_agent_os(app: FastAPI) -> None:
    """
    在 registry 预热完成后初始化 AgentOS 并挂载到 base_app。

    调用时机：startup 事件队列中排在 warm_up() 之后（在 register_routers 末尾注册，
    CoreRouter 的 _on_startup 由 include_router 先注册，故顺序正确）。
    """
    from agno.os.agent_os import AgentOS

    from app.plugin.module_agno_manage.core.registry import get_registry

    registry = get_registry()
    agents = registry.agents if registry.agents else None
    teams = registry.teams if registry.teams else None
    workflows = registry.workflows if registry.workflows else None

    if not agents and not teams and not workflows:
        log.info("[AgentOS] registry 中无 agent/team/workflow，跳过 AgentOS 初始化")
        return

    try:
        agent_os = AgentOS(
            agents=agents,
            teams=teams,
            workflows=workflows,
            base_app=app,
            telemetry=False,
        )
        agent_os.get_app()
        log.info(
            f"[AgentOS] 初始化完成 — "
            f"agents={len(registry.agents)}, "
            f"teams={len(registry.teams)}, "
            f"workflows={len(registry.workflows)}"
        )
    except Exception as e:
        log.error(f"[AgentOS] 初始化失败: {e}")
