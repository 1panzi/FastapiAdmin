"""
CompressionManagerBuilder — CompressionManager Builder。

CompressionManager 用于压缩工具调用结果，节省上下文空间。

配置项：
- model（ref 或 inline）：用于压缩的模型
- compress_tool_results：是否启用工具结果压缩
- compress_tool_results_limit：触发压缩的未压缩工具调用数量阈值
- compress_token_limit：触发压缩的 token 数量阈值
- compress_tool_call_instructions：自定义压缩提示词

build() 为 async，通过 resolver.resolve() 解析 model 依赖。
"""

from typing import Any

from app.plugin.module_agno_manage_v2.core.builder_base import BaseBuilder


class CompressionManagerBuilder(BaseBuilder):
    category = "compress"
    type = "base"
    label = "压缩管理器"
    agno_class = None

    extra_fields = [
        {
            "name": "model",
            "type": "ref_or_inline",
            "required": False,
            "order": 1,
            "source": "model",
        },
        {
            "name": "compress_tool_results",
            "type": "bool",
            "required": False,
            "default": True,
            "order": 2,
        },
        {
            "name": "compress_tool_results_limit",
            "type": "int",
            "required": False,
            "default": 3,
            "order": 3,
        },
        {
            "name": "compress_token_limit",
            "type": "int",
            "required": False,
            "order": 4,
        },
        {
            "name": "compress_tool_call_instructions",
            "type": "str",
            "required": False,
            "order": 5,
        },
    ]

    field_meta = {
        "model": {
            "label": "压缩模型",
            "group": "基础配置",
            "span": 24,
            "tooltip": "用于压缩工具调用结果的模型，留空则不能执行压缩",
        },
        "compress_tool_results": {
            "label": "启用工具结果压缩",
            "group": "压缩配置",
            "span": 24,
        },
        "compress_tool_results_limit": {
            "label": "工具调用数量阈值",
            "group": "压缩配置",
            "span": 12,
            "min": 1,
            "max": 100,
            "tooltip": "未压缩工具调用数量达到此值时触发压缩（与 token 阈值二选一或同时使用）",
        },
        "compress_token_limit": {
            "label": "Token 数量阈值",
            "group": "压缩配置",
            "span": 12,
            "min": 100,
            "tooltip": "消息 token 总量超过此值时触发压缩，留空则仅使用工具调用数量阈值",
        },
        "compress_tool_call_instructions": {
            "label": "自定义压缩提示词",
            "group": "提示词配置",
            "span": 24,
            "placeholder": "留空使用默认压缩提示词",
            "tooltip": "自定义压缩指令，用于指导模型如何压缩工具调用结果",
        },
    }

    async def build(self, config: dict, resolver) -> Any:
        from agno.compression.manager import CompressionManager

        model = await resolver.resolve(config.get("model"))

        kwargs: dict = {
            "compress_tool_results": config.get("compress_tool_results", True),
        }
        if model is not None:
            kwargs["model"] = model
        if config.get("compress_tool_results_limit") is not None:
            kwargs["compress_tool_results_limit"] = config["compress_tool_results_limit"]
        if config.get("compress_token_limit") is not None:
            kwargs["compress_token_limit"] = config["compress_token_limit"]
        if config.get("compress_tool_call_instructions"):
            kwargs["compress_tool_call_instructions"] = config["compress_tool_call_instructions"]

        return CompressionManager(**kwargs)
