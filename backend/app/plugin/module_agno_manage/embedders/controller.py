# -*- coding: utf-8 -*-

from fastapi import APIRouter, Depends, UploadFile, Body, Path, Query
from fastapi.responses import StreamingResponse, JSONResponse

from app.common.response import SuccessResponse, StreamResponse
from app.core.dependencies import AuthPermission
from app.api.v1.module_system.auth.schema import AuthSchema
from app.core.base_params import PaginationQueryParam
from app.utils.common_util import bytes2file_response
from app.core.logger import log
from app.core.base_schema import BatchSetAvailable

from .service import AgEmbedderService
from .schema import AgEmbedderCreateSchema, AgEmbedderUpdateSchema, AgEmbedderQueryParam

AgEmbedderRouter = APIRouter(prefix='/embedders', tags=["嵌入模型模块"]) 

@AgEmbedderRouter.get(
    "/detail/{id}",
    summary="获取嵌入模型详情",
    description="获取嵌入模型详情"
)
async def get_embedders_detail_controller(
    id: int = Path(..., description="ID"),
    auth: AuthSchema = Depends(AuthPermission(["module_agno_manage:embedders:query"]))
) -> JSONResponse:
    """
    获取嵌入模型详情接口
    
    参数:
    - id: int - 数据ID
    - auth: AuthSchema - 认证信息
    
    返回:
    - JSONResponse - 包含嵌入模型详情的JSON响应
    """
    result_dict = await AgEmbedderService.detail_embedders_service(auth=auth, id=id)
    log.info(f"获取嵌入模型详情成功 {id}")
    return SuccessResponse(data=result_dict, msg="获取嵌入模型详情成功")

@AgEmbedderRouter.get(
    "/list",
    summary="查询嵌入模型列表",
    description="查询嵌入模型列表"
)
async def get_embedders_list_controller(
    page: PaginationQueryParam = Depends(),
    search: AgEmbedderQueryParam = Depends(),
    auth: AuthSchema = Depends(AuthPermission(["module_agno_manage:embedders:query"]))
) -> JSONResponse:
    """
    查询嵌入模型列表接口（数据库分页）
    
    参数:
    - page: PaginationQueryParam - 分页参数
    - search: AgEmbedderQueryParam - 查询参数
    - auth: AuthSchema - 认证信息
    
    返回:
    - JSONResponse - 包含嵌入模型列表的JSON响应
    """
    result_dict = await AgEmbedderService.page_embedders_service(
        auth=auth,
        page_no=page.page_no if page.page_no is not None else 1,
        page_size=page.page_size if page.page_size is not None else 10,
        search=search,
        order_by=page.order_by
    )
    log.info("查询嵌入模型列表成功")
    return SuccessResponse(data=result_dict, msg="查询嵌入模型列表成功")

@AgEmbedderRouter.post(
    "/create",
    summary="创建嵌入模型",
    description="创建嵌入模型"
)
async def create_embedders_controller(
    data: AgEmbedderCreateSchema,
    auth: AuthSchema = Depends(AuthPermission(["module_agno_manage:embedders:create"]))
) -> JSONResponse:
    """
    创建嵌入模型接口
    
    参数:
    - data: AgEmbedderCreateSchema - 创建数据
    - auth: AuthSchema - 认证信息
    
    返回:
    - JSONResponse - 包含创建嵌入模型结果的JSON响应
    """
    result_dict = await AgEmbedderService.create_embedders_service(auth=auth, data=data)
    log.info("创建嵌入模型成功")
    return SuccessResponse(data=result_dict, msg="创建嵌入模型成功")

@AgEmbedderRouter.put(
    "/update/{id}",
    summary="修改嵌入模型",
    description="修改嵌入模型"
)
async def update_embedders_controller(
    data: AgEmbedderUpdateSchema,
    id: int = Path(..., description="ID"),
    auth: AuthSchema = Depends(AuthPermission(["module_agno_manage:embedders:update"]))
) -> JSONResponse:
    """
    修改嵌入模型接口
    
    参数:
    - id: int - 数据ID
    - data: AgEmbedderUpdateSchema - 更新数据
    - auth: AuthSchema - 认证信息
    
    返回:
    - JSONResponse - 包含修改嵌入模型结果的JSON响应
    """
    result_dict = await AgEmbedderService.update_embedders_service(auth=auth, id=id, data=data)
    log.info("修改嵌入模型成功")
    return SuccessResponse(data=result_dict, msg="修改嵌入模型成功")

