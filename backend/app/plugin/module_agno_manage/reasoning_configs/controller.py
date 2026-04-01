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

from .service import AgReasoningConfigService
from .schema import AgReasoningConfigCreateSchema, AgReasoningConfigUpdateSchema, AgReasoningConfigQueryParam

AgReasoningConfigRouter = APIRouter(prefix='/reasoning_configs', tags=["推理配置模块"]) 

@AgReasoningConfigRouter.get(
    "/detail/{id}",
    summary="获取推理配置详情",
    description="获取推理配置详情"
)
async def get_reasoning_configs_detail_controller(
    id: int = Path(..., description="ID"),
    auth: AuthSchema = Depends(AuthPermission(["module_agno_manage:reasoning_configs:query"]))
) -> JSONResponse:
    """
    获取推理配置详情接口
    
    参数:
    - id: int - 数据ID
    - auth: AuthSchema - 认证信息
    
    返回:
    - JSONResponse - 包含推理配置详情的JSON响应
    """
    result_dict = await AgReasoningConfigService.detail_reasoning_configs_service(auth=auth, id=id)
    log.info(f"获取推理配置详情成功 {id}")
    return SuccessResponse(data=result_dict, msg="获取推理配置详情成功")

@AgReasoningConfigRouter.get(
    "/list",
    summary="查询推理配置列表",
    description="查询推理配置列表"
)
async def get_reasoning_configs_list_controller(
    page: PaginationQueryParam = Depends(),
    search: AgReasoningConfigQueryParam = Depends(),
    auth: AuthSchema = Depends(AuthPermission(["module_agno_manage:reasoning_configs:query"]))
) -> JSONResponse:
    """
    查询推理配置列表接口（数据库分页）
    
    参数:
    - page: PaginationQueryParam - 分页参数
    - search: AgReasoningConfigQueryParam - 查询参数
    - auth: AuthSchema - 认证信息
    
    返回:
    - JSONResponse - 包含推理配置列表的JSON响应
    """
    result_dict = await AgReasoningConfigService.page_reasoning_configs_service(
        auth=auth,
        page_no=page.page_no if page.page_no is not None else 1,
        page_size=page.page_size if page.page_size is not None else 10,
        search=search,
        order_by=page.order_by
    )
    log.info("查询推理配置列表成功")
    return SuccessResponse(data=result_dict, msg="查询推理配置列表成功")

@AgReasoningConfigRouter.post(
    "/create",
    summary="创建推理配置",
    description="创建推理配置"
)
async def create_reasoning_configs_controller(
    data: AgReasoningConfigCreateSchema,
    auth: AuthSchema = Depends(AuthPermission(["module_agno_manage:reasoning_configs:create"]))
) -> JSONResponse:
    """
    创建推理配置接口
    
    参数:
    - data: AgReasoningConfigCreateSchema - 创建数据
    - auth: AuthSchema - 认证信息
    
    返回:
    - JSONResponse - 包含创建推理配置结果的JSON响应
    """
    result_dict = await AgReasoningConfigService.create_reasoning_configs_service(auth=auth, data=data)
    log.info("创建推理配置成功")
    return SuccessResponse(data=result_dict, msg="创建推理配置成功")

@AgReasoningConfigRouter.put(
    "/update/{id}",
    summary="修改推理配置",
    description="修改推理配置"
)
async def update_reasoning_configs_controller(
    data: AgReasoningConfigUpdateSchema,
    id: int = Path(..., description="ID"),
    auth: AuthSchema = Depends(AuthPermission(["module_agno_manage:reasoning_configs:update"]))
) -> JSONResponse:
    """
    修改推理配置接口
    
    参数:
    - id: int - 数据ID
    - data: AgReasoningConfigUpdateSchema - 更新数据
    - auth: AuthSchema - 认证信息
    
    返回:
    - JSONResponse - 包含修改推理配置结果的JSON响应
    """
    result_dict = await AgReasoningConfigService.update_reasoning_configs_service(auth=auth, id=id, data=data)
    log.info("修改推理配置成功")
    return SuccessResponse(data=result_dict, msg="修改推理配置成功")

