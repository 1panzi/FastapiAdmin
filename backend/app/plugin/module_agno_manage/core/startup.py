# -*- coding: utf-8 -*-
"""
RuntimeRegistry 预热逻辑。

触发方式：
  core/controller.py 中的 CoreRouter.add_event_handler("startup", _on_startup)
  当 get_dynamic_router() 自动发现并 include CoreRouter 后，FastAPI 启动时自动调用。
  无需修改任何上层配置文件。

幂等保证：
  使用 asyncio.Lock + _initialized 标志，重复调用安全。
"""

import asyncio

from app.core.logger import log

_init_lock = asyncio.Lock()
_initialized = False


async def warm_up() -> None:
    """预热 RuntimeRegistry（幂等，只执行一次）。"""
    global _initialized
    if _initialized:
        return
    async with _init_lock:
        if _initialized:
            return
        await _do_warm_up()
        _initialized = True


async def _do_warm_up() -> None:
    """按依赖顺序将所有启用资源加载到 RuntimeRegistry。"""
    from sqlalchemy import select
    from app.core.database import async_db_session
    from app.plugin.module_agno_manage.core.registry import RuntimeRegistry, set_registry

    registry = RuntimeRegistry()

    async with async_db_session() as db:

        # ── 第一层：无依赖基础组件 ────────────────────────────────────────
        from app.plugin.module_agno_manage.models.model import AgModelModel
        result = await db.execute(select(AgModelModel).where(AgModelModel.status == "0"))
        for row in result.scalars().all():
            try:
                registry.register_model(str(row.id), row)
            except Exception as e:
                log.warning(f"[Startup] skip model id={row.id}: {e}")

        from app.plugin.module_agno_manage.embedders.model import AgEmbedderModel
        result = await db.execute(select(AgEmbedderModel).where(AgEmbedderModel.status == "0"))
        for row in result.scalars().all():
            try:
                registry.register_embedder(str(row.id), row)
            except Exception as e:
                log.warning(f"[Startup] skip embedder id={row.id}: {e}")

        # ── 第二层：行数据缓存（按需冷启动） ─────────────────────────────
        from app.plugin.module_agno_manage.vectordbs.model import AgVectordbModel
        result = await db.execute(select(AgVectordbModel).where(AgVectordbModel.status == "0"))
        for row in result.scalars().all():
            registry._vectordb_rows[str(row.id)] = row

        from app.plugin.module_agno_manage.knowledge_bases.model import AgKnowledgeBaseModel
        result = await db.execute(select(AgKnowledgeBaseModel).where(AgKnowledgeBaseModel.status == "0"))
        for row in result.scalars().all():
            registry._kb_rows[str(row.id)] = row

        # ── 第三层：工具类 ────────────────────────────────────────────────
        from app.plugin.module_agno_manage.toolkits.model import AgToolkitModel
        result = await db.execute(select(AgToolkitModel).where(AgToolkitModel.status == "0"))
        for row in result.scalars().all():
            try:
                registry.register_toolkit(str(row.id), row)
            except Exception as e:
                log.warning(f"[Startup] skip toolkit id={row.id}: {e}")

        from app.plugin.module_agno_manage.mcp_servers.model import AgMcpServerModel
        result = await db.execute(select(AgMcpServerModel).where(AgMcpServerModel.status == "0"))
        for row in result.scalars().all():
            registry._mcp_rows[str(row.id)] = row

        from app.plugin.module_agno_manage.skills.model import AgSkillModel
        result = await db.execute(select(AgSkillModel).where(AgSkillModel.status == "0"))
        for row in result.scalars().all():
            registry._skill_rows[str(row.id)] = row

        from app.plugin.module_agno_manage.hooks.model import AgHookModel
        result = await db.execute(select(AgHookModel).where(AgHookModel.status == "0"))
        for row in result.scalars().all():
            try:
                registry.register_hook(str(row.id), row)
            except Exception as e:
                log.warning(f"[Startup] skip hook id={row.id}: {e}")

        from app.plugin.module_agno_manage.guardrails.model import AgGuardrailModel
        result = await db.execute(select(AgGuardrailModel).where(AgGuardrailModel.status == "0"))
        for row in result.scalars().all():
            try:
                registry.register_guardrail(str(row.id), row)
            except Exception as e:
                log.warning(f"[Startup] skip guardrail id={row.id}: {e}")

        # ── 第四层：子管理器行数据 ─────────────────────────────────────────
        from app.plugin.module_agno_manage.memory_managers.model import AgMemoryManagerModel
        result = await db.execute(select(AgMemoryManagerModel).where(AgMemoryManagerModel.status == "0"))
        for row in result.scalars().all():
            registry._memory_manager_rows[str(row.id)] = row

        from app.plugin.module_agno_manage.learning_configs.model import AgLearningConfigModel
        result = await db.execute(select(AgLearningConfigModel).where(AgLearningConfigModel.status == "0"))
        for row in result.scalars().all():
            registry._learning_rows[str(row.id)] = row

        from app.plugin.module_agno_manage.reasoning_configs.model import AgReasoningConfigModel
        result = await db.execute(select(AgReasoningConfigModel).where(AgReasoningConfigModel.status == "0"))
        for row in result.scalars().all():
            registry._reasoning_rows[str(row.id)] = row

        from app.plugin.module_agno_manage.compression_configs.model import AgCompressionConfigModel
        result = await db.execute(select(AgCompressionConfigModel).where(AgCompressionConfigModel.status == "0"))
        for row in result.scalars().all():
            registry._compression_rows[str(row.id)] = row

        from app.plugin.module_agno_manage.sess_summary_configs.model import AgSessSummaryConfigModel
        result = await db.execute(select(AgSessSummaryConfigModel).where(AgSessSummaryConfigModel.status == "0"))
        for row in result.scalars().all():
            registry._session_summary_rows[str(row.id)] = row

        from app.plugin.module_agno_manage.culture_configs.model import AgCultureConfigModel
        result = await db.execute(select(AgCultureConfigModel).where(AgCultureConfigModel.status == "0"))
        for row in result.scalars().all():
            registry._culture_rows[str(row.id)] = row

        # ── 第五层：Agent ──────────────────────────────────────────────────
        from app.plugin.module_agno_manage.agents.model import AgAgentModel
        agent_rows = await db.execute(
            select(AgAgentModel).where(AgAgentModel.status == "0")
        )
        for row in agent_rows.scalars():
            try:
                registry.create_agent(row)
            except Exception as e:
                log.warning(f"[Startup] failed to create agent id={row.id}: {e}")
        log.info(f"[Startup] agents loaded")

        # ── 最后层：Bindings + Integrations（行数据缓存）─────────────────
        from app.plugin.module_agno_manage.bindings.model import AgBindingModel
        result = await db.execute(select(AgBindingModel).where(AgBindingModel.status == "0"))
        for row in result.scalars().all():
            registry._binding_rows[str(row.id)] = row

        from app.plugin.module_agno_manage.integrations.model import AgIntegrationModel
        result = await db.execute(select(AgIntegrationModel).where(AgIntegrationModel.status == "0"))
        for row in result.scalars().all():
            registry._integration_rows[str(row.id)] = row

    set_registry(registry)
    log.info(
        f"[Registry] warm-up complete — "
        f"models={len(registry._model_cache)}, "
        f"embedders={len(registry._embedder_cache)}, "
        f"toolkits={len(registry._toolkit_map)}, "
        f"hooks={len(registry._hook_map)}, "
        f"guardrails={len(registry._guardrail_map)}"
    )
