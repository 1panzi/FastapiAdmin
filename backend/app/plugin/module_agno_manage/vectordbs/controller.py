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

from .service import AgVectordbService
from .schema import AgVectordbCreateSchema, AgVectordbUpdateSchema, AgVectordbQueryParam

AgVectordbRouter = APIRouter(prefix='/vectordbs', tags=["向量数据库模块"]) 

@AgVectordbRouter.get(
    "/detail/{id}",
    summary="获取向量数据库详情",
    description="获取向量数据库详情"
)
async def get_vectordbs_detail_controller(
    id: int = Path(..., description="ID"),
    auth: AuthSchema = Depends(AuthPermission(["module_agno_manage:vectordbs:query"]))
) -> JSONResponse:
    """
    获取向量数据库详情接口
    
    参数:
    - id: int - 数据ID
    - auth: AuthSchema - 认证信息
    
    返回:
    - JSONResponse - 包含向量数据库详情的JSON响应
    """
    result_dict = await AgVectordbService.detail_vectordbs_service(auth=auth, id=id)
    log.info(f"获取向量数据库详情成功 {id}")
    return SuccessResponse(data=result_dict, msg="获取向量数据库详情成功")

@AgVectordbRouter.get(
    "/list",
    summary="查询向量数据库列表",
    description="查询向量数据库列表"
)
async def get_vectordbs_list_controller(
    page: PaginationQueryParam = Depends(),
    search: AgVectordbQueryParam = Depends(),
    auth: AuthSchema = Depends(AuthPermission(["module_agno_manage:vectordbs:query"]))
) -> JSONResponse:
    """
    查询向量数据库列表接口（数据库分页）
    
    参数:
    - page: PaginationQueryParam - 分页参数
    - search: AgVectordbQueryParam - 查询参数
    - auth: AuthSchema - 认证信息
    
    返回:
    - JSONResponse - 包含向量数据库列表的JSON响应
    """
    result_dict = await AgVectordbService.page_vectordbs_service(
        auth=auth,
        page_no=page.page_no if page.page_no is not None else 1,
        page_size=page.page_size if page.page_size is not None else 10,
        search=search,
        order_by=page.order_by
    )
    log.info("查询向量数据库列表成功")
    return SuccessResponse(data=result_dict, msg="查询向量数据库列表成功")

@AgVectordbRouter.post(
    "/create",
    summary="创建向量数据库",
    description="创建向量数据库"
)
async def create_vectordbs_controller(
    data: AgVectordbCreateSchema,
    auth: AuthSchema = Depends(AuthPermission(["module_agno_manage:vectordbs:create"]))
) -> JSONResponse:
    """
    创建向量数据库接口
    
    参数:
    - data: AgVectordbCreateSchema - 创建数据
    - auth: AuthSchema - 认证信息
    
    返回:
    - JSONResponse - 包含创建向量数据库结果的JSON响应
    """
    result_dict = await AgVectordbService.create_vectordbs_service(auth=auth, data=data)
    log.info("创建向量数据库成功")
    return SuccessResponse(data=result_dict, msg="创建向量数据库成功")

@AgVectordbRouter.put(
    "/update/{id}",
    summary="修改向量数据库",
    description="修改向量数据库"
)
async def update_vectordbs_controller(
    data: AgVectordbUpdateSchema,
    id: int = Path(..., description="ID"),
    auth: AuthSchema = Depends(AuthPermission(["module_agno_manage:vectordbs:update"]))
) -> JSONResponse:
    """
    修改向量数据库接口
    
    参数:
    - id: int - 数据ID
    - data: AgVectordbUpdateSchema - 更新数据
    - auth: AuthSchema - 认证信息
    
    返回:
    - JSONResponse - 包含修改向量数据库结果的JSON响应
    """
    result_dict = await AgVectordbService.update_vectordbs_service(auth=auth, id=id, data=data)
    log.info("修改向量数据库成功")
    return SuccessResponse(data=result_dict, msg="修改向量数据库成功")