@AgReasoningConfigRouter.delete(
    "/delete",
    summary="删除推理配置",
    description="删除推理配置"
)
async def delete_reasoning_configs_controller(
    ids: list[int] = Body(..., description="ID列表"),
    auth: AuthSchema = Depends(AuthPermission(["module_agno_manage:reasoning_configs:delete"]))
) -> JSONResponse:
    """
    删除推理配置接口
    
    参数:
    - ids: list[int] - 数据ID列表
    - auth: AuthSchema - 认证信息
    
    返回:
    - JSONResponse - 包含删除推理配置结果的JSON响应
    """
    await AgReasoningConfigService.delete_reasoning_configs_service(auth=auth, ids=ids)
    log.info(f"删除推理配置成功: {ids}")
    return SuccessResponse(msg="删除推理配置成功")

@AgReasoningConfigRouter.patch(
    "/available/setting",
    summary="批量修改推理配置状态",
    description="批量修改推理配置状态"
)
async def batch_set_available_reasoning_configs_controller(
    data: BatchSetAvailable,
    auth: AuthSchema = Depends(AuthPermission(["module_agno_manage:reasoning_configs:patch"]))
) -> JSONResponse:
    """
    批量修改推理配置状态接口
    
    参数:
    - data: BatchSetAvailable - 批量修改状态数据
    - auth: AuthSchema - 认证信息
    
    返回:
    - JSONResponse - 包含批量修改推理配置状态结果的JSON响应
    """
    await AgReasoningConfigService.set_available_reasoning_configs_service(auth=auth, data=data)
    log.info(f"批量修改推理配置状态成功: {data.ids}")
    return SuccessResponse(msg="批量修改推理配置状态成功")

@AgReasoningConfigRouter.post(
    '/export',
    summary="导出推理配置",
    description="导出推理配置"
)
async def export_reasoning_configs_list_controller(
    search: AgReasoningConfigQueryParam = Depends(),
    auth: AuthSchema = Depends(AuthPermission(["module_agno_manage:reasoning_configs:export"]))
) -> StreamingResponse:
    """
    导出推理配置接口
    
    参数:
    - search: AgReasoningConfigQueryParam - 查询参数
    - auth: AuthSchema - 认证信息
    
    返回:
    - StreamingResponse - 包含导出推理配置数据的流式响应
    """
    result_dict_list = await AgReasoningConfigService.list_reasoning_configs_service(search=search, auth=auth)
    export_result = await AgReasoningConfigService.batch_export_reasoning_configs_service(obj_list=result_dict_list)
    log.info('导出推理配置成功')
    return StreamResponse(
        data=bytes2file_response(export_result),
        media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        headers={'Content-Disposition': 'attachment; filename=ag_reasoning_configs.xlsx'}
    )

@AgReasoningConfigRouter.post(
    '/import',
    summary="导入推理配置",
    description="导入推理配置"
)
async def import_reasoning_configs_list_controller(
    file: UploadFile,
    auth: AuthSchema = Depends(AuthPermission(["module_agno_manage:reasoning_configs:import"]))
) -> JSONResponse:
    """
    导入推理配置接口
    
    参数:
    - file: UploadFile - 上传的Excel文件
    - auth: AuthSchema - 认证信息
    
    返回:
    - JSONResponse - 包含导入推理配置结果的JSON响应
    """
    batch_import_result = await AgReasoningConfigService.batch_import_reasoning_configs_service(file=file, auth=auth, update_support=True)
    log.info("导入推理配置成功")
    return SuccessResponse(data=batch_import_result, msg="导入推理配置成功")

@AgReasoningConfigRouter.post(
    '/download/template',
    summary="获取推理配置导入模板",
    description="获取推理配置导入模板",
    dependencies=[Depends(AuthPermission(["module_agno_manage:reasoning_configs:download"]))]
)
async def export_reasoning_configs_template_controller() -> StreamingResponse:
    """
    获取推理配置导入模板接口
    
    返回:
    - StreamingResponse - 包含推理配置导入模板的流式响应
    """
    import_template_result = await AgReasoningConfigService.import_template_download_reasoning_configs_service()
    log.info('获取推理配置导入模板成功')
    return StreamResponse(
        data=bytes2file_response(import_template_result),
        media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        headers={'Content-Disposition': 'attachment; filename=ag_reasoning_configs_template.xlsx'}
    )