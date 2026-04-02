# -*- coding: utf-8 -*-
"""Agno 支持的知识库类型元数据。"""
from typing import TypedDict


class KnowledgeTypeInfo(TypedDict):
    knowledge_type: str
    label: str
    agno_class: str
    agno_module: str
    description: str
    config_example: dict


_TYPES: list[KnowledgeTypeInfo] = [
    {
        "knowledge_type": "pdf",
        "label": "PDF 文档",
        "agno_class": "PDFKnowledgeBase",
        "agno_module": "agno.knowledge.pdf",
        "description": "从 PDF 文件构建知识库",
        "config_example": {"path": "/data/docs/"},
    },
    {
        "knowledge_type": "pdf_url",
        "label": "PDF URL",
        "agno_class": "PDFUrlKnowledgeBase",
        "agno_module": "agno.knowledge.pdf_url",
        "description": "从 PDF URL 构建知识库",
        "config_example": {"urls": ["https://example.com/doc.pdf"]},
    },
    {
        "knowledge_type": "text",
        "label": "文本文件",
        "agno_class": "TextKnowledgeBase",
        "agno_module": "agno.knowledge.text",
        "description": "从纯文本文件构建知识库",
        "config_example": {"path": "/data/texts/"},
    },
    {
        "knowledge_type": "url",
        "label": "网页 URL",
        "agno_class": "UrlKnowledgeBase",
        "agno_module": "agno.knowledge.url",
        "description": "从网页 URL 抓取内容构建知识库",
        "config_example": {"urls": ["https://docs.example.com/"]},
    },
    {
        "knowledge_type": "website",
        "label": "网站爬取",
        "agno_class": "WebsiteKnowledgeBase",
        "agno_module": "agno.knowledge.website",
        "description": "递归爬取整个网站构建知识库",
        "config_example": {"urls": ["https://docs.example.com/"], "max_links": 10},
    },
    {
        "knowledge_type": "docx",
        "label": "Word 文档",
        "agno_class": "DocxKnowledgeBase",
        "agno_module": "agno.knowledge.docx",
        "description": "从 Word .docx 文件构建知识库",
        "config_example": {"path": "/data/docs/"},
    },
    {
        "knowledge_type": "json",
        "label": "JSON / JSONL",
        "agno_class": "JSONKnowledgeBase",
        "agno_module": "agno.knowledge.json",
        "description": "从 JSON 或 JSONL 文件构建知识库",
        "config_example": {"path": "/data/data.jsonl"},
    },
    {
        "knowledge_type": "csv",
        "label": "CSV 文件",
        "agno_class": "CSVKnowledgeBase",
        "agno_module": "agno.knowledge.csv",
        "description": "从 CSV 文件构建知识库",
        "config_example": {"path": "/data/data.csv"},
    },
    {
        "knowledge_type": "arxiv",
        "label": "ArXiv 论文",
        "agno_class": "ArxivKnowledgeBase",
        "agno_module": "agno.knowledge.arxiv",
        "description": "从 ArXiv 论文构建知识库",
        "config_example": {"queries": ["machine learning", "LLM"]},
    },
    {
        "knowledge_type": "combined",
        "label": "混合知识库",
        "agno_class": "CombinedKnowledgeBase",
        "agno_module": "agno.knowledge.combined",
        "description": "合并多个知识库",
        "config_example": {},
    },
]


def list_knowledge_types() -> list[KnowledgeTypeInfo]:
    return _TYPES


def get_knowledge_type_names() -> list[str]:
    return [t["knowledge_type"] for t in _TYPES]
