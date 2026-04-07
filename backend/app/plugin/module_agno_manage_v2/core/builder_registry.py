"""
全局 Builder 注册表。

key = (category, type) tuple
value = BaseBuilder 实例
"""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.plugin.module_agno_manage_v2.core.builder_base import BaseBuilder

# ── Model Builders ──────────────────────────────────────────────────────────
from app.plugin.module_agno_manage_v2.builders.models.openai import OpenAIModelBuilder
from app.plugin.module_agno_manage_v2.builders.models.anthropic import AnthropicModelBuilder
from app.plugin.module_agno_manage_v2.builders.models.ollama import OllamaModelBuilder
from app.plugin.module_agno_manage_v2.builders.models.groq import GroqModelBuilder
from app.plugin.module_agno_manage_v2.builders.models.deepseek import DeepSeekModelBuilder
from app.plugin.module_agno_manage_v2.builders.models.mistral import MistralModelBuilder
from app.plugin.module_agno_manage_v2.builders.models.azure import AzureModelBuilder
from app.plugin.module_agno_manage_v2.builders.models.cohere import CohereModelBuilder
from app.plugin.module_agno_manage_v2.builders.models.together import TogetherModelBuilder
from app.plugin.module_agno_manage_v2.builders.models.openai_like import OpenAILikeModelBuilder

# ── Embedder Builders ────────────────────────────────────────────────────────
from app.plugin.module_agno_manage_v2.builders.embedders.openai import OpenAIEmbedderBuilder
from app.plugin.module_agno_manage_v2.builders.embedders.azure import AzureEmbedderBuilder
from app.plugin.module_agno_manage_v2.builders.embedders.ollama import OllamaEmbedderBuilder
from app.plugin.module_agno_manage_v2.builders.embedders.cohere import CohereEmbedderBuilder
from app.plugin.module_agno_manage_v2.builders.embedders.google import GoogleEmbedderBuilder

# ── Reader Builders ──────────────────────────────────────────────────────────
from app.plugin.module_agno_manage_v2.builders.readers.pdf import PdfReaderBuilder
from app.plugin.module_agno_manage_v2.builders.readers.docx import DocxReaderBuilder
from app.plugin.module_agno_manage_v2.builders.readers.text import TextReaderBuilder
from app.plugin.module_agno_manage_v2.builders.readers.csv import CsvReaderBuilder
from app.plugin.module_agno_manage_v2.builders.readers.json_reader import JsonReaderBuilder
from app.plugin.module_agno_manage_v2.builders.readers.website import WebsiteReaderBuilder
from app.plugin.module_agno_manage_v2.builders.readers.youtube import YoutubeReaderBuilder
from app.plugin.module_agno_manage_v2.builders.readers.arxiv import ArxivReaderBuilder

# ── Toolkit Builders ─────────────────────────────────────────────────────────
from app.plugin.module_agno_manage_v2.builders.toolkits.duckduckgo import DuckDuckGoBuilder
from app.plugin.module_agno_manage_v2.builders.toolkits.python import PythonToolsBuilder
from app.plugin.module_agno_manage_v2.builders.toolkits.custom import CustomToolkitBuilder

# ── Knowledge Builders ───────────────────────────────────────────────────────
from app.plugin.module_agno_manage_v2.builders.knowledge.base import KnowledgeBuilder

# ── Agent Builders ───────────────────────────────────────────────────────────
from app.plugin.module_agno_manage_v2.builders.agents.base import AgentBuilder

# ── Team Builders ────────────────────────────────────────────────────────────
from app.plugin.module_agno_manage_v2.builders.teams.base import TeamBuilder

# 注册表：(category, type) -> Builder 实例
builder_registry: dict[tuple[str, str], "BaseBuilder"] = {
    # models
    ("model", "openai"):      OpenAIModelBuilder(),
    ("model", "anthropic"):   AnthropicModelBuilder(),
    ("model", "ollama"):      OllamaModelBuilder(),
    ("model", "groq"):        GroqModelBuilder(),
    ("model", "deepseek"):    DeepSeekModelBuilder(),
    ("model", "mistral"):     MistralModelBuilder(),
    ("model", "azure"):       AzureModelBuilder(),
    ("model", "cohere"):      CohereModelBuilder(),
    ("model", "together"):    TogetherModelBuilder(),
    ("model", "openai_like"): OpenAILikeModelBuilder(),
    # embedders
    ("embedder", "openai"):   OpenAIEmbedderBuilder(),
    ("embedder", "azure"):    AzureEmbedderBuilder(),
    ("embedder", "ollama"):   OllamaEmbedderBuilder(),
    ("embedder", "cohere"):   CohereEmbedderBuilder(),
    ("embedder", "google"):   GoogleEmbedderBuilder(),
    # readers
    ("reader", "pdf"):        PdfReaderBuilder(),
    ("reader", "docx"):       DocxReaderBuilder(),
    ("reader", "text"):       TextReaderBuilder(),
    ("reader", "csv"):        CsvReaderBuilder(),
    ("reader", "json"):       JsonReaderBuilder(),
    ("reader", "website"):    WebsiteReaderBuilder(),
    ("reader", "youtube"):    YoutubeReaderBuilder(),
    ("reader", "arxiv"):      ArxivReaderBuilder(),
    # toolkits
    ("toolkit", "duckduckgo"): DuckDuckGoBuilder(),
    ("toolkit", "python"):     PythonToolsBuilder(),
    ("toolkit", "custom"):     CustomToolkitBuilder(),
    # knowledge
    ("knowledge", "base"):     KnowledgeBuilder(),
    # agents
    ("agent", "base"):         AgentBuilder(),
    # teams
    ("team", "base"):          TeamBuilder(),
}
