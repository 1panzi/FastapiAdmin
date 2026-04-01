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

from .service import AgIntegrationService
from .schema import AgIntegrationCreateSchema, AgIntegrationUpdateSchema, AgIntegrationQueryParam

AgIntegrationRouter = APIRouter(prefix='/integrations', tags=["渠道集成管理模块"]) 

@AgIntegrationRouter.get(
    "/detail/{id}",
    summary="获取渠道集成管理详情",
    description="获取渠道集成管理详情"
)
async def get_integrations_detail_controller(
    id: int = Path(..., description="ID"),
    auth: AuthSchema = Depends(AuthPermission(["module_agno_manage:integrations:query"]))
) -> JSONResponse:
    """
    获取渠道集成管理详情接口
    
    参数:
    - id: int - 数据ID
    - auth: AuthSchema - 认证信息
    
    返回:
    - JSONResponse - 包含渠道集成管理详情的JSON响应
    """
    result_dict = await AgIntegrationService.detail_integrations_service(auth=auth, id=id)
    log.info(f"获取渠道集成管理详情成功 {id}")
    return SuccessResponse(data=result_dict, msg="获取渠道集成管理详情成功")

@AgIntegrationRouter.get(
    "/list",
    summary="查询渠道集成管理列表",
    description="查询渠道集成管理列表"
)
async def get_integrations_list_controller(
    page: PaginationQueryParam = Depends(),
    search: AgIntegrationQueryParam = Depends(),
    auth: AuthSchema = Depends(AuthPermission(["module_agno_manage:integrations:query"]))
) -> JSONResponse:
    """
    查询渠道集成管理列表接口（数据库分页）
    
    参数:
    - page: PaginationQueryParam - 分页参数
    - search: AgIntegrationQueryParam - 查询参数
    - auth: AuthSchema - 认证信息
    
    返回:
    - JSONResponse - 包含渠道集成管理列表的JSON响应
    """
    result_dict = await AgIntegrationService.page_integrations_service(
        auth=auth,
        page_no=page.page_no if page.page_no is not None else 1,
        page_size=page.page_size if page.page_size is not None else 10,
        search=search,
        order_by=page.order_by
    )
    log.info("查询渠道集成管理列表成功")
    return SuccessResponse(data=result_dict, msg="查询渠道集成管理列表成功")

@AgIntegrationRouter.post(
    "/create",
    summary="创建渠道集成管理",
    description="创建渠道集成管理"
)
async def create_integrations_controller(
    data: AgIntegrationCreateSchema,
    auth: AuthSchema = Depends(AuthPermission(["module_agno_manage:integrations:create"]))
) -> JSONResponse:
    """
    创建渠道集成管理接口
    
    参数:
    - data: AgIntegrationCreateSchema - 创建数据
    - auth: AuthSchema - 认证信息
    
    返回:
    - JSONResponse - 包含创建渠道集成管理结果的JSON响应
    """
    result_dict = await AgIntegrationService.create_integrations_service(auth=auth, data=data)
    log.info("创建渠道集成管理成功")
    return SuccessResponse(data=result_dict, msg="创建渠道集成管理成功")

@AgIntegrationRouter.put(
    "/update/{id}",
    summary="修改渠道集成管理",
    description="修改渠道集成管理"
)
async def update_integrations_controller(
    data: AgIntegrationUpdateSchema,
    id: int = Path(..., description="ID"),
    auth: AuthSchema = Depends(AuthPermission(["module_agno_manage:integrations:update"]))
) -> JSONResponse:
    """
    修改渠道集成管理接口
    
    参数:
    - id: int - 数据ID
    - data: AgIntegrationUpdateSchema - 更新数据
    - auth: AuthSchema - 认证信息
    
    返回:
    - JSONResponse - 包含修改渠道集成管理结果的JSON响应
    """
    result_dict = await AgIntegrationService.update_integrations_service(auth=auth, id=id, data=data)
    log.info("修改渠道集成管理成功")
    return SuccessResponse(data=result_dict, msg="修改渠道集成管理成功")

