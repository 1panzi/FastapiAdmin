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

from .service import AgRoleService
from .schema import AgRoleCreateSchema, AgRoleUpdateSchema, AgRoleQueryParam

AgRoleRouter = APIRouter(prefix='/roles', tags=["agno角色管理模块"]) 

@AgRoleRouter.get(
    "/detail/{id}",
    summary="获取agno角色管理详情",
    description="获取agno角色管理详情"
)
async def get_roles_detail_controller(
    id: int = Path(..., description="ID"),
    auth: AuthSchema = Depends(AuthPermission(["module_agno_manage:roles:query"]))
) -> JSONResponse:
    """
    获取agno角色管理详情接口
    
    参数:
    - id: int - 数据ID
    - auth: AuthSchema - 认证信息
    
    返回:
    - JSONResponse - 包含agno角色管理详情的JSON响应
    """
    result_dict = await AgRoleService.detail_roles_service(auth=auth, id=id)
    log.info(f"获取agno角色管理详情成功 {id}")
    return SuccessResponse(data=result_dict, msg="获取agno角色管理详情成功")

@AgRoleRouter.get(
    "/list",
    summary="查询agno角色管理列表",
    description="查询agno角色管理列表"
)
async def get_roles_list_controller(
    page: PaginationQueryParam = Depends(),
    search: AgRoleQueryParam = Depends(),
    auth: AuthSchema = Depends(AuthPermission(["module_agno_manage:roles:query"]))
) -> JSONResponse:
    """
    查询agno角色管理列表接口（数据库分页）
    
    参数:
    - page: PaginationQueryParam - 分页参数
    - search: AgRoleQueryParam - 查询参数
    - auth: AuthSchema - 认证信息
    
    返回:
    - JSONResponse - 包含agno角色管理列表的JSON响应
    """
    result_dict = await AgRoleService.page_roles_service(
        auth=auth,
        page_no=page.page_no if page.page_no is not None else 1,
        page_size=page.page_size if page.page_size is not None else 10,
        search=search,
        order_by=page.order_by
    )
    log.info("查询agno角色管理列表成功")
    return SuccessResponse(data=result_dict, msg="查询agno角色管理列表成功")

@AgRoleRouter.post(
    "/create",
    summary="创建agno角色管理",
    description="创建agno角色管理"
)
async def create_roles_controller(
    data: AgRoleCreateSchema,
    auth: AuthSchema = Depends(AuthPermission(["module_agno_manage:roles:create"]))
) -> JSONResponse:
    """
    创建agno角色管理接口
    
    参数:
    - data: AgRoleCreateSchema - 创建数据
    - auth: AuthSchema - 认证信息
    
    返回:
    - JSONResponse - 包含创建agno角色管理结果的JSON响应
    """
    result_dict = await AgRoleService.create_roles_service(auth=auth, data=data)
    log.info("创建agno角色管理成功")
    return SuccessResponse(data=result_dict, msg="创建agno角色管理成功")

@AgRoleRouter.put(
    "/update/{id}",
    summary="修改agno角色管理",
    description="修改agno角色管理"
)
async def update_roles_controller(
    data: AgRoleUpdateSchema,
    id: int = Path(..., description="ID"),
    auth: AuthSchema = Depends(AuthPermission(["module_agno_manage:roles:update"]))
) -> JSONResponse:
    """
    修改agno角色管理接口
    
    参数:
    - id: int - 数据ID
    - data: AgRoleUpdateSchema - 更新数据
    - auth: AuthSchema - 认证信息
    
    返回:
    - JSONResponse - 包含修改agno角色管理结果的JSON响应
    """
    result_dict = await AgRoleService.update_roles_service(auth=auth, id=id, data=data)
    log.info("修改agno角色管理成功")
    return SuccessResponse(data=result_dict, msg="修改agno角色管理成功")

