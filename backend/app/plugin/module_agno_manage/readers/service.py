
import io

import pandas as pd
from fastapi import UploadFile

from app.api.v1.module_system.auth.schema import AuthSchema
from app.core.base_schema import BatchSetAvailable
from app.core.exceptions import CustomException
from app.core.logger import log
from app.plugin.module_agno_manage.core.registry import get_registry
from app.utils.excel_util import ExcelUtil

from .agno_catalog import (
    ChunkingStrategyInfo,
    ReaderInfo,
    get_chunking_strategy_info,
    get_reader_info,
    get_supported_strategies_for_reader,
    list_chunking_strategies,
    list_reader_types,
)
from .crud import AgReaderCRUD
from .schema import (
    AgReaderCreateSchema,
    AgReaderOutSchema,
    AgReaderQueryParam,
    AgReaderUpdateSchema,
)


class AgReaderService:
    """
    reader管理服务层
    """

    @classmethod
    async def detail_readers_service(cls, auth: AuthSchema, id: int) -> dict:
        """
        详情
        
        参数:
        - auth: AuthSchema - 认证信息
        - id: int - 数据ID
        
        返回:
        - dict - 数据详情
        """
        obj = await AgReaderCRUD(auth).get_by_id_readers_crud(id=id)
        if not obj:
            raise CustomException(msg="该数据不存在")
        return AgReaderOutSchema.model_validate(obj).model_dump()

    @classmethod
    async def list_readers_service(cls, auth: AuthSchema, search: AgReaderQueryParam | None = None, order_by: list[dict] | None = None) -> list[dict]:
        """
        列表查询
        
        参数:
        - auth: AuthSchema - 认证信息
        - search: AgReaderQueryParam | None - 查询参数
        - order_by: list[dict] | None - 排序参数
        
        返回:
        - list[dict] - 数据列表
        """
        search_dict = search.__dict__ if search else None
        obj_list = await AgReaderCRUD(auth).list_readers_crud(search=search_dict, order_by=order_by)
        return [AgReaderOutSchema.model_validate(obj).model_dump() for obj in obj_list]

    @classmethod
    async def page_readers_service(cls, auth: AuthSchema, page_no: int, page_size: int, search: AgReaderQueryParam | None = None, order_by: list[dict] | None = None) -> dict:
        """
        分页查询（数据库分页）
        
        参数:
        - auth: AuthSchema - 认证信息
        - page_no: int - 页码
        - page_size: int - 每页数量
        - search: AgReaderQueryParam | None - 查询参数
        - order_by: list[dict] | None - 排序参数
        
        返回:
        - dict - 分页查询结果
        """
        search_dict = search.__dict__ if search else {}
        order_by_list = order_by or [{'id': 'asc'}]
        offset = (page_no - 1) * page_size
        result = await AgReaderCRUD(auth).page_readers_crud(
            offset=offset,
            limit=page_size,
            order_by=order_by_list,
            search=search_dict
        )
        return result

    @classmethod
    async def create_readers_service(cls, auth: AuthSchema, data: AgReaderCreateSchema) -> dict:
        """
        创建
        
        参数:
        - auth: AuthSchema - 认证信息
        - data: AgReaderCreateSchema - 创建数据
        
        返回:
        - dict - 创建结果
        """
        obj = await AgReaderCRUD(auth).create_readers_crud(data=data)
        if obj and obj.status == "0":
            get_registry().update_reader_row(str(obj.id), obj)
        return AgReaderOutSchema.model_validate(obj).model_dump()

    @classmethod
    async def update_readers_service(cls, auth: AuthSchema, id: int, data: AgReaderUpdateSchema) -> dict:
        """
        更新
        
        参数:
        - auth: AuthSchema - 认证信息
        - id: int - 数据ID
        - data: AgReaderUpdateSchema - 更新数据
        
        返回:
        - dict - 更新结果
        """
        # 检查数据是否存在
        obj = await AgReaderCRUD(auth).get_by_id_readers_crud(id=id)
        if not obj:
            raise CustomException(msg='更新失败，该数据不存在')

        # 检查唯一性约束

        obj = await AgReaderCRUD(auth).update_readers_crud(id=id, data=data)
        if obj:
            if obj.status == "0":
                get_registry().update_reader_row(str(obj.id), obj)
            else:
                get_registry().remove_reader_row(str(obj.id))
        return AgReaderOutSchema.model_validate(obj).model_dump()

    @classmethod
    async def delete_readers_service(cls, auth: AuthSchema, ids: list[int]) -> None:
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
            obj = await AgReaderCRUD(auth).get_by_id_readers_crud(id=id)
            if not obj:
                raise CustomException(msg=f'删除失败，ID为{id}的数据不存在')
        for id in ids:
            get_registry().remove_reader_row(str(id))
        await AgReaderCRUD(auth).delete_readers_crud(ids=ids)

    @classmethod
    async def set_available_readers_service(cls, auth: AuthSchema, data: BatchSetAvailable) -> None:
        """
        批量设置状态
        
        参数:
        - auth: AuthSchema - 认证信息
        - data: BatchSetAvailable - 批量设置状态数据
        
        返回:
        - None
        """
        await AgReaderCRUD(auth).set_available_readers_crud(ids=data.ids, status=data.status)
        for id in data.ids:
            if data.status == "0":
                obj = await AgReaderCRUD(auth).get_by_id_readers_crud(id=id)
                if obj:
                    get_registry().update_reader_row(str(id), obj)
            else:
                get_registry().remove_reader_row(str(id))

    @classmethod
    async def batch_export_readers_service(cls, obj_list: list[dict]) -> bytes:
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
            'name': 'Reader名称',
            'reader_type': 'Reader类型(pdf/csv/excel/docx/pptx/json/markdown/text/website/firecrawl/tavily/youtube/arxiv/wikipedia/web_search/field_labeled_csv)',
            'chunk': '是否对内容分块',
            'chunk_size': '分块大小（字符数）',
            'encoding': '文本编码（utf-8/gbk等，文本类Reader使用）',
            'chunking_strategy': 'Chunking策略(FixedSizeChunker/RecursiveChunker/DocumentChunker/MarkdownChunker/RowChunker/SemanticChunker/AgenticChunker/CodeChunker)',
            'chunk_overlap': 'Chunk重叠字符数（FixedSize/Recursive/Document/Markdown策略支持）',
            'reader_config': 'Reader专属参数（按reader_type不同，见表注释）',
            'embedder_id': '关联Embedder ID（SemanticChunker使用）',
            'model_id': '关联Model ID（AgenticChunker使用）',
            'status': '是否启用(0:启用 1:禁用)',
            'description': '备注/描述',
            'created_time': '创建时间',
            'updated_time': '更新时间',
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
    async def batch_import_readers_service(cls, auth: AuthSchema, file: UploadFile, update_support: bool = False) -> str:
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
            'Reader名称': 'name',
            'Reader类型(pdf/csv/excel/docx/pptx/json/markdown/text/website/firecrawl/tavily/youtube/arxiv/wikipedia/web_search/field_labeled_csv)': 'reader_type',
            '是否对内容分块': 'chunk',
            '分块大小（字符数）': 'chunk_size',
            '文本编码（utf-8/gbk等，文本类Reader使用）': 'encoding',
            'Chunking策略(FixedSizeChunker/RecursiveChunker/DocumentChunker/MarkdownChunker/RowChunker/SemanticChunker/AgenticChunker/CodeChunker)': 'chunking_strategy',
            'Chunk重叠字符数（FixedSize/Recursive/Document/Markdown策略支持）': 'chunk_overlap',
            'Reader专属参数（按reader_type不同，见表注释）': 'reader_config',
            '关联Embedder ID（SemanticChunker使用）': 'embedder_id',
            '关联Model ID（AgenticChunker使用）': 'model_id',
            '是否启用(0:启用 1:禁用)': 'status',
            '备注/描述': 'description',
            '创建时间': 'created_time',
            '更新时间': 'updated_time',
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
                        "reader_type": row['reader_type'],
                        "chunk": row['chunk'],
                        "chunk_size": row['chunk_size'],
                        "encoding": row['encoding'],
                        "chunking_strategy": row['chunking_strategy'],
                        "chunk_overlap": row['chunk_overlap'],
                        "reader_config": row['reader_config'],
                        "embedder_id": row['embedder_id'],
                        "model_id": row['model_id'],
                        "status": row['status'],
                        "description": row['description'],
                        "created_time": row['created_time'],
                        "updated_time": row['updated_time'],
                        "created_id": row['created_id'],
                        "updated_id": row['updated_id'],
                    }
                    # 使用CreateSchema做校验后入库
                    create_schema = AgReaderCreateSchema.model_validate(data)

                    # 检查唯一性约束

                    await AgReaderCRUD(auth).create_readers_crud(data=create_schema)
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
    async def import_template_download_readers_service(cls) -> bytes:
        """
        下载导入模板
        
        返回:
        - bytes - Excel文件的二进制数据
        """
        header_list = [
            '',
            '',
            'Reader名称',
            'Reader类型(pdf/csv/excel/docx/pptx/json/markdown/text/website/firecrawl/tavily/youtube/arxiv/wikipedia/web_search/field_labeled_csv)',
            '是否对内容分块',
            '分块大小（字符数）',
            '文本编码（utf-8/gbk等，文本类Reader使用）',
            'Chunking策略(FixedSizeChunker/RecursiveChunker/DocumentChunker/MarkdownChunker/RowChunker/SemanticChunker/AgenticChunker/CodeChunker)',
            'Chunk重叠字符数（FixedSize/Recursive/Document/Markdown策略支持）',
            'Reader专属参数（按reader_type不同，见表注释）',
            '关联Embedder ID（SemanticChunker使用）',
            '关联Model ID（AgenticChunker使用）',
            '是否启用(0:启用 1:禁用)',
            '备注/描述',
            '创建时间',
            '更新时间',
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
    def list_reader_types_service(cls) -> list[ReaderInfo]:
        """返回所有支持的 Reader 类型元数据（供前端动态渲染表单）。"""
        return list_reader_types()

    @classmethod
    def get_reader_info_service(cls, reader_type: str) -> ReaderInfo | None:
        """返回指定 reader_type 的元数据，不存在返回 None。"""
        return get_reader_info(reader_type)

    @classmethod
    def list_chunking_strategies_service(cls) -> list[ChunkingStrategyInfo]:
        """返回所有支持的 Chunking 策略元数据。"""
        return list_chunking_strategies()

    @classmethod
    def get_chunking_strategy_info_service(cls, strategy: str) -> ChunkingStrategyInfo | None:
        """返回指定策略的详细参数 schema，不存在返回 None。"""
        return get_chunking_strategy_info(strategy)

    @classmethod
    def get_supported_strategies_service(cls, reader_type: str) -> list[str]:
        """返回指定 reader_type 支持的 chunking 策略名列表（直接调 Agno reader 类）。"""
        return get_supported_strategies_for_reader(reader_type)