@AgVectordbRouter.delete(
    "/delete",
    summary="删除向量数据库",
    description="删除向量数据库"
)
async def delete_vectordbs_controller(
    ids: list[int] = Body(..., description="ID列表"),
    auth: AuthSchema = Depends(AuthPermission(["module_agno_manage:vectordbs:delete"]))
) -> JSONResponse:
    """
    删除向量数据库接口
    
    参数:
    - ids: list[int] - 数据ID列表
    - auth: AuthSchema - 认证信息
    
    返回:
    - JSONResponse - 包含删除向量数据库结果的JSON响应
    """
    await AgVectordbService.delete_vectordbs_service(auth=auth, ids=ids)
    log.info(f"删除向量数据库成功: {ids}")
    return SuccessResponse(msg="删除向量数据库成功")

@AgVectordbRouter.patch(
    "/available/setting",
    summary="批量修改向量数据库状态",
    description="批量修改向量数据库状态"
)
async def batch_set_available_vectordbs_controller(
    data: BatchSetAvailable,
    auth: AuthSchema = Depends(AuthPermission(["module_agno_manage:vectordbs:patch"]))
) -> JSONResponse:
    """
    批量修改向量数据库状态接口
    
    参数:
    - data: BatchSetAvailable - 批量修改状态数据
    - auth: AuthSchema - 认证信息
    
    返回:
    - JSONResponse - 包含批量修改向量数据库状态结果的JSON响应
    """
    await AgVectordbService.set_available_vectordbs_service(auth=auth, data=data)
    log.info(f"批量修改向量数据库状态成功: {data.ids}")
    return SuccessResponse(msg="批量修改向量数据库状态成功")

@AgVectordbRouter.post(
    '/export',
    summary="导出向量数据库",
    description="导出向量数据库"
)
async def export_vectordbs_list_controller(
    search: AgVectordbQueryParam = Depends(),
    auth: AuthSchema = Depends(AuthPermission(["module_agno_manage:vectordbs:export"]))
) -> StreamingResponse:
    """
    导出向量数据库接口
    
    参数:
    - search: AgVectordbQueryParam - 查询参数
    - auth: AuthSchema - 认证信息
    
    返回:
    - StreamingResponse - 包含导出向量数据库数据的流式响应
    """
    result_dict_list = await AgVectordbService.list_vectordbs_service(search=search, auth=auth)
    export_result = await AgVectordbService.batch_export_vectordbs_service(obj_list=result_dict_list)
    log.info('导出向量数据库成功')
    return StreamResponse(
        data=bytes2file_response(export_result),
        media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        headers={'Content-Disposition': 'attachment; filename=ag_vectordbs.xlsx'}
    )

@AgVectordbRouter.post(
    '/import',
    summary="导入向量数据库",
    description="导入向量数据库"
)
async def import_vectordbs_list_controller(
    file: UploadFile,
    auth: AuthSchema = Depends(AuthPermission(["module_agno_manage:vectordbs:import"]))
) -> JSONResponse:
    """
    导入向量数据库接口
    
    参数:
    - file: UploadFile - 上传的Excel文件
    - auth: AuthSchema - 认证信息
    
    返回:
    - JSONResponse - 包含导入向量数据库结果的JSON响应
    """
    batch_import_result = await AgVectordbService.batch_import_vectordbs_service(file=file, auth=auth, update_support=True)
    log.info("导入向量数据库成功")
    return SuccessResponse(data=batch_import_result, msg="导入向量数据库成功")

@AgVectordbRouter.post(
    '/download/template',
    summary="获取向量数据库导入模板",
    description="获取向量数据库导入模板",
    dependencies=[Depends(AuthPermission(["module_agno_manage:vectordbs:download"]))]
)
async def export_vectordbs_template_controller() -> StreamingResponse:
    """
    获取向量数据库导入模板接口
    
    返回:
    - StreamingResponse - 包含向量数据库导入模板的流式响应
    """
    import_template_result = await AgVectordbService.import_template_download_vectordbs_service()
    log.info('获取向量数据库导入模板成功')
    return StreamResponse(
        data=bytes2file_response(import_template_result),
        media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        headers={'Content-Disposition': 'attachment; filename=ag_vectordbs_template.xlsx'}
    )