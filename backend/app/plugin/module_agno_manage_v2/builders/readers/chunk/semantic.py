from typing import Any
from app.plugin.module_agno_manage_v2.builders.readers.chunk.base import BaseChunkerBuilder


class SemanticChunkerBuilder(BaseChunkerBuilder):
    type = "SemanticChunker"
    label = "语义分块"
    extra_fields = [
        {
            "name": "chunk_size", "type": "int", "default": 5000, "required": False,
            "label": "分块大小", "group": "分块参数", "span": 12, "min": 100,
        },
        {
            "name": "embedder", "type": "ref_or_inline", "required": False,
            "label": "向量模型（Embedder）", "group": "分块参数", "span": 24,
            "source": "embedder",
            "tooltip": "用于计算语义相似度，不填则使用 OpenAI Embedder",
        },
        {
            "name": "similarity_threshold", "type": "float", "default": 0.5, "required": False,
            "label": "相似度阈值", "group": "分块参数", "span": 8,
            "min": 0.0, "max": 1.0, "step": 0.05,
            "tooltip": "低于此值触发分块，越小分块越细",
        },
        {
            "name": "similarity_window", "type": "int", "default": 3, "required": False,
            "label": "相似度窗口", "group": "分块参数", "span": 8, "min": 1,
            "tooltip": "计算相似度时前后参考的句子数",
        },
        {
            "name": "min_sentences_per_chunk", "type": "int", "default": 1, "required": False,
            "label": "最少句子/块", "group": "分块参数", "span": 8, "min": 1,
        },
    ]

    def build(self, config: dict, resolver) -> Any:
        from agno.knowledge.chunking.semantic import SemanticChunking
        embedder = resolver.resolve(config.get("embedder")) if config.get("embedder") else None
        kwargs: dict = {"chunk_size": config.get("chunk_size", 5000)}
        if embedder is not None:
            kwargs["embedder"] = embedder
        for k in ("similarity_threshold", "similarity_window", "min_sentences_per_chunk"):
            if k in config:
                kwargs[k] = config[k]
        return SemanticChunking(**kwargs)
