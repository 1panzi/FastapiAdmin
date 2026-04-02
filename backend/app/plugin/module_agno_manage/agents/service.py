
import io

import pandas as pd
from fastapi import UploadFile

from app.api.v1.module_system.auth.schema import AuthSchema
from app.core.base_schema import BatchSetAvailable
from app.core.exceptions import CustomException
from app.core.logger import log
from app.plugin.module_agno_manage.core.registry import get_registry
from app.utils.excel_util import ExcelUtil

from .crud import AgAgentCRUD
from .schema import AgAgentCreateSchema, AgAgentOutSchema, AgAgentQueryParam, AgAgentUpdateSchema


class AgAgentService:
    """
    Agent管理服务层
    """

    @classmethod
    async def detail_agents_service(cls, auth: AuthSchema, id: int) -> dict:
        """
        详情
        
        参数:
        - auth: AuthSchema - 认证信息
        - id: int - 数据ID
        
        返回:
        - dict - 数据详情
        """
        obj = await AgAgentCRUD(auth).get_by_id_agents_crud(id=id)
        if not obj:
            raise CustomException(msg="该数据不存在")
        return AgAgentOutSchema.model_validate(obj).model_dump()

    @classmethod
    async def list_agents_service(cls, auth: AuthSchema, search: AgAgentQueryParam | None = None, order_by: list[dict] | None = None) -> list[dict]:
        """
        列表查询
        
        参数:
        - auth: AuthSchema - 认证信息
        - search: AgAgentQueryParam | None - 查询参数
        - order_by: list[dict] | None - 排序参数
        
        返回:
        - list[dict] - 数据列表
        """
        search_dict = search.__dict__ if search else None
        obj_list = await AgAgentCRUD(auth).list_agents_crud(search=search_dict, order_by=order_by)
        return [AgAgentOutSchema.model_validate(obj).model_dump() for obj in obj_list]

    @classmethod
    async def page_agents_service(cls, auth: AuthSchema, page_no: int, page_size: int, search: AgAgentQueryParam | None = None, order_by: list[dict] | None = None) -> dict:
        """
        分页查询（数据库分页）
        
        参数:
        - auth: AuthSchema - 认证信息
        - page_no: int - 页码
        - page_size: int - 每页数量
        - search: AgAgentQueryParam | None - 查询参数
        - order_by: list[dict] | None - 排序参数
        
        返回:
        - dict - 分页查询结果
        """
        search_dict = search.__dict__ if search else {}
        order_by_list = order_by or [{'id': 'asc'}]
        offset = (page_no - 1) * page_size
        result = await AgAgentCRUD(auth).page_agents_crud(
            offset=offset,
            limit=page_size,
            order_by=order_by_list,
            search=search_dict
        )
        return result

    @classmethod
    async def create_agents_service(cls, auth: AuthSchema, data: AgAgentCreateSchema) -> dict:
        """
        创建
        
        参数:
        - auth: AuthSchema - 认证信息
        - data: AgAgentCreateSchema - 创建数据
        
        返回:
        - dict - 创建结果
        """
        obj = await AgAgentCRUD(auth).create_agents_crud(data=data)
        # 注册到 RuntimeRegistry（仅启用状态）
        if obj and obj.status == "0":
            try:
                get_registry().create_agent(obj)
            except Exception as e:
                log.warning(f"[Agents] registry create_agent failed for id={obj.id}: {e}")
        return AgAgentOutSchema.model_validate(obj).model_dump()

    @classmethod
    async def update_agents_service(cls, auth: AuthSchema, id: int, data: AgAgentUpdateSchema) -> dict:
        """
        更新
        
        参数:
        - auth: AuthSchema - 认证信息
        - id: int - 数据ID
        - data: AgAgentUpdateSchema - 更新数据
        
        返回:
        - dict - 更新结果
        """
        # 检查数据是否存在
        obj = await AgAgentCRUD(auth).get_by_id_agents_crud(id=id)
        if not obj:
            raise CustomException(msg='更新失败，该数据不存在')

        # 检查唯一性约束

        obj = await AgAgentCRUD(auth).update_agents_crud(id=id, data=data)
        # 更新 RuntimeRegistry
        if obj:
            try:
                if obj.status == "0":
                    get_registry().create_agent(obj)  # create_agent 兼容更新（替换已有实例）
                else:
                    get_registry().remove_agent(str(obj.id))
            except Exception as e:
                log.warning(f"[Agents] registry update failed for id={obj.id}: {e}")
        return AgAgentOutSchema.model_validate(obj).model_dump()

    @classmethod
    async def delete_agents_service(cls, auth: AuthSchema, ids: list[int]) -> None:
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
            obj = await AgAgentCRUD(auth).get_by_id_agents_crud(id=id)
            if not obj:
                raise CustomException(msg=f'删除失败，ID为{id}的数据不存在')
            ids_to_remove.append(str(obj.id))
        await AgAgentCRUD(auth).delete_agents_crud(ids=ids)
        for aid in ids_to_remove:
            get_registry().remove_agent(aid)

    @classmethod
    async def set_available_agents_service(cls, auth: AuthSchema, data: BatchSetAvailable) -> None:
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
            obj = await AgAgentCRUD(auth).get_by_id_agents_crud(id=id)
            if obj:
                obj_list.append(obj)
        await AgAgentCRUD(auth).set_available_agents_crud(ids=data.ids, status=data.status)
        for obj in obj_list:
            try:
                if data.status == "0":
                    get_registry().create_agent(obj)
                else:
                    get_registry().remove_agent(str(obj.id))
            except Exception as e:
                log.warning(f"[Agents] registry set_available failed for id={obj.id}: {e}")

    @classmethod
    async def batch_export_agents_service(cls, obj_list: list[dict]) -> bytes:
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
            'name': 'Agent名称',
            'model_id': '主模型ID',
            'reasoning_model_id': '推理模型ID',
            'output_model_id': '输出模型ID（response_model）',
            'parser_model_id': '解析模型ID',
            'memory_manager_id': '记忆管理器ID',
            'learning_config_id': '学习机配置ID',
            'reasoning_config_id': '推理配置ID',
            'compression_config_id': '压缩管理器配置ID',
            'session_summary_config_id': '会话摘要配置ID',
            'culture_config_id': '文化管理器配置ID',
            'instructions': 'Agent指令（system prompt）',
            'expected_output': '期望输出格式说明',
            'additional_context': '附加上下文',
            'reasoning': '是否开启推理',
            'reasoning_min_steps': '最少推理步数',
            'reasoning_max_steps': '最多推理步数',
            'learning': '是否开启学习',
            'search_knowledge': '是否搜索知识库',
            'update_knowledge': '是否允许更新知识库',
            'add_knowledge_to_context': '是否将知识库内容加入上下文',
            'enable_agentic_knowledge_filters': '是否开启智能知识过滤',
            'enable_agentic_state': '是否开启智能状态',
            'enable_agentic_memory': '是否开启智能记忆',
            'update_memory_on_run': '是否每次运行后更新记忆',
            'add_memories_to_context': '是否将记忆加入上下文',
            'add_history_to_context': '是否将历史记录加入上下文',
            'num_history_runs': '加入上下文的历史运行次数',
            'num_history_messages': '加入上下文的历史消息数',
            'search_past_sessions': '是否搜索历史会话',
            'num_past_sessions_to_search': '搜索历史会话数量',
            'enable_session_summaries': '是否开启会话摘要',
            'add_session_summary_to_context': '是否将会话摘要加入上下文',
            'tool_call_limit': '工具调用次数上限',
            'tool_choice': '工具选择策略(none/auto/specific)',
            'output_schema': '输出结构体JSON Schema',
            'input_schema': '输入结构体JSON Schema',
            'use_json_mode': '是否使用JSON输出模式',
            'structured_outputs': '是否使用结构化输出',
            'parse_response': '是否解析响应',
            'retries': '失败重试次数',
            'delay_between_retries': '重试间隔秒数',
            'exponential_backoff': '是否指数退避重试',
            'add_datetime_to_context': '是否将当前时间加入上下文',
            'add_name_to_context': '是否将Agent名称加入上下文',
            'compress_tool_results': '是否压缩工具结果',
            'stream': '是否开启流式输出',
            'stream_events': '是否流式推送事件',
            'store_events': '是否存储事件',
            'markdown': '是否输出Markdown格式',
            'followups': '是否生成追问',
            'num_followups': '追问数量',
            'debug_mode': '是否开启调试模式',
            'debug_level': '调试级别',
            'a2a_enabled': '是否对外暴露A2A接口',
            'is_remote': '是否为远程Agent',
            'remote_url': '远程Agent地址',
            'remote_agent_id': '远程Agent标识符',
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
    async def batch_import_agents_service(cls, auth: AuthSchema, file: UploadFile, update_support: bool = False) -> str:
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
            'Agent名称': 'name',
            '主模型ID': 'model_id',
            '推理模型ID': 'reasoning_model_id',
            '输出模型ID（response_model）': 'output_model_id',
            '解析模型ID': 'parser_model_id',
            '记忆管理器ID': 'memory_manager_id',
            '学习机配置ID': 'learning_config_id',
            '推理配置ID': 'reasoning_config_id',
            '压缩管理器配置ID': 'compression_config_id',
            '会话摘要配置ID': 'session_summary_config_id',
            '文化管理器配置ID': 'culture_config_id',
            'Agent指令（system prompt）': 'instructions',
            '期望输出格式说明': 'expected_output',
            '附加上下文': 'additional_context',
            '是否开启推理': 'reasoning',
            '最少推理步数': 'reasoning_min_steps',
            '最多推理步数': 'reasoning_max_steps',
            '是否开启学习': 'learning',
            '是否搜索知识库': 'search_knowledge',
            '是否允许更新知识库': 'update_knowledge',
            '是否将知识库内容加入上下文': 'add_knowledge_to_context',
            '是否开启智能知识过滤': 'enable_agentic_knowledge_filters',
            '是否开启智能状态': 'enable_agentic_state',
            '是否开启智能记忆': 'enable_agentic_memory',
            '是否每次运行后更新记忆': 'update_memory_on_run',
            '是否将记忆加入上下文': 'add_memories_to_context',
            '是否将历史记录加入上下文': 'add_history_to_context',
            '加入上下文的历史运行次数': 'num_history_runs',
            '加入上下文的历史消息数': 'num_history_messages',
            '是否搜索历史会话': 'search_past_sessions',
            '搜索历史会话数量': 'num_past_sessions_to_search',
            '是否开启会话摘要': 'enable_session_summaries',
            '是否将会话摘要加入上下文': 'add_session_summary_to_context',
            '工具调用次数上限': 'tool_call_limit',
            '工具选择策略(none/auto/specific)': 'tool_choice',
            '输出结构体JSON Schema': 'output_schema',
            '输入结构体JSON Schema': 'input_schema',
            '是否使用JSON输出模式': 'use_json_mode',
            '是否使用结构化输出': 'structured_outputs',
            '是否解析响应': 'parse_response',
            '失败重试次数': 'retries',
            '重试间隔秒数': 'delay_between_retries',
            '是否指数退避重试': 'exponential_backoff',
            '是否将当前时间加入上下文': 'add_datetime_to_context',
            '是否将Agent名称加入上下文': 'add_name_to_context',
            '是否压缩工具结果': 'compress_tool_results',
            '是否开启流式输出': 'stream',
            '是否流式推送事件': 'stream_events',
            '是否存储事件': 'store_events',
            '是否输出Markdown格式': 'markdown',
            '是否生成追问': 'followups',
            '追问数量': 'num_followups',
            '是否开启调试模式': 'debug_mode',
            '调试级别': 'debug_level',
            '是否对外暴露A2A接口': 'a2a_enabled',
            '是否为远程Agent': 'is_remote',
            '远程Agent地址': 'remote_url',
            '远程Agent标识符': 'remote_agent_id',
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
                        "reasoning_model_id": row['reasoning_model_id'],
                        "output_model_id": row['output_model_id'],
                        "parser_model_id": row['parser_model_id'],
                        "memory_manager_id": row['memory_manager_id'],
                        "learning_config_id": row['learning_config_id'],
                        "reasoning_config_id": row['reasoning_config_id'],
                        "compression_config_id": row['compression_config_id'],
                        "session_summary_config_id": row['session_summary_config_id'],
                        "culture_config_id": row['culture_config_id'],
                        "instructions": row['instructions'],
                        "expected_output": row['expected_output'],
                        "additional_context": row['additional_context'],
                        "reasoning": row['reasoning'],
                        "reasoning_min_steps": row['reasoning_min_steps'],
                        "reasoning_max_steps": row['reasoning_max_steps'],
                        "learning": row['learning'],
                        "search_knowledge": row['search_knowledge'],
                        "update_knowledge": row['update_knowledge'],
                        "add_knowledge_to_context": row['add_knowledge_to_context'],
                        "enable_agentic_knowledge_filters": row['enable_agentic_knowledge_filters'],
                        "enable_agentic_state": row['enable_agentic_state'],
                        "enable_agentic_memory": row['enable_agentic_memory'],
                        "update_memory_on_run": row['update_memory_on_run'],
                        "add_memories_to_context": row['add_memories_to_context'],
                        "add_history_to_context": row['add_history_to_context'],
                        "num_history_runs": row['num_history_runs'],
                        "num_history_messages": row['num_history_messages'],
                        "search_past_sessions": row['search_past_sessions'],
                        "num_past_sessions_to_search": row['num_past_sessions_to_search'],
                        "enable_session_summaries": row['enable_session_summaries'],
                        "add_session_summary_to_context": row['add_session_summary_to_context'],
                        "tool_call_limit": row['tool_call_limit'],
                        "tool_choice": row['tool_choice'],
                        "output_schema": row['output_schema'],
                        "input_schema": row['input_schema'],
                        "use_json_mode": row['use_json_mode'],
                        "structured_outputs": row['structured_outputs'],
                        "parse_response": row['parse_response'],
                        "retries": row['retries'],
                        "delay_between_retries": row['delay_between_retries'],
                        "exponential_backoff": row['exponential_backoff'],
                        "add_datetime_to_context": row['add_datetime_to_context'],
                        "add_name_to_context": row['add_name_to_context'],
                        "compress_tool_results": row['compress_tool_results'],
                        "stream": row['stream'],
                        "stream_events": row['stream_events'],
                        "store_events": row['store_events'],
                        "markdown": row['markdown'],
                        "followups": row['followups'],
                        "num_followups": row['num_followups'],
                        "debug_mode": row['debug_mode'],
                        "debug_level": row['debug_level'],
                        "a2a_enabled": row['a2a_enabled'],
                        "is_remote": row['is_remote'],
                        "remote_url": row['remote_url'],
                        "remote_agent_id": row['remote_agent_id'],
                        "metadata_config": row['metadata_config'],
                        "status": row['status'],
                        "description": row['description'],
                        "created_time": row['created_time'],
                        "updated_time": row['updated_time'],
                        "created_id": row['created_id'],
                        "updated_id": row['updated_id'],
                    }
                    # 使用CreateSchema做校验后入库
                    create_schema = AgAgentCreateSchema.model_validate(data)

                    # 检查唯一性约束

                    await AgAgentCRUD(auth).create_agents_crud(data=create_schema)
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
    async def import_template_download_agents_service(cls) -> bytes:
        """
        下载导入模板
        
        返回:
        - bytes - Excel文件的二进制数据
        """
        header_list = [
            '',
            '',
            'Agent名称',
            '主模型ID',
            '推理模型ID',
            '输出模型ID（response_model）',
            '解析模型ID',
            '记忆管理器ID',
            '学习机配置ID',
            '推理配置ID',
            '压缩管理器配置ID',
            '会话摘要配置ID',
            '文化管理器配置ID',
            'Agent指令（system prompt）',
            '期望输出格式说明',
            '附加上下文',
            '是否开启推理',
            '最少推理步数',
            '最多推理步数',
            '是否开启学习',
            '是否搜索知识库',
            '是否允许更新知识库',
            '是否将知识库内容加入上下文',
            '是否开启智能知识过滤',
            '是否开启智能状态',
            '是否开启智能记忆',
            '是否每次运行后更新记忆',
            '是否将记忆加入上下文',
            '是否将历史记录加入上下文',
            '加入上下文的历史运行次数',
            '加入上下文的历史消息数',
            '是否搜索历史会话',
            '搜索历史会话数量',
            '是否开启会话摘要',
            '是否将会话摘要加入上下文',
            '工具调用次数上限',
            '工具选择策略(none/auto/specific)',
            '输出结构体JSON Schema',
            '输入结构体JSON Schema',
            '是否使用JSON输出模式',
            '是否使用结构化输出',
            '是否解析响应',
            '失败重试次数',
            '重试间隔秒数',
            '是否指数退避重试',
            '是否将当前时间加入上下文',
            '是否将Agent名称加入上下文',
            '是否压缩工具结果',
            '是否开启流式输出',
            '是否流式推送事件',
            '是否存储事件',
            '是否输出Markdown格式',
            '是否生成追问',
            '追问数量',
            '是否开启调试模式',
            '调试级别',
            '是否对外暴露A2A接口',
            '是否为远程Agent',
            '远程Agent地址',
            '远程Agent标识符',
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