@AgRoleRouter.delete(
    "/delete",
    summary="删除agno角色管理",
    description="删除agno角色管理"
)
async def delete_roles_controller(
    ids: list[int] = Body(..., description="ID列表"),
    auth: AuthSchema = Depends(AuthPermission(["module_agno_manage:roles:delete"]))
) -> JSONResponse:
    """
    删除agno角色管理接口
    
    参数:
    - ids: list[int] - 数据ID列表
    - auth: AuthSchema - 认证信息
    
    返回:
    - JSONResponse - 包含删除agno角色管理结果的JSON响应
    """
    await AgRoleService.delete_roles_service(auth=auth, ids=ids)
    log.info(f"删除agno角色管理成功: {ids}")
    return SuccessResponse(msg="删除agno角色管理成功")

@AgRoleRouter.patch(
    "/available/setting",
    summary="批量修改agno角色管理状态",
    description="批量修改agno角色管理状态"
)
async def batch_set_available_roles_controller(
    data: BatchSetAvailable,
    auth: AuthSchema = Depends(AuthPermission(["module_agno_manage:roles:patch"]))
) -> JSONResponse:
    """
    批量修改agno角色管理状态接口
    
    参数:
    - data: BatchSetAvailable - 批量修改状态数据
    - auth: AuthSchema - 认证信息
    
    返回:
    - JSONResponse - 包含批量修改agno角色管理状态结果的JSON响应
    """
    await AgRoleService.set_available_roles_service(auth=auth, data=data)
    log.info(f"批量修改agno角色管理状态成功: {data.ids}")
    return SuccessResponse(msg="批量修改agno角色管理状态成功")

@AgRoleRouter.post(
    '/export',
    summary="导出agno角色管理",
    description="导出agno角色管理"
)
async def export_roles_list_controller(
    search: AgRoleQueryParam = Depends(),
    auth: AuthSchema = Depends(AuthPermission(["module_agno_manage:roles:export"]))
) -> StreamingResponse:
    """
    导出agno角色管理接口
    
    参数:
    - search: AgRoleQueryParam - 查询参数
    - auth: AuthSchema - 认证信息
    
    返回:
    - StreamingResponse - 包含导出agno角色管理数据的流式响应
    """
    result_dict_list = await AgRoleService.list_roles_service(search=search, auth=auth)
    export_result = await AgRoleService.batch_export_roles_service(obj_list=result_dict_list)
    log.info('导出agno角色管理成功')
    return StreamResponse(
        data=bytes2file_response(export_result),
        media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        headers={'Content-Disposition': 'attachment; filename=ag_roles.xlsx'}
    )

@AgRoleRouter.post(
    '/import',
    summary="导入agno角色管理",
    description="导入agno角色管理"
)
async def import_roles_list_controller(
    file: UploadFile,
    auth: AuthSchema = Depends(AuthPermission(["module_agno_manage:roles:import"]))
) -> JSONResponse:
    """
    导入agno角色管理接口
    
    参数:
    - file: UploadFile - 上传的Excel文件
    - auth: AuthSchema - 认证信息
    
    返回:
    - JSONResponse - 包含导入agno角色管理结果的JSON响应
    """
    batch_import_result = await AgRoleService.batch_import_roles_service(file=file, auth=auth, update_support=True)
    log.info("导入agno角色管理成功")
    return SuccessResponse(data=batch_import_result, msg="导入agno角色管理成功")

@AgRoleRouter.post(
    '/download/template',
    summary="获取agno角色管理导入模板",
    description="获取agno角色管理导入模板",
    dependencies=[Depends(AuthPermission(["module_agno_manage:roles:download"]))]
)
async def export_roles_template_controller() -> StreamingResponse:
    """
    获取agno角色管理导入模板接口
    
    返回:
    - StreamingResponse - 包含agno角色管理导入模板的流式响应
    """
    import_template_result = await AgRoleService.import_template_download_roles_service()
    log.info('获取agno角色管理导入模板成功')
    return StreamResponse(
        data=bytes2file_response(import_template_result),
        media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        headers={'Content-Disposition': 'attachment; filename=ag_roles_template.xlsx'}
    )