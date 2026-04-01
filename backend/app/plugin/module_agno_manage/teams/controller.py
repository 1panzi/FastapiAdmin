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

from .service import AgTeamService
from .schema import AgTeamCreateSchema, AgTeamUpdateSchema, AgTeamQueryParam

AgTeamRouter = APIRouter(prefix='/teams', tags=["Team管理模块"]) 

@AgTeamRouter.get(
    "/detail/{id}",
    summary="获取Team管理详情",
    description="获取Team管理详情"
)
async def get_teams_detail_controller(
    id: int = Path(..., description="ID"),
    auth: AuthSchema = Depends(AuthPermission(["module_agno_manage:teams:query"]))
) -> JSONResponse:
    """
    获取Team管理详情接口
    
    参数:
    - id: int - 数据ID
    - auth: AuthSchema - 认证信息
    
    返回:
    - JSONResponse - 包含Team管理详情的JSON响应
    """
    result_dict = await AgTeamService.detail_teams_service(auth=auth, id=id)
    log.info(f"获取Team管理详情成功 {id}")
    return SuccessResponse(data=result_dict, msg="获取Team管理详情成功")

@AgTeamRouter.get(
    "/list",
    summary="查询Team管理列表",
    description="查询Team管理列表"
)
async def get_teams_list_controller(
    page: PaginationQueryParam = Depends(),
    search: AgTeamQueryParam = Depends(),
    auth: AuthSchema = Depends(AuthPermission(["module_agno_manage:teams:query"]))
) -> JSONResponse:
    """
    查询Team管理列表接口（数据库分页）
    
    参数:
    - page: PaginationQueryParam - 分页参数
    - search: AgTeamQueryParam - 查询参数
    - auth: AuthSchema - 认证信息
    
    返回:
    - JSONResponse - 包含Team管理列表的JSON响应
    """
    result_dict = await AgTeamService.page_teams_service(
        auth=auth,
        page_no=page.page_no if page.page_no is not None else 1,
        page_size=page.page_size if page.page_size is not None else 10,
        search=search,
        order_by=page.order_by
    )
    log.info("查询Team管理列表成功")
    return SuccessResponse(data=result_dict, msg="查询Team管理列表成功")

@AgTeamRouter.post(
    "/create",
    summary="创建Team管理",
    description="创建Team管理"
)
async def create_teams_controller(
    data: AgTeamCreateSchema,
    auth: AuthSchema = Depends(AuthPermission(["module_agno_manage:teams:create"]))
) -> JSONResponse:
    """
    创建Team管理接口
    
    参数:
    - data: AgTeamCreateSchema - 创建数据
    - auth: AuthSchema - 认证信息
    
    返回:
    - JSONResponse - 包含创建Team管理结果的JSON响应
    """
    result_dict = await AgTeamService.create_teams_service(auth=auth, data=data)
    log.info("创建Team管理成功")
    return SuccessResponse(data=result_dict, msg="创建Team管理成功")

@AgTeamRouter.put(
    "/update/{id}",
    summary="修改Team管理",
    description="修改Team管理"
)
async def update_teams_controller(
    data: AgTeamUpdateSchema,
    id: int = Path(..., description="ID"),
    auth: AuthSchema = Depends(AuthPermission(["module_agno_manage:teams:update"]))
) -> JSONResponse:
    """
    修改Team管理接口
    
    参数:
    - id: int - 数据ID
    - data: AgTeamUpdateSchema - 更新数据
    - auth: AuthSchema - 认证信息
    
    返回:
    - JSONResponse - 包含修改Team管理结果的JSON响应
    """
    result_dict = await AgTeamService.update_teams_service(auth=auth, id=id, data=data)
    log.info("修改Team管理成功")
    return SuccessResponse(data=result_dict, msg="修改Team管理成功")

