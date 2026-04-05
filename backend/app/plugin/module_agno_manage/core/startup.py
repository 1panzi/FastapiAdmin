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
    from app.plugin.module_agno_manage.core.registry import get_registry

    # 使用全局单例，而非新建实例——保证 AgentOS 持有的 agents 列表引用始终有效
    registry = get_registry()

    async with async_db_session() as db:

        # ── 第零层：自动发现工具并 upsert 入库 ───────────────────────────
        await _sync_discovered_tools(db)

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
        kb_rows = result.scalars().all()
        for row in kb_rows:
            registry._kb_rows[str(row.id)] = row

        from app.plugin.module_agno_manage.readers.model import AgReaderModel
        result = await db.execute(select(AgReaderModel).where(AgReaderModel.status == "0"))
        for row in result.scalars().all():
            registry._reader_rows[str(row.id)] = row

        # 预构建所有 Knowledge 实例（vectordb_rows + reader_rows 已就绪）
        for row in kb_rows:
            try:
                kb = registry._build_knowledge(str(row.id), row)
                if kb:
                    registry._knowledge_map[str(row.id)] = kb
            except Exception as e:
                log.warning(f"[Startup] skip knowledge build id={row.id}: {e}")

        # ── 第三层：工具类 ────────────────────────────────────────────────
        from app.plugin.module_agno_manage.toolkits.model import AgToolkitModel
        result = await db.execute(
            select(AgToolkitModel).where(
                AgToolkitModel.status == "0",
                AgToolkitModel.global_enabled == True,  # noqa: E712
            )
        )
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

        from app.plugin.module_agno_manage.sess_summary_configs.model import (
            AgSessSummaryConfigModel,
        )
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
        log.info("[Startup] agents loaded")

        # ── 最后层：Bindings + Integrations（行数据缓存）─────────────────
        from app.plugin.module_agno_manage.bindings.model import AgBindingModel
        result = await db.execute(select(AgBindingModel).where(AgBindingModel.status == "0"))
        for row in result.scalars().all():
            registry._binding_rows[str(row.id)] = row

        from app.plugin.module_agno_manage.integrations.model import AgIntegrationModel
        result = await db.execute(select(AgIntegrationModel).where(AgIntegrationModel.status == "0"))
        for row in result.scalars().all():
            registry._integration_rows[str(row.id)] = row

    log.info(
        f"[Registry] warm-up complete — "
        f"models={len(registry._model_cache)}, "
        f"embedders={len(registry._embedder_cache)}, "
        f"knowledge={len(registry._knowledge_map)}, "
        f"toolkits={len(registry._toolkit_rows)}, "
        f"hooks={len(registry._hook_map)}, "
        f"guardrails={len(registry._guardrail_map)}"
    )


async def _sync_discovered_tools(db) -> None:
    """扫描 agno + custom 工具，将新发现的工具 upsert 入库。

    规则：
    - 以 module_path + class_name 判断唯一性
    - 不存在 → INSERT（status='0', global_enabled=True）
    - 已存在 → 只更新 category / description（保留用户改过的 config/status）
    """
    from sqlalchemy import and_, select

    from app.plugin.module_agno_manage.toolkits.discovery import scan_all_tools
    from app.plugin.module_agno_manage.toolkits.model import AgToolkitModel

    try:
        discovered = scan_all_tools()
    except Exception as e:
        log.warning(f"[Startup] 工具扫描失败，跳过 upsert: {e}")
        return

    if not discovered:
        return

    inserted = updated = 0
    for tool in discovered:
        try:
            result = await db.execute(
                select(AgToolkitModel).where(
                    and_(
                        AgToolkitModel.module_path == tool["module_path"],
                        AgToolkitModel.class_name == tool["class_name"],
                    )
                )
            )
            existing = result.scalar_one_or_none()
            if existing is None:
                row = AgToolkitModel(
                    name=tool["name"],
                    type=tool["type"],
                    module_path=tool["module_path"],
                    class_name=tool["class_name"],
                    category=tool["category"],
                    description=tool["description"],
                    tool_from=tool["tool_from"],
                    param_schema=tool["param_schema"],
                    status="0",
                    global_enabled=True,
                )
                db.add(row)
                inserted += 1
            else:
                # 只更新描述性元数据，不覆盖用户配置
                existing.category = tool["category"]
                existing.description = tool["description"]
                existing.tool_from = tool["tool_from"]
                existing.param_schema = tool["param_schema"]
                updated += 1
        except Exception as e:
            log.warning(f"[Startup] upsert toolkit {tool['module_path']}.{tool['class_name']} 失败: {e}")

    await db.commit()
    log.info(f"[Startup] 工具同步完成 — 新增={inserted}, 更新元数据={updated}")
