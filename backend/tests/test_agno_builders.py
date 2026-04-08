"""
test_agno_builders.py — 测试 module_agno_manage_v2 各 Builder 的 build() 方法。

使用 MockResolver 代替数据库，支持：
  - inline 模式：直接传 {category, type, ...config} 构建子资源
  - ref 模式：从预置的 refs 字典按 uuid 查找再构建

运行：
  cd backend
  pytest tests/test_agno_builders.py -v
"""

import inspect
import uuid
from typing import Any

import pytest

# ─────────────────────────────────────────────────────────────────────────────
# MockResolver：无需数据库，支持 inline + ref
# ─────────────────────────────────────────────────────────────────────────────


class MockResolver:
    """
    测试用 Resolver，功能与 RefResolver 相同，但用内存字典代替数据库。

    refs 格式：
        {
            "some-uuid": {
                "category": "model",
                "type": "openai",
                "model_id": "gpt-4o",
            }
        }
    """

    def __init__(self, refs: dict[str, dict] | None = None):
        self._refs = refs or {}
        self._cache: dict[str, Any] = {}

    async def resolve(self, value: dict | None) -> Any:
        if value is None:
            return None

        from app.plugin.module_agno_manage_v2.core.builder_registry import builder_registry

        if "ref" in value:
            ref_id = value["ref"]
            override = value.get("override") or {}
            cache_key = f"{ref_id}:{override}" if override else ref_id

            if cache_key in self._cache:
                return self._cache[cache_key]

            entry = self._refs.get(ref_id)
            if entry is None:
                raise ValueError(f"MockResolver: unknown ref '{ref_id}'")

            merged = {**entry, **override}
            category = merged.pop("category")
            type_ = merged.pop("type")
            builder = builder_registry[(category, type_)]
            result = builder.build(merged, self)
            if inspect.iscoroutine(result):
                result = await result
            self._cache[cache_key] = result
            return result

        # inline 模式
        value = dict(value)
        category = value.pop("category")
        type_ = value.pop("type")
        builder = builder_registry[(category, type_)]
        result = builder.build(value, self)
        if inspect.iscoroutine(result):
            result = await result
        return result

    async def resolve_list(self, values: list | None) -> list:
        if not values:
            return []
        results = []
        for v in values:
            obj = await self.resolve(v)
            if obj is not None:
                results.append(obj)
        return results


# ─────────────────────────────────────────────────────────────────────────────
# 公用 fixture
# ─────────────────────────────────────────────────────────────────────────────

@pytest.fixture
def resolver():
    """空 MockResolver，无预置 ref。"""
    return MockResolver()


def inline(category: str, type_: str, **kwargs) -> dict:
    """构造 inline 资源引用 dict，方便书写。"""
    return {"category": category, "type": type_, **kwargs}


# ═════════════════════════════════════════════════════════════════════════════
# 1. Model Builders
# ═════════════════════════════════════════════════════════════════════════════

class TestModelBuilders:

    @pytest.mark.asyncio
    async def test_openai_model(self, resolver):
        from agno.models.openai import OpenAIChat
        result = await resolver.resolve(inline(
            "model", "openai",
            model_id="gpt-4o",
            temperature=0.5,
            max_tokens=1024,
        ))
        assert isinstance(result, OpenAIChat)
        assert result.id == "gpt-4o"

    @pytest.mark.asyncio
    async def test_openai_model_defaults(self, resolver):
        """model_id 不填时也能构建。"""
        from agno.models.openai import OpenAIChat
        result = await resolver.resolve(inline("model", "openai"))
        assert isinstance(result, OpenAIChat)

    @pytest.mark.asyncio
    async def test_anthropic_model(self, resolver):
        from agno.models.anthropic import Claude
        result = await resolver.resolve(inline(
            "model", "anthropic",
            model_id="claude-opus-4-5",
        ))
        assert isinstance(result, Claude)

    @pytest.mark.asyncio
    async def test_deepseek_model(self, resolver):
        from agno.models.deepseek import DeepSeek
        result = await resolver.resolve(inline(
            "model", "deepseek",
            model_id="deepseek-chat",
        ))
        assert isinstance(result, DeepSeek)

    @pytest.mark.asyncio
    async def test_openai_like_model(self, resolver):
        """OpenAI-compatible 第三方模型（如本地 vLLM）。"""
        from agno.models.openai.like import OpenAILike
        result = await resolver.resolve(inline(
            "model", "openai_like",
            model_id="qwen2.5-72b",
            base_url="http://localhost:8000/v1",
        ))
        assert isinstance(result, OpenAILike)


