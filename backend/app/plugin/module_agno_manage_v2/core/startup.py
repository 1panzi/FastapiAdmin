"""
RuntimeRegistry v2 预热逻辑。

触发方式：
  core/controller.py 中的 CoreV2Router.add_event_handler("startup", _on_startup)
  当 get_dynamic_router() 自动发现并 include CoreV2Router 后，FastAPI 启动时自动调用。
  无需修改任何上层配置文件。

幂等保证：
  使用 asyncio.Lock + _initialized 标志，重复调用安全。

预热逻辑：
  从 ag_resources 表读取所有 status="0" 的 agent/team 行，
  通过 builder_registry + RefResolver 构建 Agno 对象并注册到 RuntimeRegistry。
"""

import asyncio
import inspect

from app.core.logger import log

_init_lock = asyncio.Lock()
_initialized = False


async def warm_up() -> None:
    """预热 RuntimeRegistry v2（幂等，只执行一次）。"""
    global _initialized
    if _initialized:
        return
    async with _init_lock:
        if _initialized:
            return
        await _do_warm_up()
        _initialized = True


async def _do_warm_up() -> None:
    """按依赖顺序将 agent/team 加载到 RuntimeRegistry v2。"""
    from sqlalchemy import select

    from app.core.database import async_db_session
    from app.plugin.module_agno_manage_v2.core.builder_registry import builder_registry
    from app.plugin.module_agno_manage_v2.core.ref_resolver import RefResolver
    from app.plugin.module_agno_manage_v2.core.registry import RuntimeRegistry, set_registry
    from app.plugin.module_agno_manage_v2.resource.model import AgResourceModel

    # 创建并设置全局单例（startup 时初始化）
    runtime_registry = RuntimeRegistry()
    set_registry(runtime_registry)

    agent_count = 0
    team_count = 0

    async with async_db_session() as db:
        # ── 加载 agents ──────────────────────────────────────────────────────
        result = await db.execute(
            select(AgResourceModel).where(
                AgResourceModel.category == "agent",
                AgResourceModel.status == "0",
            )
        )
        agent_rows = result.scalars().all()

        # RefResolver 需要 db session，startup 时用同一个 session
        # 每个 resolver 独享 cache，避免跨 row 污染
        for row in agent_rows:
            try:
                resolver = RefResolver(db=db)
                builder = builder_registry.get(("agent", row.type))
                if builder is None:
                    log.warning(
                        f"[StartupV2] 未找到 builder agent/{row.type}，跳过 uuid={row.uuid}"
                    )
                    continue
                obj = builder.build(row.config or {}, resolver)
                if inspect.iscoroutine(obj):
                    obj = await obj
                runtime_registry.add_agent(str(row.uuid), obj)
                agent_count += 1
            except Exception as e:
                log.warning(f"[StartupV2] skip agent uuid={row.uuid}: {e}")

        # ── 加载 teams ───────────────────────────────────────────────────────
        result = await db.execute(
            select(AgResourceModel).where(
                AgResourceModel.category == "team",
                AgResourceModel.status == "0",
            )
        )
        team_rows = result.scalars().all()

        for row in team_rows:
            try:
                resolver = RefResolver(db=db)
                builder = builder_registry.get(("team", row.type))
                if builder is None:
                    log.warning(
                        f"[StartupV2] 未找到 builder team/{row.type}，跳过 uuid={row.uuid}"
                    )
                    continue
                obj = builder.build(row.config or {}, resolver)
                if inspect.iscoroutine(obj):
                    obj = await obj
                runtime_registry.add_team(str(row.uuid), obj)
                team_count += 1
            except Exception as e:
                log.warning(f"[StartupV2] skip team uuid={row.uuid}: {e}")

    log.info(
        f"[AgnoV2] RuntimeRegistry 预热完成 — "
        f"agents={agent_count}, teams={team_count}"
    )
