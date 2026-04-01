# -*- coding: utf-8 -*-
"""
Agno Registry 生命周期控制器。

此文件无路由端点，仅用于将 RuntimeRegistry 的启动/关闭事件
挂载到 FastAPI app 上。

机制：
  get_dynamic_router() 扫描 module_*/controller.py，会 import 本文件并将
  CoreRouter 通过 container_router.include_router → root_router.include_router
  → app.include_router 逐层传递，FastAPI 在每次 include_router 时都会把
  router.on_startup/on_shutdown 列表复制到上层，最终注册到 app。
"""

from fastapi import APIRouter

from app.core.logger import log

CoreRouter = APIRouter(prefix="/agno_manage/core", tags=["Agno Registry"])


async def _on_startup() -> None:
    from app.plugin.module_agno_manage.core.startup import warm_up
    log.info("[Registry] startup triggered by CoreRouter")
    await warm_up()


async def _on_shutdown() -> None:
    from app.plugin.module_agno_manage.core.registry import get_registry
    log.info("[Registry] shutdown triggered by CoreRouter")
    try:
        get_registry().shutdown()
    except Exception as e:
        log.warning(f"[Registry] shutdown error: {e}")


CoreRouter.add_event_handler("startup", _on_startup)
CoreRouter.add_event_handler("shutdown", _on_shutdown)
