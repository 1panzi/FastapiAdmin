# -*- coding: utf-8 -*-
"""
AgentOS 事件处理模块。

用于将 AgentOS 的初始化和关闭逻辑作为事件添加到全局事件列表中。
"""

from fastapi import FastAPI


async def init_agent_os_event(app: FastAPI, **kwargs) -> None:
    """
    初始化 AgentOS 事件。

    参数:
    - app (FastAPI): FastAPI 应用实例。
    - **kwargs: 额外参数。

    返回:
    - None
    """
    from .agno_os import init_agent_os
    await init_agent_os(app)
