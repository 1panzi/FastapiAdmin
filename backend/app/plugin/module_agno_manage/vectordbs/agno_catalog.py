"""Agno 支持的向量数据库类型元数据。"""
from typing import TypedDict


class VectorDbTypeInfo(TypedDict):
    db_type: str
    label: str
    agno_class: str
    agno_module: str
    description: str
    needs_embedder: bool
    config_example: dict   # 示例 config 参数


_TYPES: list[VectorDbTypeInfo] = [
    {
        "db_type": "pgvector",
        "label": "PostgreSQL + pgvector",
        "agno_class": "PgVector",
        "agno_module": "agno.vectordb.pgvector",
        "description": "基于 PostgreSQL 的向量扩展，开发/生产推荐",
        "needs_embedder": True,
        "config_example": {"table_name": "embeddings", "db_url": "postgresql+psycopg://..."},
    },
    {
        "db_type": "qdrant",
        "label": "Qdrant",
        "agno_class": "Qdrant",
        "agno_module": "agno.vectordb.qdrant",
        "description": "高性能向量搜索引擎",
        "needs_embedder": True,
        "config_example": {"collection": "my_docs", "url": "http://localhost:6333"},
    },
    {
        "db_type": "pinecone",
        "label": "Pinecone",
        "agno_class": "Pinecone",
        "agno_module": "agno.vectordb.pinecone",
        "description": "全托管向量数据库云服务",
        "needs_embedder": True,
        "config_example": {"index_name": "my-index", "api_key": "..."},
    },
    {
        "db_type": "chroma",
        "label": "ChromaDB",
        "agno_class": "ChromaDb",
        "agno_module": "agno.vectordb.chroma",
        "description": "轻量级本地向量数据库，适合原型开发",
        "needs_embedder": True,
        "config_example": {"collection": "my_docs", "path": "/tmp/chroma"},
    },
    {
        "db_type": "milvus",
        "label": "Milvus",
        "agno_class": "Milvus",
        "agno_module": "agno.vectordb.milvus",
        "description": "开源向量数据库，支持大规模生产部署",
        "needs_embedder": True,
        "config_example": {"collection": "my_docs", "uri": "http://localhost:19530"},
    },
    {
        "db_type": "weaviate",
        "label": "Weaviate",
        "agno_class": "Weaviate",
        "agno_module": "agno.vectordb.weaviate",
        "description": "开源向量数据库，支持混合搜索",
        "needs_embedder": True,
        "config_example": {"collection": "MyDocs", "url": "http://localhost:8080"},
    },
    {
        "db_type": "lancedb",
        "label": "LanceDB",
        "agno_class": "LanceDb",
        "agno_module": "agno.vectordb.lancedb",
        "description": "嵌入式向量数据库，零依赖本地存储",
        "needs_embedder": True,
        "config_example": {"table_name": "docs", "uri": "/tmp/lancedb"},
    },
    {
        "db_type": "mongodb",
        "label": "MongoDB Atlas Vector Search",
        "agno_class": "MongoDbVector",
        "agno_module": "agno.vectordb.mongodb",
        "description": "MongoDB Atlas 向量搜索",
        "needs_embedder": True,
        "config_example": {"collection": "docs", "db_url": "mongodb+srv://...", "database": "mydb"},
    },
]


def list_vectordb_types() -> list[VectorDbTypeInfo]:
    return _TYPES


def get_vectordb_type_names() -> list[str]:
    return [t["db_type"] for t in _TYPES]
