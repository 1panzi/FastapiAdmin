# -*- coding: utf-8 -*-
"""Agno Agent Hook 类型元数据。"""
from typing import TypedDict


class HookTypeInfo(TypedDict):
    hook_type: str
    label: str
    description: str
    signature: str   # 函数签名说明


_HOOK_TYPES: list[HookTypeInfo] = [
    {
        "hook_type": "pre_run",
        "label": "运行前 (pre_run)",
        "description": "在 Agent 每次 run() 开始前调用，可修改输入或拒绝执行",
        "signature": "async def hook(agent, message, **kwargs) -> None",
    },
    {
        "hook_type": "post_run",
        "label": "运行后 (post_run)",
        "description": "在 Agent 每次 run() 完成后调用，可处理输出或记录日志",
        "signature": "async def hook(agent, message, response, **kwargs) -> None",
    },
    {
        "hook_type": "pre_tool_call",
        "label": "工具调用前 (pre_tool_call)",
        "description": "在每次工具调用前触发，可修改参数或拦截调用",
        "signature": "async def hook(agent, tool_call, **kwargs) -> None",
    },
    {
        "hook_type": "post_tool_call",
        "label": "工具调用后 (post_tool_call)",
        "description": "在每次工具调用完成后触发，可处理或修改工具结果",
        "signature": "async def hook(agent, tool_call, result, **kwargs) -> None",
    },
    {
        "hook_type": "on_error",
        "label": "错误处理 (on_error)",
        "description": "当 Agent 运行出错时触发",
        "signature": "async def hook(agent, error, **kwargs) -> None",
    },
]


def list_hook_types() -> list[HookTypeInfo]:
    return _HOOK_TYPES


def get_hook_type_names() -> list[str]:
    return [h["hook_type"] for h in _HOOK_TYPES]
