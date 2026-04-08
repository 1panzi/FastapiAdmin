"""
全局 Builder 注册表。

key = (category, type) tuple
value = BaseBuilder 实例

- Reader: 每种类型独立 Builder 文件，BaseReaderBuilder 负责 chunking schema 动态生成
- Toolkit: GenericToolkitBuilder 按 catalog 懒加载（100+ agno 工具，不逐一写 Builder）
"""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.plugin.module_agno_manage_v2.core.builder_base import BaseBuilder

# ── Model Builders ──────────────────────────────────────────────────────────
# ── Agent Builders ───────────────────────────────────────────────────────────
from app.plugin.module_agno_manage_v2.builders.agents.base import AgentBuilder

# ── Compress Builders ─────────────────────────────────────────────────────────
from app.plugin.module_agno_manage_v2.builders.compress.base import CompressionManagerBuilder

# ── Culture Builders ──────────────────────────────────────────────────────────
from app.plugin.module_agno_manage_v2.builders.culture.base import CultureManagerBuilder
from app.plugin.module_agno_manage_v2.builders.embedders.azure import AzureEmbedderBuilder
from app.plugin.module_agno_manage_v2.builders.embedders.cohere import CohereEmbedderBuilder
from app.plugin.module_agno_manage_v2.builders.embedders.google import GoogleEmbedderBuilder
from app.plugin.module_agno_manage_v2.builders.embedders.ollama import OllamaEmbedderBuilder

# ── Embedder Builders ────────────────────────────────────────────────────────
from app.plugin.module_agno_manage_v2.builders.embedders.openai import OpenAIEmbedderBuilder

# ── Guardrail Builders ────────────────────────────────────────────────────────
from app.plugin.module_agno_manage_v2.builders.guardrails.base import (
    OpenAIModerationGuardrailBuilder,
    PIIDetectionGuardrailBuilder,
    PromptInjectionGuardrailBuilder,
)

# ── Knowledge Builders ───────────────────────────────────────────────────────
from app.plugin.module_agno_manage_v2.builders.knowledge.base import KnowledgeBuilder

# ── Learn Builders ────────────────────────────────────────────────────────────
from app.plugin.module_agno_manage_v2.builders.learn.base import LearningMachineBuilder

# ── Memory Builders ───────────────────────────────────────────────────────────
from app.plugin.module_agno_manage_v2.builders.memory.base import MemoryManagerBuilder
from app.plugin.module_agno_manage_v2.builders.models.anthropic import AnthropicModelBuilder
from app.plugin.module_agno_manage_v2.builders.models.azure import AzureModelBuilder
from app.plugin.module_agno_manage_v2.builders.models.cohere import CohereModelBuilder
from app.plugin.module_agno_manage_v2.builders.models.deepseek import DeepSeekModelBuilder
from app.plugin.module_agno_manage_v2.builders.models.groq import GroqModelBuilder
from app.plugin.module_agno_manage_v2.builders.models.mistral import MistralModelBuilder
from app.plugin.module_agno_manage_v2.builders.models.ollama import OllamaModelBuilder
from app.plugin.module_agno_manage_v2.builders.models.openai import OpenAIModelBuilder
from app.plugin.module_agno_manage_v2.builders.models.openai_like import OpenAILikeModelBuilder
from app.plugin.module_agno_manage_v2.builders.models.together import TogetherModelBuilder
from app.plugin.module_agno_manage_v2.builders.readers.arxiv import ArxivReaderBuilder
from app.plugin.module_agno_manage_v2.builders.readers.csv import CsvReaderBuilder
from app.plugin.module_agno_manage_v2.builders.readers.docx import DocxReaderBuilder
from app.plugin.module_agno_manage_v2.builders.readers.json_reader import JsonReaderBuilder

# ── Reader Builders ───────────────────────────────────────────────────────────
from app.plugin.module_agno_manage_v2.builders.readers.pdf import PdfReaderBuilder
from app.plugin.module_agno_manage_v2.builders.readers.text import TextReaderBuilder
from app.plugin.module_agno_manage_v2.builders.readers.website import WebsiteReaderBuilder
from app.plugin.module_agno_manage_v2.builders.readers.youtube import YoutubeReaderBuilder

# ── Reasoning Builders ────────────────────────────────────────────────────────
from app.plugin.module_agno_manage_v2.builders.reasoning.base import ReasoningBuilder

# ── SessionSummary Builders ───────────────────────────────────────────────────
from app.plugin.module_agno_manage_v2.builders.session_summary.base import (
    SessionSummaryManagerBuilder,
)

