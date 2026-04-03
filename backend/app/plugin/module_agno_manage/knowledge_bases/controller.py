
from fastapi import APIRouter, Body, Depends, Path, UploadFile
from fastapi.responses import JSONResponse, StreamingResponse

from app.api.v1.module_system.auth.schema import AuthSchema
from app.common.response import StreamResponse, SuccessResponse
from app.core.base_params import PaginationQueryParam
from app.core.base_schema import BatchSetAvailable
from app.core.dependencies import AuthPermission
from app.core.logger import log
from app.utils.common_util import bytes2file_response

from .schema import (
    AgKnowledgeBaseCreateSchema,
    AgKnowledgeBaseQueryParam,
    AgKnowledgeBaseUpdateSchema,
)
from .service import AgKnowledgeBaseService

AgKnowledgeBaseRouter = APIRouter(prefix='/knowledge_bases', tags=["知识库模块"])


@AgKnowledgeBaseRouter.get(
    "/detail/{id}",
    summary="获取知识库详情",
    description="获取知识库详情"
)
async def get_knowledge_bases_detail_controller(
    id: int = Path(..., description="ID"),
    auth: AuthSchema = Depends(AuthPermission(["module_agno_manage:knowledge_bases:query"]))
) -> JSONResponse:
    """
    获取知识库详情接口
    
    参数:
    - id: int - 数据ID
    - auth: AuthSchema - 认证信息
    
    返回:
    - JSONResponse - 包含知识库详情的JSON响应
    """
    result_dict = await AgKnowledgeBaseService.detail_knowledge_bases_service(auth=auth, id=id)
    log.info(f"获取知识库详情成功 {id}")
    return SuccessResponse(data=result_dict, msg="获取知识库详情成功")


@AgKnowledgeBaseRouter.get(
    "/list",
    summary="查询知识库列表",
    description="查询知识库列表"
)
async def get_knowledge_bases_list_controller(
    page: PaginationQueryParam = Depends(),
    search: AgKnowledgeBaseQueryParam = Depends(),
    auth: AuthSchema = Depends(AuthPermission(["module_agno_manage:knowledge_bases:query"]))
) -> JSONResponse:
    """
    查询知识库列表接口（数据库分页）
    
    参数:
    - page: PaginationQueryParam - 分页参数
    - search: AgKnowledgeBaseQueryParam - 查询参数
    - auth: AuthSchema - 认证信息
    
    返回:
    - JSONResponse - 包含知识库列表的JSON响应
    """
    result_dict = await AgKnowledgeBaseService.page_knowledge_bases_service(
        auth=auth,
        page_no=page.page_no if page.page_no is not None else 1,
        page_size=page.page_size if page.page_size is not None else 10,
        search=search,
        order_by=page.order_by
    )
    log.info("查询知识库列表成功")
    return SuccessResponse(data=result_dict, msg="查询知识库列表成功")


@AgKnowledgeBaseRouter.post(
    "/create",
    summary="创建知识库",
    description="创建知识库"
)
async def create_knowledge_bases_controller(
    data: AgKnowledgeBaseCreateSchema,
    auth: AuthSchema = Depends(AuthPermission(["module_agno_manage:knowledge_bases:create"]))
) -> JSONResponse:
    """
    创建知识库接口
    
    参数:
    - data: AgKnowledgeBaseCreateSchema - 创建数据
    - auth: AuthSchema - 认证信息
    
    返回:
    - JSONResponse - 包含创建知识库结果的JSON响应
    """
    result_dict = await AgKnowledgeBaseService.create_knowledge_bases_service(auth=auth, data=data)
    log.info("创建知识库成功")
    return SuccessResponse(data=result_dict, msg="创建知识库成功")


@AgKnowledgeBaseRouter.put(
    "/update/{id}",
    summary="修改知识库",
    description="修改知识库"
)
async def update_knowledge_bases_controller(
    data: AgKnowledgeBaseUpdateSchema,
    id: int = Path(..., description="ID"),
    auth: AuthSchema = Depends(AuthPermission(["module_agno_manage:knowledge_bases:update"]))
) -> JSONResponse:
    """
    修改知识库接口
    
    参数:
    - id: int - 数据ID
    - data: AgKnowledgeBaseUpdateSchema - 更新数据
    - auth: AuthSchema - 认证信息
    
    返回:
    - JSONResponse - 包含修改知识库结果的JSON响应
    """
    result_dict = await AgKnowledgeBaseService.update_knowledge_bases_service(auth=auth, id=id, data=data)
    log.info("修改知识库成功")
    return SuccessResponse(data=result_dict, msg="修改知识库成功")