@AgEmbedderRouter.delete(
    "/delete",
    summary="删除嵌入模型",
    description="删除嵌入模型"
)
async def delete_embedders_controller(
    ids: list[int] = Body(..., description="ID列表"),
    auth: AuthSchema = Depends(AuthPermission(["module_agno_manage:embedders:delete"]))
) -> JSONResponse:
    """
    删除嵌入模型接口
    
    参数:
    - ids: list[int] - 数据ID列表
    - auth: AuthSchema - 认证信息
    
    返回:
    - JSONResponse - 包含删除嵌入模型结果的JSON响应
    """
    await AgEmbedderService.delete_embedders_service(auth=auth, ids=ids)
    log.info(f"删除嵌入模型成功: {ids}")
    return SuccessResponse(msg="删除嵌入模型成功")

@AgEmbedderRouter.patch(
    "/available/setting",
    summary="批量修改嵌入模型状态",
    description="批量修改嵌入模型状态"
)
async def batch_set_available_embedders_controller(
    data: BatchSetAvailable,
    auth: AuthSchema = Depends(AuthPermission(["module_agno_manage:embedders:patch"]))
) -> JSONResponse:
    """
    批量修改嵌入模型状态接口
    
    参数:
    - data: BatchSetAvailable - 批量修改状态数据
    - auth: AuthSchema - 认证信息
    
    返回:
    - JSONResponse - 包含批量修改嵌入模型状态结果的JSON响应
    """
    await AgEmbedderService.set_available_embedders_service(auth=auth, data=data)
    log.info(f"批量修改嵌入模型状态成功: {data.ids}")
    return SuccessResponse(msg="批量修改嵌入模型状态成功")

@AgEmbedderRouter.post(
    '/export',
    summary="导出嵌入模型",
    description="导出嵌入模型"
)
async def export_embedders_list_controller(
    search: AgEmbedderQueryParam = Depends(),
    auth: AuthSchema = Depends(AuthPermission(["module_agno_manage:embedders:export"]))
) -> StreamingResponse:
    """
    导出嵌入模型接口
    
    参数:
    - search: AgEmbedderQueryParam - 查询参数
    - auth: AuthSchema - 认证信息
    
    返回:
    - StreamingResponse - 包含导出嵌入模型数据的流式响应
    """
    result_dict_list = await AgEmbedderService.list_embedders_service(search=search, auth=auth)
    export_result = await AgEmbedderService.batch_export_embedders_service(obj_list=result_dict_list)
    log.info('导出嵌入模型成功')
    return StreamResponse(
        data=bytes2file_response(export_result),
        media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        headers={'Content-Disposition': 'attachment; filename=ag_embedders.xlsx'}
    )

@AgEmbedderRouter.post(
    '/import',
    summary="导入嵌入模型",
    description="导入嵌入模型"
)
async def import_embedders_list_controller(
    file: UploadFile,
    auth: AuthSchema = Depends(AuthPermission(["module_agno_manage:embedders:import"]))
) -> JSONResponse:
    """
    导入嵌入模型接口
    
    参数:
    - file: UploadFile - 上传的Excel文件
    - auth: AuthSchema - 认证信息
    
    返回:
    - JSONResponse - 包含导入嵌入模型结果的JSON响应
    """
    batch_import_result = await AgEmbedderService.batch_import_embedders_service(file=file, auth=auth, update_support=True)
    log.info("导入嵌入模型成功")
    return SuccessResponse(data=batch_import_result, msg="导入嵌入模型成功")

@AgEmbedderRouter.post(
    '/download/template',
    summary="获取嵌入模型导入模板",
    description="获取嵌入模型导入模板",
    dependencies=[Depends(AuthPermission(["module_agno_manage:embedders:download"]))]
)
async def export_embedders_template_controller() -> StreamingResponse:
    """
    获取嵌入模型导入模板接口
    
    返回:
    - StreamingResponse - 包含嵌入模型导入模板的流式响应
    """
    import_template_result = await AgEmbedderService.import_template_download_embedders_service()
    log.info('获取嵌入模型导入模板成功')
    return StreamResponse(
        data=bytes2file_response(import_template_result),
        media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        headers={'Content-Disposition': 'attachment; filename=ag_embedders_template.xlsx'}
    )