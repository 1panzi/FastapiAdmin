
from fastapi import APIRouter, Body, Depends, Path, UploadFile
from fastapi.responses import JSONResponse, StreamingResponse

from app.api.v1.module_system.auth.schema import AuthSchema
from app.common.response import StreamResponse, SuccessResponse
from app.core.base_params import PaginationQueryParam
from app.core.base_schema import BatchSetAvailable
from app.core.dependencies import AuthPermission
from app.core.logger import log
from app.utils.common_util import bytes2file_response

from .schema import AgDocumentCreateSchema, AgDocumentQueryParam, AgDocumentUpdateSchema
from .service import AgDocumentService

AgDocumentRouter = APIRouter(prefix='/documents', tags=["知识库文档模块"])


@AgDocumentRouter.get(
    "/detail/{id}",
    summary="获取知识库文档详情",
    description="获取知识库文档详情"
)
async def get_documents_detail_controller(
    id: int = Path(..., description="ID"),
    auth: AuthSchema = Depends(AuthPermission(["module_agno_manage:documents:query"]))
) -> JSONResponse:
    """
    获取知识库文档详情接口
    
    参数:
    - id: int - 数据ID
    - auth: AuthSchema - 认证信息
    
    返回:
    - JSONResponse - 包含知识库文档详情的JSON响应
    """
    result_dict = await AgDocumentService.detail_documents_service(auth=auth, id=id)
    log.info(f"获取知识库文档详情成功 {id}")
    return SuccessResponse(data=result_dict, msg="获取知识库文档详情成功")


@AgDocumentRouter.get(
    "/list",
    summary="查询知识库文档列表",
    description="查询知识库文档列表"
)
async def get_documents_list_controller(
    page: PaginationQueryParam = Depends(),
    search: AgDocumentQueryParam = Depends(),
    auth: AuthSchema = Depends(AuthPermission(["module_agno_manage:documents:query"]))
) -> JSONResponse:
    """
    查询知识库文档列表接口（数据库分页）
    
    参数:
    - page: PaginationQueryParam - 分页参数
    - search: AgDocumentQueryParam - 查询参数
    - auth: AuthSchema - 认证信息
    
    返回:
    - JSONResponse - 包含知识库文档列表的JSON响应
    """
    result_dict = await AgDocumentService.page_documents_service(
        auth=auth,
        page_no=page.page_no if page.page_no is not None else 1,
        page_size=page.page_size if page.page_size is not None else 10,
        search=search,
        order_by=page.order_by
    )
    log.info("查询知识库文档列表成功")
    return SuccessResponse(data=result_dict, msg="查询知识库文档列表成功")


@AgDocumentRouter.post(
    "/create",
    summary="创建知识库文档",
    description="创建知识库文档"
)
async def create_documents_controller(
    data: AgDocumentCreateSchema,
    auth: AuthSchema = Depends(AuthPermission(["module_agno_manage:documents:create"]))
) -> JSONResponse:
    """
    创建知识库文档接口
    
    参数:
    - data: AgDocumentCreateSchema - 创建数据
    - auth: AuthSchema - 认证信息
    
    返回:
    - JSONResponse - 包含创建知识库文档结果的JSON响应
    """
    result_dict = await AgDocumentService.create_documents_service(auth=auth, data=data)
    log.info("创建知识库文档成功")
    return SuccessResponse(data=result_dict, msg="创建知识库文档成功")


@AgDocumentRouter.put(
    "/update/{id}",
    summary="修改知识库文档",
    description="修改知识库文档"
)
async def update_documents_controller(
    data: AgDocumentUpdateSchema,
    id: int = Path(..., description="ID"),
    auth: AuthSchema = Depends(AuthPermission(["module_agno_manage:documents:update"]))
) -> JSONResponse:
    """
    修改知识库文档接口
    
    参数:
    - id: int - 数据ID
    - data: AgDocumentUpdateSchema - 更新数据
    - auth: AuthSchema - 认证信息
    
    返回:
    - JSONResponse - 包含修改知识库文档结果的JSON响应
    """
    result_dict = await AgDocumentService.update_documents_service(auth=auth, id=id, data=data)
    log.info("修改知识库文档成功")
    return SuccessResponse(data=result_dict, msg="修改知识库文档成功")


