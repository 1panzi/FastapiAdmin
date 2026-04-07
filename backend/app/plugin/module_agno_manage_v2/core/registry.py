"""
RuntimeRegistry（极简版）— 只管 agent/team 运行时对象列表。

v2 设计原则：
- registry 极简，只维护 agent/team 的列表和 uuid→对象 映射
- 其余资源（model/embedder/reader/toolkit 等）通过 RefResolver 按需构建
- 不再做复杂的行数据缓存和 callable factory 路由
"""

from typing import Any


class RuntimeRegistry:
    """
    全局运行时对象注册中心（v2 极简版）。

    维护 agent/team 列表，供 AgentOS 路由直接引用。
    所有 key = str(uuid)。
    """

    def __init__(self):
        # AgentOS 直接引用这两个列表（传引用，append 即时生效）
        self.agents: list = []
        self.teams: list = []

        # uuid → 对象 映射，用于快速查找和更新
        self._agents_map: dict[str, Any] = {}
        self._teams_map: dict[str, Any] = {}

    # ── Agent ────────────────────────────────────────────────────────────────

    def add_agent(self, uuid: str, agent) -> None:
        """注册 Agent，追加到 agents 列表并建立 uuid 映射。"""
        self._agents_map[uuid] = agent
        self.agents.append(agent)

    def remove_agent(self, uuid: str) -> None:
        """注销 Agent，从列表和映射中移除。"""
        agent = self._agents_map.pop(uuid, None)
        if agent is not None:
            self.agents[:] = [a for a in self.agents if a is not agent]

    def replace_agent(self, uuid: str, new_agent) -> None:
        """替换已有 Agent（更新时使用）。"""
        self.remove_agent(uuid)
        self.add_agent(uuid, new_agent)

    def get_agent(self, uuid: str) -> Any | None:
        """按 uuid 取 Agent 实例。"""
        return self._agents_map.get(uuid)

    # ── Team ─────────────────────────────────────────────────────────────────

    def add_team(self, uuid: str, team) -> None:
        """注册 Team，追加到 teams 列表并建立 uuid 映射。"""
        self._teams_map[uuid] = team
        self.teams.append(team)

    def remove_team(self, uuid: str) -> None:
        """注销 Team，从列表和映射中移除。"""
        team = self._teams_map.pop(uuid, None)
        if team is not None:
            self.teams[:] = [t for t in self.teams if t is not team]

    def replace_team(self, uuid: str, new_team) -> None:
        """替换已有 Team（更新时使用）。"""
        self.remove_team(uuid)
        self.add_team(uuid, new_team)

    def get_team(self, uuid: str) -> Any | None:
        """按 uuid 取 Team 实例。"""
        return self._teams_map.get(uuid)

    # ── Shutdown ──────────────────────────────────────────────────────────────

    def shutdown(self) -> None:
        """预留关闭钩子，v2 暂不需要清理。"""
        pass


# ── 全局单例 ──────────────────────────────────────────────────────────────────

_registry: RuntimeRegistry | None = None


def get_registry() -> RuntimeRegistry:
    """获取全局 RuntimeRegistry 单例，未初始化时抛出 AssertionError。"""
    assert _registry is not None, "Registry not initialized"
    return _registry


def set_registry(registry: RuntimeRegistry) -> None:
    """设置全局 RuntimeRegistry 单例（由 startup 调用）。"""
    global _registry
    _registry = registry
