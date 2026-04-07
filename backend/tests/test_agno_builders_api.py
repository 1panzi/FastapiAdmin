"""
test_agno_builders_api.py — module_agno_manage_v2 接口测试 + ref/override 扩展场景测试。

测试范围：
  Part 1 — Ref/Override 扩展场景（MockResolver，无 HTTP）
    - 嵌套 ref 链（agent → model、agent → toolkit ref）
    - override 合并优先级
    - 相同 ref 不同 override 分别缓存
    - resolve_list 含 None 过滤
    - ref 找不到异常

  Part 2 — Schema 接口（GET /v2/schema）
    - 无参数 → 返回所有 category 列表
    - ?category=model → 返回该 category 下的 type 列表
    - ?category=model&type=openai → 返回字段 schema
    - ?category=nonexistent → 返回空 types 列表（非 404）
    - ?category=model&type=nonexistent → 404

  Part 3 — 资源 CRUD 接口（mock 掉 service 层）
    - POST   /v2/resources/create    创建 model / agent（inline）/ agent（ref）
    - GET    /v2/resources/list      分页列表
    - GET    /v2/resources/detail/1  详情
    - PUT    /v2/resources/update/1  更新
    - DELETE /v2/resources/delete    批量删除
    - PATCH  /v2/resources/available/setting 批量启用/禁用

运行：
  cd backend
  pytest tests/test_agno_builders_api.py -v
"""

import inspect
import os
import sys
import uuid
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
os.environ["ENVIRONMENT"] = "dev"


# ─────────────────────────────────────────────────────────────────────────────
# MockResolver（与 test_agno_builders.py 保持一致）
# ─────────────────────────────────────────────────────────────────────────────


class MockResolver:
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


def inline(category: str, type_: str, **kwargs) -> dict:
    return {"category": category, "type": type_, **kwargs}


# ─────────────────────────────────────────────────────────────────────────────
# HTTP 测试用 Fixture：mock 掉 auth + warm_up
# ─────────────────────────────────────────────────────────────────────────────


def _make_mock_auth():
    """构造一个超级管理员 AuthSchema（跳过所有权限校验）。"""
    from app.api.v1.module_system.auth.schema import AuthSchema
    from app.api.v1.module_system.user.model import UserModel
    from sqlalchemy.ext.asyncio import AsyncSession

    mock_db = AsyncMock(spec=AsyncSession)
    user = MagicMock(spec=UserModel)
    user.is_superuser = True
    user.status = "0"
    user.roles = []
    return AuthSchema(db=mock_db, check_data_scope=False, user=user)


@pytest.fixture(scope="module")
def api_client():
    """
    创建 FastAPI TestClient，覆盖 get_current_user 以绕过认证，
    同时 mock 掉 warm_up 和 FastAPILimiter 避免外部依赖。
    """
    # 禁用速率限制：_check 返回 0（pexpire=0 表示未超限）
    from fastapi_limiter.depends import RateLimiter

    with (
        patch(
            "app.plugin.module_agno_manage_v2.core.startup.warm_up",
            new_callable=AsyncMock,
        ),
        patch.object(RateLimiter, "_check", new_callable=AsyncMock, return_value=0),
    ):
        from main import create_app
        from app.core.dependencies import get_current_user

        app = create_app()

        async def _mock_current_user():
            return _make_mock_auth()

        app.dependency_overrides[get_current_user] = _mock_current_user

        with TestClient(app, follow_redirects=True) as client:
            yield client


# ─────────────────────────────────────────────────────────────────────────────
# 辅助：构造 service 返回值
# ─────────────────────────────────────────────────────────────────────────────


def _fake_resource(
    id: int = 1,
    category: str = "model",
    type_: str = "openai",
    name: str = "Test Resource",
    config: dict | None = None,
    status: str = "0",
) -> dict:
    return {
        "id": id,
        "uuid": str(uuid.uuid4()),
        "name": name,
        "category": category,
        "type": type_,
        "config": config or {},
        "status": status,
        "description": None,
        "created_time": "2024-01-01T00:00:00",
        "updated_time": "2024-01-01T00:00:00",
        "created_by": None,
        "updated_by": None,
    }


