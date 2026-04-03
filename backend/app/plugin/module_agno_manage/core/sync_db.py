"""
同步数据库访问层，专供 callable factory 使用。

背景：
  Agno 的 callable factory 通过 invoke_callable_factory() 同步调用（在 run() 时），
  无法 await，因此 resolve_tools / resolve_knowledge 必须走同步查询。
  使用独立同步连接池，与主 asyncpg 连接池隔离。

依赖：
  settings.DB_URI — 同步数据库 URL（如 postgresql+psycopg://...）
"""

from collections import namedtuple

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from app.config.setting import settings
from app.core.logger import log


def _create_sync_engine():
    return create_engine(
        settings.DB_URI,
        pool_size=5,
        max_overflow=5,
        pool_pre_ping=True,
    )


_sync_engine = _create_sync_engine()
_SyncSession = sessionmaker(bind=_sync_engine)

# ── namedtuple 轻量返回值 ──────────────────────────────────────────────────────
Binding = namedtuple("Binding", ["resource_type", "resource_id","priority", "config_override"])
TeamMember = namedtuple("TeamMember", ["member_id", "member_type", "member_order", "role"])


class SyncBindingRepo:
    """
    同步查询 ag_bindings，供 callable factory 在 Agno run() 时调用。
    返回 Binding(resource_type, resource_id) namedtuple 列表。
    """

    @staticmethod
    def get_active(
        owner_id: str,
        owner_type: str = "agent",
        resource_type: str | None = None,
    ) -> list[Binding]:
        sql = """
            SELECT resource_type, resource_id::text, priority, config_override
            FROM ag_bindings
            WHERE owner_id = :owner_id
              AND owner_type = :owner_type
              AND status = '0'
        """
        # ag_bindings.owner_id 是整数列，需要传整数避免类型不匹配
        try:
            owner_id_int = int(owner_id)
        except (ValueError, TypeError):
            return []
        params: dict = {"owner_id": owner_id_int, "owner_type": owner_type}
        if resource_type:
            sql += " AND resource_type = :resource_type"
            params["resource_type"] = resource_type

        try:
            with _SyncSession() as session:
                rows = session.execute(text(sql), params).fetchall()
            # resource_id 是整数，转为字符串与 registry key 保持一致
            binding_results = []
            for row in rows:
                if row.config_override and isinstance(row.config_override, str):
                    row.config_override = json.loads(row.config_override)
                binding_results.append(Binding(row.resource_type, str(row.resource_id), row.priority, row.config_override))
            return binding_results
        except Exception as e:
            log.error(f"[SyncBindingRepo] query failed: {e}")
            return []


class SyncTeamMemberRepo:
    """
    同步查询 ag_team_members，供 Team callable factory 使用。
    返回 TeamMember namedtuple 列表，按 member_order 排序。
    """

    @staticmethod
    def get_active(team_id: str) -> list[TeamMember]:
        sql = """
            SELECT member_id::text, member_type, member_order, role
            FROM ag_team_members
            WHERE team_id = :team_id AND status = '0'
            ORDER BY member_order
        """
        try:
            with _SyncSession() as session:
                rows = session.execute(text(sql), {"team_id": team_id}).fetchall()
            return [TeamMember(r.member_id, r.member_type, r.member_order, r.role) for r in rows]
        except Exception as e:
            log.error(f"[SyncTeamMemberRepo] query failed: {e}")
            return []
