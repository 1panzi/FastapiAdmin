# -*- coding: utf-8 -*-

import io
import pandas as pd
from fastapi import UploadFile

from app.api.v1.module_system.auth.schema import AuthSchema
from app.core.base_schema import BatchSetAvailable
from app.core.exceptions import CustomException
from app.core.logger import log
from app.utils.excel_util import ExcelUtil

from app.plugin.module_agno_manage.core.registry import get_registry
from .crud import AgGuardrailCRUD
from .schema import (
    AgGuardrailCreateSchema,
    AgGuardrailUpdateSchema,
    AgGuardrailOutSchema,
    AgGuardrailQueryParam
)


class AgGuardrailService:
    """
    护栏服务层
    """
    
    @classmethod
    async def detail_guardrails_service(cls, auth: AuthSchema, id: int) -> dict:
        """
        详情
        
        参数:
        - auth: AuthSchema - 认证信息
        - id: int - 数据ID
        
        返回:
        - dict - 数据详情
        """
        obj = await AgGuardrailCRUD(auth).get_by_id_guardrails_crud(id=id)
        if not obj:
            raise CustomException(msg="该数据不存在")
        return AgGuardrailOutSchema.model_validate(obj).model_dump()
    
    @classmethod
    async def list_guardrails_service(cls, auth: AuthSchema, search: AgGuardrailQueryParam | None = None, order_by: list[dict] | None = None) -> list[dict]:
        """
        列表查询
        
        参数:
        - auth: AuthSchema - 认证信息
        - search: AgGuardrailQueryParam | None - 查询参数
        - order_by: list[dict] | None - 排序参数
        
        返回:
        - list[dict] - 数据列表
        """
        search_dict = search.__dict__ if search else None
        obj_list = await AgGuardrailCRUD(auth).list_guardrails_crud(search=search_dict, order_by=order_by)
        return [AgGuardrailOutSchema.model_validate(obj).model_dump() for obj in obj_list]

    @classmethod
    async def page_guardrails_service(cls, auth: AuthSchema, page_no: int, page_size: int, search: AgGuardrailQueryParam | None = None, order_by: list[dict] | None = None) -> dict:
        """
        分页查询（数据库分页）
        
        参数:
        - auth: AuthSchema - 认证信息
        - page_no: int - 页码
        - page_size: int - 每页数量
        - search: AgGuardrailQueryParam | None - 查询参数
        - order_by: list[dict] | None - 排序参数
        
        返回:
        - dict - 分页查询结果
        """
        search_dict = search.__dict__ if search else {}
        order_by_list = order_by or [{'id': 'asc'}]
        offset = (page_no - 1) * page_size
        result = await AgGuardrailCRUD(auth).page_guardrails_crud(
            offset=offset,
            limit=page_size,
            order_by=order_by_list,
            search=search_dict
        )
        return result
    
    @classmethod
    async def create_guardrails_service(cls, auth: AuthSchema, data: AgGuardrailCreateSchema) -> dict:
        """
        创建
        
        参数:
        - auth: AuthSchema - 认证信息
        - data: AgGuardrailCreateSchema - 创建数据
        
        返回:
        - dict - 创建结果
        """
        obj = await AgGuardrailCRUD(auth).create_guardrails_crud(data=data)
        if obj and obj.status == "0":
            try:
                get_registry().register_guardrail(str(obj.id), obj)
            except Exception as e:
                log.warning(f"[Guardrails] registry register failed for id={obj.id}: {e}")
        return AgGuardrailOutSchema.model_validate(obj).model_dump()
    
    @classmethod
    async def update_guardrails_service(cls, auth: AuthSchema, id: int, data: AgGuardrailUpdateSchema) -> dict:
        """
        更新
        
        参数:
        - auth: AuthSchema - 认证信息
        - id: int - 数据ID
        - data: AgGuardrailUpdateSchema - 更新数据
        
        返回:
        - dict - 更新结果
        """
        # 检查数据是否存在
        obj = await AgGuardrailCRUD(auth).get_by_id_guardrails_crud(id=id)
        if not obj:
            raise CustomException(msg='更新失败，该数据不存在')
        
        # 检查唯一性约束
            
        obj = await AgGuardrailCRUD(auth).update_guardrails_crud(id=id, data=data)
        if obj:
            try:
                if obj.status == "0":
                    get_registry().register_guardrail(str(obj.id), obj)
                else:
                    get_registry().unregister_guardrail(str(obj.id))
            except Exception as e:
                log.warning(f"[Guardrails] registry update failed for id={obj.id}: {e}")
        return AgGuardrailOutSchema.model_validate(obj).model_dump()
    
    @classmethod
    async def delete_guardrails_service(cls, auth: AuthSchema, ids: list[int]) -> None:
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
            obj = await AgGuardrailCRUD(auth).get_by_id_guardrails_crud(id=id)
            if not obj:
                raise CustomException(msg=f'删除失败，ID为{id}的数据不存在')
            ids_to_remove.append(str(obj.id))
        await AgGuardrailCRUD(auth).delete_guardrails_crud(ids=ids)
        for rid in ids_to_remove:
            get_registry().unregister_guardrail(rid)
    
    @classmethod
    async def set_available_guardrails_service(cls, auth: AuthSchema, data: BatchSetAvailable) -> None:
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
            obj = await AgGuardrailCRUD(auth).get_by_id_guardrails_crud(id=id)
            if obj:
                obj_list.append(obj)
        await AgGuardrailCRUD(auth).set_available_guardrails_crud(ids=data.ids, status=data.status)
        for obj in obj_list:
            try:
                if data.status == "0":
                    get_registry().register_guardrail(str(obj.id), obj)
                else:
                    get_registry().unregister_guardrail(str(obj.id))
            except Exception as e:
                log.warning(f"[Guardrails] registry set_available failed for id={obj.id}: {e}")
    
    @classmethod
    async def batch_export_guardrails_service(cls, obj_list: list[dict]) -> bytes:
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
            'name': '护栏名称',
            'type': '护栏类型(openai_moderation/pii/prompt_injection/custom)',
            'hook_type': '作用阶段(pre/post)',
            'config': '护栏配置参数',
            'module_path': '自定义护栏模块路径（type=custom时使用）',
            'class_name': '自定义护栏类名（type=custom时使用）',
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
    async def batch_import_guardrails_service(cls, auth: AuthSchema, file: UploadFile, update_support: bool = False) -> str:
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
            '护栏名称': 'name',
            '护栏类型(openai_moderation/pii/prompt_injection/custom)': 'type',
            '作用阶段(pre/post)': 'hook_type',
            '护栏配置参数': 'config',
            '自定义护栏模块路径（type=custom时使用）': 'module_path',
            '自定义护栏类名（type=custom时使用）': 'class_name',
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
                        "hook_type": row['hook_type'],
                        "config": row['config'],
                        "module_path": row['module_path'],
                        "class_name": row['class_name'],
                        "status": row['status'],
                        "description": row['description'],
                        "created_time": row['created_time'],
                        "updated_time": row['updated_time'],
                        "created_id": row['created_id'],
                        "updated_id": row['updated_id'],
                    }
                    # 使用CreateSchema做校验后入库
                    create_schema = AgGuardrailCreateSchema.model_validate(data)
                    
                    # 检查唯一性约束
                    
                    await AgGuardrailCRUD(auth).create_guardrails_crud(data=create_schema)
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
    async def import_template_download_guardrails_service(cls) -> bytes:
        """
        下载导入模板
        
        返回:
        - bytes - Excel文件的二进制数据
        """
        header_list = [
            '',
            '',
            '护栏名称',
            '护栏类型(openai_moderation/pii/prompt_injection/custom)',
            '作用阶段(pre/post)',
            '护栏配置参数',
            '自定义护栏模块路径（type=custom时使用）',
            '自定义护栏类名（type=custom时使用）',
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