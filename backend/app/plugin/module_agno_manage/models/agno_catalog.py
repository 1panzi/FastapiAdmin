# -*- coding: utf-8 -*-
"""Agno 支持的 LLM 提供商元数据，供前端创建模型时选择。"""
from typing import TypedDict


class ModelProviderInfo(TypedDict):
    provider: str            # registry key, e.g. "openai"
    label: str               # display name, e.g. "OpenAI"
    agno_class: str          # Agno class name
    agno_module: str         # import path
    needs_api_key: bool
    needs_base_url: bool     # 是否有 base_url 参数
    base_url_label: str      # base_url 字段说明，没有时为空字符串
    description: str
    popular_models: list[str]  # 常见 model_id 示例


_PROVIDERS: list[ModelProviderInfo] = [
    {
        "provider": "openai",
        "label": "OpenAI",
        "agno_class": "OpenAIChat",
        "agno_module": "agno.models.openai",
        "needs_api_key": True,
        "needs_base_url": False,
        "base_url_label": "",
        "description": "OpenAI GPT 系列模型",
        "popular_models": ["gpt-4o", "gpt-4o-mini", "gpt-4-turbo", "gpt-3.5-turbo"],
    },
    {
        "provider": "anthropic",
        "label": "Anthropic (Claude)",
        "agno_class": "Claude",
        "agno_module": "agno.models.anthropic",
        "needs_api_key": True,
        "needs_base_url": False,
        "base_url_label": "",
        "description": "Anthropic Claude 系列模型",
        "popular_models": ["claude-opus-4-5", "claude-sonnet-4-5", "claude-haiku-4-5"],
    },
    {
        "provider": "google",
        "label": "Google (Gemini)",
        "agno_class": "Gemini",
        "agno_module": "agno.models.google",
        "needs_api_key": True,
        "needs_base_url": False,
        "base_url_label": "",
        "description": "Google Gemini 系列模型",
        "popular_models": ["gemini-2.0-flash", "gemini-1.5-pro", "gemini-1.5-flash"],
    },
    {
        "provider": "ollama",
        "label": "Ollama",
        "agno_class": "Ollama",
        "agno_module": "agno.models.ollama",
        "needs_api_key": False,
        "needs_base_url": True,
        "base_url_label": "Ollama 服务地址（默认 http://localhost:11434）",
        "description": "本地部署的 Ollama 模型",
        "popular_models": ["llama3.3", "llama3.2", "qwen2.5", "deepseek-r1", "mistral"],
    },
    {
        "provider": "groq",
        "label": "Groq",
        "agno_class": "Groq",
        "agno_module": "agno.models.groq",
        "needs_api_key": True,
        "needs_base_url": False,
        "base_url_label": "",
        "description": "Groq 超高速推理服务",
        "popular_models": ["llama-3.3-70b-versatile", "llama-3.1-8b-instant", "mixtral-8x7b-32768"],
    },
    {
        "provider": "deepseek",
        "label": "DeepSeek",
        "agno_class": "DeepSeek",
        "agno_module": "agno.models.deepseek",
        "needs_api_key": True,
        "needs_base_url": False,
        "base_url_label": "",
        "description": "DeepSeek 系列模型",
        "popular_models": ["deepseek-chat", "deepseek-reasoner"],
    },
    {
        "provider": "mistral",
        "label": "Mistral AI",
        "agno_class": "MistralChat",
        "agno_module": "agno.models.mistral",
        "needs_api_key": True,
        "needs_base_url": False,
        "base_url_label": "",
        "description": "Mistral AI 系列模型",
        "popular_models": ["mistral-large-latest", "mistral-small-latest", "open-mistral-7b"],
    },
    {
        "provider": "azure",
        "label": "Azure OpenAI",
        "agno_class": "AzureOpenAI",
        "agno_module": "agno.models.azure",
        "needs_api_key": True,
        "needs_base_url": True,
        "base_url_label": "Azure 端点地址（azure_endpoint）",
        "description": "微软 Azure 托管的 OpenAI 模型",
        "popular_models": ["gpt-4o", "gpt-4", "gpt-35-turbo"],
    },
    {
        "provider": "cohere",
        "label": "Cohere",
        "agno_class": "CohereChat",
        "agno_module": "agno.models.cohere",
        "needs_api_key": True,
        "needs_base_url": False,
        "base_url_label": "",
        "description": "Cohere Command 系列模型",
        "popular_models": ["command-r-plus", "command-r", "command"],
    },
    {
        "provider": "together",
        "label": "Together AI",
        "agno_class": "Together",
        "agno_module": "agno.models.together",
        "needs_api_key": True,
        "needs_base_url": False,
        "base_url_label": "",
        "description": "Together AI 开源模型托管",
        "popular_models": ["meta-llama/Llama-3-70b-chat-hf", "mistralai/Mixtral-8x7B-Instruct-v0.1"],
    },
    {
        "provider": "openai_like",
        "label": "OpenAI 兼容接口",
        "agno_class": "OpenAIChat",
        "agno_module": "agno.models.openai",
        "needs_api_key": True,
        "needs_base_url": True,
        "base_url_label": "自定义 API 地址（如 vLLM/LM Studio/本地服务）",
        "description": "兼容 OpenAI 接口的自定义或私有模型服务",
        "popular_models": [],
    },
]


def list_model_providers() -> list[ModelProviderInfo]:
    return _PROVIDERS


def get_provider_names() -> list[str]:
    return [p["provider"] for p in _PROVIDERS]