@AgIntegrationRouter.delete(
    "/delete",
    summary="删除渠道集成管理",
    description="删除渠道集成管理"
)
async def delete_integrations_controller(
    ids: list[int] = Body(..., description="ID列表"),
    auth: AuthSchema = Depends(AuthPermission(["module_agno_manage:integrations:delete"]))
) -> JSONResponse:
    """
    删除渠道集成管理接口
    
    参数:
    - ids: list[int] - 数据ID列表
    - auth: AuthSchema - 认证信息
    
    返回:
    - JSONResponse - 包含删除渠道集成管理结果的JSON响应
    """
    await AgIntegrationService.delete_integrations_service(auth=auth, ids=ids)
    log.info(f"删除渠道集成管理成功: {ids}")
    return SuccessResponse(msg="删除渠道集成管理成功")

@AgIntegrationRouter.patch(
    "/available/setting",
    summary="批量修改渠道集成管理状态",
    description="批量修改渠道集成管理状态"
)
async def batch_set_available_integrations_controller(
    data: BatchSetAvailable,
    auth: AuthSchema = Depends(AuthPermission(["module_agno_manage:integrations:patch"]))
) -> JSONResponse:
    """
    批量修改渠道集成管理状态接口
    
    参数:
    - data: BatchSetAvailable - 批量修改状态数据
    - auth: AuthSchema - 认证信息
    
    返回:
    - JSONResponse - 包含批量修改渠道集成管理状态结果的JSON响应
    """
    await AgIntegrationService.set_available_integrations_service(auth=auth, data=data)
    log.info(f"批量修改渠道集成管理状态成功: {data.ids}")
    return SuccessResponse(msg="批量修改渠道集成管理状态成功")

@AgIntegrationRouter.post(
    '/export',
    summary="导出渠道集成管理",
    description="导出渠道集成管理"
)
async def export_integrations_list_controller(
    search: AgIntegrationQueryParam = Depends(),
    auth: AuthSchema = Depends(AuthPermission(["module_agno_manage:integrations:export"]))
) -> StreamingResponse:
    """
    导出渠道集成管理接口
    
    参数:
    - search: AgIntegrationQueryParam - 查询参数
    - auth: AuthSchema - 认证信息
    
    返回:
    - StreamingResponse - 包含导出渠道集成管理数据的流式响应
    """
    result_dict_list = await AgIntegrationService.list_integrations_service(search=search, auth=auth)
    export_result = await AgIntegrationService.batch_export_integrations_service(obj_list=result_dict_list)
    log.info('导出渠道集成管理成功')
    return StreamResponse(
        data=bytes2file_response(export_result),
        media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        headers={'Content-Disposition': 'attachment; filename=ag_integrations.xlsx'}
    )

@AgIntegrationRouter.post(
    '/import',
    summary="导入渠道集成管理",
    description="导入渠道集成管理"
)
async def import_integrations_list_controller(
    file: UploadFile,
    auth: AuthSchema = Depends(AuthPermission(["module_agno_manage:integrations:import"]))
) -> JSONResponse:
    """
    导入渠道集成管理接口
    
    参数:
    - file: UploadFile - 上传的Excel文件
    - auth: AuthSchema - 认证信息
    
    返回:
    - JSONResponse - 包含导入渠道集成管理结果的JSON响应
    """
    batch_import_result = await AgIntegrationService.batch_import_integrations_service(file=file, auth=auth, update_support=True)
    log.info("导入渠道集成管理成功")
    return SuccessResponse(data=batch_import_result, msg="导入渠道集成管理成功")

@AgIntegrationRouter.post(
    '/download/template',
    summary="获取渠道集成管理导入模板",
    description="获取渠道集成管理导入模板",
    dependencies=[Depends(AuthPermission(["module_agno_manage:integrations:download"]))]
)
async def export_integrations_template_controller() -> StreamingResponse:
    """
    获取渠道集成管理导入模板接口
    
    返回:
    - StreamingResponse - 包含渠道集成管理导入模板的流式响应
    """
    import_template_result = await AgIntegrationService.import_template_download_integrations_service()
    log.info('获取渠道集成管理导入模板成功')
    return StreamResponse(
        data=bytes2file_response(import_template_result),
        media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        headers={'Content-Disposition': 'attachment; filename=ag_integrations_template.xlsx'}
    )