# ═════════════════════════════════════════════════════════════════════════════
# 2. Embedder Builders
# ═════════════════════════════════════════════════════════════════════════════

class TestEmbedderBuilders:

    @pytest.mark.asyncio
    async def test_openai_embedder(self, resolver):
        from agno.knowledge.embedder.openai import OpenAIEmbedder
        result = await resolver.resolve(inline(
            "embedder", "openai",
            model="text-embedding-3-small",
            dimensions=1536,
        ))
        assert isinstance(result, OpenAIEmbedder)

    @pytest.mark.asyncio
    async def test_azure_embedder(self, resolver):
        from agno.knowledge.embedder.azure_openai import AzureOpenAIEmbedder
        result = await resolver.resolve(inline(
            "embedder", "azure",
            model="text-embedding-ada-002",
            azure_endpoint="https://my.openai.azure.com",
        ))
        assert isinstance(result, AzureOpenAIEmbedder)


# ═════════════════════════════════════════════════════════════════════════════
# 3. Toolkit Builders
# ═════════════════════════════════════════════════════════════════════════════

class TestToolkitBuilders:

    @pytest.mark.asyncio
    async def test_calculator_toolkit(self, resolver):
        from agno.tools.calculator import CalculatorTools
        result = await resolver.resolve(inline("toolkit", "calculator"))
        assert isinstance(result, CalculatorTools)

    @pytest.mark.asyncio
    async def test_wikipedia_toolkit(self, resolver):
        from agno.tools.wikipedia import WikipediaTools
        result = await resolver.resolve(inline("toolkit", "wikipedia"))
        assert isinstance(result, WikipediaTools)

    @pytest.mark.asyncio
    async def test_yfinance_toolkit(self, resolver):
        from agno.tools.yfinance import YFinanceTools
        result = await resolver.resolve(inline(
            "toolkit", "yfinance",
            stock_price=True,
            stock_fundamentals=True,
        ))
        assert isinstance(result, YFinanceTools)


# ═════════════════════════════════════════════════════════════════════════════
# 4. Chunker Builders
# ═════════════════════════════════════════════════════════════════════════════

class TestChunkerBuilders:

    @pytest.mark.asyncio
    async def test_fixed_size_chunker(self):
        from agno.knowledge.chunking.fixed import FixedSizeChunking

        from app.plugin.module_agno_manage_v2.builders.readers.chunk import CHUNKER_REGISTRY
        builder = CHUNKER_REGISTRY["FixedSizeChunker"]
        result = await builder.build({"chunk_size": 2000, "overlap": 100}, None)
        assert isinstance(result, FixedSizeChunking)

    @pytest.mark.asyncio
    async def test_recursive_chunker(self):
        from agno.knowledge.chunking.recursive import RecursiveChunking

        from app.plugin.module_agno_manage_v2.builders.readers.chunk import CHUNKER_REGISTRY
        builder = CHUNKER_REGISTRY["RecursiveChunker"]
        result = await builder.build({"chunk_size": 3000}, None)
        assert isinstance(result, RecursiveChunking)

    @pytest.mark.asyncio
    async def test_row_chunker(self):
        from agno.knowledge.chunking.row import RowChunking

        from app.plugin.module_agno_manage_v2.builders.readers.chunk import CHUNKER_REGISTRY
        builder = CHUNKER_REGISTRY["RowChunker"]
        result = await builder.build({"skip_header": True, "clean_rows": True}, None)
        assert isinstance(result, RowChunking)

    @pytest.mark.asyncio
    async def test_semantic_chunker_no_embedder(self, resolver):
        """SemanticChunker 不传 embedder 时仍能构建（使用默认）。"""
        from agno.knowledge.chunking.semantic import SemanticChunking

        from app.plugin.module_agno_manage_v2.builders.readers.chunk import CHUNKER_REGISTRY
        builder = CHUNKER_REGISTRY["SemanticChunker"]
        result = await builder.build({"chunk_size": 5000, "similarity_threshold": 0.6}, resolver)
        assert isinstance(result, SemanticChunking)

    @pytest.mark.asyncio
    async def test_semantic_chunker_with_inline_embedder(self, resolver):
        """SemanticChunker 通过 inline embedder 异步 resolve。"""
        from agno.knowledge.chunking.semantic import SemanticChunking

        from app.plugin.module_agno_manage_v2.builders.readers.chunk import CHUNKER_REGISTRY
        builder = CHUNKER_REGISTRY["SemanticChunker"]
        result = await builder.build(
            {
                "chunk_size": 5000,
                "embedder": inline("embedder", "openai", model="text-embedding-3-small"),
            },
            resolver,
        )
        assert isinstance(result, SemanticChunking)


