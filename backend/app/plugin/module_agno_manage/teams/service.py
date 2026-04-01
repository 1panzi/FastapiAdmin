# -*- coding: utf-8 -*-

import io
import pandas as pd
from fastapi import UploadFile

from app.api.v1.module_system.auth.schema import AuthSchema
from app.core.base_schema import BatchSetAvailable
from app.core.exceptions import CustomException
from app.core.logger import log
from app.utils.excel_util import ExcelUtil

from .crud import AgTeamCRUD
from .schema import (
    AgTeamCreateSchema,
    AgTeamUpdateSchema,
    AgTeamOutSchema,
    AgTeamQueryParam
)


class AgTeamService:
    """
    Team管理服务层
    """
    
    @classmethod
    async def detail_teams_service(cls, auth: AuthSchema, id: int) -> dict:
        """
        详情
        
        参数:
        - auth: AuthSchema - 认证信息
        - id: int - 数据ID
        
        返回:
        - dict - 数据详情
        """
        obj = await AgTeamCRUD(auth).get_by_id_teams_crud(id=id)
        if not obj:
            raise CustomException(msg="该数据不存在")
        return AgTeamOutSchema.model_validate(obj).model_dump()
    
    @classmethod
    async def list_teams_service(cls, auth: AuthSchema, search: AgTeamQueryParam | None = None, order_by: list[dict] | None = None) -> list[dict]:
        """
        列表查询
        
        参数:
        - auth: AuthSchema - 认证信息
        - search: AgTeamQueryParam | None - 查询参数
        - order_by: list[dict] | None - 排序参数
        
        返回:
        - list[dict] - 数据列表
        """
        search_dict = search.__dict__ if search else None
        obj_list = await AgTeamCRUD(auth).list_teams_crud(search=search_dict, order_by=order_by)
        return [AgTeamOutSchema.model_validate(obj).model_dump() for obj in obj_list]

    @classmethod
    async def page_teams_service(cls, auth: AuthSchema, page_no: int, page_size: int, search: AgTeamQueryParam | None = None, order_by: list[dict] | None = None) -> dict:
        """
        分页查询（数据库分页）
        
        参数:
        - auth: AuthSchema - 认证信息
        - page_no: int - 页码
        - page_size: int - 每页数量
        - search: AgTeamQueryParam | None - 查询参数
        - order_by: list[dict] | None - 排序参数
        
        返回:
        - dict - 分页查询结果
        """
        search_dict = search.__dict__ if search else {}
        order_by_list = order_by or [{'id': 'asc'}]
        offset = (page_no - 1) * page_size
        result = await AgTeamCRUD(auth).page_teams_crud(
            offset=offset,
            limit=page_size,
            order_by=order_by_list,
            search=search_dict
        )
        return result
    
    @classmethod
    async def create_teams_service(cls, auth: AuthSchema, data: AgTeamCreateSchema) -> dict:
        """
        创建
        
        参数:
        - auth: AuthSchema - 认证信息
        - data: AgTeamCreateSchema - 创建数据
        
        返回:
        - dict - 创建结果
        """
        obj = await AgTeamCRUD(auth).create_teams_crud(data=data)
        return AgTeamOutSchema.model_validate(obj).model_dump()
    
    @classmethod
    async def update_teams_service(cls, auth: AuthSchema, id: int, data: AgTeamUpdateSchema) -> dict:
        """
        更新
        
        参数:
        - auth: AuthSchema - 认证信息
        - id: int - 数据ID
        - data: AgTeamUpdateSchema - 更新数据
        
        返回:
        - dict - 更新结果
        """
        # 检查数据是否存在
        obj = await AgTeamCRUD(auth).get_by_id_teams_crud(id=id)
        if not obj:
            raise CustomException(msg='更新失败，该数据不存在')
        
        # 检查唯一性约束
            
        obj = await AgTeamCRUD(auth).update_teams_crud(id=id, data=data)
        return AgTeamOutSchema.model_validate(obj).model_dump()
    
    @classmethod
    async def delete_teams_service(cls, auth: AuthSchema, ids: list[int]) -> None:
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
            obj = await AgTeamCRUD(auth).get_by_id_teams_crud(id=id)
            if not obj:
                raise CustomException(msg=f'删除失败，ID为{id}的数据不存在')
        await AgTeamCRUD(auth).delete_teams_crud(ids=ids)
    
    @classmethod
    async def set_available_teams_service(cls, auth: AuthSchema, data: BatchSetAvailable) -> None:
        """
        批量设置状态
        
        参数:
        - auth: AuthSchema - 认证信息
        - data: BatchSetAvailable - 批量设置状态数据
        
        返回:
        - None
        """
        await AgTeamCRUD(auth).set_available_teams_crud(ids=data.ids, status=data.status)
    
    @classmethod
    async def batch_export_teams_service(cls, obj_list: list[dict]) -> bytes:
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
            'name': 'Team名称',
            'model_id': '主模型ID',
            'memory_manager_id': '记忆管理器ID',
            'mode': '协作模式(route/coordinate/collaborate/tasks)',
            'respond_directly': '是否直接响应（不经过协调）',
            'delegate_to_all_members': '是否分发给所有成员',
            'determine_input_for_members': '是否为成员决定输入内容',
            'max_iterations': '最大迭代次数',
            'instructions': 'Team指令',
            'expected_output': '期望输出格式说明',
            'markdown': '是否输出Markdown格式',
            'add_team_history_to_members': '是否将Team历史传给成员',
            'num_team_history_runs': '传给成员的历史运行次数',
            'share_member_interactions': '是否共享成员交互记录',
            'add_member_tools_to_context': '是否将成员工具加入上下文',
            'read_chat_history': '是否读取聊天历史',
            'search_past_sessions': '是否搜索历史会话',
            'num_past_sessions_to_search': '搜索历史会话数量',
            'search_knowledge': '是否搜索知识库',
            'update_knowledge': '是否允许更新知识库',
            'enable_agentic_knowledge_filters': '是否开启智能知识过滤',
            'enable_agentic_state': '是否开启智能状态',
            'enable_agentic_memory': '是否开启智能记忆',
            'update_memory_on_run': '是否每次运行后更新记忆',
            'enable_session_summaries': '是否开启会话摘要',
            'add_session_summary_to_context': '是否将会话摘要加入上下文',
            'tool_call_limit': '工具调用次数上限',
            'stream': '是否开启流式输出',
            'stream_events': '是否流式推送事件',
            'debug_mode': '是否开启调试模式',
            'metadata_config': '元数据',
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
    async def batch_import_teams_service(cls, auth: AuthSchema, file: UploadFile, update_support: bool = False) -> str:
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
            'Team名称': 'name',
            '主模型ID': 'model_id',
            '记忆管理器ID': 'memory_manager_id',
            '协作模式(route/coordinate/collaborate/tasks)': 'mode',
            '是否直接响应（不经过协调）': 'respond_directly',
            '是否分发给所有成员': 'delegate_to_all_members',
            '是否为成员决定输入内容': 'determine_input_for_members',
            '最大迭代次数': 'max_iterations',
            'Team指令': 'instructions',
            '期望输出格式说明': 'expected_output',
            '是否输出Markdown格式': 'markdown',
            '是否将Team历史传给成员': 'add_team_history_to_members',
            '传给成员的历史运行次数': 'num_team_history_runs',
            '是否共享成员交互记录': 'share_member_interactions',
            '是否将成员工具加入上下文': 'add_member_tools_to_context',
            '是否读取聊天历史': 'read_chat_history',
            '是否搜索历史会话': 'search_past_sessions',
            '搜索历史会话数量': 'num_past_sessions_to_search',
            '是否搜索知识库': 'search_knowledge',
            '是否允许更新知识库': 'update_knowledge',
            '是否开启智能知识过滤': 'enable_agentic_knowledge_filters',
            '是否开启智能状态': 'enable_agentic_state',
            '是否开启智能记忆': 'enable_agentic_memory',
            '是否每次运行后更新记忆': 'update_memory_on_run',
            '是否开启会话摘要': 'enable_session_summaries',
            '是否将会话摘要加入上下文': 'add_session_summary_to_context',
            '工具调用次数上限': 'tool_call_limit',
            '是否开启流式输出': 'stream',
            '是否流式推送事件': 'stream_events',
            '是否开启调试模式': 'debug_mode',
            '元数据': 'metadata_config',
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
                        "model_id": row['model_id'],
                        "memory_manager_id": row['memory_manager_id'],
                        "mode": row['mode'],
                        "respond_directly": row['respond_directly'],
                        "delegate_to_all_members": row['delegate_to_all_members'],
                        "determine_input_for_members": row['determine_input_for_members'],
                        "max_iterations": row['max_iterations'],
                        "instructions": row['instructions'],
                        "expected_output": row['expected_output'],
                        "markdown": row['markdown'],
                        "add_team_history_to_members": row['add_team_history_to_members'],
                        "num_team_history_runs": row['num_team_history_runs'],
                        "share_member_interactions": row['share_member_interactions'],
                        "add_member_tools_to_context": row['add_member_tools_to_context'],
                        "read_chat_history": row['read_chat_history'],
                        "search_past_sessions": row['search_past_sessions'],
                        "num_past_sessions_to_search": row['num_past_sessions_to_search'],
                        "search_knowledge": row['search_knowledge'],
                        "update_knowledge": row['update_knowledge'],
                        "enable_agentic_knowledge_filters": row['enable_agentic_knowledge_filters'],
                        "enable_agentic_state": row['enable_agentic_state'],
                        "enable_agentic_memory": row['enable_agentic_memory'],
                        "update_memory_on_run": row['update_memory_on_run'],
                        "enable_session_summaries": row['enable_session_summaries'],
                        "add_session_summary_to_context": row['add_session_summary_to_context'],
                        "tool_call_limit": row['tool_call_limit'],
                        "stream": row['stream'],
                        "stream_events": row['stream_events'],
                        "debug_mode": row['debug_mode'],
                        "metadata_config": row['metadata_config'],
                        "status": row['status'],
                        "description": row['description'],
                        "created_time": row['created_time'],
                        "updated_time": row['updated_time'],
                        "created_id": row['created_id'],
                        "updated_id": row['updated_id'],
                    }
                    # 使用CreateSchema做校验后入库
                    create_schema = AgTeamCreateSchema.model_validate(data)
                    
                    # 检查唯一性约束
                    
                    await AgTeamCRUD(auth).create_teams_crud(data=create_schema)
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
    async def import_template_download_teams_service(cls) -> bytes:
        """
        下载导入模板
        
        返回:
        - bytes - Excel文件的二进制数据
        """
        header_list = [
            '',
            '',
            'Team名称',
            '主模型ID',
            '记忆管理器ID',
            '协作模式(route/coordinate/collaborate/tasks)',
            '是否直接响应（不经过协调）',
            '是否分发给所有成员',
            '是否为成员决定输入内容',
            '最大迭代次数',
            'Team指令',
            '期望输出格式说明',
            '是否输出Markdown格式',
            '是否将Team历史传给成员',
            '传给成员的历史运行次数',
            '是否共享成员交互记录',
            '是否将成员工具加入上下文',
            '是否读取聊天历史',
            '是否搜索历史会话',
            '搜索历史会话数量',
            '是否搜索知识库',
            '是否允许更新知识库',
            '是否开启智能知识过滤',
            '是否开启智能状态',
            '是否开启智能记忆',
            '是否每次运行后更新记忆',
            '是否开启会话摘要',
            '是否将会话摘要加入上下文',
            '工具调用次数上限',
            '是否开启流式输出',
            '是否流式推送事件',
            '是否开启调试模式',
            '元数据',
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