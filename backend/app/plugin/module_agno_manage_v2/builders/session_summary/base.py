"""
SessionSummaryManagerBuilder — SessionSummaryManager Builder。

SessionSummaryManager 在每次对话后自动生成会话摘要，并可将摘要注入上下文。

build() 为 async，通过 resolver.resolve() 解析 model 依赖。
"""

from typing import Any

from app.plugin.module_agno_manage_v2.core.builder_base import BaseBuilder


class SessionSummaryManagerBuilder(BaseBuilder):
    category = "session_summary"
    type = "base"
    label = "会话摘要管理器"
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
            "name": "session_summary_prompt",
            "type": "str",
            "required": False,
            "order": 2,
        },
        {
            "name": "summary_request_message",
            "type": "str",
            "required": False,
            "default": "Provide the summary of the conversation.",
            "order": 3,
        },
    ]

    field_meta = {
        "model": {
            "label": "摘要模型",
            "group": "基础配置",
            "span": 24,
            "tooltip": "用于生成会话摘要的模型，留空则使用 Agent 的主模型",
        },
        "session_summary_prompt": {
            "label": "摘要提示词",
            "group": "提示词配置",
            "span": 24,
            "placeholder": "留空使用默认摘要提示词",
        },
        "summary_request_message": {
            "label": "摘要请求消息",
            "group": "提示词配置",
            "span": 24,
            "tooltip": "向模型发送的请求摘要的用户消息",
        },
    }

    async def build(self, config: dict, resolver) -> Any:
        from agno.session.summary import SessionSummaryManager

        model = await resolver.resolve(config.get("model"))

        kwargs: dict = {}
        if model is not None:
            kwargs["model"] = model
        if config.get("session_summary_prompt"):
            kwargs["session_summary_prompt"] = config["session_summary_prompt"]
        if config.get("summary_request_message"):
            kwargs["summary_request_message"] = config["summary_request_message"]

        return SessionSummaryManager(**kwargs)
