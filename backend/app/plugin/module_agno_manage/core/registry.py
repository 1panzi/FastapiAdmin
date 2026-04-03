"""
RuntimeRegistry — 内存单例，管理所有 Agno 运行时对象。

Key 约定：所有 registry 字典的 key = str(row.id)（整数主键字符串）
  - 与 ag_bindings.owner_id / resource_id（Integer 列）保持一致
  - SyncBindingRepo 返回的 resource_id 可直接用于 dict 查找

AgentOS 路由约定：Agno agent_id = str(row.id)（如 "42"）
  → AgentOS 路由为 /agents/42/runs

热区（全量常驻）：Model / Embedder / Toolkit / Hook / Guardrail / Agent / Team
冷区（LRU 按需）：Knowledge（外部）/ MCP stdio
行数据缓存（按需实例化子管理器）：vectordb / kb / mcp / skill / memory_manager / sub-configs
"""

from collections import OrderedDict

from app.core.logger import log

from .agno_os import _build_agno_db

# ── LRU 缓存 ──────────────────────────────────────────────────────────────────


class LRUCache:
    """带 close() 回调的 LRU 缓存，用于 MCP 和 Knowledge 的冷热管理。"""

    def __init__(self, maxsize: int):
        self.maxsize = maxsize
        self._cache: OrderedDict = OrderedDict()

    def get(self, key: str):
        if key in self._cache:
            self._cache.move_to_end(key)
            return self._cache[key]
        return None

    def set(self, key: str, value) -> None:
        if key in self._cache:
            self._cache.move_to_end(key)
        else:
            if len(self._cache) >= self.maxsize:
                _, evicted = self._cache.popitem(last=False)
                if hasattr(evicted, "close"):
                    try:
                        evicted.close()
                    except Exception:
                        pass
        self._cache[key] = value

    def remove(self, key: str) -> None:
        obj = self._cache.pop(key, None)
        if obj is not None and hasattr(obj, "close"):
            try:
                obj.close()
            except Exception:
                pass

    def clear(self) -> None:
        for obj in self._cache.values():
            if hasattr(obj, "close"):
                try:
                    obj.close()
                except Exception:
                    pass
        self._cache.clear()


# ── RuntimeRegistry ──────────────────────────────────────────────────────────

