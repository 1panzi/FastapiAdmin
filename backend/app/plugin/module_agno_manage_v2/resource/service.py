"""
AgResourceService — v2 资源管理服务层。

职责：
- 调 CRUD 层做 DB 操作
- 对 agent/team 类型资源同步维护 RuntimeRegistry（add/replace/remove）
- build 时通过 RefResolver + builder_registry 构建 Agno 对象
"""

import inspect

from app.api.v1.module_system.auth.schema import AuthSchema
from app.core.exceptions import CustomException
from app.core.logger import log
from app.plugin.module_agno_manage_v2.core.builder_registry import builder_registry
from app.plugin.module_agno_manage_v2.core.ref_resolver import RefResolver
from app.plugin.module_agno_manage_v2.core.registry import get_registry
from app.plugin.module_agno_manage_v2.resource.crud import AgResourceCRUD
from app.plugin.module_agno_manage_v2.resource.schema import (
    AgResourceCreateSchema,
    AgResourceOutSchema,
    AgResourceUpdateSchema,
)


async def _build_and_register(row, auth: AuthSchema) -> None:
    """根据 row 构建 Agno 对象，并注册到 RuntimeRegistry（仅 agent/team）。"""
    builder = builder_registry.get((row.category, row.type))
    if not builder:
        return
    resolver = RefResolver(db=auth.db)
    result = builder.build(row.config or {}, resolver)
    if inspect.iscoroutine(result):
        result = await result
    registry = get_registry()
    uuid = str(row.uuid)
    if row.category == "agent":
        registry.replace_agent(uuid, result)
    elif row.category == "team":
        registry.replace_team(uuid, result)


