
import io

import pandas as pd
from fastapi import UploadFile

from app.api.v1.module_system.auth.schema import AuthSchema
from app.core.base_schema import BatchSetAvailable
from app.core.exceptions import CustomException
from app.core.logger import log
from app.utils.excel_util import ExcelUtil

from .crud import AgWorkflowNodeCRUD
from .schema import (
    AgWorkflowNodeCreateSchema,
    AgWorkflowNodeOutSchema,
    AgWorkflowNodeQueryParam,
    AgWorkflowNodeUpdateSchema,
)


class AgWorkflowNodeService:
    """
    工作流节点服务层
    """

    @classmethod
    async def detail_workflow_nodes_service(cls, auth: AuthSchema, id: int) -> dict:
        """
        详情
        
        参数:
        - auth: AuthSchema - 认证信息
        - id: int - 数据ID
        
        返回:
        - dict - 数据详情
        """
        obj = await AgWorkflowNodeCRUD(auth).get_by_id_workflow_nodes_crud(id=id)
        if not obj:
            raise CustomException(msg="该数据不存在")
        return AgWorkflowNodeOutSchema.model_validate(obj).model_dump()

    @classmethod
    async def list_workflow_nodes_service(cls, auth: AuthSchema, search: AgWorkflowNodeQueryParam | None = None, order_by: list[dict] | None = None) -> list[dict]:
        """
        列表查询
        
        参数:
        - auth: AuthSchema - 认证信息
        - search: AgWorkflowNodeQueryParam | None - 查询参数
        - order_by: list[dict] | None - 排序参数
        
        返回:
        - list[dict] - 数据列表
        """
        search_dict = search.__dict__ if search else None
        obj_list = await AgWorkflowNodeCRUD(auth).list_workflow_nodes_crud(search=search_dict, order_by=order_by)
        return [AgWorkflowNodeOutSchema.model_validate(obj).model_dump() for obj in obj_list]

    @classmethod
    async def page_workflow_nodes_service(cls, auth: AuthSchema, page_no: int, page_size: int, search: AgWorkflowNodeQueryParam | None = None, order_by: list[dict] | None = None) -> dict:
        """
        分页查询（数据库分页）
        
        参数:
        - auth: AuthSchema - 认证信息
        - page_no: int - 页码
        - page_size: int - 每页数量
        - search: AgWorkflowNodeQueryParam | None - 查询参数
        - order_by: list[dict] | None - 排序参数
        
        返回:
        - dict - 分页查询结果
        """
        search_dict = search.__dict__ if search else {}
        order_by_list = order_by or [{'id': 'asc'}]
        offset = (page_no - 1) * page_size
        result = await AgWorkflowNodeCRUD(auth).page_workflow_nodes_crud(
            offset=offset,
            limit=page_size,
            order_by=order_by_list,
            search=search_dict
        )
        return result

    @classmethod
    async def create_workflow_nodes_service(cls, auth: AuthSchema, data: AgWorkflowNodeCreateSchema) -> dict:
        """
        创建
        
        参数:
        - auth: AuthSchema - 认证信息
        - data: AgWorkflowNodeCreateSchema - 创建数据
        
        返回:
        - dict - 创建结果
        """
        obj = await AgWorkflowNodeCRUD(auth).create_workflow_nodes_crud(data=data)
        return AgWorkflowNodeOutSchema.model_validate(obj).model_dump()

    @classmethod
    async def update_workflow_nodes_service(cls, auth: AuthSchema, id: int, data: AgWorkflowNodeUpdateSchema) -> dict:
        """
        更新
        
        参数:
        - auth: AuthSchema - 认证信息
        - id: int - 数据ID
        - data: AgWorkflowNodeUpdateSchema - 更新数据
        
        返回:
        - dict - 更新结果
        """
        # 检查数据是否存在
        obj = await AgWorkflowNodeCRUD(auth).get_by_id_workflow_nodes_crud(id=id)
        if not obj:
            raise CustomException(msg='更新失败，该数据不存在')

        # 检查唯一性约束

        obj = await AgWorkflowNodeCRUD(auth).update_workflow_nodes_crud(id=id, data=data)
        return AgWorkflowNodeOutSchema.model_validate(obj).model_dump()

    @classmethod
    async def delete_workflow_nodes_service(cls, auth: AuthSchema, ids: list[int]) -> None:
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
        for id in ids:
            obj = await AgWorkflowNodeCRUD(auth).get_by_id_workflow_nodes_crud(id=id)
            if not obj:
                raise CustomException(msg=f'删除失败，ID为{id}的数据不存在')
        await AgWorkflowNodeCRUD(auth).delete_workflow_nodes_crud(ids=ids)

    @classmethod
    async def set_available_workflow_nodes_service(cls, auth: AuthSchema, data: BatchSetAvailable) -> None:
        """
        批量设置状态
        
        参数:
        - auth: AuthSchema - 认证信息
        - data: BatchSetAvailable - 批量设置状态数据
        
        返回:
        - None
        """
        await AgWorkflowNodeCRUD(auth).set_available_workflow_nodes_crud(ids=data.ids, status=data.status)

    @classmethod
    async def batch_export_workflow_nodes_service(cls, obj_list: list[dict]) -> bytes:
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
            'workflow_id': '所属工作流ID',
            'parent_node_id': '父节点ID（NULL为顶层节点）',
            'node_order': '节点顺序',
            'node_type': '节点类型(step/condition/loop/parallel/router)',
            'name': '节点名称',
            'executor_type': '执行器类型(agent/team/custom)',
            'agent_id': '联AgentID（executor_type=agent时）',
            'team_id': '关联TeamID（executor_type=team时）',
            'executor_module': '自定义执行器模块路径（executor_type=custom时）',
            'add_workflow_history': '是否传入工作流历史',
            'num_history_runs': '传入历史运行次数',
            'strict_input_validation': '是否严格校验输入',
            'max_retries': '最大重试次数',
            'skip_on_failure': '失败时是否跳过',
            'evaluator_type': '条件评估器类型(bool/cel/function)',
            'evaluator_value': '条件评估器值',
            'branch': '分支标记(if/else)',
            'max_iterations': '循环最大迭代次数',
            'end_condition_type': '循环终止条件类型',
            'end_condition_value': '循环终止条件值',
            'forward_iteration_output': '是否传递迭代输出',
            'selector_type': '路由选择器类型',
            'selector_value': '路由选择器值',
            'allow_multiple_selections': '是否允许多路由选择',
            'requires_confirmation': '是否需要用户确认（HITL）',
            'confirmation_message': '确认提示消息',
            'requires_user_input': '是否需要用户输入（HITL）',
            'user_input_message': '用户输入提示消息',
            'user_input_schema': '用户输入结构体Schema',
            'on_reject': '用户拒绝时处理策略(skip/abort)',
            'on_error': '节点出错时处理策略(skip/abort)',
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
    async def batch_import_workflow_nodes_service(cls, auth: AuthSchema, file: UploadFile, update_support: bool = False) -> str:
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
            '所属工作流ID': 'workflow_id',
            '父节点ID（NULL为顶层节点）': 'parent_node_id',
            '节点顺序': 'node_order',
            '节点类型(step/condition/loop/parallel/router)': 'node_type',
            '节点名称': 'name',
            '执行器类型(agent/team/custom)': 'executor_type',
            '联AgentID（executor_type=agent时）': 'agent_id',
            '关联TeamID（executor_type=team时）': 'team_id',
            '自定义执行器模块路径（executor_type=custom时）': 'executor_module',
            '是否传入工作流历史': 'add_workflow_history',
            '传入历史运行次数': 'num_history_runs',
            '是否严格校验输入': 'strict_input_validation',
            '最大重试次数': 'max_retries',
            '失败时是否跳过': 'skip_on_failure',
            '条件评估器类型(bool/cel/function)': 'evaluator_type',
            '条件评估器值': 'evaluator_value',
            '分支标记(if/else)': 'branch',
            '循环最大迭代次数': 'max_iterations',
            '循环终止条件类型': 'end_condition_type',
            '循环终止条件值': 'end_condition_value',
            '是否传递迭代输出': 'forward_iteration_output',
            '路由选择器类型': 'selector_type',
            '路由选择器值': 'selector_value',
            '是否允许多路由选择': 'allow_multiple_selections',
            '是否需要用户确认（HITL）': 'requires_confirmation',
            '确认提示消息': 'confirmation_message',
            '是否需要用户输入（HITL）': 'requires_user_input',
            '用户输入提示消息': 'user_input_message',
            '用户输入结构体Schema': 'user_input_schema',
            '用户拒绝时处理策略(skip/abort)': 'on_reject',
            '节点出错时处理策略(skip/abort)': 'on_error',
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
                        "workflow_id": row['workflow_id'],
                        "parent_node_id": row['parent_node_id'],
                        "node_order": row['node_order'],
                        "node_type": row['node_type'],
                        "name": row['name'],
                        "executor_type": row['executor_type'],
                        "agent_id": row['agent_id'],
                        "team_id": row['team_id'],
                        "executor_module": row['executor_module'],
                        "add_workflow_history": row['add_workflow_history'],
                        "num_history_runs": row['num_history_runs'],
                        "strict_input_validation": row['strict_input_validation'],
                        "max_retries": row['max_retries'],
                        "skip_on_failure": row['skip_on_failure'],
                        "evaluator_type": row['evaluator_type'],
                        "evaluator_value": row['evaluator_value'],
                        "branch": row['branch'],
                        "max_iterations": row['max_iterations'],
                        "end_condition_type": row['end_condition_type'],
                        "end_condition_value": row['end_condition_value'],
                        "forward_iteration_output": row['forward_iteration_output'],
                        "selector_type": row['selector_type'],
                        "selector_value": row['selector_value'],
                        "allow_multiple_selections": row['allow_multiple_selections'],
                        "requires_confirmation": row['requires_confirmation'],
                        "confirmation_message": row['confirmation_message'],
                        "requires_user_input": row['requires_user_input'],
                        "user_input_message": row['user_input_message'],
                        "user_input_schema": row['user_input_schema'],
                        "on_reject": row['on_reject'],
                        "on_error": row['on_error'],
                        "status": row['status'],
                        "description": row['description'],
                        "created_time": row['created_time'],
                        "updated_time": row['updated_time'],
                        "created_id": row['created_id'],
                        "updated_id": row['updated_id'],
                    }
                    # 使用CreateSchema做校验后入库
                    create_schema = AgWorkflowNodeCreateSchema.model_validate(data)

                    # 检查唯一性约束

                    await AgWorkflowNodeCRUD(auth).create_workflow_nodes_crud(data=create_schema)
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
    async def import_template_download_workflow_nodes_service(cls) -> bytes:
        """
        下载导入模板
        
        返回:
        - bytes - Excel文件的二进制数据
        """
        header_list = [
            '',
            '',
            '所属工作流ID',
            '父节点ID（NULL为顶层节点）',
            '节点顺序',
            '节点类型(step/condition/loop/parallel/router)',
            '节点名称',
            '执行器类型(agent/team/custom)',
            '联AgentID（executor_type=agent时）',
            '关联TeamID（executor_type=team时）',
            '自定义执行器模块路径（executor_type=custom时）',
            '是否传入工作流历史',
            '传入历史运行次数',
            '是否严格校验输入',
            '最大重试次数',
            '失败时是否跳过',
            '条件评估器类型(bool/cel/function)',
            '条件评估器值',
            '分支标记(if/else)',
            '循环最大迭代次数',
            '循环终止条件类型',
            '循环终止条件值',
            '是否传递迭代输出',
            '路由选择器类型',
            '路由选择器值',
            '是否允许多路由选择',
            '是否需要用户确认（HITL）',
            '确认提示消息',
            '是否需要用户输入（HITL）',
            '用户输入提示消息',
            '用户输入结构体Schema',
            '用户拒绝时处理策略(skip/abort)',
            '节点出错时处理策略(skip/abort)',
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