# ═════════════════════════════════════════════════════════════════════════════
# 5. Skill Builder
# ═════════════════════════════════════════════════════════════════════════════

class TestSkillBuilder:

    @pytest.mark.asyncio
    async def test_inline_skill(self, resolver):
        from agno.skills import Skills
        result = await resolver.resolve(inline(
            "skill", "base",
            source="inline",
            name="sql_expert",
            description="SQL 查询优化专家",
            instructions="# SQL Expert\n\n当用户询问 SQL 问题时，请提供优化建议。",
            allowed_tools="sql, postgres",
        ))
        assert isinstance(result, Skills)

    @pytest.mark.asyncio
    async def test_inline_skill_no_allowed_tools(self, resolver):
        from agno.skills import Skills
        result = await resolver.resolve(inline(
            "skill", "base",
            source="inline",
            name="general_advisor",
            instructions="你是一个通用顾问。",
        ))
        assert isinstance(result, Skills)

    @pytest.mark.asyncio
    async def test_inline_skill_missing_name_raises(self, resolver):
        """inline 模式下 name 为空应抛出 ValueError。"""
        with pytest.raises(ValueError, match="name 不能为空"):
            await resolver.resolve(inline(
                "skill", "base",
                source="inline",
                instructions="没有名字的 skill",
            ))

    @pytest.mark.asyncio
    async def test_path_skill_missing_path_raises(self, resolver):
        """path 模式下 skill_path 为空应抛出 ValueError。"""
        with pytest.raises(ValueError, match="skill_path 不能为空"):
            await resolver.resolve(inline(
                "skill", "base",
                source="path",
                skill_path="",
            ))


# ═════════════════════════════════════════════════════════════════════════════
# 6. Memory / Learn / Compress / SessionSummary / Reasoning Builders
# ═════════════════════════════════════════════════════════════════════════════

