"""Agno 支持的 Embedder 提供商元数据。"""
from typing import TypedDict


class EmbedderProviderInfo(TypedDict):
    provider: str
    label: str
    agno_class: str
    agno_module: str
    needs_api_key: bool
    needs_base_url: bool
    base_url_label: str
    description: str
    popular_models: list[str]
    default_dimensions: int | None


_PROVIDERS: list[EmbedderProviderInfo] = [
    {
        "provider": "openai",
        "label": "OpenAI",
        "agno_class": "OpenAIEmbedder",
        "agno_module": "agno.embedder.openai",
        "needs_api_key": True,
        "needs_base_url": False,
        "base_url_label": "",
        "description": "OpenAI 文本嵌入模型",
        "popular_models": ["text-embedding-3-small", "text-embedding-3-large", "text-embedding-ada-002"],
        "default_dimensions": 1536,
    },
    {
        "provider": "azure",
        "label": "Azure OpenAI",
        "agno_class": "AzureOpenAIEmbedder",
        "agno_module": "agno.embedder.azure",
        "needs_api_key": True,
        "needs_base_url": True,
        "base_url_label": "Azure 端点地址（azure_endpoint）",
        "description": "Azure 托管的 OpenAI 嵌入模型",
        "popular_models": ["text-embedding-3-small", "text-embedding-ada-002"],
        "default_dimensions": 1536,
    },
    {
        "provider": "ollama",
        "label": "Ollama",
        "agno_class": "OllamaEmbedder",
        "agno_module": "agno.embedder.ollama",
        "needs_api_key": False,
        "needs_base_url": True,
        "base_url_label": "Ollama 服务地址（默认 http://localhost:11434）",
        "description": "本地 Ollama 嵌入模型",
        "popular_models": ["nomic-embed-text", "mxbai-embed-large", "all-minilm"],
        "default_dimensions": 768,
    },
    {
        "provider": "cohere",
        "label": "Cohere",
        "agno_class": "CohereEmbedder",
        "agno_module": "agno.embedder.cohere",
        "needs_api_key": True,
        "needs_base_url": False,
        "base_url_label": "",
        "description": "Cohere 嵌入模型",
        "popular_models": ["embed-english-v3.0", "embed-multilingual-v3.0"],
        "default_dimensions": 1024,
    },
    {
        "provider": "google",
        "label": "Google (Gemini)",
        "agno_class": "GeminiEmbedder",
        "agno_module": "agno.embedder.google",
        "needs_api_key": True,
        "needs_base_url": False,
        "base_url_label": "",
        "description": "Google Gemini 嵌入模型",
        "popular_models": ["models/text-embedding-004", "models/embedding-001"],
        "default_dimensions": 768,
    },
    {
        "provider": "huggingface",
        "label": "HuggingFace",
        "agno_class": "HuggingfaceCustomEmbedder",
        "agno_module": "agno.embedder.huggingface",
        "needs_api_key": False,
        "needs_base_url": False,
        "base_url_label": "",
        "description": "本地 HuggingFace 嵌入模型",
        "popular_models": ["sentence-transformers/all-MiniLM-L6-v2", "BAAI/bge-large-zh-v1.5"],
        "default_dimensions": 384,
    },
    {
        "provider": "openai_like",
        "label": "OpenAI 兼容接口",
        "agno_class": "OpenAIEmbedder",
        "agno_module": "agno.embedder.openai",
        "needs_api_key": True,
        "needs_base_url": True,
        "base_url_label": "自定义嵌入服务地址",
        "description": "兼容 OpenAI 嵌入接口的自定义服务",
        "popular_models": [],
        "default_dimensions": None,
    },
]


def list_embedder_providers() -> list[EmbedderProviderInfo]:
    return _PROVIDERS


def get_embedder_provider_names() -> list[str]:
    return [p["provider"] for p in _PROVIDERS]
