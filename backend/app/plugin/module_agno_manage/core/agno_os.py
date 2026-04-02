# -*- coding: utf-8 -*-
"""
AgentOS 初始化模块。

在 warm_up() 完成后由 init_app.py 中注册的 startup 事件触发。
使用 base_app 模式将 AgentOS 路由注入现有 FastAPI 实例，复用其中间件和路由体系。
"""

from fastapi import FastAPI

from app.core.logger import log


def _build_agno_db():
    """根据项目 DATABASE_TYPE 构建对应的 Agno 同步 BaseDb 实例。

    使用同步 BaseDb（非 AsyncBaseDb），以支持 AgentOS 全部功能（含 components 路由）。
    复用项目 settings.DB_URI（同步驱动：pymysql / psycopg / sqlite）。
    """
    from agno.db.mysql.mysql import MySQLDb
    from agno.db.postgres.postgres import PostgresDb
    from agno.db.sqlite.sqlite import SqliteDb

    from app.config.setting import settings

    db_uri = settings.DB_URI

    db_mapping = {
        "mysql": lambda: MySQLDb(db_url=db_uri),
        "postgres": lambda: PostgresDb(db_url=db_uri),
        "sqlite": lambda: SqliteDb(db_file=db_uri.replace("sqlite:///", "")),
    }

    db_type = settings.DATABASE_TYPE
    if db_type not in db_mapping:
        raise ValueError(f"[AgentOS] 不支持的数据库类型: {db_type}")

    return db_mapping[db_type]()


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
        db = _build_agno_db()
        agent_os = AgentOS(
            agents=agents,
            teams=teams,
            workflows=workflows,
            db=db,
            base_app=app,
            telemetry=False,
        )
        agent_os.get_app()
        log.info(
            f"[AgentOS] 初始化完成 — "
            f"agents={len(registry.agents)}, "
            f"teams={len(registry.teams)}, "
            f"workflows={len(registry.workflows)}, "
            f"db={db.__class__.__name__}"
        )
    except Exception as e:
        log.error(f"[AgentOS] 初始化失败: {e}")
