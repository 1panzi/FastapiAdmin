# -*- coding: utf-8 -*-
"""MCP Server 类型元数据。"""
from typing import TypedDict


class McpServerTypeInfo(TypedDict):
    server_type: str
    label: str
    description: str
    config_fields: list[dict]  # 所需配置字段说明


_TYPES: list[McpServerTypeInfo] = [
    {
        "server_type": "http",
        "label": "HTTP/SSE",
        "description": "通过 HTTP SSE 连接的 MCP 服务（如远程 MCP 服务器）",
        "config_fields": [
            {"field": "url", "label": "服务地址", "required": True, "example": "http://localhost:8000/sse"},
            {"field": "headers", "label": "请求头（dict）", "required": False, "example": {"Authorization": "Bearer xxx"}},
            {"field": "timeout", "label": "超时秒数", "required": False, "example": 30},
        ],
    },
    {
        "server_type": "stdio",
        "label": "Stdio 进程",
        "description": "通过 stdio 启动本地进程的 MCP 服务",
        "config_fields": [
            {"field": "command", "label": "启动命令", "required": True, "example": "npx"},
            {"field": "args", "label": "命令参数列表", "required": False, "example": ["-y", "@modelcontextprotocol/server-filesystem"]},
            {"field": "env", "label": "环境变量（dict）", "required": False, "example": {"PATH": "/usr/bin"}},
        ],
    },
]


def list_mcp_server_types() -> list[McpServerTypeInfo]:
    return _TYPES