class RuntimeRegistry:
    """全局运行时对象注册中心。所有 key = str(row.id)。"""

    def __init__(self):
        # ── 运行时列表（AgentOS 直接引用，传引用后 append 即时生效） ───────
        self.agents: list = []
        self.teams: list = []
        self.workflows: list = []
        self._agents_map: dict[str, object] = {}   # str(id) → Agent
        self._teams_map: dict[str, object] = {}
        self._workflows_map: dict[str, object] = {}

        # ── 构建好的对象缓存（热区） ──────────────────────────────────────
        self._model_cache: dict[str, object] = {}      # str(id) → Agno Model
        self._embedder_cache: dict[str, object] = {}   # str(id) → Agno Embedder
        self._toolkit_rows: dict[str, object] = {}     # str(id) → row（懒加载，不预实例化）
        self._hook_map: dict[str, object] = {}         # str(id) → {func, hook_type}
        self._guardrail_map: dict[str, object] = {}    # str(id) → {obj, guardrail_type}

        # ── 行数据缓存（供 Agent 构建时按需实例化） ──────────────────────
        self._vectordb_rows: dict[str, object] = {}
        self._mcp_rows: dict[str, object] = {}
        self._kb_rows: dict[str, object] = {}
        self._skill_rows: dict[str, object] = {}
        self._memory_manager_rows: dict[str, object] = {}
        self._learning_rows: dict[str, object] = {}
        self._reasoning_rows: dict[str, object] = {}
        self._compression_rows: dict[str, object] = {}
        self._session_summary_rows: dict[str, object] = {}
        self._culture_rows: dict[str, object] = {}
        self._integration_rows: dict[str, object] = {}
        self._binding_rows: dict[str, object] = {}

        # ── 冷区（LRU 按需加载） ──────────────────────────────────────────
        self._knowledge_cache: LRUCache = LRUCache(maxsize=50)
        self._mcp_cache: LRUCache = LRUCache(maxsize=20)

        # ── 共享资源（lifespan 注入） ──────────────────────────────────────
        self._agno_db = _build_agno_db()

    # ── Model ────────────────────────────────────────────────────────────────

    def register_model(self, model_id: str, row) -> None:
        """根据 row.provider 构建 Agno Model 实例并存入 _model_cache。
        model_id = str(row.id)（整数主键字符串）"""
        provider = row.provider
        mid = row.model_id
        api_key = row.api_key
        base_url = row.base_url
        config = dict(row.config or {})

        try:
            if provider == "openai":
                from agno.models.openai import OpenAIChat
                obj = OpenAIChat(id=mid, api_key=api_key, base_url=base_url, **config)
            elif provider == "anthropic":
                from agno.models.anthropic import Claude
                obj = Claude(id=mid, api_key=api_key, **config)
            elif provider == "google":
                from agno.models.google import Gemini
                obj = Gemini(id=mid, api_key=api_key, **config)
            elif provider == "ollama":
                from agno.models.ollama import Ollama
                obj = Ollama(id=mid, host=base_url, **config)
            elif provider == "groq":
                from agno.models.groq import Groq
                obj = Groq(id=mid, api_key=api_key, **config)
            elif provider == "deepseek":
                from agno.models.deepseek import DeepSeek
                obj = DeepSeek(id=mid, api_key=api_key, base_url=base_url, **config)
            elif provider == "mistral":
                from agno.models.mistral import MistralChat
                obj = MistralChat(id=mid, api_key=api_key, **config)
            elif provider == "azure":
                from agno.models.azure import AzureOpenAI
                obj = AzureOpenAI(id=mid, api_key=api_key, azure_endpoint=base_url, **config)
            elif provider == "cohere":
                from agno.models.cohere import CohereChat
                obj = CohereChat(id=mid, api_key=api_key, **config)
            elif provider == "together":
                from agno.models.together import Together
                obj = Together(id=mid, api_key=api_key, **config)
            elif provider == "openai_like":
                from agno.models.openai import OpenAIChat
                obj = OpenAIChat(id=mid, api_key=api_key, base_url=base_url, **config)
            else:
                raise ValueError(f"Unsupported model provider: {provider}")

            self._model_cache[model_id] = obj
            log.debug(f"[Registry] model registered: id={model_id}, provider={provider}")

        except Exception as e:
            log.error(f"[Registry] failed to register model id={model_id}: {e}")
            raise

    def unregister_model(self, model_id: str) -> None:
        self._model_cache.pop(model_id, None)
        log.debug(f"[Registry] model unregistered: id={model_id}")

    def get_model(self, model_id: str) -> object | None:
        return self._model_cache.get(model_id)

    # ── Embedder ─────────────────────────────────────────────────────────────

    def register_embedder(self, embedder_id: str, row) -> None:
        provider = row.provider
        mid = row.model_id
        api_key = row.api_key
        base_url = row.base_url
        config = dict(row.config or {})
        dimensions = getattr(row, "dimensions", None)
        if dimensions:
            config.setdefault("dimensions", dimensions)

        try:
            if provider == "openai":
                from agno.knowledge.embedder.openai import OpenAIEmbedder
                obj = OpenAIEmbedder(id=mid, api_key=api_key, **config)
            elif provider == "azure":
                from agno.knowledge.embedder.azure_openai import AzureOpenAIEmbedder
                obj = AzureOpenAIEmbedder(id=mid, api_key=api_key, azure_endpoint=base_url, **config)
            elif provider == "ollama":
                from agno.knowledge.embedder.ollama import OllamaEmbedder
                obj = OllamaEmbedder(id=mid, host=base_url, **config)
            elif provider == "cohere":
                from agno.knowledge.embedder.cohere import CohereEmbedder
                obj = CohereEmbedder(id=mid, api_key=api_key, **config)
            elif provider == "google":
                from agno.knowledge.embedder.google import GeminiEmbedder
                obj = GeminiEmbedder(id=mid, api_key=api_key, **config)
            elif provider == "huggingface":
                from agno.knowledge.embedder.huggingface import HuggingfaceCustomEmbedder
                obj = HuggingfaceCustomEmbedder(id=mid, **config)
            elif provider == "openai_like":
                from agno.knowledge.embedder.openai import OpenAIEmbedder
                obj = OpenAIEmbedder(id=mid, api_key=api_key, base_url=base_url, **config)
            else:
                raise ValueError(f"Unsupported embedder provider: {provider}")

            self._embedder_cache[embedder_id] = obj
            log.debug(f"[Registry] embedder registered: id={embedder_id}")

        except Exception as e:
            log.error(f"[Registry] failed to register embedder id={embedder_id}: {e}")
            raise

    def unregister_embedder(self, embedder_id: str) -> None:
        self._embedder_cache.pop(embedder_id, None)

    def get_embedder(self, embedder_id: str) -> object | None:
        return self._embedder_cache.get(embedder_id)

    # ── Toolkit ──────────────────────────────────────────────────────────────

    def register_toolkit(self, toolkit_id: str, row) -> None:
        """注册工具行数据，不实例化（懒加载，在 resolve_tools 时按需实例化）。"""
        import importlib

        # 全局禁用直接跳过
        if getattr(row, "global_enabled", True) is False:
            log.debug(f"[Registry] toolkit id={toolkit_id} global_enabled=False, skip")
            return

        # 验证能否导入（type=code 跳过验证，exec 在运行时做）
        if getattr(row, "type", None) != "code":
            try:
                mod = importlib.import_module(row.module_path)
                if row.type == "toolkit":
                    getattr(mod, row.class_name)  # 验证类存在
                elif row.type == "function":
                    getattr(mod, row.func_name)   # 验证函数存在
            except Exception as e:
                log.error(f"[Registry] toolkit id={toolkit_id} 导入失败: {e}")
                raise

        # 只存 row，不实例化
        self._toolkit_rows[toolkit_id] = row
        log.debug(f"[Registry] toolkit registered (lazy): id={toolkit_id}, type={row.type}")

    def unregister_toolkit(self, toolkit_id: str) -> None:
        self._toolkit_rows.pop(toolkit_id, None)

    def get_toolkit_row(self, toolkit_id: str) -> object | None:
        """获取工具行数据（用于 resolve_tools 懒加载）。"""
        return self._toolkit_rows.get(toolkit_id)

    def _build_toolkit(self, row, config: dict) -> object:
        """根据 row + config 实例化工具（懒加载时调用）。"""
        import importlib

        from agno.tools import Function
        from agno.tools.toolkit import Toolkit

        if row.type == "code":
            # 执行 source_code，提取函数，包装成 Toolkit
            source_code = getattr(row, "source_code", None)
            if not source_code:
                raise ValueError(f"code toolkit id={row.id} source_code 为空")

            # 注入 CONFIG 到 namespace，用户代码可通过 CONFIG 访问配置
            namespace: dict = {"CONFIG": config}
            exec(compile(source_code, f"<toolkit:{row.id}>", "exec"), namespace)

            tools = []
            for name, obj in namespace.items():
                if name.startswith("_") or name == "CONFIG":
                    continue
                if isinstance(obj, Function):
                    tools.append(obj)
                elif callable(obj) and not isinstance(obj, type) and getattr(obj, "__module__", None) is None:
                    tools.append(obj)

            if not tools:
                raise ValueError(f"code toolkit id={row.id} 未找到任何可用函数")

            return Toolkit(name=row.name or f"code_toolkit_{row.id}", tools=tools)

        else:
            # 普通 toolkit/function
            mod = importlib.import_module(row.module_path)
            if row.type == "toolkit":
                cls = getattr(mod, row.class_name)
                return cls(**config)
            else:
                # type == "function"：直接返回函数
                return getattr(mod, row.func_name)

    # ── Hook ─────────────────────────────────────────────────────────────────

    def register_hook(self, hook_id: str, row) -> None:
        import importlib
        try:
            mod = importlib.import_module(row.module_path)
            func = getattr(mod, row.function_name)
            self._hook_map[hook_id] = {"func": func, "hook_type": row.hook_type}
            log.debug(f"[Registry] hook registered: id={hook_id}")
        except Exception as e:
            log.error(f"[Registry] failed to register hook id={hook_id}: {e}")
            raise

    def unregister_hook(self, hook_id: str) -> None:
        self._hook_map.pop(hook_id, None)

    # ── Guardrail ────────────────────────────────────────────────────────────

    def register_guardrail(self, guardrail_id: str, row) -> None:
        import importlib
        config = dict(row.config or {})
        try:
            mod = importlib.import_module(row.module_path)
            cls = getattr(mod, row.class_name)
            obj = cls(**config)
            self._guardrail_map[guardrail_id] = {"obj": obj, "guardrail_type": row.guardrail_type}
            log.debug(f"[Registry] guardrail registered: id={guardrail_id}")
        except Exception as e:
            log.error(f"[Registry] failed to register guardrail id={guardrail_id}: {e}")
            raise

    def unregister_guardrail(self, guardrail_id: str) -> None:
        self._guardrail_map.pop(guardrail_id, None)

    # ── MCP（冷区，LRU）──────────────────────────────────────────────────────

    def get_or_build_mcp(self, mcp_id: str, row) -> object:
        cached = self._mcp_cache.get(mcp_id)
        if cached:
            return cached
        config = dict(row.config or {})
        server_type = getattr(row, "server_type", "http")
        try:
            if server_type == "http":
                from agno.tools.mcp import MCPTools
                obj = MCPTools(url=row.url, **config)
            elif server_type == "stdio":
                from agno.tools.mcp import MCPTools
                obj = MCPTools(command=row.command, args=list(row.args or []))
            else:
                raise ValueError(f"Unsupported MCP type: {server_type}")
            self._mcp_cache.set(mcp_id, obj)
            return obj
        except Exception as e:
            log.error(f"[Registry] failed to build MCP id={mcp_id}: {e}")
            raise

    # ── Agent ────────────────────────────────────────────────────────────────

    def create_agent(self, row) -> object:
        """
        根据 ag_agents 行构建 Agno Agent 并追加到 agents 列表。
        使用 callable factory（cache_callables=False）实现热插拔。
        agent_id = str(row.id)，对应 AgentOS 路由 /agents/{id}/runs
        """
        from agno.agent import Agent as AgnoAgent

        agent_id = str(row.id)

        # 获取主模型
        model = self.get_model(str(row.model_id)) if row.model_id else None
        if model is None and row.model_id:
            log.warning(f"[Registry] agent {agent_id}: model id={row.model_id} not found in registry")

        # 构建 callable factory（capture agent_id by value with default arg）
        def _tools(aid=agent_id):
            return self.resolve_tools(aid)

        def _knowledge(aid=agent_id):
            return self.resolve_knowledge(aid)

        # 整理 Agent 的可选参数（只传非 None 值）
        kwargs: dict = {}
        bool_fields = [
            "reasoning", "learning", "search_knowledge", "update_knowledge",
            "add_knowledge_to_context", "enable_agentic_knowledge_filters",
            "enable_agentic_state", "enable_agentic_memory", "update_memory_on_run",
            "add_memories_to_context", "add_history_to_context", "search_past_sessions",
            "enable_session_summaries", "add_session_summary_to_context",
            "use_json_mode", "structured_outputs", "parse_response",
            "exponential_backoff", "add_datetime_to_context", "add_name_to_context",
            "compress_tool_results", "stream", "stream_events", "store_events",
            "markdown", "followups", "debug_mode", "a2a_enabled",
        ]
        int_fields = [
            "reasoning_min_steps", "reasoning_max_steps", "num_history_runs",
            "num_history_messages", "num_past_sessions_to_search",
            "tool_call_limit", "retries", "delay_between_retries",
            "num_followups", "debug_level",
        ]
        str_fields = [
            "instructions", "expected_output", "additional_context", "tool_choice",
        ]
        for f in bool_fields + int_fields + str_fields:
            v = getattr(row, f, None)
            if v is not None:
                kwargs[f] = v

        agent = AgnoAgent(
            id=agent_id,
            name=row.name,
            model=model,
            tools=_tools,
            knowledge=_knowledge,
            cache_callables=False,   # ⚠️ 必须关闭，热插拔绑定时无需重建 AgnoAgent
            db=self._agno_db,
            **kwargs,
        )

        # 追加到 agents 列表（AgentOS 传引用，append 后立即可路由）
        if agent_id not in self._agents_map:
            self.agents.append(agent)
        else:
            # 更新：替换列表中的旧实例
            idx = next((i for i, a in enumerate(self.agents) if getattr(a, "agent_id", None) == agent_id), None)
            if idx is not None:
                self.agents[idx] = agent

        self._agents_map[agent_id] = agent
        log.info(f"[Registry] agent created/updated: id={agent_id}, name={row.name}")
        return agent

    def remove_agent(self, agent_id: str) -> None:
        agent = self._agents_map.pop(agent_id, None)
        if agent and agent in self.agents:
            self.agents.remove(agent)
        log.debug(f"[Registry] agent removed: id={agent_id}")

    # ── resolve（callable factory，同步调用）─────────────────────────────────

    def resolve_tools(self, agent_id: str) -> list:
        """每次 Agno run() 时被 callable factory 同步调用，读最新绑定并懒加载实例化。"""
        from app.plugin.module_agno_manage.core.sync_db import SyncBindingRepo
        tools = []
        for b in SyncBindingRepo.get_active(agent_id, "agent"):
            if b.resource_type == "toolkit":
                row = self._toolkit_rows.get(b.resource_id)
                if row:
                    # 合并 config：系统默认 + 用户覆盖
                    merged_config = {**(row.config or {}), **(b.config_override or {})}
                    try:
                        toolkit = self._build_toolkit(row, merged_config)
                        tools.append(toolkit)
                    except Exception as e:
                        log.warning(f"[Registry] resolve_tools 实例化 toolkit id={b.resource_id} 失败: {e}")
            elif b.resource_type == "mcp":
                mcp_row = self._mcp_rows.get(b.resource_id)
                if mcp_row:
                    t = self.get_or_build_mcp(b.resource_id, mcp_row)
                    tools.append(t)
        return tools

    def resolve_knowledge(self, agent_id: str):
        """每次 Agno run() 时被 callable factory 同步调用，读最新绑定。"""
        from app.plugin.module_agno_manage.core.sync_db import SyncBindingRepo
        kbs = []
        for b in SyncBindingRepo.get_active(agent_id, "agent", resource_type="knowledge"):
            kb_row = self._kb_rows.get(b.resource_id)
            if kb_row:
                kb = self._knowledge_cache.get(b.resource_id)
                if kb is None:
                    kb = self._build_knowledge(b.resource_id, kb_row)
                    if kb:
                        self._knowledge_cache.set(b.resource_id, kb)
                if kb:
                    kbs.append(kb)
        return kbs[0] if kbs else None

    def _build_knowledge(self, kb_id: str, row) -> object | None:
        try:
            embedder = self.get_embedder(str(row.embedder_id)) if getattr(row, "embedder_id", None) else None
            kb_type = getattr(row, "knowledge_type", "pdf")
            config = dict(row.config or {})
            # TODO 此处存在问题，知识库库，不分类型文件类型，只是区分 向量库和readers 以及向量DB  向量DB中才存入 embedder 还没有完全完成
            if kb_type == "pdf":
                from agno.knowledge.knowledge import Knowledge
                # vector_db
                # contents_db: Optional[Union[BaseDb, AsyncBaseDb]] = None  self._agno_db
                return Knowledge(**config)
            if kb_type == "filesystem":
                from agno.knowledge.filesystem import FileSystemKnowledge
                return FileSystemKnowledge(**config)
            else:
                log.warning(f"[Registry] unknown knowledge type: {kb_type}")
                return None
        except Exception as e:
            log.error(f"[Registry] failed to build knowledge id={kb_id}: {e}")
            return None

    # ── Row cache management (public API) ────────────────────────────────────

    def update_vectordb_row(self, vid: str, row) -> None:
        self._vectordb_rows[vid] = row
        log.debug(f"[Registry] vectordb row updated: id={vid}")

    def remove_vectordb_row(self, vid: str) -> None:
        self._vectordb_rows.pop(vid, None)

    def update_kb_row(self, kid: str, row) -> None:
        self._kb_rows[kid] = row
        # 行数据变了，让 LRU 缓存失效，下次 resolve 时重建
        self._knowledge_cache.remove(kid)
        log.debug(f"[Registry] kb row updated: id={kid}")

    def remove_kb_row(self, kid: str) -> None:
        self._kb_rows.pop(kid, None)
        self._knowledge_cache.remove(kid)

    def update_mcp_row(self, mid: str, row) -> None:
        self._mcp_rows[mid] = row
        self._mcp_cache.remove(mid)
        log.debug(f"[Registry] mcp row updated: id={mid}")

    def remove_mcp_row(self, mid: str) -> None:
        self._mcp_rows.pop(mid, None)
        self._mcp_cache.remove(mid)

    def update_skill_row(self, sid: str, row) -> None:
        self._skill_rows[sid] = row
        log.debug(f"[Registry] skill row updated: id={sid}")

    def remove_skill_row(self, sid: str) -> None:
        self._skill_rows.pop(sid, None)

    def update_memory_manager_row(self, mid: str, row) -> None:
        self._memory_manager_rows[mid] = row

    def remove_memory_manager_row(self, mid: str) -> None:
        self._memory_manager_rows.pop(mid, None)

    def update_learning_row(self, lid: str, row) -> None:
        self._learning_rows[lid] = row

    def remove_learning_row(self, lid: str) -> None:
        self._learning_rows.pop(lid, None)

    def update_reasoning_row(self, rid: str, row) -> None:
        self._reasoning_rows[rid] = row

    def remove_reasoning_row(self, rid: str) -> None:
        self._reasoning_rows.pop(rid, None)

    def update_compression_row(self, cid: str, row) -> None:
        self._compression_rows[cid] = row

    def remove_compression_row(self, cid: str) -> None:
        self._compression_rows.pop(cid, None)

    def update_session_summary_row(self, sid: str, row) -> None:
        self._session_summary_rows[sid] = row

    def remove_session_summary_row(self, sid: str) -> None:
        self._session_summary_rows.pop(sid, None)

    def update_culture_row(self, cid: str, row) -> None:
        self._culture_rows[cid] = row

    def remove_culture_row(self, cid: str) -> None:
        self._culture_rows.pop(cid, None)

    def update_integration_row(self, iid: str, row) -> None:
        self._integration_rows[iid] = row
        log.debug(f"[Registry] integration row updated: id={iid}")

    def remove_integration_row(self, iid: str) -> None:
        self._integration_rows.pop(iid, None)

    def update_binding_row(self, bid: str, row) -> None:
        self._binding_rows[bid] = row
        log.debug(f"[Registry] binding row updated: id={bid}")

    def remove_binding_row(self, bid: str) -> None:
        self._binding_rows.pop(bid, None)

    # ── Team ─────────────────────────────────────────────────────────────────

    def create_team(self, row) -> object:
        """根据 ag_teams 行构建 Agno Team 并注册。"""
        from agno.team import Team
        team_id = str(row.id)
        config = dict(row.config or {})
        # 收集成员 agents
        member_agents = [a for a in self.agents if getattr(a, "agent_id", None) in (
            [str(m) for m in (row.member_ids or [])] if hasattr(row, "member_ids") else []
        )]
        try:
            team = Team(
                team_id=team_id,
                name=row.name,
                members=member_agents or [],
                **{k: v for k, v in config.items()},
            )
            if team_id not in self._teams_map:
                self.teams.append(team)
            else:
                idx = next((i for i, t in enumerate(self.teams) if getattr(t, "team_id", None) == team_id), None)
                if idx is not None:
                    self.teams[idx] = team
            self._teams_map[team_id] = team
            log.info(f"[Registry] team created/updated: id={team_id}, name={row.name}")
            return team
        except Exception as e:
            log.error(f"[Registry] failed to create team id={team_id}: {e}")
            raise

    def remove_team(self, team_id: str) -> None:
        team = self._teams_map.pop(team_id, None)
        if team and team in self.teams:
            self.teams.remove(team)
        log.debug(f"[Registry] team removed: id={team_id}")

    # ── Workflow ──────────────────────────────────────────────────────────────

    def create_workflow(self, row) -> object:
        """根据 ag_workflows 行构建 Agno Workflow 并注册。"""
        from agno.workflow import Workflow
        workflow_id = str(row.id)
        config = dict(row.config or {})
        try:
            workflow = Workflow(
                workflow_id=workflow_id,
                name=row.name,
                **{k: v for k, v in config.items()},
            )
            if workflow_id not in self._workflows_map:
                self.workflows.append(workflow)
            else:
                idx = next((i for i, w in enumerate(self.workflows) if getattr(w, "workflow_id", None) == workflow_id), None)
                if idx is not None:
                    self.workflows[idx] = workflow
            self._workflows_map[workflow_id] = workflow
            log.info(f"[Registry] workflow created/updated: id={workflow_id}, name={row.name}")
            return workflow
        except Exception as e:
            log.error(f"[Registry] failed to create workflow id={workflow_id}: {e}")
            raise

    def remove_workflow(self, workflow_id: str) -> None:
        workflow = self._workflows_map.pop(workflow_id, None)
        if workflow and workflow in self.workflows:
            self.workflows.remove(workflow)
        log.debug(f"[Registry] workflow removed: id={workflow_id}")

    # ── Shutdown ──────────────────────────────────────────────────────────────

    def shutdown(self) -> None:
        self._mcp_cache.clear()
        self._knowledge_cache.clear()
        log.info("[Registry] shutdown complete")


# ── 全局单例 ──────────────────────────────────────────────────────────────────

_registry: RuntimeRegistry | None = None


def get_registry() -> RuntimeRegistry:
    global _registry
    if _registry is None:
        _registry = RuntimeRegistry()
    return _registry


def set_registry(registry: RuntimeRegistry) -> None:
    global _registry
    _registry = registry
