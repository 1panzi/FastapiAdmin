from typing import Any

from sqlalchemy import and_, or_, select
from sqlalchemy.sql.elements import ColumnElement

from app.api.v1.module_system.auth.schema import AuthSchema
from app.api.v1.module_system.dept.model import DeptModel
from app.api.v1.module_system.user.model import UserModel
from app.common.enums import PermissionFilterStrategy
from app.utils.common_util import get_child_id_map, get_child_recursion


class Permission:
    """
    为业务模型提供数据权限过滤功能

    使用策略模式，根据模型的 __permission_strategy__ 属性选择合适的过滤策略
    """

    # 数据权限常量定义，提高代码可读性
    DATA_SCOPE_SELF = 1  # 仅本人数据
    DATA_SCOPE_DEPT = 2  # 本部门数据
    DATA_SCOPE_DEPT_AND_CHILD = 3  # 本部门及以下数据
    DATA_SCOPE_ALL = 4  # 全部数据
    DATA_SCOPE_CUSTOM = 5  # 自定义数据

    def __init__(self, model: Any, auth: AuthSchema) -> None:
        """
        初始化权限过滤器实例

        Args:
            db: 数据库会话
            model: 数据模型类
            current_user: 当前用户对象
            auth: 认证信息对象
        """
        self.model = model
        self.auth = auth
        self.conditions: list[ColumnElement] = []  # 权限条件列表

    async def filter_query(self, query: Any) -> Any:
        """
        异步过滤查询对象

        Args:
            query: SQLAlchemy查询对象

        Returns:
            过滤后的查询对象
        """
        condition = await self.__permission_condition()
        return query.where(condition) if condition is not None else query

    async def __permission_condition(self) -> ColumnElement | None:
        """
        应用数据范围权限隔离

        根据模型的权限过滤策略，选择合适的过滤方法
        """
        # 如果不需要检查数据权限,则不限制
        if not self.auth.user:
            return None

        # 如果检查数据权限为False,则不限制
        if not self.auth.check_data_scope:
            return None

        # 超级管理员可以查看所有数据
        if self.auth.user.is_superuser:
            return None

        # 获取模型的权限过滤策略
        strategy = getattr(self.model, "__permission_strategy__", PermissionFilterStrategy.DATA_SCOPE)

        # 根据策略选择过滤方法
        if strategy == PermissionFilterStrategy.ROLE_BASED:
            return await self.__filter_by_role_based()
        elif strategy == PermissionFilterStrategy.DEPT_BASED:
            return await self.__filter_by_dept_based()
        elif strategy == PermissionFilterStrategy.SELF_ONLY:
            return await self.__filter_by_self_only()
        elif strategy == PermissionFilterStrategy.USER_ROLE:
            return await self.__filter_by_user_role()
        else:
            return await self.__filter_by_data_scope()

    async def __filter_by_role_based(self) -> ColumnElement | None:
        """
        基于角色授权的权限过滤（适用于菜单等）

        只显示用户角色授权的菜单
        """
        roles = getattr(self.auth.user, "roles", []) or []
        if not roles:
            id_attr = getattr(self.model, "id", None)
            if id_attr is not None:
                return id_attr == -1
            return None

        menu_ids = set()
        for role in roles:
            if hasattr(role, "menus") and role.menus:
                menu_ids.update(menu.id for menu in role.menus if menu.status == "0")

        if menu_ids:
            id_attr = getattr(self.model, "id", None)
            if id_attr is not None:
                return id_attr.in_(list(menu_ids))

        id_attr = getattr(self.model, "id", None)
        if id_attr is not None:
            return id_attr == -1
        return None

    async def __filter_by_user_role(self) -> ColumnElement | None:
        """
        基于当前用户绑定角色的权限过滤（适用于角色列表）

        只显示当前用户绑定的角色
        """
        roles = getattr(self.auth.user, "roles", []) or []
        if not roles:
            id_attr = getattr(self.model, "id", None)
            if id_attr is not None:
                return id_attr == -1
            return None

        role_ids = [role.id for role in roles]
        id_attr = getattr(self.model, "id", None)
        if id_attr is not None:
            return id_attr.in_(role_ids)
        return None

    async def __filter_by_dept_based(self) -> ColumnElement | None:
        """
        基于部门关联的权限过滤（适用于部门、角色等）

        根据用户的部门权限范围过滤数据
        """
        # 如果用户没有角色,则只能查看自己部门的数据
        roles = getattr(self.auth.user, "roles", []) or []
        if not roles:
            user_dept_id = getattr(self.auth.user, "dept_id", None)
            if user_dept_id is not None and hasattr(self.model, "id"):
                id_attr = getattr(self.model, "id", None)
                if id_attr is not None:
                    return id_attr == user_dept_id
            return None

        # 获取用户所有角色的权限范围（支持菜单/按钮级覆盖）
        data_scopes, custom_dept_ids = await self.__resolve_menu_data_scope(
            roles, self.auth.current_permission
        )

        # 全部数据权限最高优先级
        if self.DATA_SCOPE_ALL in data_scopes:
            return None

        # 收集所有可访问的部门ID
        accessible_dept_ids = await self.__get_accessible_dept_ids(data_scopes, custom_dept_ids)

        # 根据模型类型过滤
        if self.model.__name__ == "DeptModel":
            return self.__filter_dept_model(accessible_dept_ids)
        elif self.model.__name__ == "UserModel":
            return self.__filter_user_model(accessible_dept_ids)
        else:
            return None

    async def __filter_by_self_only(self) -> ColumnElement | None:
        """
        仅本人数据权限过滤
        """
        created_id_attr = getattr(self.model, "created_id", None)
        if created_id_attr is not None and self.auth.user:
            return created_id_attr == self.auth.user.id
        return None

    async def __filter_by_data_scope(self) -> ColumnElement | None:
        """
        基于数据范围权限的通用过滤（默认策略）

        适用于大多数业务模型
        """
        # 如果模型没有创建人created_id字段,则不限制
        if not hasattr(self.model, "created_id"):
            return None

        # 如果用户没有角色,则只能查看自己的数据
        roles = getattr(self.auth.user, "roles", []) or []
        if not roles:
            created_id_attr = getattr(self.model, "created_id", None)
            if created_id_attr is not None and self.auth.user:
                return created_id_attr == self.auth.user.id
            return None

        # 获取用户所有角色的权限范围（支持菜单/按钮级覆盖）
        data_scopes, custom_dept_ids = await self.__resolve_menu_data_scope(
            roles, self.auth.current_permission
        )

        # 全部数据权限最高优先级
        if self.DATA_SCOPE_ALL in data_scopes:
            return None

        # 收集所有可访问的部门ID
        accessible_dept_ids = await self.__get_accessible_dept_ids(data_scopes, custom_dept_ids)

        # 如果有部门权限，使用部门过滤
        if accessible_dept_ids:
            # 特殊处理：如果模型本身就是UserModel，直接过滤用户的dept_id
            if self.model.__name__ == "UserModel" and hasattr(self.model, "dept_id"):
                dept_id_attr = getattr(self.model, "dept_id", None)
                if dept_id_attr is not None:
                    return dept_id_attr.in_(list(accessible_dept_ids))

            # 其他模型：通过created_by关系过滤创建人的部门
            creator_rel = getattr(self.model, "created_by", None)
            if creator_rel is not None and hasattr(UserModel, "dept_id"):
                return creator_rel.has(UserModel.dept_id.in_(list(accessible_dept_ids)))

            # 降级方案：只能查看自己的数据
            created_id_attr = getattr(self.model, "created_id", None)
            if created_id_attr is not None and self.auth.user:
                return created_id_attr == self.auth.user.id
            return None

        # 处理仅本人数据权限
        if self.DATA_SCOPE_SELF in data_scopes:
            created_id_attr = getattr(self.model, "created_id", None)
            if created_id_attr is not None and self.auth.user:
                return created_id_attr == self.auth.user.id
            return None

        # 默认情况：只能查看自己的数据
        created_id_attr = getattr(self.model, "created_id", None)
        if created_id_attr is not None and self.auth.user:
            return created_id_attr == self.auth.user.id
        return None

    async def __resolve_menu_data_scope(
        self, roles: list, current_permission: str | None
    ) -> tuple[set[int], set[int]]:
        """
        解析数据权限范围，支持菜单/按钮级覆盖

        三级继承链路：按钮自身 data_scope → 父菜单 data_scope → 角色 data_scope
        多角色场景采用并集策略（权限最大化）

        Args:
            roles: 用户的角色列表
            current_permission: 当前请求的权限标识（如 "module_system:user:query"）

        Returns:
            (data_scopes, custom_dept_ids) 元组
        """
        data_scopes: set[int] = set()
        custom_dept_ids: set[int] = set()

        if not current_permission:
            # 回退：使用角色级 data_scope（现有行为）
            for role in roles:
                data_scopes.add(role.data_scope)
                if role.data_scope == self.DATA_SCOPE_CUSTOM and hasattr(role, "depts") and role.depts:
                    custom_dept_ids.update(dept.id for dept in role.depts)
            return data_scopes, custom_dept_ids

        # 在所有角色中查找匹配 current_permission 的菜单，同时记录菜单对象以获取 type 和 parent_id
        role_menu_pairs: list[tuple[int, int, Any, Any]] = []  # (role_id, menu_id, role, menu)
        for role in roles:
            for menu in (getattr(role, "menus", None) or []):
                if (
                    getattr(menu, "permission", None) == current_permission
                    and getattr(menu, "status", None) == "0"
                ):
                    role_menu_pairs.append((role.id, menu.id, role, menu))
                    break  # 每个角色只取一个匹配

        if not role_menu_pairs:
            # 没有角色包含此权限——回退到角色级
            for role in roles:
                data_scopes.add(role.data_scope)
                if role.data_scope == self.DATA_SCOPE_CUSTOM and hasattr(role, "depts") and role.depts:
                    custom_dept_ids.update(dept.id for dept in role.depts)
            return data_scopes, custom_dept_ids

        # 批量查询 RoleMenusModel 中的菜单级 data_scope
        from app.api.v1.module_system.role.model import RoleMenuDeptsModel, RoleMenusModel

        pairs_filter = or_(
            *[
                and_(RoleMenusModel.role_id == rid, RoleMenusModel.menu_id == mid)
                for rid, mid, _, _ in role_menu_pairs
            ]
        )
        result = await self.auth.db.execute(
            select(RoleMenusModel.role_id, RoleMenusModel.menu_id, RoleMenusModel.data_scope).where(
                pairs_filter
            )
        )
        per_menu_scopes = {(row.role_id, row.menu_id): row.data_scope for row in result}

        # 对 type=3 且自身 data_scope 为 NULL 的按钮，收集需要查询父菜单 data_scope 的对
        parent_lookups: list[tuple[int, int]] = []  # (role_id, parent_menu_id)
        for role_id, menu_id, _, menu in role_menu_pairs:
            scope = per_menu_scopes.get((role_id, menu_id))
            parent_id = getattr(menu, "parent_id", None)
            if scope is None and getattr(menu, "type", None) == 3 and parent_id:
                parent_lookups.append((role_id, parent_id))

        # 批量查询父菜单 data_scope
        parent_scopes: dict[tuple[int, int], int | None] = {}
        if parent_lookups:
            parent_filter = or_(
                *[
                    and_(RoleMenusModel.role_id == rid, RoleMenusModel.menu_id == pid)
                    for rid, pid in parent_lookups
                ]
            )
            parent_result = await self.auth.db.execute(
                select(
                    RoleMenusModel.role_id, RoleMenusModel.menu_id, RoleMenusModel.data_scope
                ).where(parent_filter)
            )
            parent_scopes = {(row.role_id, row.menu_id): row.data_scope for row in parent_result}

        # 解析每个角色在该权限下的实际 data_scope（三级继承）
        for role_id, menu_id, role, menu in role_menu_pairs:
            scope = per_menu_scopes.get((role_id, menu_id))
            # 记录 scope 实际来源的 menu_id（用于查找自定义部门）
            scope_menu_id: int | None = menu_id

            # 三级继承：按钮自身 → 父菜单 → 角色
            if scope is None and getattr(menu, "type", None) == 3 and getattr(menu, "parent_id", None):
                parent_scope = parent_scopes.get((role_id, menu.parent_id))
                if parent_scope is not None:
                    scope = parent_scope
                    scope_menu_id = menu.parent_id  # scope 来源于父菜单

            if scope is None:
                scope = role.data_scope  # 最终回退到角色级
                scope_menu_id = None  # scope 来源于角色级

            data_scopes.add(scope)

            if scope == self.DATA_SCOPE_CUSTOM:
                if scope_menu_id is not None:
                    # 从 scope 来源的菜单级查找自定义部门
                    dept_result = await self.auth.db.execute(
                        select(RoleMenuDeptsModel.dept_id).where(
                            RoleMenuDeptsModel.role_id == role_id,
                            RoleMenuDeptsModel.menu_id == scope_menu_id,
                        )
                    )
                    menu_dept_ids = {row.dept_id for row in dept_result}
                    if menu_dept_ids:
                        custom_dept_ids.update(menu_dept_ids)
                    elif hasattr(role, "depts") and role.depts:
                        # 菜单级没有配置部门，回退到角色级自定义部门
                        custom_dept_ids.update(dept.id for dept in role.depts)
                elif hasattr(role, "depts") and role.depts:
                    # scope 来源于角色级，直接使用角色级自定义部门
                    custom_dept_ids.update(dept.id for dept in role.depts)

        return data_scopes, custom_dept_ids

    async def __get_accessible_dept_ids(
        self, data_scopes: set, custom_dept_ids: set
    ) -> set[int]:
        """
        获取用户可访问的所有部门ID

        Args:
            data_scopes: 用户角色的数据权限范围集合
            custom_dept_ids: 自定义权限关联的部门ID集合

        Returns:
            可访问的部门ID集合
        """
        accessible_dept_ids = set()
        user_dept_id = getattr(self.auth.user, "dept_id", None)

        # 处理自定义数据权限（5）
        if self.DATA_SCOPE_CUSTOM in data_scopes:
            accessible_dept_ids.update(custom_dept_ids)

        # 处理本部门数据权限（2）
        if self.DATA_SCOPE_DEPT in data_scopes and user_dept_id is not None:
            accessible_dept_ids.add(user_dept_id)

        # 处理本部门及以下数据权限（3）
        if self.DATA_SCOPE_DEPT_AND_CHILD in data_scopes and user_dept_id is not None:
            try:
                dept_sql = select(DeptModel)
                dept_result = await self.auth.db.execute(dept_sql)
                dept_objs = dept_result.scalars().all()
                id_map = get_child_id_map(dept_objs)
                dept_with_children_ids = get_child_recursion(id=user_dept_id, id_map=id_map)
                accessible_dept_ids.update(dept_with_children_ids)
            except Exception:
                accessible_dept_ids.add(user_dept_id)

        return accessible_dept_ids

    def __filter_dept_model(self, accessible_dept_ids: set[int]) -> ColumnElement | None:
        """
        过滤部门模型
        """
        if accessible_dept_ids:
            id_attr = getattr(self.model, "id", None)
            if id_attr is not None:
                return id_attr.in_(list(accessible_dept_ids))
        user_dept_id = getattr(self.auth.user, "dept_id", None)
        if user_dept_id is not None:
            id_attr = getattr(self.model, "id", None)
            if id_attr is not None:
                return id_attr == user_dept_id
        return None

    def __filter_user_model(self, accessible_dept_ids: set[int]) -> ColumnElement | None:
        """
        过滤用户模型
        """
        if accessible_dept_ids:
            dept_id_attr = getattr(self.model, "dept_id", None)
            if dept_id_attr is not None:
                return dept_id_attr.in_(list(accessible_dept_ids))
        return None
