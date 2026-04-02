# -*- coding: utf-8 -*-
"""
Agno Registry 生命周期控制器。

warm_up() 和 shutdown() 均由 init_app.py 的 lifespan 直接调用。
此文件保留 CoreRouter 供动态路由发现机制扫描（无路由端点）。
"""

from fastapi import APIRouter

from app.core.logger import log

CoreRouter = APIRouter(prefix="/agno_manage/core", tags=["Agno Registry"])


async def on_shutdown() -> None:
    from app.plugin.module_agno_manage.core.registry import get_registry
    log.info("[Registry] shutdown")
    try:
        get_registry().shutdown()
    except Exception as e:
        log.warning(f"[Registry] shutdown error: {e}")