class TestManagerBuilders:

    @pytest.mark.asyncio
    async def test_memory_manager(self, resolver):
        from agno.memory.manager import MemoryManager
        result = await resolver.resolve(inline(
            "memory", "base",
            model=inline("model", "openai", model_id="gpt-4o-mini"),
        ))
        assert isinstance(result, MemoryManager)

    @pytest.mark.asyncio
    async def test_learning_machine(self, resolver):
        from agno.learn.machine import LearningMachine
        result = await resolver.resolve(inline(
            "learn", "base",
            model=inline("model", "openai", model_id="gpt-4o-mini"),
            enable_user_profile=True,
            enable_user_memory=True,
        ))
        assert isinstance(result, LearningMachine)

    @pytest.mark.asyncio
    async def test_compression_manager(self, resolver):
        from agno.compression.manager import CompressionManager
        result = await resolver.resolve(inline(
            "compress", "base",
            model=inline("model", "openai", model_id="gpt-4o-mini"),
            compress_tool_results=True,
            compress_tool_results_limit=5,
        ))
        assert isinstance(result, CompressionManager)

    @pytest.mark.asyncio
    async def test_session_summary_manager(self, resolver):
        from agno.session.summary import SessionSummaryManager
        result = await resolver.resolve(inline(
            "session_summary", "base",
            model=inline("model", "openai", model_id="gpt-4o-mini"),
        ))
        assert isinstance(result, SessionSummaryManager)

    @pytest.mark.asyncio
    async def test_reasoning_builder_returns_dict(self, resolver):
        """ReasoningBuilder 返回参数 dict，而非 Agno 对象。"""
        result = await resolver.resolve(inline(
            "reasoning", "base",
            reasoning_model=inline("model", "openai", model_id="o1-mini"),
            min_steps=2,
            max_steps=8,
        ))
        assert isinstance(result, dict)
        assert result["min_steps"] == 2
        assert result["max_steps"] == 8

    @pytest.mark.asyncio
    async def test_culture_manager(self, resolver):
        from agno.culture.manager import CultureManager
        result = await resolver.resolve(inline(
            "culture", "base",
            model=inline("model", "openai", model_id="gpt-4o-mini"),
        ))
        assert isinstance(result, CultureManager)


# ═════════════════════════════════════════════════════════════════════════════
# 7. Guardrail Builders
# ═════════════════════════════════════════════════════════════════════════════

class TestGuardrailBuilders:

    @pytest.mark.asyncio
    async def test_openai_moderation(self, resolver):
        from agno.guardrails.openai import OpenAIModerationGuardrail
        result = await resolver.resolve(inline(
            "guardrail", "openai_moderation",
            moderation_model="omni-moderation-latest",
        ))
        assert isinstance(result, OpenAIModerationGuardrail)

    @pytest.mark.asyncio
    async def test_pii_detection(self, resolver):
        from agno.guardrails.pii import PIIDetectionGuardrail
        result = await resolver.resolve(inline(
            "guardrail", "pii_detection",
            mask_pii=True,
            enable_email_check=True,
            enable_phone_check=False,
        ))
        assert isinstance(result, PIIDetectionGuardrail)

    @pytest.mark.asyncio
    async def test_prompt_injection(self, resolver):
        from agno.guardrails.prompt_injection import PromptInjectionGuardrail
        result = await resolver.resolve(inline(
            "guardrail", "prompt_injection",
            injection_patterns="ignore previous instructions\nforget everything",
        ))
        assert isinstance(result, PromptInjectionGuardrail)

    @pytest.mark.asyncio
    async def test_prompt_injection_empty_patterns(self, resolver):
        """injection_patterns 为空时使用内置规则，不应报错。"""
        from agno.guardrails.prompt_injection import PromptInjectionGuardrail
        result = await resolver.resolve(inline("guardrail", "prompt_injection"))
        assert isinstance(result, PromptInjectionGuardrail)


# ═════════════════════════════════════════════════════════════════════════════
# 8. Agent Builder
# ═════════════════════════════════════════════════════════════════════════════