@AgDocumentRouter.delete(
    "/delete",
    summary="删除知识库文档",
    description="删除知识库文档"
)
async def delete_documents_controller(
    ids: list[int] = Body(..., description="ID列表"),
    auth: AuthSchema = Depends(AuthPermission(["module_agno_manage:documents:delete"]))
) -> JSONResponse:
    """
    删除知识库文档接口
    
    参数:
    - ids: list[int] - 数据ID列表
    - auth: AuthSchema - 认证信息
    
    返回:
    - JSONResponse - 包含删除知识库文档结果的JSON响应
    """
    await AgDocumentService.delete_documents_service(auth=auth, ids=ids)
    log.info(f"删除知识库文档成功: {ids}")
    return SuccessResponse(msg="删除知识库文档成功")


@AgDocumentRouter.patch(
    "/available/setting",
    summary="批量修改知识库文档状态",
    description="批量修改知识库文档状态"
)
async def batch_set_available_documents_controller(
    data: BatchSetAvailable,
    auth: AuthSchema = Depends(AuthPermission(["module_agno_manage:documents:patch"]))
) -> JSONResponse:
    """
    批量修改知识库文档状态接口
    
    参数:
    - data: BatchSetAvailable - 批量修改状态数据
    - auth: AuthSchema - 认证信息
    
    返回:
    - JSONResponse - 包含批量修改知识库文档状态结果的JSON响应
    """
    await AgDocumentService.set_available_documents_service(auth=auth, data=data)
    log.info(f"批量修改知识库文档状态成功: {data.ids}")
    return SuccessResponse(msg="批量修改知识库文档状态成功")


@AgDocumentRouter.post(
    '/export',
    summary="导出知识库文档",
    description="导出知识库文档"
)
async def export_documents_list_controller(
    search: AgDocumentQueryParam = Depends(),
    auth: AuthSchema = Depends(AuthPermission(["module_agno_manage:documents:export"]))
) -> StreamingResponse:
    """
    导出知识库文档接口
    
    参数:
    - search: AgDocumentQueryParam - 查询参数
    - auth: AuthSchema - 认证信息
    
    返回:
    - StreamingResponse - 包含导出知识库文档数据的流式响应
    """
    result_dict_list = await AgDocumentService.list_documents_service(search=search, auth=auth)
    export_result = await AgDocumentService.batch_export_documents_service(obj_list=result_dict_list)
    log.info('导出知识库文档成功')
    return StreamResponse(
        data=bytes2file_response(export_result),
        media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        headers={'Content-Disposition': 'attachment; filename=ag_documents.xlsx'}
    )


@AgDocumentRouter.post(
    '/import',
    summary="导入知识库文档",
    description="导入知识库文档"
)
async def import_documents_list_controller(
    file: UploadFile,
    auth: AuthSchema = Depends(AuthPermission(["module_agno_manage:documents:import"]))
) -> JSONResponse:
    """
    导入知识库文档接口
    
    参数:
    - file: UploadFile - 上传的Excel文件
    - auth: AuthSchema - 认证信息
    
    返回:
    - JSONResponse - 包含导入知识库文档结果的JSON响应
    """
    batch_import_result = await AgDocumentService.batch_import_documents_service(file=file, auth=auth, update_support=True)
    log.info("导入知识库文档成功")
    return SuccessResponse(data=batch_import_result, msg="导入知识库文档成功")


@AgDocumentRouter.post(
    '/download/template',
    summary="获取知识库文档导入模板",
    description="获取知识库文档导入模板",
    dependencies=[Depends(AuthPermission(["module_agno_manage:documents:download"]))]
)
async def export_documents_template_controller() -> StreamingResponse:
    """
    获取知识库文档导入模板接口
    
    返回:
    - StreamingResponse - 包含知识库文档导入模板的流式响应
    """
    import_template_result = await AgDocumentService.import_template_download_documents_service()
    log.info('获取知识库文档导入模板成功')
    return StreamResponse(
        data=bytes2file_response(import_template_result),
        media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        headers={'Content-Disposition': 'attachment; filename=ag_documents_template.xlsx'}
    )