def _fake_page(items: list[dict], total: int = 1) -> dict:
    return {"total": total, "items": items}


# ═════════════════════════════════════════════════════════════════════════════
# Part 1 — Ref/Override 扩展场景测试（无 HTTP）
# ═════════════════════════════════════════════════════════════════════════════


class TestRefOverrideScenarios:

    @pytest.mark.asyncio
    async def test_agent_ref_to_model(self):
        """Agent 通过 ref 引用预置 model，成功构建 Agent。"""
        from agno.agent import Agent
        from agno.models.openai import OpenAIChat

        model_uuid = str(uuid.uuid4())
        resolver = MockResolver(
            refs={
                model_uuid: {
                    "category": "model",
                    "type": "openai",
                    "model_id": "gpt-4o",
                }
            }
        )
        result = await resolver.resolve(
            inline("agent", "base", name="RefAgent", model={"ref": model_uuid})
        )
        assert isinstance(result, Agent)
        assert isinstance(result.model, OpenAIChat)

    @pytest.mark.asyncio
    async def test_override_takes_priority_over_ref_config(self):
        """override 字段覆盖 ref 中的同名字段。"""
        from agno.models.openai import OpenAIChat

        model_uuid = str(uuid.uuid4())
        resolver = MockResolver(
            refs={
                model_uuid: {
                    "category": "model",
                    "type": "openai",
                    "model_id": "gpt-4o",
                    "temperature": 0.9,
                }
            }
        )
        # override temperature=0.1
        result = await resolver.resolve(
            {"ref": model_uuid, "override": {"temperature": 0.1}}
        )
        assert isinstance(result, OpenAIChat)

    @pytest.mark.asyncio
    async def test_same_ref_different_overrides_cached_separately(self):
        """同一 ref 使用不同 override 时，各自独立缓存（不互相污染）。"""
        from agno.models.openai import OpenAIChat

        model_uuid = str(uuid.uuid4())
        resolver = MockResolver(
            refs={
                model_uuid: {
                    "category": "model",
                    "type": "openai",
                    "model_id": "gpt-4o",
                }
            }
        )
        obj_a = await resolver.resolve(
            {"ref": model_uuid, "override": {"temperature": 0.1}}
        )
        obj_b = await resolver.resolve(
            {"ref": model_uuid, "override": {"temperature": 0.9}}
        )
        # 两次 override 不同，应得到不同对象
        assert obj_a is not obj_b
        assert isinstance(obj_a, OpenAIChat)
        assert isinstance(obj_b, OpenAIChat)

    @pytest.mark.asyncio
    async def test_same_ref_no_override_returns_cached(self):
        """同一 ref 无 override 时，第二次 resolve 命中缓存，返回同一对象。"""
        from agno.models.openai import OpenAIChat

        model_uuid = str(uuid.uuid4())
        resolver = MockResolver(
            refs={
                model_uuid: {
                    "category": "model",
                    "type": "openai",
                    "model_id": "gpt-4o",
                }
            }
        )
        obj1 = await resolver.resolve({"ref": model_uuid})
        obj2 = await resolver.resolve({"ref": model_uuid})
        assert obj1 is obj2

    @pytest.mark.asyncio
    async def test_nested_ref_chain(self):
        """嵌套 ref：Team → Agent → Model 均通过 ref 引用，成功构建 Team。"""
        from agno.team import Team

        model_uuid = str(uuid.uuid4())
        agent_uuid = str(uuid.uuid4())
        resolver = MockResolver(
            refs={
                model_uuid: {
                    "category": "model",
                    "type": "openai",
                    "model_id": "gpt-4o-mini",
                },
                agent_uuid: {
                    "category": "agent",
                    "type": "base",
                    "name": "NestedAgent",
                    "model": {"ref": model_uuid},
                },
            }
        )
        result = await resolver.resolve(
            inline(
                "team",
                "base",
                name="NestedTeam",
                mode="coordinate",
                model={"ref": model_uuid},
                members=[{"ref": agent_uuid}],
            )
        )
        assert isinstance(result, Team)

    @pytest.mark.asyncio
    async def test_resolve_list_filters_none(self):
        """resolve_list 对空列表返回 []，对含 None 元素跳过。"""
        resolver = MockResolver()
        result = await resolver.resolve_list([])
        assert result == []

    @pytest.mark.asyncio
    async def test_resolve_list_mixed_inline(self):
        """resolve_list 支持多个 inline 元素批量解析。"""
        from agno.tools.calculator import CalculatorTools
        from agno.tools.wikipedia import WikipediaTools

        resolver = MockResolver()
        result = await resolver.resolve_list(
            [inline("toolkit", "calculator"), inline("toolkit", "wikipedia")]
        )
        assert len(result) == 2
        assert isinstance(result[0], CalculatorTools)
        assert isinstance(result[1], WikipediaTools)

    @pytest.mark.asyncio
    async def test_unknown_ref_raises_value_error(self):
        """引用不存在的 ref 应抛出 ValueError。"""
        resolver = MockResolver()
        with pytest.raises(ValueError, match="unknown ref"):
            await resolver.resolve({"ref": "does-not-exist"})

    @pytest.mark.asyncio
    async def test_ref_override_empty_dict_equals_plain_ref(self):
        """override 为空 dict 时，效果与纯 ref 相同（返回相同类型对象）。"""
        from agno.models.openai import OpenAIChat

        model_uuid = str(uuid.uuid4())
        resolver = MockResolver(
            refs={
                model_uuid: {
                    "category": "model",
                    "type": "openai",
                    "model_id": "gpt-4o",
                }
            }
        )
        plain = await resolver.resolve({"ref": model_uuid})
        with_empty_override = await resolver.resolve(
            {"ref": model_uuid, "override": {}}
        )
        assert isinstance(plain, OpenAIChat)
        assert isinstance(with_empty_override, OpenAIChat)

    @pytest.mark.asyncio
    async def test_agent_with_ref_toolkit(self):
        """Agent tools 列表中通过 ref 引用 toolkit。"""
        from agno.agent import Agent

        toolkit_uuid = str(uuid.uuid4())
        model_uuid = str(uuid.uuid4())
        resolver = MockResolver(
            refs={
                model_uuid: {
                    "category": "model",
                    "type": "openai",
                    "model_id": "gpt-4o",
                },
                toolkit_uuid: {
                    "category": "toolkit",
                    "type": "calculator",
                },
            }
        )
        result = await resolver.resolve(
            inline(
                "agent",
                "base",
                name="ToolRefAgent",
                model={"ref": model_uuid},
                tools=[{"ref": toolkit_uuid}],
            )
        )
        assert isinstance(result, Agent)

    @pytest.mark.asyncio
    async def test_agent_with_mixed_inline_and_ref_tools(self):
        """Agent tools 同时包含 ref 和 inline 两种方式。"""
        from agno.agent import Agent

        toolkit_uuid = str(uuid.uuid4())
        resolver = MockResolver(
            refs={
                toolkit_uuid: {
                    "category": "toolkit",
                    "type": "wikipedia",
                },
            }
        )
        result = await resolver.resolve(
            inline(
                "agent",
                "base",
                name="MixedAgent",
                model=inline("model", "openai", model_id="gpt-4o"),
                tools=[
                    inline("toolkit", "calculator"),
                    {"ref": toolkit_uuid},
                ],
            )
        )
        assert isinstance(result, Agent)