class TestAgentBuilder:

    @pytest.mark.asyncio
    async def test_agent_minimal(self, resolver):
        """最简 Agent：只有 model。"""
        from agno.agent import Agent
        result = await resolver.resolve(inline(
            "agent", "base",
            name="MinimalAgent",
            model=inline("model", "openai", model_id="gpt-4o"),
        ))
        assert isinstance(result, Agent)

    @pytest.mark.asyncio
    async def test_agent_with_tools(self, resolver):
        """Agent + 多个内联工具。"""
        from agno.agent import Agent
        result = await resolver.resolve(inline(
            "agent", "base",
            name="ToolAgent",
            instructions="你是一个工具助手。",
            model=inline("model", "openai", model_id="gpt-4o"),
            tools=[
                inline("toolkit", "calculator"),
                inline("toolkit", "wikipedia"),
            ],
            show_tool_calls=True,
        ))
        assert isinstance(result, Agent)

    @pytest.mark.asyncio
    async def test_agent_with_skill(self, resolver):
        """Agent + inline Skill。"""
        from agno.agent import Agent
        result = await resolver.resolve(inline(
            "agent", "base",
            name="SkillAgent",
            model=inline("model", "openai", model_id="gpt-4o"),
            skills=[
                inline(
                    "skill", "base",
                    source="inline",
                    name="coding_expert",
                    instructions="# 代码专家\n\n当用户询问编程问题时提供专业解答。",
                )
            ],
        ))
        assert isinstance(result, Agent)

    @pytest.mark.asyncio
    async def test_agent_with_memory(self, resolver):
        """Agent + MemoryManager。"""
        from agno.agent import Agent
        result = await resolver.resolve(inline(
            "agent", "base",
            name="MemoryAgent",
            model=inline("model", "openai", model_id="gpt-4o"),
            memory_manager=inline(
                "memory", "base",
                model=inline("model", "openai", model_id="gpt-4o-mini"),
            ),
            enable_agentic_memory=True,
            add_memories_to_context=True,
        ))
        assert isinstance(result, Agent)

    @pytest.mark.asyncio
    async def test_agent_with_guardrails(self, resolver):
        """Agent + 两条护栏。"""
        from agno.agent import Agent
        result = await resolver.resolve(inline(
            "agent", "base",
            name="SafeAgent",
            model=inline("model", "openai", model_id="gpt-4o"),
            guardrails=[
                inline("guardrail", "pii_detection", mask_pii=True),
                inline("guardrail", "prompt_injection"),
            ],
        ))
        assert isinstance(result, Agent)

    @pytest.mark.asyncio
    async def test_agent_with_reasoning(self, resolver):
        """Agent + reasoning_config。"""
        from agno.agent import Agent
        result = await resolver.resolve(inline(
            "agent", "base",
            name="ReasoningAgent",
            model=inline("model", "openai", model_id="gpt-4o"),
            reasoning_config=inline(
                "reasoning", "base",
                reasoning_model=inline("model", "openai", model_id="o1-mini"),
                min_steps=1,
                max_steps=5,
            ),
        ))
        assert isinstance(result, Agent)

    @pytest.mark.asyncio
    async def test_agent_with_ref(self):
        """Agent 通过 ref 引用预置 model（MockResolver refs 模式）。"""
        from agno.agent import Agent
        model_uuid = str(uuid.uuid4())
        resolver = MockResolver(refs={
            model_uuid: {
                "category": "model",
                "type": "openai",
                "model_id": "gpt-4o",
                "temperature": 0.3,
            }
        })
        result = await resolver.resolve(inline(
            "agent", "base",
            name="RefAgent",
            model={"ref": model_uuid},
        ))
        assert isinstance(result, Agent)

    @pytest.mark.asyncio
    async def test_agent_ref_with_override(self):
        """ref + override：共享 model，但为此 Agent 覆盖 temperature。"""
        from agno.agent import Agent
        model_uuid = str(uuid.uuid4())
        resolver = MockResolver(refs={
            model_uuid: {
                "category": "model",
                "type": "openai",
                "model_id": "gpt-4o",
                "temperature": 0.7,
            }
        })
        result = await resolver.resolve(inline(
            "agent", "base",
            name="OverrideAgent",
            model={"ref": model_uuid, "override": {"temperature": 0.1}},
        ))
        assert isinstance(result, Agent)

    @pytest.mark.asyncio
    async def test_agent_full_stack(self, resolver):
        """完整配置 Agent：model + tools + skill + memory + guardrail + session_summary。"""
        from agno.agent import Agent
        result = await resolver.resolve(inline(
            "agent", "base",
            name="FullStackAgent",
            agent_id="full-stack-001",
            instructions="你是一个全能助手，善用工具和技能。",
            model=inline("model", "openai", model_id="gpt-4o", temperature=0.6),
            tools=[
                inline("toolkit", "calculator"),
                inline("toolkit", "yfinance", stock_price=True),
            ],
            skills=[
                inline(
                    "skill", "base",
                    source="inline",
                    name="finance_expert",
                    description="金融分析专家",
                    instructions="# 金融专家\n\n提供专业的金融市场分析。",
                    allowed_tools="yfinance",
                )
            ],
            memory_manager=inline(
                "memory", "base",
                model=inline("model", "openai", model_id="gpt-4o-mini"),
            ),
            session_summary_manager=inline(
                "session_summary", "base",
                model=inline("model", "openai", model_id="gpt-4o-mini"),
            ),
            guardrails=[
                inline("guardrail", "pii_detection"),
                inline("guardrail", "prompt_injection"),
            ],
            markdown=True,
            show_tool_calls=True,
            enable_agentic_memory=True,
            add_memories_to_context=True,
        ))
        assert isinstance(result, Agent)


