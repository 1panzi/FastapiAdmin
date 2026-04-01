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

from .service import AgAgentService
from .schema import AgAgentCreateSchema, AgAgentUpdateSchema, AgAgentQueryParam

AgAgentRouter = APIRouter(prefix='/agents', tags=["Agent管理模块"]) 

@AgAgentRouter.get(
    "/detail/{id}",
    summary="获取Agent管理详情",
    description="获取Agent管理详情"
)
async def get_agents_detail_controller(
    id: int = Path(..., description="ID"),
    auth: AuthSchema = Depends(AuthPermission(["module_agno_manage:agents:query"]))
) -> JSONResponse:
    """
    获取Agent管理详情接口
    
    参数:
    - id: int - 数据ID
    - auth: AuthSchema - 认证信息
    
    返回:
    - JSONResponse - 包含Agent管理详情的JSON响应
    """
    result_dict = await AgAgentService.detail_agents_service(auth=auth, id=id)
    log.info(f"获取Agent管理详情成功 {id}")
    return SuccessResponse(data=result_dict, msg="获取Agent管理详情成功")

@AgAgentRouter.get(
    "/list",
    summary="查询Agent管理列表",
    description="查询Agent管理列表"
)
async def get_agents_list_controller(
    page: PaginationQueryParam = Depends(),
    search: AgAgentQueryParam = Depends(),
    auth: AuthSchema = Depends(AuthPermission(["module_agno_manage:agents:query"]))
) -> JSONResponse:
    """
    查询Agent管理列表接口（数据库分页）
    
    参数:
    - page: PaginationQueryParam - 分页参数
    - search: AgAgentQueryParam - 查询参数
    - auth: AuthSchema - 认证信息
    
    返回:
    - JSONResponse - 包含Agent管理列表的JSON响应
    """
    result_dict = await AgAgentService.page_agents_service(
        auth=auth,
        page_no=page.page_no if page.page_no is not None else 1,
        page_size=page.page_size if page.page_size is not None else 10,
        search=search,
        order_by=page.order_by
    )
    log.info("查询Agent管理列表成功")
    return SuccessResponse(data=result_dict, msg="查询Agent管理列表成功")

@AgAgentRouter.post(
    "/create",
    summary="创建Agent管理",
    description="创建Agent管理"
)
async def create_agents_controller(
    data: AgAgentCreateSchema,
    auth: AuthSchema = Depends(AuthPermission(["module_agno_manage:agents:create"]))
) -> JSONResponse:
    """
    创建Agent管理接口
    
    参数:
    - data: AgAgentCreateSchema - 创建数据
    - auth: AuthSchema - 认证信息
    
    返回:
    - JSONResponse - 包含创建Agent管理结果的JSON响应
    """
    result_dict = await AgAgentService.create_agents_service(auth=auth, data=data)
    log.info("创建Agent管理成功")
    return SuccessResponse(data=result_dict, msg="创建Agent管理成功")

@AgAgentRouter.put(
    "/update/{id}",
    summary="修改Agent管理",
    description="修改Agent管理"
)
async def update_agents_controller(
    data: AgAgentUpdateSchema,
    id: int = Path(..., description="ID"),
    auth: AuthSchema = Depends(AuthPermission(["module_agno_manage:agents:update"]))
) -> JSONResponse:
    """
    修改Agent管理接口
    
    参数:
    - id: int - 数据ID
    - data: AgAgentUpdateSchema - 更新数据
    - auth: AuthSchema - 认证信息
    
    返回:
    - JSONResponse - 包含修改Agent管理结果的JSON响应
    """
    result_dict = await AgAgentService.update_agents_service(auth=auth, id=id, data=data)
    log.info("修改Agent管理成功")
    return SuccessResponse(data=result_dict, msg="修改Agent管理成功")