class AgResourceService:
    """AI 资源统一管理服务层（v2）。"""

    @classmethod
    async def detail_resources_service(cls, auth: AuthSchema, id: int) -> dict:
        """
        获取资源详情，并用 schema 默认值补全 config。

        参数:
        - auth: AuthSchema — 认证信息
        - id: int — 数据 ID

        返回:
        - dict — 资源详情（config 已补全默认值）
        """
        row = await AgResourceCRUD(auth).get_by_id_resources_crud(id=id)
        if not row:
            raise CustomException(msg="该数据不存在")

        builder = builder_registry.get((row.category, row.type))
        result = AgResourceOutSchema.model_validate(row).model_dump()

        if builder:
            # 用 builder schema 的默认值补全 config
            full_config = {}
            for field in builder.schema:
                name = field["name"]
                if name in (row.config or {}):
                    full_config[name] = row.config[name]
                elif "default" in field:
                    full_config[name] = field["default"]
            result["config"] = full_config

        return result

    @classmethod
    async def page_resources_service(
        cls,
        auth: AuthSchema,
        page_no: int,
        page_size: int,
        search=None,
        order_by: list[dict] | None = None,
    ) -> dict:
        """
        分页查询（数据库分页）。

        参数:
        - auth: AuthSchema — 认证信息
        - page_no: int — 页码
        - page_size: int — 每页数量
        - search — 查询参数对象（含 __dict__）
        - order_by: list[dict] | None — 排序参数

        返回:
        - dict — 分页查询结果
        """
        search_dict = search.__dict__ if search else {}
        order_by_list = order_by or [{"id": "asc"}]
        offset = (page_no - 1) * page_size
        return await AgResourceCRUD(auth).page_resources_crud(
            offset=offset,
            limit=page_size,
            order_by=order_by_list,
            search=search_dict,
        )

    @classmethod
    async def create_resource_service(
        cls,
        auth: AuthSchema,
        data: AgResourceCreateSchema,
    ) -> dict:
        """
        创建资源，agent/team 同步注册到 RuntimeRegistry。

        参数:
        - auth: AuthSchema — 认证信息
        - data: AgResourceCreateSchema — 创建数据

        返回:
        - dict — 创建结果
        """
        row = await AgResourceCRUD(auth).create_resources_crud(data=data)
        if row and row.status == "0" and row.category in ("agent", "team"):
            try:
                await _build_and_register(row, auth)
            except Exception as e:
                log.warning(
                    f"[ResourceV2] registry build failed on create uuid={row.uuid}: {e}"
                )
        return AgResourceOutSchema.model_validate(row).model_dump()

    @classmethod
    async def update_resource_service(
        cls,
        auth: AuthSchema,
        id: int,
        data: AgResourceUpdateSchema,
    ) -> dict:
        """
        更新资源，agent/team 同步重建 RuntimeRegistry 中的实例。

        参数:
        - auth: AuthSchema — 认证信息
        - id: int — 数据 ID
        - data: AgResourceUpdateSchema — 更新数据

        返回:
        - dict — 更新结果
        """
        existing = await AgResourceCRUD(auth).get_by_id_resources_crud(id=id)
        if not existing:
            raise CustomException(msg="更新失败，该数据不存在")

        row = await AgResourceCRUD(auth).update_resources_crud(id=id, data=data)
        if row and row.category in ("agent", "team"):
            try:
                registry = get_registry()
                uuid = str(row.uuid)
                if row.status == "0":
                    await _build_and_register(row, auth)
                else:
                    # 禁用时从 registry 移除
                    if row.category == "agent":
                        registry.remove_agent(uuid)
                    else:
                        registry.remove_team(uuid)
            except Exception as e:
                log.warning(
                    f"[ResourceV2] registry build failed on update uuid={row.uuid}: {e}"
                )
        return AgResourceOutSchema.model_validate(row).model_dump()

    @classmethod
    async def delete_resource_service(cls, auth: AuthSchema, ids: list[int]) -> None:
        """
        删除资源，同步从 RuntimeRegistry 移除 agent/team。

        参数:
        - auth: AuthSchema — 认证信息
        - ids: list[int] — 数据 ID 列表

        返回:
        - None
        """
        if len(ids) < 1:
            raise CustomException(msg="删除失败，删除对象不能为空")

        uuids_to_remove: list[tuple[str, str]] = []  # [(uuid, category)]
        for id in ids:
            row = await AgResourceCRUD(auth).get_by_id_resources_crud(id=id)
            if not row:
                raise CustomException(msg=f"删除失败，ID 为 {id} 的数据不存在")
            if row.category in ("agent", "team"):
                uuids_to_remove.append((str(row.uuid), row.category))

        await AgResourceCRUD(auth).delete_resources_crud(ids=ids)

        registry = get_registry()
        for uuid, category in uuids_to_remove:
            try:
                if category == "agent":
                    registry.remove_agent(uuid)
                else:
                    registry.remove_team(uuid)
            except Exception as e:
                log.warning(
                    f"[ResourceV2] registry remove failed on delete uuid={uuid}: {e}"
                )

    @classmethod
    async def set_available_resource_service(
        cls,
        auth: AuthSchema,
        ids: list[int],
        status: str,
    ) -> None:
        """
        批量设置可用状态，同步更新 RuntimeRegistry。

        参数:
        - auth: AuthSchema — 认证信息
        - ids: list[int] — 数据 ID 列表
        - status: str — 目标状态 ("0"=启用, "1"=禁用)

        返回:
        - None
        """
        # 先取出行数据（操作前获取，避免更新后拿不到 uuid）
        rows = []
        for id in ids:
            row = await AgResourceCRUD(auth).get_by_id_resources_crud(id=id)
            if row:
                rows.append(row)

        await AgResourceCRUD(auth).set_available_resources_crud(ids=ids, status=status)

        registry = get_registry()
        for row in rows:
            if row.category not in ("agent", "team"):
                continue
            uuid = str(row.uuid)
            try:
                if status == "0":
                    # 重新构建并注册（需要刷新 row 以拿到最新 config）
                    refreshed = await AgResourceCRUD(auth).get_by_id_resources_crud(
                        id=row.id
                    )
                    if refreshed:
                        await _build_and_register(refreshed, auth)
                else:
                    if row.category == "agent":
                        registry.remove_agent(uuid)
                    else:
                        registry.remove_team(uuid)
            except Exception as e:
                log.warning(
                    f"[ResourceV2] registry update failed on set_available uuid={uuid}: {e}"
                )