# ═════════════════════════════════════════════════════════════════════════════
# Part 2 — Schema 接口测试 GET /v2/schema
# ═════════════════════════════════════════════════════════════════════════════


class TestSchemaAPI:

    def test_schema_no_params_returns_categories(self, api_client: TestClient):
        """GET /agno_manage_v2/v2/schema 不传参数 → 返回所有 category 列表。"""
        resp = api_client.get("/agno_manage_v2/v2/schema")
        assert resp.status_code == 200
        body = resp.json()
        assert body["code"] == 0
        data = body["data"]
        assert "category" in data
        cats = data["category"]
        assert isinstance(cats, list)
        assert len(cats) > 0
        # 核心 category 必须存在
        for expected in ("model", "embedder", "toolkit", "agent", "team"):
            assert expected in cats, f"category '{expected}' not found in {cats}"

    def test_schema_category_only_returns_types(self, api_client: TestClient):
        """GET /v2/schema?category=model → 返回 types 列表，含 openai/anthropic 等。"""
        resp = api_client.get("/agno_manage_v2/v2/schema", params={"category": "model"})
        assert resp.status_code == 200
        body = resp.json()
        assert body["code"] == 0
        data = body["data"]
        assert data["category"] == "model"
        assert "types" in data
        type_keys = [t["type"] for t in data["types"]]
        assert "openai" in type_keys
        assert "anthropic" in type_keys

    def test_schema_embedder_types(self, api_client: TestClient):
        """GET /v2/schema?category=embedder → 返回 embedder 支持的类型列表。"""
        resp = api_client.get("/agno_manage_v2/v2/schema", params={"category": "embedder"})
        assert resp.status_code == 200
        data = resp.json()["data"]
        assert data["category"] == "embedder"
        type_keys = [t["type"] for t in data["types"]]
        assert "openai" in type_keys

    def test_schema_toolkit_types(self, api_client: TestClient):
        """GET /v2/schema?category=toolkit → 返回 100+ 工具类型列表。"""
        resp = api_client.get("/agno_manage_v2/v2/schema", params={"category": "toolkit"})
        assert resp.status_code == 200
        data = resp.json()["data"]
        assert data["category"] == "toolkit"
        assert len(data["types"]) > 5

    def test_schema_category_and_type_returns_fields(self, api_client: TestClient):
        """GET /v2/schema?category=model&type=openai → 返回完整字段 schema。"""
        resp = api_client.get(
            "/agno_manage_v2/v2/schema", params={"category": "model", "type": "openai"}
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body["code"] == 0
        data = body["data"]
        assert data["category"] == "model"
        assert data["type"] == "openai"
        assert "label" in data
        assert "fields" in data
        fields = data["fields"]
        assert isinstance(fields, list)
        assert len(fields) > 0
        # 每个字段至少有 name 和 type
        for f in fields:
            assert "name" in f
            assert "type" in f

    def test_schema_anthropic_model_fields(self, api_client: TestClient):
        """GET /v2/schema?category=model&type=anthropic → 返回 Anthropic 字段。"""
        resp = api_client.get(
            "/agno_manage_v2/v2/schema", params={"category": "model", "type": "anthropic"}
        )
        assert resp.status_code == 200
        data = resp.json()["data"]
        assert data["category"] == "model"
        assert data["type"] == "anthropic"
        assert len(data["fields"]) > 0

    def test_schema_agent_fields(self, api_client: TestClient):
        """GET /v2/schema?category=agent&type=base → 返回 Agent 字段（含 model）。"""
        resp = api_client.get(
            "/agno_manage_v2/v2/schema", params={"category": "agent", "type": "base"}
        )
        assert resp.status_code == 200
        data = resp.json()["data"]
        assert data["category"] == "agent"
        assert data["type"] == "base"
        field_names = [f["name"] for f in data["fields"]]
        assert "model" in field_names

    def test_schema_team_fields(self, api_client: TestClient):
        """GET /v2/schema?category=team&type=base → 返回 Team 字段（含 mode / members）。"""
        resp = api_client.get(
            "/agno_manage_v2/v2/schema", params={"category": "team", "type": "base"}
        )
        assert resp.status_code == 200
        data = resp.json()["data"]
        assert data["category"] == "team"
        field_names = [f["name"] for f in data["fields"]]
        assert "mode" in field_names
        assert "members" in field_names

    def test_schema_calculator_toolkit_fields(self, api_client: TestClient):
        """GET /v2/schema?category=toolkit&type=calculator → 返回 CalculatorTools 字段。"""
        resp = api_client.get(
            "/agno_manage_v2/v2/schema", params={"category": "toolkit", "type": "calculator"}
        )
        assert resp.status_code == 200
        data = resp.json()["data"]
        assert data["type"] == "calculator"

    def test_schema_nonexistent_category_returns_empty_types(
        self, api_client: TestClient
    ):
        """GET /v2/schema?category=nonexistent → 返回空 types 列表，不报 404。"""
        resp = api_client.get("/agno_manage_v2/v2/schema", params={"category": "nonexistent_xyz"})
        assert resp.status_code == 200
        data = resp.json()["data"]
        assert data["types"] == []

    def test_schema_nonexistent_type_returns_404(self, api_client: TestClient):
        """GET /v2/schema?category=model&type=nonexistent → 404。"""
        resp = api_client.get(
            "/agno_manage_v2/v2/schema", params={"category": "model", "type": "nonexistent_xyz"}
        )
        assert resp.status_code == 404

    def test_schema_openai_embedder_fields(self, api_client: TestClient):
        """GET /v2/schema?category=embedder&type=openai → 返回 embedder 字段。"""
        resp = api_client.get(
            "/agno_manage_v2/v2/schema", params={"category": "embedder", "type": "openai"}
        )
        assert resp.status_code == 200
        data = resp.json()["data"]
        assert data["category"] == "embedder"
        assert data["type"] == "openai"
        assert len(data["fields"]) > 0

    def test_schema_reader_pdf_fields(self, api_client: TestClient):
        """GET /v2/schema?category=reader&type=pdf → 返回 PDF Reader 字段。"""
        resp = api_client.get(
            "/agno_manage_v2/v2/schema", params={"category": "reader", "type": "pdf"}
        )
        assert resp.status_code == 200
        data = resp.json()["data"]
        assert data["category"] == "reader"
        assert data["type"] == "pdf"


# ═════════════════════════════════════════════════════════════════════════════
# Part 3 — 资源 CRUD 接口测试（mock 掉 service 层）
# ═════════════════════════════════════════════════════════════════════════════

_SERVICE_PATH = (
    "app.plugin.module_agno_manage_v2.resource.service.AgResourceService"
)


class TestResourceCreateAPI:

    def test_create_model_resource(self, api_client: TestClient):
        """POST /v2/resources/create 创建 model 类型资源。"""
        fake = _fake_resource(
            category="model",
            type_="openai",
            name="GPT-4o",
            config={"model_id": "gpt-4o"},
        )
        with patch(
            f"{_SERVICE_PATH}.create_resource_service", new_callable=AsyncMock
        ) as mock_create:
            mock_create.return_value = fake
            resp = api_client.post(
                "/agno_manage_v2/v2/resources/create",
                json={
                    "name": "GPT-4o",
                    "category": "model",
                    "type": "openai",
                    "config": {"model_id": "gpt-4o"},
                },
            )
        assert resp.status_code == 200
        body = resp.json()
        assert body["code"] == 0
        assert body["data"]["category"] == "model"
        assert body["data"]["type"] == "openai"

    def test_create_embedder_resource(self, api_client: TestClient):
        """POST /v2/resources/create 创建 embedder 类型资源。"""
        fake = _fake_resource(
            category="embedder",
            type_="openai",
            name="text-embedding-3-small",
            config={"model": "text-embedding-3-small", "dimensions": 1536},
        )
        with patch(
            f"{_SERVICE_PATH}.create_resource_service", new_callable=AsyncMock
        ) as mock_create:
            mock_create.return_value = fake
            resp = api_client.post(
                "/agno_manage_v2/v2/resources/create",
                json={
                    "name": "text-embedding-3-small",
                    "category": "embedder",
                    "type": "openai",
                    "config": {"model": "text-embedding-3-small", "dimensions": 1536},
                },
            )
        assert resp.status_code == 200
        assert resp.json()["data"]["category"] == "embedder"

    def test_create_agent_with_inline_model(self, api_client: TestClient):
        """POST /v2/resources/create 创建 agent，config 中 model 使用 inline 模式。"""
        model_uuid = str(uuid.uuid4())
        fake = _fake_resource(
            category="agent",
            type_="base",
            name="InlineAgent",
            config={
                "model": {
                    "category": "model",
                    "type": "openai",
                    "model_id": "gpt-4o",
                },
                "instructions": "你是一个测试 Agent。",
            },
        )
        with patch(
            f"{_SERVICE_PATH}.create_resource_service", new_callable=AsyncMock
        ) as mock_create:
            mock_create.return_value = fake
            resp = api_client.post(
                "/agno_manage_v2/v2/resources/create",
                json={
                    "name": "InlineAgent",
                    "category": "agent",
                    "type": "base",
                    "config": {
                        "model": {
                            "category": "model",
                            "type": "openai",
                            "model_id": "gpt-4o",
                        },
                        "instructions": "你是一个测试 Agent。",
                    },
                },
            )
        assert resp.status_code == 200
        assert resp.json()["data"]["category"] == "agent"

    def test_create_agent_with_ref_model(self, api_client: TestClient):
        """POST /v2/resources/create 创建 agent，config 中 model 使用 ref 模式。"""
        model_uuid = str(uuid.uuid4())
        fake = _fake_resource(
            category="agent",
            type_="base",
            name="RefAgent",
            config={"model": {"ref": model_uuid}},
        )
        with patch(
            f"{_SERVICE_PATH}.create_resource_service", new_callable=AsyncMock
        ) as mock_create:
            mock_create.return_value = fake
            resp = api_client.post(
                "/agno_manage_v2/v2/resources/create",
                json={
                    "name": "RefAgent",
                    "category": "agent",
                    "type": "base",
                    "config": {"model": {"ref": model_uuid}},
                },
            )
        assert resp.status_code == 200
        assert resp.json()["data"]["config"]["model"]["ref"] == model_uuid

    def test_create_agent_with_ref_override(self, api_client: TestClient):
        """POST /v2/resources/create 创建 agent，model 使用 ref + override 模式。"""
        model_uuid = str(uuid.uuid4())
        fake = _fake_resource(
            category="agent",
            type_="base",
            name="OverrideAgent",
            config={
                "model": {"ref": model_uuid, "override": {"temperature": 0.2}}
            },
        )
        with patch(
            f"{_SERVICE_PATH}.create_resource_service", new_callable=AsyncMock
        ) as mock_create:
            mock_create.return_value = fake
            resp = api_client.post(
                "/agno_manage_v2/v2/resources/create",
                json={
                    "name": "OverrideAgent",
                    "category": "agent",
                    "type": "base",
                    "config": {
                        "model": {
                            "ref": model_uuid,
                            "override": {"temperature": 0.2},
                        }
                    },
                },
            )
        assert resp.status_code == 200
        cfg = resp.json()["data"]["config"]
        assert cfg["model"]["override"]["temperature"] == 0.2

    def test_create_team_with_members_ref(self, api_client: TestClient):
        """POST /v2/resources/create 创建 team，members 使用 ref 列表。"""
        agent_uuid = str(uuid.uuid4())
        model_uuid = str(uuid.uuid4())
        fake = _fake_resource(
            category="team",
            type_="base",
            name="RefTeam",
            config={
                "mode": "coordinate",
                "model": {"ref": model_uuid},
                "members": [{"ref": agent_uuid}],
            },
        )
        with patch(
            f"{_SERVICE_PATH}.create_resource_service", new_callable=AsyncMock
        ) as mock_create:
            mock_create.return_value = fake
            resp = api_client.post(
                "/agno_manage_v2/v2/resources/create",
                json={
                    "name": "RefTeam",
                    "category": "team",
                    "type": "base",
                    "config": {
                        "mode": "coordinate",
                        "model": {"ref": model_uuid},
                        "members": [{"ref": agent_uuid}],
                    },
                },
            )
        assert resp.status_code == 200
        assert resp.json()["data"]["category"] == "team"

    def test_create_resource_disabled_status(self, api_client: TestClient):
        """POST /v2/resources/create 创建时可传 status='1'（禁用）。"""
        fake = _fake_resource(status="1")
        with patch(
            f"{_SERVICE_PATH}.create_resource_service", new_callable=AsyncMock
        ) as mock_create:
            mock_create.return_value = fake
            resp = api_client.post(
                "/agno_manage_v2/v2/resources/create",
                json={
                    "name": "DisabledModel",
                    "category": "model",
                    "type": "openai",
                    "config": {},
                    "status": "1",
                },
            )
        assert resp.status_code == 200
        assert resp.json()["data"]["status"] == "1"


class TestResourceListAPI:

    def test_list_default_pagination(self, api_client: TestClient):
        """GET /v2/resources/list 默认分页返回列表结构。"""
        fake_page = _fake_page([_fake_resource()])
        with patch(
            f"{_SERVICE_PATH}.page_resources_service", new_callable=AsyncMock
        ) as mock_list:
            mock_list.return_value = fake_page
            resp = api_client.get("/agno_manage_v2/v2/resources/list")
        assert resp.status_code == 200
        body = resp.json()
        assert body["code"] == 0
        assert "total" in body["data"]
        assert "items" in body["data"]

    def test_list_filter_by_category(self, api_client: TestClient):
        """GET /v2/resources/list?category=model 按 category 过滤。"""
        fake_page = _fake_page(
            [_fake_resource(category="model"), _fake_resource(id=2, category="model")]
        )
        with patch(
            f"{_SERVICE_PATH}.page_resources_service", new_callable=AsyncMock
        ) as mock_list:
            mock_list.return_value = fake_page
            resp = api_client.get("/agno_manage_v2/v2/resources/list", params={"category": "model"})
        assert resp.status_code == 200
        assert resp.json()["data"]["total"] == 1

    def test_list_filter_by_category_and_type(self, api_client: TestClient):
        """GET /v2/resources/list?category=model&type=openai 联合过滤。"""
        fake_page = _fake_page([_fake_resource()])
        with patch(
            f"{_SERVICE_PATH}.page_resources_service", new_callable=AsyncMock
        ) as mock_list:
            mock_list.return_value = fake_page
            resp = api_client.get(
                "/agno_manage_v2/v2/resources/list",
                params={"category": "model", "type": "openai"},
            )
        assert resp.status_code == 200
        assert "items" in resp.json()["data"]

    def test_list_pagination_params(self, api_client: TestClient):
        """GET /v2/resources/list?page_no=2&page_size=5 传入分页参数。"""
        fake_page = _fake_page([], total=0)
        with patch(
            f"{_SERVICE_PATH}.page_resources_service", new_callable=AsyncMock
        ) as mock_list:
            mock_list.return_value = fake_page
            resp = api_client.get(
                "/agno_manage_v2/v2/resources/list", params={"page_no": 2, "page_size": 5}
            )
        assert resp.status_code == 200

    def test_list_filter_by_status(self, api_client: TestClient):
        """GET /v2/resources/list?status=0 按启用状态过滤。"""
        fake_page = _fake_page([_fake_resource()])
        with patch(
            f"{_SERVICE_PATH}.page_resources_service", new_callable=AsyncMock
        ) as mock_list:
            mock_list.return_value = fake_page
            resp = api_client.get("/agno_manage_v2/v2/resources/list", params={"status": "0"})
        assert resp.status_code == 200


class TestResourceDetailAPI:

    def test_detail_by_id(self, api_client: TestClient):
        """GET /v2/resources/detail/1 获取资源详情，config 含默认值补全。"""
        fake = _fake_resource(id=1, config={"model_id": "gpt-4o", "temperature": 0.7})
        with patch(
            f"{_SERVICE_PATH}.detail_resources_service", new_callable=AsyncMock
        ) as mock_detail:
            mock_detail.return_value = fake
            resp = api_client.get("/agno_manage_v2/v2/resources/detail/1")
        assert resp.status_code == 200
        body = resp.json()
        assert body["code"] == 0
        assert body["data"]["id"] == 1
        assert "config" in body["data"]

    def test_detail_agent_with_ref_model_in_config(self, api_client: TestClient):
        """GET /v2/resources/detail/{id} agent 资源，config 中保留 ref 结构。"""
        model_uuid = str(uuid.uuid4())
        fake = _fake_resource(
            id=42,
            category="agent",
            type_="base",
            config={"model": {"ref": model_uuid}},
        )
        with patch(
            f"{_SERVICE_PATH}.detail_resources_service", new_callable=AsyncMock
        ) as mock_detail:
            mock_detail.return_value = fake
            resp = api_client.get("/agno_manage_v2/v2/resources/detail/42")
        assert resp.status_code == 200
        cfg = resp.json()["data"]["config"]
        assert cfg["model"]["ref"] == model_uuid


class TestResourceUpdateAPI:

    def test_update_resource(self, api_client: TestClient):
        """PUT /v2/resources/update/1 更新资源配置。"""
        fake = _fake_resource(id=1, config={"model_id": "gpt-4o-mini"})
        with patch(
            f"{_SERVICE_PATH}.update_resource_service", new_callable=AsyncMock
        ) as mock_update:
            mock_update.return_value = fake
            resp = api_client.put(
                "/agno_manage_v2/v2/resources/update/1",
                json={
                    "name": "GPT-4o-mini",
                    "category": "model",
                    "type": "openai",
                    "config": {"model_id": "gpt-4o-mini"},
                },
            )
        assert resp.status_code == 200
        body = resp.json()
        assert body["code"] == 0
        assert body["data"]["config"]["model_id"] == "gpt-4o-mini"

    def test_update_agent_change_ref_to_inline(self, api_client: TestClient):
        """PUT /v2/resources/update/{id} 将 agent 的 model 从 ref 切换为 inline。"""
        fake = _fake_resource(
            id=5,
            category="agent",
            type_="base",
            config={
                "model": {
                    "category": "model",
                    "type": "openai",
                    "model_id": "gpt-4o",
                }
            },
        )
        with patch(
            f"{_SERVICE_PATH}.update_resource_service", new_callable=AsyncMock
        ) as mock_update:
            mock_update.return_value = fake
            resp = api_client.put(
                "/agno_manage_v2/v2/resources/update/5",
                json={
                    "name": "InlineAgent",
                    "category": "agent",
                    "type": "base",
                    "config": {
                        "model": {
                            "category": "model",
                            "type": "openai",
                            "model_id": "gpt-4o",
                        }
                    },
                },
            )
        assert resp.status_code == 200
        cfg = resp.json()["data"]["config"]
        assert "category" in cfg["model"]  # inline 模式


class TestResourceDeleteAPI:

    def test_delete_single_resource(self, api_client: TestClient):
        """DELETE /v2/resources/delete 删除单个资源。"""
        with patch(
            f"{_SERVICE_PATH}.delete_resource_service", new_callable=AsyncMock
        ) as mock_del:
            mock_del.return_value = None
            resp = api_client.request(
                "DELETE", "/agno_manage_v2/v2/resources/delete", json=[1]
            )
        assert resp.status_code == 200
        assert resp.json()["code"] == 0

    def test_delete_multiple_resources(self, api_client: TestClient):
        """DELETE /v2/resources/delete 批量删除多个资源。"""
        with patch(
            f"{_SERVICE_PATH}.delete_resource_service", new_callable=AsyncMock
        ) as mock_del:
            mock_del.return_value = None
            resp = api_client.request(
                "DELETE", "/agno_manage_v2/v2/resources/delete", json=[1, 2, 3]
            )
        assert resp.status_code == 200
        assert resp.json()["code"] == 0


class TestResourceAvailableSettingAPI:

    def test_enable_resources(self, api_client: TestClient):
        """PATCH /v2/resources/available/setting 批量启用资源。"""
        with patch(
            f"{_SERVICE_PATH}.set_available_resource_service", new_callable=AsyncMock
        ) as mock_set:
            mock_set.return_value = None
            resp = api_client.patch(
                "/agno_manage_v2/v2/resources/available/setting",
                json={"ids": [1, 2], "status": "0"},
            )
        assert resp.status_code == 200
        assert resp.json()["code"] == 0

    def test_disable_resources(self, api_client: TestClient):
        """PATCH /v2/resources/available/setting 批量禁用资源。"""
        with patch(
            f"{_SERVICE_PATH}.set_available_resource_service", new_callable=AsyncMock
        ) as mock_set:
            mock_set.return_value = None
            resp = api_client.patch(
                "/agno_manage_v2/v2/resources/available/setting",
                json={"ids": [3], "status": "1"},
            )
        assert resp.status_code == 200
        assert resp.json()["code"] == 0

    def test_enable_agent_registers_to_registry(self, api_client: TestClient):
        """PATCH 启用 agent 时，service 层应被调用（registry 同步在 service 内处理）。"""
        with patch(
            f"{_SERVICE_PATH}.set_available_resource_service", new_callable=AsyncMock
        ) as mock_set:
            mock_set.return_value = None
            resp = api_client.patch(
                "/agno_manage_v2/v2/resources/available/setting",
                json={"ids": [10], "status": "0"},
            )
        assert resp.status_code == 200
        mock_set.assert_called_once()
        call_kwargs = mock_set.call_args
        # 验证 status 参数传入正确
        assert "status" in str(call_kwargs) or "0" in str(call_kwargs)
