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

from .service import ModelService
from .schema import ModelCreateSchema, ModelUpdateSchema, ModelQueryParam

ModelRouter = APIRouter(prefix='/models', tags=["模型管理模块"]) 

@ModelRouter.get(
    "/detail/{id}",
    summary="获取模型管理详情",
    description="获取模型管理详情"
)
async def get_models_detail_controller(
    id: int = Path(..., description="ID"),
    auth: AuthSchema = Depends(AuthPermission(["module_agno_manage:models:query"]))
) -> JSONResponse:
    """
    获取模型管理详情接口
    
    参数:
    - id: int - 数据ID
    - auth: AuthSchema - 认证信息
    
    返回:
    - JSONResponse - 包含模型管理详情的JSON响应
    """
    result_dict = await ModelService.detail_models_service(auth=auth, id=id)
    log.info(f"获取模型管理详情成功 {id}")
    return SuccessResponse(data=result_dict, msg="获取模型管理详情成功")

@ModelRouter.get(
    "/list",
    summary="查询模型管理列表",
    description="查询模型管理列表"
)
async def get_models_list_controller(
    page: PaginationQueryParam = Depends(),
    search: ModelQueryParam = Depends(),
    auth: AuthSchema = Depends(AuthPermission(["module_agno_manage:models:query"]))
) -> JSONResponse:
    """
    查询模型管理列表接口（数据库分页）
    
    参数:
    - page: PaginationQueryParam - 分页参数
    - search: ModelQueryParam - 查询参数
    - auth: AuthSchema - 认证信息
    
    返回:
    - JSONResponse - 包含模型管理列表的JSON响应
    """
    result_dict = await ModelService.page_models_service(
        auth=auth,
        page_no=page.page_no if page.page_no is not None else 1,
        page_size=page.page_size if page.page_size is not None else 10,
        search=search,
        order_by=page.order_by
    )
    log.info("查询模型管理列表成功")
    return SuccessResponse(data=result_dict, msg="查询模型管理列表成功")

@ModelRouter.post(
    "/create",
    summary="创建模型管理",
    description="创建模型管理"
)
async def create_models_controller(
    data: ModelCreateSchema,
    auth: AuthSchema = Depends(AuthPermission(["module_agno_manage:models:create"]))
) -> JSONResponse:
    """
    创建模型管理接口
    
    参数:
    - data: ModelCreateSchema - 创建数据
    - auth: AuthSchema - 认证信息
    
    返回:
    - JSONResponse - 包含创建模型管理结果的JSON响应
    """
    result_dict = await ModelService.create_models_service(auth=auth, data=data)
    log.info("创建模型管理成功")
    return SuccessResponse(data=result_dict, msg="创建模型管理成功")

@ModelRouter.put(
    "/update/{id}",
    summary="修改模型管理",
    description="修改模型管理"
)
async def update_models_controller(
    data: ModelUpdateSchema,
    id: int = Path(..., description="ID"),
    auth: AuthSchema = Depends(AuthPermission(["module_agno_manage:models:update"]))
) -> JSONResponse:
    """
    修改模型管理接口
    
    参数:
    - id: int - 数据ID
    - data: ModelUpdateSchema - 更新数据
    - auth: AuthSchema - 认证信息
    
    返回:
    - JSONResponse - 包含修改模型管理结果的JSON响应
    """
    result_dict = await ModelService.update_models_service(auth=auth, id=id, data=data)
    log.info("修改模型管理成功")
    return SuccessResponse(data=result_dict, msg="修改模型管理成功")

@ModelRouter.delete(
    "/delete",
    summary="删除模型管理",
    description="删除模型管理"
)
async def delete_models_controller(
    ids: list[int] = Body(..., description="ID列表"),
    auth: AuthSchema = Depends(AuthPermission(["module_agno_manage:models:delete"]))
) -> JSONResponse:
    """
    删除模型管理接口
    
    参数:
    - ids: list[int] - 数据ID列表
    - auth: AuthSchema - 认证信息
    
    返回:
    - JSONResponse - 包含删除模型管理结果的JSON响应
    """
    await ModelService.delete_models_service(auth=auth, ids=ids)
    log.info(f"删除模型管理成功: {ids}")
    return SuccessResponse(msg="删除模型管理成功")

@ModelRouter.patch(
    "/available/setting",
    summary="批量修改模型管理状态",
    description="批量修改模型管理状态"
)
async def batch_set_available_models_controller(
    data: BatchSetAvailable,
    auth: AuthSchema = Depends(AuthPermission(["module_agno_manage:models:patch"]))
) -> JSONResponse:
    """
    批量修改模型管理状态接口
    
    参数:
    - data: BatchSetAvailable - 批量修改状态数据
    - auth: AuthSchema - 认证信息
    
    返回:
    - JSONResponse - 包含批量修改模型管理状态结果的JSON响应
    """
    await ModelService.set_available_models_service(auth=auth, data=data)
    log.info(f"批量修改模型管理状态成功: {data.ids}")
    return SuccessResponse(msg="批量修改模型管理状态成功")

@ModelRouter.post(
    '/export',
    summary="导出模型管理",
    description="导出模型管理"
)
async def export_models_list_controller(
    search: ModelQueryParam = Depends(),
    auth: AuthSchema = Depends(AuthPermission(["module_agno_manage:models:export"]))
) -> StreamingResponse:
    """
    导出模型管理接口
    
    参数:
    - search: ModelQueryParam - 查询参数
    - auth: AuthSchema - 认证信息
    
    返回:
    - StreamingResponse - 包含导出模型管理数据的流式响应
    """
    result_dict_list = await ModelService.list_models_service(search=search, auth=auth)
    export_result = await ModelService.batch_export_models_service(obj_list=result_dict_list)
    log.info('导出模型管理成功')
    return StreamResponse(
        data=bytes2file_response(export_result),
        media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        headers={'Content-Disposition': 'attachment; filename=ag_models.xlsx'}
    )

@ModelRouter.post(
    '/import',
    summary="导入模型管理",
    description="导入模型管理"
)
async def import_models_list_controller(
    file: UploadFile,
    auth: AuthSchema = Depends(AuthPermission(["module_agno_manage:models:import"]))
) -> JSONResponse:
    """
    导入模型管理接口
    
    参数:
    - file: UploadFile - 上传的Excel文件
    - auth: AuthSchema - 认证信息
    
    返回:
    - JSONResponse - 包含导入模型管理结果的JSON响应
    """
    batch_import_result = await ModelService.batch_import_models_service(file=file, auth=auth, update_support=True)
    log.info("导入模型管理成功")
    return SuccessResponse(data=batch_import_result, msg="导入模型管理成功")

@ModelRouter.post(
    '/download/template',
    summary="获取模型管理导入模板",
    description="获取模型管理导入模板",
    dependencies=[Depends(AuthPermission(["module_agno_manage:models:download"]))]
)
async def export_models_template_controller() -> StreamingResponse:
    """
    获取模型管理导入模板接口
    
    返回:
    - StreamingResponse - 包含模型管理导入模板的流式响应
    """
    import_template_result = await ModelService.import_template_download_models_service()
    log.info('获取模型管理导入模板成功')
    return StreamResponse(
        data=bytes2file_response(import_template_result),
        media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        headers={'Content-Disposition': 'attachment; filename=ag_models_template.xlsx'}
    )