@AgKnowledgeBaseRouter.delete(
    "/delete",
    summary="删除知识库",
    description="删除知识库"
)
async def delete_knowledge_bases_controller(
    ids: list[int] = Body(..., description="ID列表"),
    auth: AuthSchema = Depends(AuthPermission(["module_agno_manage:knowledge_bases:delete"]))
) -> JSONResponse:
    """
    删除知识库接口
    
    参数:
    - ids: list[int] - 数据ID列表
    - auth: AuthSchema - 认证信息
    
    返回:
    - JSONResponse - 包含删除知识库结果的JSON响应
    """
    await AgKnowledgeBaseService.delete_knowledge_bases_service(auth=auth, ids=ids)
    log.info(f"删除知识库成功: {ids}")
    return SuccessResponse(msg="删除知识库成功")


@AgKnowledgeBaseRouter.patch(
    "/available/setting",
    summary="批量修改知识库状态",
    description="批量修改知识库状态"
)
async def batch_set_available_knowledge_bases_controller(
    data: BatchSetAvailable,
    auth: AuthSchema = Depends(AuthPermission(["module_agno_manage:knowledge_bases:patch"]))
) -> JSONResponse:
    """
    批量修改知识库状态接口
    
    参数:
    - data: BatchSetAvailable - 批量修改状态数据
    - auth: AuthSchema - 认证信息
    
    返回:
    - JSONResponse - 包含批量修改知识库状态结果的JSON响应
    """
    await AgKnowledgeBaseService.set_available_knowledge_bases_service(auth=auth, data=data)
    log.info(f"批量修改知识库状态成功: {data.ids}")
    return SuccessResponse(msg="批量修改知识库状态成功")


@AgKnowledgeBaseRouter.post(
    '/export',
    summary="导出知识库",
    description="导出知识库"
)
async def export_knowledge_bases_list_controller(
    search: AgKnowledgeBaseQueryParam = Depends(),
    auth: AuthSchema = Depends(AuthPermission(["module_agno_manage:knowledge_bases:export"]))
) -> StreamingResponse:
    """
    导出知识库接口
    
    参数:
    - search: AgKnowledgeBaseQueryParam - 查询参数
    - auth: AuthSchema - 认证信息
    
    返回:
    - StreamingResponse - 包含导出知识库数据的流式响应
    """
    result_dict_list = await AgKnowledgeBaseService.list_knowledge_bases_service(search=search, auth=auth)
    export_result = await AgKnowledgeBaseService.batch_export_knowledge_bases_service(obj_list=result_dict_list)
    log.info('导出知识库成功')
    return StreamResponse(
        data=bytes2file_response(export_result),
        media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        headers={'Content-Disposition': 'attachment; filename=ag_knowledge_bases.xlsx'}
    )


@AgKnowledgeBaseRouter.post(
    '/import',
    summary="导入知识库",
    description="导入知识库"
)
async def import_knowledge_bases_list_controller(
    file: UploadFile,
    auth: AuthSchema = Depends(AuthPermission(["module_agno_manage:knowledge_bases:import"]))
) -> JSONResponse:
    """
    导入知识库接口
    
    参数:
    - file: UploadFile - 上传的Excel文件
    - auth: AuthSchema - 认证信息
    
    返回:
    - JSONResponse - 包含导入知识库结果的JSON响应
    """
    batch_import_result = await AgKnowledgeBaseService.batch_import_knowledge_bases_service(file=file, auth=auth, update_support=True)
    log.info("导入知识库成功")
    return SuccessResponse(data=batch_import_result, msg="导入知识库成功")


@AgKnowledgeBaseRouter.post(
    '/download/template',
    summary="获取知识库导入模板",
    description="获取知识库导入模板",
    dependencies=[Depends(AuthPermission(["module_agno_manage:knowledge_bases:download"]))]
)
async def export_knowledge_bases_template_controller() -> StreamingResponse:
    """
    获取知识库导入模板接口
    
    返回:
    - StreamingResponse - 包含知识库导入模板的流式响应
    """
    import_template_result = await AgKnowledgeBaseService.import_template_download_knowledge_bases_service()
    log.info('获取知识库导入模板成功')
    return StreamResponse(
        data=bytes2file_response(import_template_result),
        media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        headers={'Content-Disposition': 'attachment; filename=ag_knowledge_bases_template.xlsx'}
    )


