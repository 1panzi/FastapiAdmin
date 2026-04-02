
import io

import pandas as pd
from fastapi import UploadFile

from app.api.v1.module_system.auth.schema import AuthSchema
from app.core.base_schema import BatchSetAvailable
from app.core.exceptions import CustomException
from app.core.logger import log
from app.plugin.module_agno_manage.bindings.crud import AgBindingCRUD
from app.plugin.module_agno_manage.bindings.schema import AgBindingCreateSchema
from app.plugin.module_agno_manage.core.registry import get_registry
from app.utils.excel_util import ExcelUtil

from .agno_catalog import AgnoToolInfo, get_categories, list_agno_tools
from .crud import AgToolkitCRUD
from .schema import (
    AgToolkitCodeValidateSchema,
    AgToolkitCodeValidateResultSchema,
    AgToolkitCreateSchema,
    AgToolkitGlobalSwitchSchema,
    AgToolkitOutSchema,
    AgToolkitQueryParam,
    AgToolkitUpdateSchema,
)


class AgToolkitService:
    """
    工具管理服务层
    """

    @classmethod
    async def detail_toolkits_service(cls, auth: AuthSchema, id: int) -> dict:
        """
        详情
        
        参数:
        - auth: AuthSchema - 认证信息
        - id: int - 数据ID
        
        返回:
        - dict - 数据详情
        """
        obj = await AgToolkitCRUD(auth).get_by_id_toolkits_crud(id=id)
        if not obj:
            raise CustomException(msg="该数据不存在")
        return AgToolkitOutSchema.model_validate(obj).model_dump()

    @classmethod
    async def list_toolkits_service(cls, auth: AuthSchema, search: AgToolkitQueryParam | None = None, order_by: list[dict] | None = None) -> list[dict]:
        """
        列表查询

        参数:
        - auth: AuthSchema - 认证信息
        - search: AgToolkitQueryParam | None - 查询参数
        - order_by: list[dict] | None - 排序参数

        返回:
        - list[dict] - 数据列表
        """
        search_dict = search.__dict__ if search else {}
        # 普通用户只能看 global_enabled=True 的工具（超管能看全部）
        if not cls._is_super_admin(auth):
            search_dict["global_enabled"] = ("eq", True)
        obj_list = await AgToolkitCRUD(auth).list_toolkits_crud(search=search_dict, order_by=order_by)
        return [AgToolkitOutSchema.model_validate(obj).model_dump() for obj in obj_list]

    @classmethod
    async def page_toolkits_service(cls, auth: AuthSchema, page_no: int, page_size: int, search: AgToolkitQueryParam | None = None, order_by: list[dict] | None = None) -> dict:
        """
        分页查询（数据库分页）

        参数:
        - auth: AuthSchema - 认证信息
        - page_no: int - 页码
        - page_size: int - 每页数量
        - search: AgToolkitQueryParam | None - 查询参数
        - order_by: list[dict] | None - 排序参数

        返回:
        - dict - 分页查询结果
        """
        search_dict = search.__dict__ if search else {}
        # 普通用户只能看 global_enabled=True 的工具（超管能看全部）
        if not cls._is_super_admin(auth):
            search_dict["global_enabled"] = ("eq", True)
        order_by_list = order_by or [{'id': 'asc'}]
        offset = (page_no - 1) * page_size
        result = await AgToolkitCRUD(auth).page_toolkits_crud(
            offset=offset,
            limit=page_size,
            order_by=order_by_list,
            search=search_dict
        )
        return result

    @staticmethod
    def _is_super_admin(auth: AuthSchema) -> bool:
        """判断是否为超管（简化版，实际应该查角色表）。"""
        # TODO: 根据实际权限系统判断，这里暂时用 user.id=1 作为超管
        return auth.user and auth.user.id == 1

    @classmethod
    async def create_toolkits_service(cls, auth: AuthSchema, data: AgToolkitCreateSchema) -> dict:
        """
        创建
        
        参数:
        - auth: AuthSchema - 认证信息
        - data: AgToolkitCreateSchema - 创建数据
        
        返回:
        - dict - 创建结果
        """
        obj = await AgToolkitCRUD(auth).create_toolkits_crud(data=data)
        if obj and obj.status == "0":
            try:
                get_registry().register_toolkit(str(obj.id), obj)
            except Exception as e:
                log.warning(f"[Toolkits] registry register failed for id={obj.id}: {e}")
        return AgToolkitOutSchema.model_validate(obj).model_dump()

    @classmethod
    async def update_toolkits_service(cls, auth: AuthSchema, id: int, data: AgToolkitUpdateSchema) -> dict:
        """
        更新
        
        参数:
        - auth: AuthSchema - 认证信息
        - id: int - 数据ID
        - data: AgToolkitUpdateSchema - 更新数据
        
        返回:
        - dict - 更新结果
        """
        # 检查数据是否存在
        obj = await AgToolkitCRUD(auth).get_by_id_toolkits_crud(id=id)
        if not obj:
            raise CustomException(msg='更新失败，该数据不存在')

        # 检查唯一性约束

        obj = await AgToolkitCRUD(auth).update_toolkits_crud(id=id, data=data)
        if obj:
            try:
                if obj.status == "0":
                    get_registry().register_toolkit(str(obj.id), obj)
                else:
                    get_registry().unregister_toolkit(str(obj.id))
            except Exception as e:
                log.warning(f"[Toolkits] registry update failed for id={obj.id}: {e}")
        return AgToolkitOutSchema.model_validate(obj).model_dump()

    @classmethod
    async def delete_toolkits_service(cls, auth: AuthSchema, ids: list[int]) -> None:
        """
        删除
        
        参数:
        - auth: AuthSchema - 认证信息
        - ids: list[int] - 数据ID列表
        
        返回:
        - None
        """
        if len(ids) < 1:
            raise CustomException(msg='删除失败，删除对象不能为空')
        ids_to_remove = []
        for id in ids:
            obj = await AgToolkitCRUD(auth).get_by_id_toolkits_crud(id=id)
            if not obj:
                raise CustomException(msg=f'删除失败，ID为{id}的数据不存在')
            ids_to_remove.append(str(obj.id))
        await AgToolkitCRUD(auth).delete_toolkits_crud(ids=ids)
        for tid in ids_to_remove:
            get_registry().unregister_toolkit(tid)

    @classmethod
    async def set_available_toolkits_service(cls, auth: AuthSchema, data: BatchSetAvailable) -> None:
        """
        批量设置状态
        
        参数:
        - auth: AuthSchema - 认证信息
        - data: BatchSetAvailable - 批量设置状态数据
        
        返回:
        - None
        """
        obj_list = []
        for id in data.ids:
            obj = await AgToolkitCRUD(auth).get_by_id_toolkits_crud(id=id)
            if obj:
                obj_list.append(obj)
        await AgToolkitCRUD(auth).set_available_toolkits_crud(ids=data.ids, status=data.status)
        for obj in obj_list:
            try:
                if data.status == "0":
                    get_registry().register_toolkit(str(obj.id), obj)
                else:
                    get_registry().unregister_toolkit(str(obj.id))
            except Exception as e:
                log.warning(f"[Toolkits] registry set_available failed for id={obj.id}: {e}")

    @classmethod
    async def batch_export_toolkits_service(cls, obj_list: list[dict]) -> bytes:
        """
        批量导出
        
        参数:
        - obj_list: list[dict] - 数据列表
        
        返回:
        - bytes - 导出的Excel文件内容
        """
        mapping_dict = {
            'id': '',
            'uuid': '',
            'name': '工具包名称',
            'type': '类型(toolkit:整个类 function:单个函数)',
            'module_path': 'Python模块路径',
            'class_name': '类名（type=toolkit时使用）',
            'func_name': '函数名（type=function时使用）',
            'config': '初始化参数',
            'instructions': '工具使用说明',
            'requires_confirmation': '是否需要确认',
            'approval_type': '审批类型(NULL/required/audit)',
            'stop_after_call': '调用后是否停止',
            'show_result': '是否展示结果',
            'cache_results': '是否缓存结果',
            'cache_ttl': '缓存TTL秒数',
            'status': '',
            'description': '',
            'created_time': '',
            'updated_time': '',
            'created_id': '',
            'updated_id': '',
        }
        # 复制数据并转换状态
        data = obj_list.copy()
        for item in data:
            # 处理状态
            item["status"] = "启用" if item.get("status") == "0" else "停用"
            # 处理创建者
            creator_info = item.get("created_id")
            if isinstance(creator_info, dict):
                item["created_id"] = creator_info.get("name", "未知")
            else:
                item["created_id"] = "未知"

        return ExcelUtil.export_list2excel(list_data=data, mapping_dict=mapping_dict)

    @classmethod
    async def batch_import_toolkits_service(cls, auth: AuthSchema, file: UploadFile, update_support: bool = False) -> str:
        """
        批量导入
        
        参数:
        - auth: AuthSchema - 认证信息
        - file: UploadFile - 上传的Excel文件
        - update_support: bool - 是否支持更新存在数据
        
        返回:
        - str - 导入结果信息
        """
        header_dict = {
            '': 'id',
            '': 'uuid',
            '工具包名称': 'name',
            '类型(toolkit:整个类 function:单个函数)': 'type',
            'Python模块路径': 'module_path',
            '类名（type=toolkit时使用）': 'class_name',
            '函数名（type=function时使用）': 'func_name',
            '初始化参数': 'config',
            '工具使用说明': 'instructions',
            '是否需要确认': 'requires_confirmation',
            '审批类型(NULL/required/audit)': 'approval_type',
            '调用后是否停止': 'stop_after_call',
            '是否展示结果': 'show_result',
            '是否缓存结果': 'cache_results',
            '缓存TTL秒数': 'cache_ttl',
            '': 'status',
            '': 'description',
            '': 'created_time',
            '': 'updated_time',
            '': 'created_id',
            '': 'updated_id',
        }

        try:
            # 读取Excel文件
            contents = await file.read()
            df = pd.read_excel(io.BytesIO(contents))
            await file.close()

            if df.empty:
                raise CustomException(msg="导入文件为空")

            # 检查表头是否完整
            missing_headers = [header for header in header_dict.keys() if header not in df.columns]
            if missing_headers:
                raise CustomException(msg=f"导入文件缺少必要的列: {', '.join(missing_headers)}")

            # 重命名列名
            df.rename(columns=header_dict, inplace=True)

            # 验证必填字段

            error_msgs = []
            success_count = 0
            count = 0

            for _index, row in df.iterrows():
                count += 1
                try:
                    data = {
                        "id": row['id'],
                        "uuid": row['uuid'],
                        "name": row['name'],
                        "type": row['type'],
                        "module_path": row['module_path'],
                        "class_name": row['class_name'],
                        "func_name": row['func_name'],
                        "config": row['config'],
                        "instructions": row['instructions'],
                        "requires_confirmation": row['requires_confirmation'],
                        "approval_type": row['approval_type'],
                        "stop_after_call": row['stop_after_call'],
                        "show_result": row['show_result'],
                        "cache_results": row['cache_results'],
                        "cache_ttl": row['cache_ttl'],
                        "status": row['status'],
                        "description": row['description'],
                        "created_time": row['created_time'],
                        "updated_time": row['updated_time'],
                        "created_id": row['created_id'],
                        "updated_id": row['updated_id'],
                    }
                    # 使用CreateSchema做校验后入库
                    create_schema = AgToolkitCreateSchema.model_validate(data)

                    # 检查唯一性约束

                    await AgToolkitCRUD(auth).create_toolkits_crud(data=create_schema)
                    success_count += 1
                except Exception as e:
                    error_msgs.append(f"第{count}行: {str(e)}")
                    continue

            result = f"成功导入 {success_count} 条数据"
            if error_msgs:
                result += "\n错误信息:\n" + "\n".join(error_msgs)
            return result

        except Exception as e:
            log.error(f"批量导入失败: {str(e)}")
            raise CustomException(msg=f"导入失败: {str(e)}")

    @classmethod
    async def import_template_download_toolkits_service(cls) -> bytes:
        """
        下载导入模板
        
        返回:
        - bytes - Excel文件的二进制数据
        """
        header_list = [
            '',
            '',
            '工具包名称',
            '类型(toolkit:整个类 function:单个函数)',
            'Python模块路径',
            '类名（type=toolkit时使用）',
            '函数名（type=function时使用）',
            '初始化参数',
            '工具使用说明',
            '是否需要确认',
            '审批类型(NULL/required/audit)',
            '调用后是否停止',
            '是否展示结果',
            '是否缓存结果',
            '缓存TTL秒数',
            '',
            '',
            '',
            '',
            '',
            '',
        ]
        selector_header_list = []
        option_list = []

        return ExcelUtil.get_excel_template(
            header_list=header_list,
            selector_header_list=selector_header_list,
            option_list=option_list
        )

    @classmethod
    def list_agno_catalog_service(cls, category: str | None = None, keyword: str | None = None) -> list[AgnoToolInfo]:
        """
        返回 Agno 内置工具目录，供前端选择 module_path + class_name。

        参数:
        - category: str | None - 按分类过滤（如 "搜索"、"数据库"）
        - keyword: str | None - 关键词模糊搜索

        返回:
        - list[AgnoToolInfo] - 工具信息列表
        """
        return list_agno_tools(category=category, keyword=keyword)

    @classmethod
    def list_agno_categories_service(cls) -> list[str]:
        """返回所有工具分类。"""
        return get_categories()

    @classmethod
    async def global_switch_toolkits_service(cls, auth: AuthSchema, id: int, data: AgToolkitGlobalSwitchSchema) -> dict:
        """
        超管全局开关：切换 global_enabled。
        global_enabled=False 时从 registry 移除；True 时重新注册。
        """
        from sqlalchemy import update as sa_update
        from app.core.database import async_db_session
        from .model import AgToolkitModel

        obj = await AgToolkitCRUD(auth).get_by_id_toolkits_crud(id=id)
        if not obj:
            raise CustomException(msg="该数据不存在")

        async with async_db_session() as db:
            await db.execute(
                sa_update(AgToolkitModel)
                .where(AgToolkitModel.id == id)
                .values(global_enabled=data.global_enabled)
            )
            await db.commit()

        obj.global_enabled = data.global_enabled
        try:
            if data.global_enabled and obj.status == "0":
                get_registry().register_toolkit(str(obj.id), obj)
            else:
                get_registry().unregister_toolkit(str(obj.id))
        except Exception as e:
            log.warning(f"[Toolkits] global_switch registry failed for id={id}: {e}")

        return AgToolkitOutSchema.model_validate(obj).model_dump()

    @classmethod
    async def pull_toolkit_service(cls, auth: AuthSchema, toolkit_id: int, config_override: dict | None) -> dict:
        """
        用户拉取工具：在 ag_bindings 插入 owner_type='user' 记录。
        """
        obj = await AgToolkitCRUD(auth).get_by_id_toolkits_crud(id=toolkit_id)
        if not obj:
            raise CustomException(msg="工具不存在")
        if not obj.global_enabled:
            raise CustomException(msg="该工具已被管理员禁用")
        if obj.status != "0":
            raise CustomException(msg="该工具未启用")

        # 检查是否已拉取
        from sqlalchemy import and_, select
        from app.core.database import async_db_session
        from app.plugin.module_agno_manage.bindings.model import AgBindingModel
        async with async_db_session() as db:
            result = await db.execute(
                select(AgBindingModel).where(
                    and_(
                        AgBindingModel.owner_type == "user",
                        AgBindingModel.owner_id == auth.user.id,
                        AgBindingModel.resource_type == "toolkit",
                        AgBindingModel.resource_id == toolkit_id,
                        AgBindingModel.status == "0",
                    )
                )
            )
            if result.scalar_one_or_none():
                raise CustomException(msg="已拉取过该工具")

        binding_data = AgBindingCreateSchema(
            owner_type="user",
            owner_id=auth.user.id,
            resource_type="toolkit",
            resource_id=toolkit_id,
            config_override=config_override,
            status="0",
        )
        binding = await AgBindingCRUD(auth).create_bindings_crud(data=binding_data)
        return {"binding_id": binding.id, "toolkit_id": toolkit_id}

    @classmethod
    async def unpull_toolkit_service(cls, auth: AuthSchema, toolkit_id: int) -> None:
        """
        用户取消拉取工具：删除对应 binding。
        """
        from sqlalchemy import and_, select
        from app.core.database import async_db_session
        from app.plugin.module_agno_manage.bindings.model import AgBindingModel
        async with async_db_session() as db:
            result = await db.execute(
                select(AgBindingModel).where(
                    and_(
                        AgBindingModel.owner_type == "user",
                        AgBindingModel.owner_id == auth.user.id,
                        AgBindingModel.resource_type == "toolkit",
                        AgBindingModel.resource_id == toolkit_id,
                        AgBindingModel.status == "0",
                    )
                )
            )
            binding = result.scalar_one_or_none()
            if not binding:
                raise CustomException(msg="未拉取过该工具")
            await AgBindingCRUD(auth).delete_bindings_crud(ids=[binding.id])

    @classmethod
    async def list_pulled_toolkits_service(cls, auth: AuthSchema) -> list[dict]:
        """
        查询当前用户已拉取的工具列表。
        """
        from sqlalchemy import and_, select
        from app.core.database import async_db_session
        from app.plugin.module_agno_manage.bindings.model import AgBindingModel
        from .model import AgToolkitModel

        async with async_db_session() as db:
            result = await db.execute(
                select(AgBindingModel, AgToolkitModel).join(
                    AgToolkitModel, AgToolkitModel.id == AgBindingModel.resource_id
                ).where(
                    and_(
                        AgBindingModel.owner_type == "user",
                        AgBindingModel.owner_id == auth.user.id,
                        AgBindingModel.resource_type == "toolkit",
                        AgBindingModel.status == "0",
                        AgToolkitModel.global_enabled == True,  # noqa: E712
                    )
                )
            )
            rows = result.all()

        return [
            {
                **AgToolkitOutSchema.model_validate(toolkit).model_dump(),
                "binding_id": binding.id,
                "config_override": binding.config_override,
            }
            for binding, toolkit in rows
        ]

    @classmethod
    def validate_code_toolkit_service(cls, data: AgToolkitCodeValidateSchema) -> AgToolkitCodeValidateResultSchema:
        """
        验证 source_code 是否可以正常 exec，并返回发现的函数列表。
        不实际注册到 registry，仅做语法和运行时检查。
        """
        from agno.tools import Function

        namespace: dict = {}
        try:
            exec(compile(data.source_code, "<validate>", "exec"), namespace)
        except Exception as e:
            return AgToolkitCodeValidateResultSchema(success=False, error=str(e))

        functions = []
        for name, obj in namespace.items():
            if name.startswith("_"):
                continue
            if isinstance(obj, Function):
                functions.append(name)
            elif callable(obj) and not isinstance(obj, type) and getattr(obj, "__module__", None) is None:
                functions.append(name)

        if not functions:
            return AgToolkitCodeValidateResultSchema(
                success=False,
                error="未找到任何可用函数，请定义至少一个函数或使用 @tool 装饰器"
            )

        return AgToolkitCodeValidateResultSchema(success=True, functions=functions)
