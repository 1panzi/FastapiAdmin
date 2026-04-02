# -*- coding: utf-8 -*-
"""Agno Guardrail 类型元数据。"""
from typing import TypedDict


class GuardrailTypeInfo(TypedDict):
    guardrail_type: str
    label: str
    description: str
    apply_to: str   # input / output / both


_GUARDRAIL_TYPES: list[GuardrailTypeInfo] = [
    {
        "guardrail_type": "input",
        "label": "输入过滤",
        "description": "在用户消息进入 Agent 前进行校验或过滤",
        "apply_to": "input",
    },
    {
        "guardrail_type": "output",
        "label": "输出过滤",
        "description": "在 Agent 响应返回给用户前进行校验或过滤",
        "apply_to": "output",
    },
    {
        "guardrail_type": "both",
        "label": "双向过滤",
        "description": "同时对输入和输出进行校验",
        "apply_to": "both",
    },
]


def list_guardrail_types() -> list[GuardrailTypeInfo]:
    return _GUARDRAIL_TYPES


def get_guardrail_type_names() -> list[str]:
    return [g["guardrail_type"] for g in _GUARDRAIL_TYPES]