# ── Skill Builders ────────────────────────────────────────────────────────────
from app.plugin.module_agno_manage_v2.builders.skills.base import SkillBuilder

# ── Team Builders ────────────────────────────────────────────────────────────
from app.plugin.module_agno_manage_v2.builders.teams.base import TeamBuilder

# ── Toolkit Builders (Catalog-based) ─────────────────────────────────────────
from app.plugin.module_agno_manage_v2.builders.toolkits.catalog import TOOLKIT_CATALOG
from app.plugin.module_agno_manage_v2.builders.toolkits.custom import CustomToolkitBuilder
from app.plugin.module_agno_manage_v2.builders.toolkits.generic import GenericToolkitBuilder
from app.plugin.module_agno_manage_v2.builders.vectordbs.chroma import ChromaBuilder
from app.plugin.module_agno_manage_v2.builders.vectordbs.lancedb import LanceDbBuilder
from app.plugin.module_agno_manage_v2.builders.vectordbs.milvus import MilvusBuilder
from app.plugin.module_agno_manage_v2.builders.vectordbs.mongodb import MongodbBuilder

# ── DB Builders ──────────────────────────────────────────────────────────────
from app.plugin.module_agno_manage_v2.builders.dbs.sqlite import SqliteDbBuilder
from app.plugin.module_agno_manage_v2.builders.dbs.postgres import PostgresDbBuilder
from app.plugin.module_agno_manage_v2.builders.dbs.in_memory import InMemoryDbBuilder

# ── VectorDB Builders ────────────────────────────────────────────────────────
from app.plugin.module_agno_manage_v2.builders.vectordbs.pgvector import PgVectorBuilder
from app.plugin.module_agno_manage_v2.builders.vectordbs.pinecone import PineconeBuilder
from app.plugin.module_agno_manage_v2.builders.vectordbs.qdrant import QdrantBuilder
from app.plugin.module_agno_manage_v2.builders.vectordbs.weaviate import WeaviateBuilder

# ── 注册表 ────────────────────────────────────────────────────────────────────
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
    # vectordbs
    ("vectordb", "pgvector"):  PgVectorBuilder(),
    ("vectordb", "qdrant"):    QdrantBuilder(),
    ("vectordb", "chroma"):    ChromaBuilder(),
    ("vectordb", "pinecone"):  PineconeBuilder(),
    ("vectordb", "weaviate"):  WeaviateBuilder(),
    ("vectordb", "milvus"):    MilvusBuilder(),
    ("vectordb", "mongodb"):   MongodbBuilder(),
    ("vectordb", "lancedb"):   LanceDbBuilder(),
    # readers
    ("reader", "pdf"):     PdfReaderBuilder(),
    ("reader", "docx"):    DocxReaderBuilder(),
    ("reader", "text"):    TextReaderBuilder(),
    ("reader", "csv"):     CsvReaderBuilder(),
    ("reader", "json"):    JsonReaderBuilder(),
    ("reader", "website"): WebsiteReaderBuilder(),
    ("reader", "youtube"): YoutubeReaderBuilder(),
    ("reader", "arxiv"):   ArxivReaderBuilder(),
    # knowledge
    ("knowledge", "base"): KnowledgeBuilder(),
    # db
    ("db", "sqlite"):    SqliteDbBuilder(),
    ("db", "postgres"):  PostgresDbBuilder(),
    ("db", "in_memory"): InMemoryDbBuilder(),
    # agents
    ("agent", "base"):     AgentBuilder(),
    # teams
    ("team", "base"):      TeamBuilder(),
    # memory
    ("memory", "base"):    MemoryManagerBuilder(),
    # learn
    ("learn", "base"):     LearningMachineBuilder(),
    # compress
    ("compress", "base"):  CompressionManagerBuilder(),
    # guardrails
    ("guardrail", "openai_moderation"):  OpenAIModerationGuardrailBuilder(),
    ("guardrail", "pii_detection"):      PIIDetectionGuardrailBuilder(),
    ("guardrail", "prompt_injection"):   PromptInjectionGuardrailBuilder(),
    # reasoning
    ("reasoning", "base"): ReasoningBuilder(),
    # culture
    ("culture", "base"):          CultureManagerBuilder(),
    # session_summary
    ("session_summary", "base"):  SessionSummaryManagerBuilder(),
    # skills
    ("skill", "base"):            SkillBuilder(),
}

# toolkits：按 catalog 批量注册 + custom 单独注册
for _type_key in TOOLKIT_CATALOG:
    builder_registry[("toolkit", _type_key)] = GenericToolkitBuilder(_type_key)
builder_registry[("toolkit", "custom")] = CustomToolkitBuilder()