@AgTeamRouter.delete(
    "/delete",
    summary="删除Team管理",
    description="删除Team管理"
)
async def delete_teams_controller(
    ids: list[int] = Body(..., description="ID列表"),
    auth: AuthSchema = Depends(AuthPermission(["module_agno_manage:teams:delete"]))
) -> JSONResponse:
    """
    删除Team管理接口
    
    参数:
    - ids: list[int] - 数据ID列表
    - auth: AuthSchema - 认证信息
    
    返回:
    - JSONResponse - 包含删除Team管理结果的JSON响应
    """
    await AgTeamService.delete_teams_service(auth=auth, ids=ids)
    log.info(f"删除Team管理成功: {ids}")
    return SuccessResponse(msg="删除Team管理成功")

@AgTeamRouter.patch(
    "/available/setting",
    summary="批量修改Team管理状态",
    description="批量修改Team管理状态"
)
async def batch_set_available_teams_controller(
    data: BatchSetAvailable,
    auth: AuthSchema = Depends(AuthPermission(["module_agno_manage:teams:patch"]))
) -> JSONResponse:
    """
    批量修改Team管理状态接口
    
    参数:
    - data: BatchSetAvailable - 批量修改状态数据
    - auth: AuthSchema - 认证信息
    
    返回:
    - JSONResponse - 包含批量修改Team管理状态结果的JSON响应
    """
    await AgTeamService.set_available_teams_service(auth=auth, data=data)
    log.info(f"批量修改Team管理状态成功: {data.ids}")
    return SuccessResponse(msg="批量修改Team管理状态成功")

@AgTeamRouter.post(
    '/export',
    summary="导出Team管理",
    description="导出Team管理"
)
async def export_teams_list_controller(
    search: AgTeamQueryParam = Depends(),
    auth: AuthSchema = Depends(AuthPermission(["module_agno_manage:teams:export"]))
) -> StreamingResponse:
    """
    导出Team管理接口
    
    参数:
    - search: AgTeamQueryParam - 查询参数
    - auth: AuthSchema - 认证信息
    
    返回:
    - StreamingResponse - 包含导出Team管理数据的流式响应
    """
    result_dict_list = await AgTeamService.list_teams_service(search=search, auth=auth)
    export_result = await AgTeamService.batch_export_teams_service(obj_list=result_dict_list)
    log.info('导出Team管理成功')
    return StreamResponse(
        data=bytes2file_response(export_result),
        media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        headers={'Content-Disposition': 'attachment; filename=ag_teams.xlsx'}
    )

@AgTeamRouter.post(
    '/import',
    summary="导入Team管理",
    description="导入Team管理"
)
async def import_teams_list_controller(
    file: UploadFile,
    auth: AuthSchema = Depends(AuthPermission(["module_agno_manage:teams:import"]))
) -> JSONResponse:
    """
    导入Team管理接口
    
    参数:
    - file: UploadFile - 上传的Excel文件
    - auth: AuthSchema - 认证信息
    
    返回:
    - JSONResponse - 包含导入Team管理结果的JSON响应
    """
    batch_import_result = await AgTeamService.batch_import_teams_service(file=file, auth=auth, update_support=True)
    log.info("导入Team管理成功")
    return SuccessResponse(data=batch_import_result, msg="导入Team管理成功")

@AgTeamRouter.post(
    '/download/template',
    summary="获取Team管理导入模板",
    description="获取Team管理导入模板",
    dependencies=[Depends(AuthPermission(["module_agno_manage:teams:download"]))]
)
async def export_teams_template_controller() -> StreamingResponse:
    """
    获取Team管理导入模板接口
    
    返回:
    - StreamingResponse - 包含Team管理导入模板的流式响应
    """
    import_template_result = await AgTeamService.import_template_download_teams_service()
    log.info('获取Team管理导入模板成功')
    return StreamResponse(
        data=bytes2file_response(import_template_result),
        media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        headers={'Content-Disposition': 'attachment; filename=ag_teams_template.xlsx'}
    )