# ═════════════════════════════════════════════════════════════════════════════
# 9. Team Builder
# ═════════════════════════════════════════════════════════════════════════════

class TestTeamBuilder:

    @pytest.mark.asyncio
    async def test_team_coordinate_mode(self, resolver):
        """Team coordinate 模式：协调多个 Agent。"""
        from agno.team import Team
        result = await resolver.resolve(inline(
            "team", "base",
            name="CoordinateTeam",
            mode="coordinate",
            model=inline("model", "openai", model_id="gpt-4o"),
            members=[
                inline(
                    "agent", "base",
                    name="Researcher",
                    model=inline("model", "openai", model_id="gpt-4o-mini"),
                ),
                inline(
                    "agent", "base",
                    name="Writer",
                    model=inline("model", "openai", model_id="gpt-4o-mini"),
                ),
            ],
        ))
        assert isinstance(result, Team)

    @pytest.mark.asyncio
    async def test_team_route_mode(self, resolver):
        """Team route 模式：路由到最合适的 Agent。"""
        from agno.team import Team
        result = await resolver.resolve(inline(
            "team", "base",
            name="RouterTeam",
            mode="route",
            model=inline("model", "openai", model_id="gpt-4o"),
            members=[
                inline(
                    "agent", "base",
                    name="MathAgent",
                    instructions="专门处理数学问题。",
                    model=inline("model", "openai", model_id="gpt-4o-mini"),
                    tools=[inline("toolkit", "calculator")],
                ),
                inline(
                    "agent", "base",
                    name="SearchAgent",
                    instructions="专门处理搜索和知识查询。",
                    model=inline("model", "openai", model_id="gpt-4o-mini"),
                    tools=[inline("toolkit", "wikipedia")],
                ),
            ],
            max_iterations=5,
        ))
        assert isinstance(result, Team)

    @pytest.mark.asyncio
    async def test_team_with_memory(self, resolver):
        """Team + MemoryManager。"""
        from agno.team import Team
        result = await resolver.resolve(inline(
            "team", "base",
            name="MemoryTeam",
            mode="collaborate",
            model=inline("model", "openai", model_id="gpt-4o"),
            members=[
                inline(
                    "agent", "base",
                    name="Member1",
                    model=inline("model", "openai", model_id="gpt-4o-mini"),
                ),
            ],
            memory_manager=inline(
                "memory", "base",
                model=inline("model", "openai", model_id="gpt-4o-mini"),
            ),
            enable_agentic_memory=True,
        ))
        assert isinstance(result, Team)

    @pytest.mark.asyncio
    async def test_team_members_via_ref(self):
        """Team 成员通过 ref 引用，验证 resolver 缓存（同一 Agent 只构建一次）。"""
        from agno.team import Team
        agent_uuid = str(uuid.uuid4())
        resolver = MockResolver(refs={
            agent_uuid: {
                "category": "agent",
                "type": "base",
                "name": "SharedAgent",
                "model": inline("model", "openai", model_id="gpt-4o-mini"),
            }
        })
        result = await resolver.resolve(inline(
            "team", "base",
            name="RefTeam",
            mode="coordinate",
            model=inline("model", "openai", model_id="gpt-4o"),
            members=[{"ref": agent_uuid}],
        ))
        assert isinstance(result, Team)


