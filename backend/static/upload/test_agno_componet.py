"""
test-agent.py

验证两个核心机制：
  机制一：Callable Factory + cache_callables=False（热插拔）
  机制二：共享可变列表（动态注册，AgentOS 立即可路由）

模拟设计文档中的 RuntimeRegistry 行为：
  - _bindings: 内存 dict 代替 platform_bindings 表
  - _toolkit_map: 内存 dict 代替 registry._toolkit_map
  - 热插拔只需改 _bindings，下次 run 自动生效
"""

from typing import List

from agno.agent import Agent
from agno.db.sqlite import SqliteDb
from agno.models.ollama import Ollama
from agno.os import AgentOS
from agno.tools.duckduckgo import DuckDuckGoTools
from agno.tools.calculator import CalculatorTools
from agno.knowledge.embedder.openai_like import OpenAILikeEmbedder


agnodb_db = SqliteDb(db_file="./agno.db")

# ── 模型 ──────────────────────────────────────────────────────────────────────
model = Ollama(
    id="isotnek/qwen3.5:9B-Unsloth-UD-Q4_K_XL",
    host="http://192.168.81.15:7869",
)

#测试模型
agent = Agent(id="agno_test_lcoal",model=model)
agent.print_response("你好")
#测试工具
agent = Agent(id="agno_test_lcoal",model=model,tools=[CalculatorTools()])
agent.print_response("你好,你有什么工具，请你搜索 计算2*5")

#测试embeder
embeder = OpenAILikeEmbedder(id="qwen3-e4b",
    dimensions=512,base_url="http://192.168.81.51:9998/v1")
# print(embeder.get_embedding_and_usage("你好"))
# print(embeder.get_embedding("你好"))

## 向量数据库
from agno.vectordb.chroma import ChromaDb
from agno.vectordb.search import SearchType
vector_db=ChromaDb(
        name="agno_docs",
        collection="agno_docs",
        path="tmp/chromadb",
        persistent_client=True,
        # Enable hybrid search - combines vector similarity with keyword matching using RRF
        search_type=SearchType.hybrid,
        # RRF (Reciprocal Rank Fusion) constant - controls ranking smoothness.
        # Higher values (e.g., 60) give more weight to lower-ranked results,
        # Lower values make top results more dominant. Default is 60 (per original RRF paper).
        hybrid_rrf_k=60,
        embedder=embeder,
    )

#测试知识库
from agno.knowledge import Knowledge
knowledge = Knowledge(
    name="Agno Documentation",
    vector_db=vector_db,
    # Return 5 results on query
    max_results=5,
    # Store metadata about the contents in the agent database, table_name="agno_knowledge"
    contents_db=agnodb_db,
)
knowledge.insert(text_content="张杰的个人简介")
kg_result = knowledge.search("个人简介")
print(kg_result)



# agent_os = AgentOS(
#     base_app=app,
#     agents=agent_pool,
#     db=SqliteDb(db_file="./agno.db"),
# )
# app = agent_os.get_app()


# # ── 启动 ───────────────────────────────────────────────────────────────────────
# if __name__ == "__main__":
#     import uvicorn
#     print("\n可用工具 ID（用于绑定测试）：")
#     print(f"  搜索工具: {TOOLKIT_ID_SEARCH}")
#     print(f"  财经工具: {TOOLKIT_ID_FINANCE}")
#     print(f"\n默认 Agent ID: {AGENT_ID_DEFAULT}")
#     print("\n测试流程：")
#     print("  1. GET  /management/agents                          查看已注册 Agent")
#     print("  2. POST /v1/agents/agent-default-001/runs           发消息（带搜索工具）")
#     print(f"  3. PATCH /management/agents/{AGENT_ID_DEFAULT}/bindings/<toolkit_id>  热插拔工具")
#     print("  4. POST /v1/agents/agent-default-001/runs           再发消息（工具已变化）")
#     print("  5. POST /management/agents                          动态创建新 Agent")
#     uvicorn.run(app, host="0.0.0.0", port=9008)
