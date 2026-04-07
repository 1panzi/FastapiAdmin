"""
AgnoV2 Registry 生命周期控制器。

此文件无路由端点，仅用于将 RuntimeRegistry v2 的启动/关闭事件
挂载到 FastAPI app 上。

机制：
  get_dynamic_router() 扫描 module_*/controller.py，会 import 本文件并将
  CoreV2Router 通过 container_router.include_router → root_router.include_router
  → app.include_router 逐层传递，FastAPI 在每次 include_router 时都会把
  router.on_startup/on_shutdown 列表复制到上层，最终注册到 app。
"""

from fastapi import APIRouter

from app.core.logger import log

CoreV2Router = APIRouter(prefix="/agno_manage/v2/core", tags=["AgnoV2 Registry"])


async def _on_startup() -> None:
    from app.plugin.module_agno_manage_v2.core.startup import warm_up

    log.info("[AgnoV2] startup triggered by CoreV2Router")
    await warm_up()


async def _on_shutdown() -> None:
    from app.plugin.module_agno_manage_v2.core.registry import get_registry

    log.info("[AgnoV2] shutdown triggered by CoreV2Router")
    try:
        get_registry().shutdown()
    except Exception as e:
        log.warning(f"[AgnoV2] shutdown error: {e}")


CoreV2Router.add_event_handler("startup", _on_startup)
CoreV2Router.add_event_handler("shutdown", _on_shutdown)