# ═════════════════════════════════════════════════════════════════════════════
# 10. Resolver 行为测试
# ═════════════════════════════════════════════════════════════════════════════

class TestResolverBehavior:

    @pytest.mark.asyncio
    async def test_resolve_none_returns_none(self, resolver):
        result = await resolver.resolve(None)
        assert result is None

    @pytest.mark.asyncio
    async def test_resolve_list_empty(self, resolver):
        result = await resolver.resolve_list([])
        assert result == []

    @pytest.mark.asyncio
    async def test_resolve_list_multiple(self, resolver):
        from agno.tools.calculator import CalculatorTools
        from agno.tools.wikipedia import WikipediaTools
        result = await resolver.resolve_list([
            inline("toolkit", "calculator"),
            inline("toolkit", "wikipedia"),
        ])
        assert len(result) == 2
        assert isinstance(result[0], CalculatorTools)
        assert isinstance(result[1], WikipediaTools)

    @pytest.mark.asyncio
    async def test_ref_cache_same_object(self):
        """同一 ref 两次 resolve 应返回同一对象（缓存命中）。"""
        model_uuid = str(uuid.uuid4())
        resolver = MockResolver(refs={
            model_uuid: {
                "category": "model",
                "type": "openai",
                "model_id": "gpt-4o",
            }
        })
        obj1 = await resolver.resolve({"ref": model_uuid})
        obj2 = await resolver.resolve({"ref": model_uuid})
        assert obj1 is obj2  # 同一对象，缓存生效

    @pytest.mark.asyncio
    async def test_unknown_ref_raises(self, resolver):
        with pytest.raises(ValueError, match="unknown ref"):
            await resolver.resolve({"ref": "non-existent-uuid"})

    @pytest.mark.asyncio
    async def test_inline_missing_category_raises(self, resolver):
        with pytest.raises((ValueError, KeyError)):
            await resolver.resolve({"type": "openai", "model_id": "gpt-4o"})


# ═════════════════════════════════════════════════════════════════════════════
# N. DB Builders
# ═════════════════════════════════════════════════════════════════════════════

class TestDbBuilders:

    @pytest.mark.asyncio
    async def test_in_memory_db(self, resolver):
        """InMemoryDb 无需任何参数。"""
        from agno.db.in_memory import InMemoryDb
        result = await resolver.resolve(inline("db", "in_memory"))
        assert isinstance(result, InMemoryDb)

    @pytest.mark.asyncio
    async def test_sqlite_db_with_url(self, resolver):
        """SqliteDb 通过 db_url 构建。"""
        from agno.db.sqlite.sqlite import SqliteDb
        result = await resolver.resolve(inline(
            "db", "sqlite",
            db_url="sqlite:///./test_agno.db",
        ))
        assert isinstance(result, SqliteDb)

    @pytest.mark.asyncio
    async def test_sqlite_db_with_file(self, resolver):
        """SqliteDb 通过 db_file 构建。"""
        from agno.db.sqlite.sqlite import SqliteDb
        result = await resolver.resolve(inline(
            "db", "sqlite",
            db_file="./test_agno.db",
        ))
        assert isinstance(result, SqliteDb)

    @pytest.mark.asyncio
    async def test_sqlite_db_with_table_names(self, resolver):
        """SqliteDb 支持自定义表名。"""
        from agno.db.sqlite.sqlite import SqliteDb
        result = await resolver.resolve(inline(
            "db", "sqlite",
            db_url="sqlite:///./test_agno.db",
            session_table="my_sessions",
            memory_table="my_memories",
        ))
        assert isinstance(result, SqliteDb)

    @pytest.mark.asyncio
    async def test_postgres_db(self, resolver):
        """PostgresDb 通过 db_url 构建（不连接，只验证对象创建）。"""
        from agno.db.postgres.postgres import PostgresDb
        result = await resolver.resolve(inline(
            "db", "postgres",
            db_url="postgresql+psycopg://user:pass@localhost:5432/agno",
            db_schema="public",
            create_schema=False,
        ))
        assert isinstance(result, PostgresDb)
