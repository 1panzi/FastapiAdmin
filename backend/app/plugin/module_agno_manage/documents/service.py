
import io

import pandas as pd
from fastapi import UploadFile

from app.api.v1.module_system.auth.schema import AuthSchema
from app.core.base_schema import BatchSetAvailable
from app.core.exceptions import CustomException
from app.core.logger import log
from app.utils.excel_util import ExcelUtil
from agno.knowledge import Knowledge
from .crud import AgDocumentCRUD
from .schema import (
    AgDocumentCreateSchema,
    AgDocumentOutSchema,
    AgDocumentQueryParam,
    AgDocumentUpdateSchema,
)


class AgDocumentService:
    """
    知识库文档服务层
    """

    @classmethod
    async def detail_documents_service(cls, auth: AuthSchema, id: int) -> dict:
        """
        详情
        
        参数:
        - auth: AuthSchema - 认证信息
        - id: int - 数据ID
        
        返回:
        - dict - 数据详情
        """
        obj = await AgDocumentCRUD(auth).get_by_id_documents_crud(id=id)
        if not obj:
            raise CustomException(msg="该数据不存在")
        return AgDocumentOutSchema.model_validate(obj).model_dump()

    @classmethod
    async def list_documents_service(cls, auth: AuthSchema, search: AgDocumentQueryParam | None = None, order_by: list[dict] | None = None) -> list[dict]:
        """
        列表查询
        
        参数:
        - auth: AuthSchema - 认证信息
        - search: AgDocumentQueryParam | None - 查询参数
        - order_by: list[dict] | None - 排序参数
        
        返回:
        - list[dict] - 数据列表
        """
        search_dict = search.__dict__ if search else None
        obj_list = await AgDocumentCRUD(auth).list_documents_crud(search=search_dict, order_by=order_by)
        return [AgDocumentOutSchema.model_validate(obj).model_dump() for obj in obj_list]

    @classmethod
    async def page_documents_service(cls, auth: AuthSchema, page_no: int, page_size: int, search: AgDocumentQueryParam | None = None, order_by: list[dict] | None = None) -> dict:
        """
        分页查询（数据库分页）
        
        参数:
        - auth: AuthSchema - 认证信息
        - page_no: int - 页码
        - page_size: int - 每页数量
        - search: AgDocumentQueryParam | None - 查询参数
        - order_by: list[dict] | None - 排序参数
        
        返回:
        - dict - 分页查询结果
        """
        search_dict = search.__dict__ if search else {}
        order_by_list = order_by or [{'id': 'asc'}]
        offset = (page_no - 1) * page_size
        result = await AgDocumentCRUD(auth).page_documents_crud(
            offset=offset,
            limit=page_size,
            order_by=order_by_list,
            search=search_dict
        )
        return result

    @classmethod
    async def create_documents_service(cls, auth: AuthSchema, data: AgDocumentCreateSchema) -> dict:
        """
        创建
        
        参数:
        - auth: AuthSchema - 认证信息
        - data: AgDocumentCreateSchema - 创建数据
        
        返回:
        - dict - 创建结果
        """
        obj = await AgDocumentCRUD(auth).create_documents_crud(data=data)
        return AgDocumentOutSchema.model_validate(obj).model_dump()

    @classmethod
    async def update_documents_service(cls, auth: AuthSchema, id: int, data: AgDocumentUpdateSchema) -> dict:
        """
        更新
        
        参数:
        - auth: AuthSchema - 认证信息
        - id: int - 数据ID
        - data: AgDocumentUpdateSchema - 更新数据
        
        返回:
        - dict - 更新结果
        """
        # 检查数据是否存在
        obj = await AgDocumentCRUD(auth).get_by_id_documents_crud(id=id)
        if not obj:
            raise CustomException(msg='更新失败，该数据不存在')

        # 检查唯一性约束

        obj = await AgDocumentCRUD(auth).update_documents_crud(id=id, data=data)
        return AgDocumentOutSchema.model_validate(obj).model_dump()

    @classmethod
    async def delete_documents_service(cls, auth: AuthSchema, ids: list[int]) -> None:
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
            obj = await AgDocumentCRUD(auth).get_by_id_documents_crud(id=id)
            if not obj:
                raise CustomException(msg=f'删除失败，ID为{id}的数据不存在')
        await AgDocumentCRUD(auth).delete_documents_crud(ids=ids)

    @classmethod
    async def set_available_documents_service(cls, auth: AuthSchema, data: BatchSetAvailable) -> None:
        """
        批量设置状态
        
        参数:
        - auth: AuthSchema - 认证信息
        - data: BatchSetAvailable - 批量设置状态数据
        
        返回:
        - None
        """
        await AgDocumentCRUD(auth).set_available_documents_crud(ids=data.ids, status=data.status)

    @classmethod
    async def batch_export_documents_service(cls, obj_list: list[dict]) -> bytes:
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
            'kb_id': '所属知识库ID',
            'name': '文档名称',
            'storage_type': '存储类型(local/s3/gcs/url)',
            'storage_path': '存储路径或URL',
            'doc_status': '处理状态(pending/processing/indexed/failed)',
            'error_msg': '处理失败错误信息',
            'metadata_config': '文档元数据',
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
    async def batch_import_documents_service(cls, auth: AuthSchema, file: UploadFile, update_support: bool = False) -> str:
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
            '所属知识库ID': 'kb_id',
            '文档名称': 'name',
            '存储类型(local/s3/gcs/url)': 'storage_type',
            '存储路径或URL': 'storage_path',
            '处理状态(pending/processing/indexed/failed)': 'doc_status',
            '处理失败错误信息': 'error_msg',
            '文档元数据': 'metadata_config',
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
                        "kb_id": row['kb_id'],
                        "name": row['name'],
                        "storage_type": row['storage_type'],
                        "storage_path": row['storage_path'],
                        "doc_status": row['doc_status'],
                        "error_msg": row['error_msg'],
                        "metadata_config": row['metadata_config'],
                        "status": row['status'],
                        "description": row['description'],
                        "created_time": row['created_time'],
                        "updated_time": row['updated_time'],
                        "created_id": row['created_id'],
                        "updated_id": row['updated_id'],
                    }
                    # 使用CreateSchema做校验后入库
                    create_schema = AgDocumentCreateSchema.model_validate(data)

                    # 检查唯一性约束

                    await AgDocumentCRUD(auth).create_documents_crud(data=create_schema)
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
    async def import_template_download_documents_service(cls) -> bytes:
        """
        下载导入模板
        
        返回:
        - bytes - Excel文件的二进制数据
        """
        header_list = [
            '',
            '',
            '所属知识库ID',
            '文档名称',
            '存储类型(local/s3/gcs/url)',
            '存储路径或URL',
            '处理状态(pending/processing/indexed/failed)',
            '处理失败错误信息',
            '文档元数据',
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

    # ── 知识库文档管理（向量化相关）──────────────────────────────────────────

    @classmethod
    async def upload_document_service(
        cls,
        auth: AuthSchema,
        kb_id: int,
        file,
        name: str | None,
        description: str | None,
        metadata_config: dict | None,
        background_tasks,
        reader_id: int | None = None,
    ) -> dict:
        """
        上传文件到 knowledge base：
        1. 保存文件到 settings.UPLOAD_FILE_PATH/knowledge/{kb_id}/
        2. 写 ag_documents 记录（doc_status=pending，记录 reader_id）
        3. 后台任务向量化（若指定 reader_id，用该 reader；否则 Agno 自动路由）
        """
        import uuid
        from pathlib import Path
        from app.config.setting import settings
        from app.plugin.module_agno_manage.core.registry import get_registry

        kb = get_registry().get_knowledge(str(kb_id))
        if kb is None:
            raise CustomException(msg=f"知识库 {kb_id} 不存在或未启用")

        content_bytes = await file.read()
        suffix = Path(file.filename).suffix if file.filename else ""
        save_dir = settings.UPLOAD_FILE_PATH / "knowledge" / str(kb_id)
        save_dir.mkdir(parents=True, exist_ok=True)
        file_name = f"{uuid.uuid4().hex}{suffix}"
        file_path = save_dir / file_name
        file_path.write_bytes(content_bytes)

        create_data = AgDocumentCreateSchema(
            kb_id=kb_id,
            name=name or file.filename or file_name,
            storage_type="local",
            storage_path=str(file_path.resolve()),
            doc_status="pending",
            metadata_config=metadata_config,
            description=description,
            reader_id=reader_id,
        )
        obj = await AgDocumentCRUD(auth).create_documents_crud(data=create_data)

        background_tasks.add_task(
            cls._vectorize_file,
            doc_id=obj.id,
            kb=kb,
            content_bytes=content_bytes,
            filename=file.filename,
            content_type=file.content_type,
            file_size=file.size,
            name=name or file.filename,
            description=description,
            metadata_config=metadata_config,
            reader_id=reader_id,
        )

        return AgDocumentOutSchema.model_validate(obj).model_dump()

    @classmethod
    async def insert_document_service(
        cls,
        auth: AuthSchema,
        kb_id: int,
        url: str | None,
        text_content: str | None,
        name: str | None,
        description: str | None,
        metadata_config: dict | None,
        background_tasks,
        reader_id: int | None = None,
    ) -> dict:
        """插入 URL 或纯文本到知识库，后台向量化。"""
        from app.plugin.module_agno_manage.core.registry import get_registry

        if not url and not text_content:
            raise CustomException(msg="url 和 text_content 不能同时为空")

        kb = get_registry().get_knowledge(str(kb_id))
        if kb is None:
            raise CustomException(msg=f"知识库 {kb_id} 不存在或未启用")

        storage_type = "url" if url else "text"
        storage_path = url or (text_content[:500] if text_content else "")

        create_data = AgDocumentCreateSchema(
            kb_id=kb_id,
            name=name or url or "text_content",
            storage_type=storage_type,
            storage_path=storage_path,
            doc_status="pending",
            metadata_config=metadata_config,
            description=description,
            reader_id=reader_id,
        )
        obj = await AgDocumentCRUD(auth).create_documents_crud(data=create_data)

        background_tasks.add_task(
            cls._vectorize_url_or_text,
            doc_id=obj.id,
            kb=kb,
            url=url,
            text_content=text_content,
            name=name,
            description=description,
            metadata_config=metadata_config,
            reader_id=reader_id,
        )

        return AgDocumentOutSchema.model_validate(obj).model_dump()

    @classmethod
    async def reprocess_document_service(
        cls,
        auth: AuthSchema,
        kb_id: int,
        doc_id: int,
        background_tasks,
    ) -> dict:
        """重新向量化已有文档（从原始文件 / storage_path 重建，复用存储的 reader_id）。"""
        from app.core.database import async_db_session
        from app.plugin.module_agno_manage.core.registry import get_registry

        obj = await AgDocumentCRUD(auth).get_by_id_documents_crud(id=doc_id)
        if not obj or obj.kb_id != kb_id:
            raise CustomException(msg="文档不存在")

        kb = get_registry().get_knowledge(str(kb_id))
        if kb is None:
            raise CustomException(msg=f"知识库 {kb_id} 不存在或未启用")

        if obj.storage_type == "local":
            from pathlib import Path
            file_path = Path(obj.storage_path)
            if not file_path.exists():
                raise CustomException(msg=f"原始文件不存在: {obj.storage_path}")
            content_bytes = file_path.read_bytes()
            background_tasks.add_task(
                cls._vectorize_file,
                doc_id=doc_id,
                kb=kb,
                content_bytes=content_bytes,
                filename=obj.name,
                content_type=None,
                file_size=len(content_bytes),
                name=obj.name,
                description=obj.description,
                metadata_config=obj.metadata_config,
                reader_id=obj.reader_id,
            )
        else:
            background_tasks.add_task(
                cls._vectorize_url_or_text,
                doc_id=doc_id,
                kb=kb,
                url=obj.storage_path if obj.storage_type == "url" else None,
                text_content=obj.storage_path if obj.storage_type == "text" else None,
                name=obj.name,
                description=obj.description,
                metadata_config=obj.metadata_config,
                reader_id=obj.reader_id,
            )

        async with async_db_session() as session:
            await AgDocumentCRUD.update_status_internal_crud(session, doc_id, "pending")

        return AgDocumentOutSchema.model_validate(obj).model_dump()

    @classmethod
    async def delete_document_with_vectors_service(
        cls,
        auth: AuthSchema,
        kb_id: int,
        doc_id: int,
    ) -> None:
        """删除文档记录及 Agno 侧向量数据。"""
        from app.plugin.module_agno_manage.core.registry import get_registry

        obj = await AgDocumentCRUD(auth).get_by_id_documents_crud(id=doc_id)
        if not obj or obj.kb_id != kb_id:
            raise CustomException(msg="文档不存在")

        if obj.content_id:
            kb = get_registry().get_knowledge(str(kb_id))
            if kb:
                try:
                    await kb.aremove_content_by_id(content_id=obj.content_id)
                except Exception as e:
                    log.warning(f"[Documents] 删除 Agno content {obj.content_id} 失败: {e}")

        await AgDocumentCRUD(auth).delete_documents_crud(ids=[doc_id])

    @classmethod
    async def search_knowledge_service(
        cls,
        auth: AuthSchema,
        kb_id: int,
        query: str,
        limit: int = 10,
    ) -> list[dict]:
        """向量检索知识库内容。"""
        from app.plugin.module_agno_manage.core.registry import get_registry

        kb = get_registry().get_knowledge(str(kb_id))
        if kb is None:
            raise CustomException(msg=f"知识库 {kb_id} 不存在或未启用")

        docs = await kb.asearch(query=query, max_results=limit)
        return [
            {
                "name": doc.name,
                "content": doc.content,
                "meta_data": doc.meta_data,
                "reranking_score": getattr(doc, "reranking_score", None),
            }
            for doc in docs
        ]

    @staticmethod
    async def _vectorize_file(
        doc_id: int,
        kb,
        content_bytes: bytes,
        filename: str | None,
        content_type: str | None,
        file_size: int | None,
        name: str | None,
        description: str | None,
        metadata_config: dict | None,
        reader_id: int | None = None,
    ) -> None:
        """
        后台任务：将文件向量化并回写 ag_documents 状态。
        若指定 reader_id，从 registry 按 ID 构建对应 reader，临时注入 kb.readers 覆盖 Agno 自动路由；
        否则 Agno 依文件类型自动选 reader。
        """
        from agno.knowledge.content import Content, FileData
        from agno.utils.string import generate_id
        from app.core.database import async_db_session
        from app.core.logger import log

        async with async_db_session() as session:
            await AgDocumentCRUD.update_status_internal_crud(session, doc_id, "processing")

        file_data = FileData(
            content=content_bytes,
            type=content_type,
            filename=filename,
            size=file_size,
        )
        content = Content(
            name=name,
            description=description,
            metadata=metadata_config,
            file_data=file_data,
            size=file_size,
        )
        content.content_hash = kb._build_content_hash(content)
        content.id = generate_id(content.content_hash)

        # 若指定 reader_id，临时覆盖 kb.readers 以强制使用该 reader
        saved_readers = None
        if reader_id is not None:
            from app.plugin.module_agno_manage.core.registry import get_registry
            reg = get_registry()
            reader_row = reg._reader_rows.get(str(reader_id))
            if reader_row:
                specific_reader = reg._build_reader(reader_row)
                if specific_reader:
                    saved_readers = getattr(kb, "readers", None)
                    kb.readers = {reader_row.reader_type: specific_reader}
                else:
                    log.warning(f"[Documents] reader_id={reader_id} 构建失败，回退 Agno 自动路由")
            else:
                log.warning(f"[Documents] reader_id={reader_id} 不在 registry，回退 Agno 自动路由")

        try:
            await kb._aload_content(content, upsert=True, skip_if_exists=False)
            async with async_db_session() as session:
                await AgDocumentCRUD.update_status_internal_crud(
                    session, doc_id, "indexed", content_id=content.id
                )
        except Exception as e:
            log.error(f"[Documents] 向量化失败 doc_id={doc_id}: {e}")
            async with async_db_session() as session:
                await AgDocumentCRUD.update_status_internal_crud(
                    session, doc_id, "failed", error_msg=str(e)
                )
        finally:
            if saved_readers is not None:
                kb.readers = saved_readers

    @staticmethod
    async def _vectorize_url_or_text(
        doc_id: int,
        kb,
        url: str | None,
        text_content: str | None,
        name: str | None,
        description: str | None,
        metadata_config: dict | None,
        reader_id: int | None = None,
    ) -> None:
        """
        后台任务：将 URL/文本向量化并回写 ag_documents 状态。
        若指定 reader_id，从 registry 按 ID 构建对应 reader，临时注入 kb.readers；
        否则 Agno 依内容类型自动选 reader。
        """
        from app.core.database import async_db_session
        from app.core.logger import log

        async with async_db_session() as session:
            await AgDocumentCRUD.update_status_internal_crud(session, doc_id, "processing")

        # 若指定 reader_id，临时覆盖 kb.readers
        saved_readers = None
        if reader_id is not None:
            from app.plugin.module_agno_manage.core.registry import get_registry
            reg = get_registry()
            reader_row = reg._reader_rows.get(str(reader_id))
            if reader_row:
                specific_reader = reg._build_reader(reader_row)
                if specific_reader:
                    saved_readers = getattr(kb, "readers", None)
                    kb.readers = {reader_row.reader_type: specific_reader}
                else:
                    log.warning(f"[Documents] reader_id={reader_id} 构建失败，回退 Agno 自动路由")
            else:
                log.warning(f"[Documents] reader_id={reader_id} 不在 registry，回退 Agno 自动路由")

        try:
            await kb.ainsert(
                name=name,
                description=description,
                url=url,
                text_content=text_content,
                metadata=metadata_config,
                upsert=True,
            )
            async with async_db_session() as session:
                await AgDocumentCRUD.update_status_internal_crud(session, doc_id, "indexed")
        except Exception as e:
            log.error(f"[Documents] URL/文本向量化失败 doc_id={doc_id}: {e}")
            async with async_db_session() as session:
                await AgDocumentCRUD.update_status_internal_crud(
                    session, doc_id, "failed", error_msg=str(e)
                )
        finally:
            if saved_readers is not None:
                kb.readers = saved_readers