@AgAgentRouter.delete(
    "/delete",
    summary="删除Agent管理",
    description="删除Agent管理"
)
async def delete_agents_controller(
    ids: list[int] = Body(..., description="ID列表"),
    auth: AuthSchema = Depends(AuthPermission(["module_agno_manage:agents:delete"]))
) -> JSONResponse:
    """
    删除Agent管理接口
    
    参数:
    - ids: list[int] - 数据ID列表
    - auth: AuthSchema - 认证信息
    
    返回:
    - JSONResponse - 包含删除Agent管理结果的JSON响应
    """
    await AgAgentService.delete_agents_service(auth=auth, ids=ids)
    log.info(f"删除Agent管理成功: {ids}")
    return SuccessResponse(msg="删除Agent管理成功")

@AgAgentRouter.patch(
    "/available/setting",
    summary="批量修改Agent管理状态",
    description="批量修改Agent管理状态"
)
async def batch_set_available_agents_controller(
    data: BatchSetAvailable,
    auth: AuthSchema = Depends(AuthPermission(["module_agno_manage:agents:patch"]))
) -> JSONResponse:
    """
    批量修改Agent管理状态接口
    
    参数:
    - data: BatchSetAvailable - 批量修改状态数据
    - auth: AuthSchema - 认证信息
    
    返回:
    - JSONResponse - 包含批量修改Agent管理状态结果的JSON响应
    """
    await AgAgentService.set_available_agents_service(auth=auth, data=data)
    log.info(f"批量修改Agent管理状态成功: {data.ids}")
    return SuccessResponse(msg="批量修改Agent管理状态成功")

@AgAgentRouter.post(
    '/export',
    summary="导出Agent管理",
    description="导出Agent管理"
)
async def export_agents_list_controller(
    search: AgAgentQueryParam = Depends(),
    auth: AuthSchema = Depends(AuthPermission(["module_agno_manage:agents:export"]))
) -> StreamingResponse:
    """
    导出Agent管理接口
    
    参数:
    - search: AgAgentQueryParam - 查询参数
    - auth: AuthSchema - 认证信息
    
    返回:
    - StreamingResponse - 包含导出Agent管理数据的流式响应
    """
    result_dict_list = await AgAgentService.list_agents_service(search=search, auth=auth)
    export_result = await AgAgentService.batch_export_agents_service(obj_list=result_dict_list)
    log.info('导出Agent管理成功')
    return StreamResponse(
        data=bytes2file_response(export_result),
        media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        headers={'Content-Disposition': 'attachment; filename=ag_agents.xlsx'}
    )

@AgAgentRouter.post(
    '/import',
    summary="导入Agent管理",
    description="导入Agent管理"
)
async def import_agents_list_controller(
    file: UploadFile,
    auth: AuthSchema = Depends(AuthPermission(["module_agno_manage:agents:import"]))
) -> JSONResponse:
    """
    导入Agent管理接口
    
    参数:
    - file: UploadFile - 上传的Excel文件
    - auth: AuthSchema - 认证信息
    
    返回:
    - JSONResponse - 包含导入Agent管理结果的JSON响应
    """
    batch_import_result = await AgAgentService.batch_import_agents_service(file=file, auth=auth, update_support=True)
    log.info("导入Agent管理成功")
    return SuccessResponse(data=batch_import_result, msg="导入Agent管理成功")

@AgAgentRouter.post(
    '/download/template',
    summary="获取Agent管理导入模板",
    description="获取Agent管理导入模板",
    dependencies=[Depends(AuthPermission(["module_agno_manage:agents:download"]))]
)
async def export_agents_template_controller() -> StreamingResponse:
    """
    获取Agent管理导入模板接口
    
    返回:
    - StreamingResponse - 包含Agent管理导入模板的流式响应
    """
    import_template_result = await AgAgentService.import_template_download_agents_service()
    log.info('获取Agent管理导入模板成功')
    return StreamResponse(
        data=bytes2file_response(import_template_result),
        media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        headers={'Content-Disposition': 'attachment; filename=ag_agents_template.xlsx'}
    )