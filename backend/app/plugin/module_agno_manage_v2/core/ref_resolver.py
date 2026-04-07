"""
RefResolver — 统一处理 ref/inline/override 三种资源引用模式。

支持的 value 格式：
  - None                         → return None
  - {"ref": "uuid"}              → 查 ag_resources，展开 config，递归 build
  - {"ref": "uuid", "override": {...}} → 查表，merge override，build
  - {"category": ..., "type": ..., ...} → inline，直接 build

缓存策略：
  - 无 override：cache_key = uuid
  - 有 override：cache_key = f"{uuid}:{hash(str(sorted(override.items())))}"

注意：因为 FastapiAdmin 使用 async SQLAlchemy，resolve 方法为 async。
"""

import inspect
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.plugin.module_agno_manage_v2.resource.model import AgResourceModel


class RefResolver:
    """
    统一处理 ref/inline/override 三种资源引用格式，并缓存已构建对象。

    Usage:
        resolver = RefResolver(db)
        model = await resolver.resolve({"ref": "some-uuid"})
        tools = await resolver.resolve_list([{"ref": "t1"}, {"ref": "t2"}])
    """

    def __init__(self, db: AsyncSession):
        self.db = db
        self._cache: dict[str, Any] = {}

    async def resolve(self, value: dict | None) -> Any:
        """
        解析单个资源引用。

        Args:
            value: ref dict / inline dict / None

        Returns:
            已构建的 Agno 对象，或 None
        """
        if value is None:
            return None

        if "ref" in value:
            uuid = value["ref"]
            override = value.get("override") or {}

            # 构建 cache_key
            if override:
                cache_key = f"{uuid}:{hash(str(sorted(override.items())))}"
            else:
                cache_key = uuid

            if cache_key in self._cache:
                return self._cache[cache_key]

            # 查询 ag_resources
            result = await self.db.execute(
                select(AgResourceModel).where(
                    AgResourceModel.uuid == uuid,
                    AgResourceModel.status == "0",
                )
            )
            row = result.scalar_one_or_none()
            if row is None:
                raise ValueError(f"Resource {uuid} not found or disabled")

            # merge config + override
            config = {**(row.config or {}), **override}

            # 调用对应 builder
            from app.plugin.module_agno_manage_v2.core.builder_registry import builder_registry
            builder = builder_registry.get((row.category, row.type))
            if builder is None:
                raise ValueError(
                    f"No builder registered for category={row.category}, type={row.type}"
                )

            result = builder.build(config, self)
            if inspect.iscoroutine(result):
                result = await result
            self._cache[cache_key] = result
            return result

        # inline 模式：必须包含 category + type
        value = dict(value)
        category = value.pop("category", None)
        type_ = value.pop("type", None)
        if category is None or type_ is None:
            raise ValueError(
                f"Inline resource must have 'category' and 'type' fields, got: {list(value.keys())}"
            )

        from app.plugin.module_agno_manage_v2.core.builder_registry import builder_registry
        builder = builder_registry.get((category, type_))
        if builder is None:
            raise ValueError(
                f"No builder registered for category={category}, type={type_}"
            )

        result = builder.build(value, self)
        if inspect.iscoroutine(result):
            result = await result
        return result

    async def resolve_list(self, values: list | None) -> list:
        """
        解析资源引用列表，对每个元素调用 resolve。

        Args:
            values: ref/inline dict 的列表，或 None

        Returns:
            已构建对象的列表（跳过 None 结果）
        """
        if not values:
            return []
        results = []
        for v in values:
            obj = await self.resolve(v)
            if obj is not None:
                results.append(obj)
        return results
