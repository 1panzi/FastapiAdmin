
import io

import pandas as pd
from fastapi import UploadFile

from app.api.v1.module_system.auth.schema import AuthSchema
from app.core.base_schema import BatchSetAvailable
from app.core.exceptions import CustomException
from app.core.logger import log
from app.plugin.module_agno_manage.core.registry import get_registry
from app.utils.excel_util import ExcelUtil

from app.plugin.module_agno_manage.readers.crud import AgReaderCRUD

from .crud import AgBindingCRUD
from .schema import (
    AgBindingCreateSchema,
    AgBindingOutSchema,
    AgBindingQueryParam,
    AgBindingUpdateSchema,
)


class AgBindingService:
    """
    资源绑定关系服务层
    """

    @classmethod
    async def _check_knowledge_reader_type_unique(
        cls,
        auth: AuthSchema,
        owner_id: int,
        reader_id: int,
        exclude_binding_id: int | None = None,
    ) -> None:
        """
        校验：同一知识库下每种 reader_type 只允许绑定一个。

        参数:
        - auth: 认证信息
        - owner_id: 知识库 ID
        - reader_id: 新绑定的 reader ID
        - exclude_binding_id: 更新时排除自身 binding ID
        """
        new_reader = await AgReaderCRUD(auth).get_by_id_readers_crud(id=reader_id)
        if not new_reader:
            raise CustomException(msg=f"Reader ID={reader_id} 不存在")

        existing_bindings = await AgBindingCRUD(auth).list_bindings_crud(search={
            "owner_type": ("eq", "knowledge"),
            "owner_id": ("eq", owner_id),
            "resource_type": ("eq", "reader"),
        })
        for b in existing_bindings:
            if exclude_binding_id and b.id == exclude_binding_id:
                continue
            existing_reader = await AgReaderCRUD(auth).get_by_id_readers_crud(id=b.resource_id)
            if existing_reader and existing_reader.reader_type == new_reader.reader_type:
                raise CustomException(
                    msg=f"该知识库已绑定同类型 Reader（{new_reader.reader_type}），每种类型只允许绑定一个"
                )

    @classmethod
    async def detail_bindings_service(cls, auth: AuthSchema, id: int) -> dict:
        """
        详情
        
        参数:
        - auth: AuthSchema - 认证信息
        - id: int - 数据ID
        
        返回:
        - dict - 数据详情
        """
        obj = await AgBindingCRUD(auth).get_by_id_bindings_crud(id=id)
        if not obj:
            raise CustomException(msg="该数据不存在")
        return AgBindingOutSchema.model_validate(obj).model_dump()

    @classmethod
    async def list_bindings_service(cls, auth: AuthSchema, search: AgBindingQueryParam | None = None, order_by: list[dict] | None = None) -> list[dict]:
        """
        列表查询
        
        参数:
        - auth: AuthSchema - 认证信息
        - search: AgBindingQueryParam | None - 查询参数
        - order_by: list[dict] | None - 排序参数
        
        返回:
        - list[dict] - 数据列表
        """
        search_dict = search.__dict__ if search else None
        obj_list = await AgBindingCRUD(auth).list_bindings_crud(search=search_dict, order_by=order_by)
        return [AgBindingOutSchema.model_validate(obj).model_dump() for obj in obj_list]

    @classmethod
    async def page_bindings_service(cls, auth: AuthSchema, page_no: int, page_size: int, search: AgBindingQueryParam | None = None, order_by: list[dict] | None = None) -> dict:
        """
        分页查询（数据库分页）
        
        参数:
        - auth: AuthSchema - 认证信息
        - page_no: int - 页码
        - page_size: int - 每页数量
        - search: AgBindingQueryParam | None - 查询参数
        - order_by: list[dict] | None - 排序参数
        
        返回:
        - dict - 分页查询结果
        """
        search_dict = search.__dict__ if search else {}
        order_by_list = order_by or [{'id': 'asc'}]
        offset = (page_no - 1) * page_size
        result = await AgBindingCRUD(auth).page_bindings_crud(
            offset=offset,
            limit=page_size,
            order_by=order_by_list,
            search=search_dict
        )
        return result

    @classmethod
    async def create_bindings_service(cls, auth: AuthSchema, data: AgBindingCreateSchema) -> dict:
        """
        创建
        
        参数:
        - auth: AuthSchema - 认证信息
        - data: AgBindingCreateSchema - 创建数据
        
        返回:
        - dict - 创建结果
        """
        if data.owner_type == "knowledge" and data.resource_type == "reader":
            await cls._check_knowledge_reader_type_unique(auth, data.owner_id, data.resource_id)
        obj = await AgBindingCRUD(auth).create_bindings_crud(data=data)
        if obj and obj.status == "0":
            get_registry().update_binding_row(str(obj.id), obj)
        return AgBindingOutSchema.model_validate(obj).model_dump()

    @classmethod
    async def update_bindings_service(cls, auth: AuthSchema, id: int, data: AgBindingUpdateSchema) -> dict:
        """
        更新
        
        参数:
        - auth: AuthSchema - 认证信息
        - id: int - 数据ID
        - data: AgBindingUpdateSchema - 更新数据
        
        返回:
        - dict - 更新结果
        """
        # 检查数据是否存在
        obj = await AgBindingCRUD(auth).get_by_id_bindings_crud(id=id)
        if not obj:
            raise CustomException(msg='更新失败，该数据不存在')

        # 检查唯一性约束
        if data.owner_type == "knowledge" and data.resource_type == "reader":
            await cls._check_knowledge_reader_type_unique(auth, data.owner_id, data.resource_id, exclude_binding_id=id)

        obj = await AgBindingCRUD(auth).update_bindings_crud(id=id, data=data)
        if obj:
            if obj.status == "0":
                get_registry().update_binding_row(str(obj.id), obj)
            else:
                get_registry().remove_binding_row(str(obj.id))
        return AgBindingOutSchema.model_validate(obj).model_dump()

    @classmethod
    async def delete_bindings_service(cls, auth: AuthSchema, ids: list[int]) -> None:
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
            obj = await AgBindingCRUD(auth).get_by_id_bindings_crud(id=id)
            if not obj:
                raise CustomException(msg=f'删除失败，ID为{id}的数据不存在')
            ids_to_remove.append(str(obj.id))
        await AgBindingCRUD(auth).delete_bindings_crud(ids=ids)
        for rid in ids_to_remove:
            get_registry().remove_binding_row(rid)

    @classmethod
    async def set_available_bindings_service(cls, auth: AuthSchema, data: BatchSetAvailable) -> None:
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
            obj = await AgBindingCRUD(auth).get_by_id_bindings_crud(id=id)
            if obj:
                obj_list.append(obj)
        await AgBindingCRUD(auth).set_available_bindings_crud(ids=data.ids, status=data.status)
        for obj in obj_list:
            if data.status == "0":
                get_registry().update_binding_row(str(obj.id), obj)
            else:
                get_registry().remove_binding_row(str(obj.id))

    @classmethod
    async def batch_export_bindings_service(cls, obj_list: list[dict]) -> bytes:
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
            'owner_type': '拥有者类型(agent/team)',
            'owner_id': '拥有者ID',
            'resource_type': '资源类型(toolkit/skill/mcp/knowledge/hook/guardrail)',
            'resource_id': '资源ID',
            'priority': '优先级（数字小优先）',
            'config_override': '覆盖资源默认配置（如特定Agent使用不同API Key）',
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
    async def batch_import_bindings_service(cls, auth: AuthSchema, file: UploadFile, update_support: bool = False) -> str:
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
            '拥有者类型(agent/team)': 'owner_type',
            '拥有者ID': 'owner_id',
            '资源类型(toolkit/skill/mcp/knowledge/hook/guardrail)': 'resource_type',
            '资源ID': 'resource_id',
            '优先级（数字小优先）': 'priority',
            '覆盖资源默认配置（如特定Agent使用不同API Key）': 'config_override',
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
                        "owner_type": row['owner_type'],
                        "owner_id": row['owner_id'],
                        "resource_type": row['resource_type'],
                        "resource_id": row['resource_id'],
                        "priority": row['priority'],
                        "config_override": row['config_override'],
                        "status": row['status'],
                        "description": row['description'],
                        "created_time": row['created_time'],
                        "updated_time": row['updated_time'],
                        "created_id": row['created_id'],
                        "updated_id": row['updated_id'],
                    }
                    # 使用CreateSchema做校验后入库
                    create_schema = AgBindingCreateSchema.model_validate(data)

                    # 检查唯一性约束

                    await AgBindingCRUD(auth).create_bindings_crud(data=create_schema)
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
    async def import_template_download_bindings_service(cls) -> bytes:
        """
        下载导入模板
        
        返回:
        - bytes - Excel文件的二进制数据
        """
        header_list = [
            '',
            '',
            '拥有者类型(agent/team)',
            '拥有者ID',
            '资源类型(toolkit/skill/mcp/knowledge/hook/guardrail)',
            '资源ID',
            '优先级（数字小优先）',
            '覆盖资源默认配置（如特定Agent使用不同API Key）',
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
