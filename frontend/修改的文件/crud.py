from collections.abc import Sequence

from sqlalchemy import delete, select, update

from app.api.v1.module_system.auth.schema import AuthSchema
from app.api.v1.module_system.dept.crud import DeptCRUD
from app.api.v1.module_system.menu.crud import MenuCRUD
from app.core.base_crud import CRUDBase

from .model import RoleMenuDeptsModel, RoleMenusModel, RoleModel
from .schema import MenuDataScopeItem, RoleCreateSchema, RoleUpdateSchema


class RoleCRUD(CRUDBase[RoleModel, RoleCreateSchema, RoleUpdateSchema]):
    """角色模块数据层"""

    def __init__(self, auth: AuthSchema) -> None:
        """
        初始化角色模块数据层

        参数:
        - auth (AuthSchema): 认证信息模型
        """
        self.auth = auth
        super().__init__(model=RoleModel, auth=auth)

    async def get_by_id_crud(self, id: int, preload: list | None = None) -> RoleModel | None:
        """
        根据id获取角色信息

        参数:
        - id (int): 角色ID
        - preload (list | None): 预加载选项

        返回:
        - RoleModel | None: 角色模型对象
        """
        return await self.get(id=id, preload=preload)

    async def get_list_crud(
        self,
        search: dict | None = None,
        order_by: list | None = None,
        preload: list | None = None,
    ) -> Sequence[RoleModel]:
        """
        获取角色列表

        参数:
        - search (dict | None): 查询参数
        - order_by (list | None): 排序参数
        - preload (list | None): 预加载选项

        返回:
        - Sequence[RoleModel]: 角色模型对象列表
        """
        return await self.list(search=search, order_by=order_by, preload=preload)

    async def set_role_menus_crud(self, role_ids: list[int], menu_ids: list[int]) -> None:
        """
        设置角色的菜单权限

        参数:
        - role_ids (List[int]): 角色ID列表
        - menu_ids (List[int]): 菜单ID列表

        返回:
        - None
        """
        roles = await self.list(search={"id": ("in", role_ids)})
        menus = await MenuCRUD(self.auth).get_list_crud(search={"id": ("in", menu_ids)})

        for obj in roles:
            relationship = obj.menus
            relationship.clear()
            relationship.extend(menus)
        await self.auth.db.flush()

    async def set_role_data_scope_crud(self, role_ids: list[int], data_scope: int) -> None:
        """
        设置角色的数据范围

        参数:
        - role_ids (list[int]): 角色ID列表
        - data_scope (int): 数据范围

        返回:
        - None
        """
        await self.set(ids=role_ids, data_scope=data_scope)

    async def set_role_depts_crud(self, role_ids: list[int], dept_ids: list[int]) -> None:
        """
        设置角色的部门权限

        参数:
        - role_ids (list[int]): 角色ID列表
        - dept_ids (list[int]): 部门ID列表

        返回:
        - None
        """
        roles = await self.list(search={"id": ("in", role_ids)})
        depts = await DeptCRUD(self.auth).get_list_crud(search={"id": ("in", dept_ids)})

        for obj in roles:
            relationship = obj.depts
            relationship.clear()
            relationship.extend(depts)
        await self.auth.db.flush()

    async def set_available_crud(self, ids: list[int], status: str) -> None:
        """
        设置角色的可用状态

        参数:
        - ids (list[int]): 角色ID列表
        - status (str): 可用状态

        返回:
        - None
        """
        await self.set(ids=ids, status=status)

    async def set_role_menu_data_scopes_crud(
        self, role_id: int, menu_data_scopes: list[MenuDataScopeItem]
    ) -> None:
        """
        设置角色的菜单级数据权限

        参数:
        - role_id (int): 角色ID
        - menu_data_scopes (list[MenuDataScopeItem]): 菜单级数据权限配置列表

        返回:
        - None
        """
        for item in menu_data_scopes:
            # 更新 sys_role_menus 中的 data_scope
            await self.auth.db.execute(
                update(RoleMenusModel)
                .where(RoleMenusModel.role_id == role_id, RoleMenusModel.menu_id == item.menu_id)
                .values(data_scope=item.data_scope)
            )

            # 先清除该（角色, 菜单）对的旧自定义部门记录
            await self.auth.db.execute(
                delete(RoleMenuDeptsModel).where(
                    RoleMenuDeptsModel.role_id == role_id,
                    RoleMenuDeptsModel.menu_id == item.menu_id,
                )
            )

            # 如果 data_scope=5，写入新的自定义部门记录
            if item.data_scope == 5 and item.dept_ids:
                for dept_id in item.dept_ids:
                    self.auth.db.add(
                        RoleMenuDeptsModel(role_id=role_id, menu_id=item.menu_id, dept_id=dept_id)
                    )

        await self.auth.db.flush()

    async def get_role_menu_data_scopes_crud(self, role_id: int) -> list[dict]:
        """
        获取角色的菜单级数据权限配置

        参数:
        - role_id (int): 角色ID

        返回:
        - list[dict]: 菜单级数据权限配置列表
        """
        # 查询所有设置了菜单级 data_scope 的记录
        result = await self.auth.db.execute(
            select(RoleMenusModel.menu_id, RoleMenusModel.data_scope).where(
                RoleMenusModel.role_id == role_id,
                RoleMenusModel.data_scope.isnot(None),
            )
        )
        rows = result.all()

        items = []
        for row in rows:
            dept_ids: list[int] = []
            if row.data_scope == 5:
                # 查询自定义部门
                dept_result = await self.auth.db.execute(
                    select(RoleMenuDeptsModel.dept_id).where(
                        RoleMenuDeptsModel.role_id == role_id,
                        RoleMenuDeptsModel.menu_id == row.menu_id,
                    )
                )
                dept_ids = [r.dept_id for r in dept_result.all()]

            items.append(
                {"menu_id": row.menu_id, "data_scope": row.data_scope, "dept_ids": dept_ids}
            )

        return items
