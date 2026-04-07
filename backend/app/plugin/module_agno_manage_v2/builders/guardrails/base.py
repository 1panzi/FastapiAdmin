"""
Guardrail Builders — 输入安全护栏 Builders。

agno 内置三种护栏：
1. openai_moderation：调用 OpenAI Moderation API 检测违规内容
2. pii_detection：正则匹配检测个人隐私信息（SSN/信用卡/邮箱/手机号）
3. prompt_injection：关键词匹配检测提示词注入攻击

每种护栄都是独立 Builder，category="guardrail"，type 各异。
build() 同步即可（护栏本身不需要异步 resolve 依赖）。
"""

from typing import Any

from app.plugin.module_agno_manage_v2.core.builder_base import BaseBuilder


class BaseGuardrailBuilder(BaseBuilder):
    category = "guardrail"
    agno_class = None
    extra_fields: list[dict] = []
    field_meta: dict[str, dict] = {}

    def build(self, config: dict, resolver) -> Any:
        raise NotImplementedError

    async def build(self, config: dict, resolver) -> Any:  # type: ignore[misc]
        return self._sync_build(config)

    def _sync_build(self, config: dict) -> Any:
        raise NotImplementedError


# ── OpenAI Moderation ────────────────────────────────────────────────────────

MODERATION_CATEGORIES = [
    "sexual", "sexual/minors", "harassment", "harassment/threatening",
    "hate", "hate/threatening", "illicit", "illicit/violent",
    "self-harm", "self-harm/intent", "self-harm/instructions",
    "violence", "violence/graphic",
]


class OpenAIModerationGuardrailBuilder(BaseGuardrailBuilder):
    type = "openai_moderation"
    label = "OpenAI 内容审核"

    extra_fields = [
        {
            "name": "moderation_model",
            "type": "str",
            "required": False,
            "default": "omni-moderation-latest",
            "order": 1,
        },
        {
            "name": "api_key",
            "type": "password",
            "required": False,
            "order": 2,
        },
        {
            "name": "raise_for_categories",
            "type": "select",
            "required": False,
            "order": 3,
            "options": [{"value": c, "label": c} for c in MODERATION_CATEGORIES],
        },
    ]

    field_meta = {
        "moderation_model": {
            "label": "审核模型",
            "group": "基础配置",
            "span": 12,
            "tooltip": "用于内容审核的 OpenAI Moderation 模型",
        },
        "api_key": {
            "label": "API Key",
            "group": "基础配置",
            "span": 12,
            "placeholder": "留空使用环境变量 OPENAI_API_KEY",
        },
        "raise_for_categories": {
            "label": "拦截类别",
            "group": "拦截规则",
            "span": 24,
            "tooltip": "留空则拦截所有违规类别",
            "multiselect": True,
        },
    }

    def _sync_build(self, config: dict) -> Any:
        from agno.guardrails.openai import OpenAIModerationGuardrail

        categories = config.get("raise_for_categories") or None
        if isinstance(categories, str):
            categories = [categories] if categories else None

        return OpenAIModerationGuardrail(
            moderation_model=config.get("moderation_model", "omni-moderation-latest"),
            api_key=config.get("api_key") or None,
            raise_for_categories=categories,
        )


# ── PII Detection ─────────────────────────────────────────────────────────────

class PIIDetectionGuardrailBuilder(BaseGuardrailBuilder):
    type = "pii_detection"
    label = "PII 隐私信息检测"

    extra_fields = [
        {
            "name": "mask_pii",
            "type": "bool",
            "required": False,
            "default": False,
            "order": 1,
        },
        {
            "name": "enable_ssn_check",
            "type": "bool",
            "required": False,
            "default": True,
            "order": 2,
        },
        {
            "name": "enable_credit_card_check",
            "type": "bool",
            "required": False,
            "default": True,
            "order": 3,
        },
        {
            "name": "enable_email_check",
            "type": "bool",
            "required": False,
            "default": True,
            "order": 4,
        },
        {
            "name": "enable_phone_check",
            "type": "bool",
            "required": False,
            "default": True,
            "order": 5,
        },
    ]

    field_meta = {
        "mask_pii": {
            "label": "遮盖而非拦截",
            "group": "基础配置",
            "span": 24,
            "tooltip": "开启后将用 *** 遮盖 PII，而不是抛出错误",
        },
        "enable_ssn_check": {"label": "检测社保号（SSN）", "group": "检测项目", "span": 12},
        "enable_credit_card_check": {"label": "检测信用卡号", "group": "检测项目", "span": 12},
        "enable_email_check": {"label": "检测邮箱地址", "group": "检测项目", "span": 12},
        "enable_phone_check": {"label": "检测手机号码", "group": "检测项目", "span": 12},
    }

    def _sync_build(self, config: dict) -> Any:
        from agno.guardrails.pii import PIIDetectionGuardrail

        return PIIDetectionGuardrail(
            mask_pii=config.get("mask_pii", False),
            enable_ssn_check=config.get("enable_ssn_check", True),
            enable_credit_card_check=config.get("enable_credit_card_check", True),
            enable_email_check=config.get("enable_email_check", True),
            enable_phone_check=config.get("enable_phone_check", True),
        )


# ── Prompt Injection ──────────────────────────────────────────────────────────

class PromptInjectionGuardrailBuilder(BaseGuardrailBuilder):
    type = "prompt_injection"
    label = "提示词注入检测"

    extra_fields = [
        {
            "name": "injection_patterns",
            "type": "str",
            "required": False,
            "order": 1,
        },
    ]

    field_meta = {
        "injection_patterns": {
            "label": "自定义检测关键词",
            "group": "基础配置",
            "span": 24,
            "placeholder": "每行一个关键词，留空使用内置规则",
            "tooltip": "留空使用 agno 内置关键词列表（含 ignore previous instructions 等）",
        },
    }

    def _sync_build(self, config: dict) -> Any:
        from agno.guardrails.prompt_injection import PromptInjectionGuardrail

        raw = config.get("injection_patterns") or ""
        patterns = [p.strip() for p in raw.splitlines() if p.strip()] or None

        return PromptInjectionGuardrail(injection_patterns=patterns)
