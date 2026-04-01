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

from .service import AgUserRoleService
from .schema import AgUserRoleCreateSchema, AgUserRoleUpdateSchema, AgUserRoleQueryParam

AgUserRoleRouter = APIRouter(prefix='/user_roles', tags=["用户角色关联模块"]) 

@AgUserRoleRouter.get(
    "/detail/{id}",
    summary="获取用户角色关联详情",
    description="获取用户角色关联详情"
)
async def get_user_roles_detail_controller(
    id: int = Path(..., description="ID"),
    auth: AuthSchema = Depends(AuthPermission(["module_agno_manage:user_roles:query"]))
) -> JSONResponse:
    """
    获取用户角色关联详情接口
    
    参数:
    - id: int - 数据ID
    - auth: AuthSchema - 认证信息
    
    返回:
    - JSONResponse - 包含用户角色关联详情的JSON响应
    """
    result_dict = await AgUserRoleService.detail_user_roles_service(auth=auth, id=id)
    log.info(f"获取用户角色关联详情成功 {id}")
    return SuccessResponse(data=result_dict, msg="获取用户角色关联详情成功")

@AgUserRoleRouter.get(
    "/list",
    summary="查询用户角色关联列表",
    description="查询用户角色关联列表"
)
async def get_user_roles_list_controller(
    page: PaginationQueryParam = Depends(),
    search: AgUserRoleQueryParam = Depends(),
    auth: AuthSchema = Depends(AuthPermission(["module_agno_manage:user_roles:query"]))
) -> JSONResponse:
    """
    查询用户角色关联列表接口（数据库分页）
    
    参数:
    - page: PaginationQueryParam - 分页参数
    - search: AgUserRoleQueryParam - 查询参数
    - auth: AuthSchema - 认证信息
    
    返回:
    - JSONResponse - 包含用户角色关联列表的JSON响应
    """
    result_dict = await AgUserRoleService.page_user_roles_service(
        auth=auth,
        page_no=page.page_no if page.page_no is not None else 1,
        page_size=page.page_size if page.page_size is not None else 10,
        search=search,
        order_by=page.order_by
    )
    log.info("查询用户角色关联列表成功")
    return SuccessResponse(data=result_dict, msg="查询用户角色关联列表成功")

@AgUserRoleRouter.post(
    "/create",
    summary="创建用户角色关联",
    description="创建用户角色关联"
)
async def create_user_roles_controller(
    data: AgUserRoleCreateSchema,
    auth: AuthSchema = Depends(AuthPermission(["module_agno_manage:user_roles:create"]))
) -> JSONResponse:
    """
    创建用户角色关联接口
    
    参数:
    - data: AgUserRoleCreateSchema - 创建数据
    - auth: AuthSchema - 认证信息
    
    返回:
    - JSONResponse - 包含创建用户角色关联结果的JSON响应
    """
    result_dict = await AgUserRoleService.create_user_roles_service(auth=auth, data=data)
    log.info("创建用户角色关联成功")
    return SuccessResponse(data=result_dict, msg="创建用户角色关联成功")

@AgUserRoleRouter.put(
    "/update/{id}",
    summary="修改用户角色关联",
    description="修改用户角色关联"
)
async def update_user_roles_controller(
    data: AgUserRoleUpdateSchema,
    id: int = Path(..., description="ID"),
    auth: AuthSchema = Depends(AuthPermission(["module_agno_manage:user_roles:update"]))
) -> JSONResponse:
    """
    修改用户角色关联接口
    
    参数:
    - id: int - 数据ID
    - data: AgUserRoleUpdateSchema - 更新数据
    - auth: AuthSchema - 认证信息
    
    返回:
    - JSONResponse - 包含修改用户角色关联结果的JSON响应
    """
    result_dict = await AgUserRoleService.update_user_roles_service(auth=auth, id=id, data=data)
    log.info("修改用户角色关联成功")
    return SuccessResponse(data=result_dict, msg="修改用户角色关联成功")

@AgUserRoleRouter.delete(
    "/delete",
    summary="删除用户角色关联",
    description="删除用户角色关联"
)
async def delete_user_roles_controller(
    ids: list[int] = Body(..., description="ID列表"),
    auth: AuthSchema = Depends(AuthPermission(["module_agno_manage:user_roles:delete"]))
) -> JSONResponse:
    """
    删除用户角色关联接口
    
    参数:
    - ids: list[int] - 数据ID列表
    - auth: AuthSchema - 认证信息
    
    返回:
    - JSONResponse - 包含删除用户角色关联结果的JSON响应
    """
    await AgUserRoleService.delete_user_roles_service(auth=auth, ids=ids)
    log.info(f"删除用户角色关联成功: {ids}")
    return SuccessResponse(msg="删除用户角色关联成功")

@AgUserRoleRouter.patch(
    "/available/setting",
    summary="批量修改用户角色关联状态",
    description="批量修改用户角色关联状态"
)
async def batch_set_available_user_roles_controller(
    data: BatchSetAvailable,
    auth: AuthSchema = Depends(AuthPermission(["module_agno_manage:user_roles:patch"]))
) -> JSONResponse:
    """
    批量修改用户角色关联状态接口
    
    参数:
    - data: BatchSetAvailable - 批量修改状态数据
    - auth: AuthSchema - 认证信息
    
    返回:
    - JSONResponse - 包含批量修改用户角色关联状态结果的JSON响应
    """
    await AgUserRoleService.set_available_user_roles_service(auth=auth, data=data)
    log.info(f"批量修改用户角色关联状态成功: {data.ids}")
    return SuccessResponse(msg="批量修改用户角色关联状态成功")

@AgUserRoleRouter.post(
    '/export',
    summary="导出用户角色关联",
    description="导出用户角色关联"
)
async def export_user_roles_list_controller(
    search: AgUserRoleQueryParam = Depends(),
    auth: AuthSchema = Depends(AuthPermission(["module_agno_manage:user_roles:export"]))
) -> StreamingResponse:
    """
    导出用户角色关联接口
    
    参数:
    - search: AgUserRoleQueryParam - 查询参数
    - auth: AuthSchema - 认证信息
    
    返回:
    - StreamingResponse - 包含导出用户角色关联数据的流式响应
    """
    result_dict_list = await AgUserRoleService.list_user_roles_service(search=search, auth=auth)
    export_result = await AgUserRoleService.batch_export_user_roles_service(obj_list=result_dict_list)
    log.info('导出用户角色关联成功')
    return StreamResponse(
        data=bytes2file_response(export_result),
        media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        headers={'Content-Disposition': 'attachment; filename=ag_user_roles.xlsx'}
    )

@AgUserRoleRouter.post(
    '/import',
    summary="导入用户角色关联",
    description="导入用户角色关联"
)
async def import_user_roles_list_controller(
    file: UploadFile,
    auth: AuthSchema = Depends(AuthPermission(["module_agno_manage:user_roles:import"]))
) -> JSONResponse:
    """
    导入用户角色关联接口
    
    参数:
    - file: UploadFile - 上传的Excel文件
    - auth: AuthSchema - 认证信息
    
    返回:
    - JSONResponse - 包含导入用户角色关联结果的JSON响应
    """
    batch_import_result = await AgUserRoleService.batch_import_user_roles_service(file=file, auth=auth, update_support=True)
    log.info("导入用户角色关联成功")
    return SuccessResponse(data=batch_import_result, msg="导入用户角色关联成功")

@AgUserRoleRouter.post(
    '/download/template',
    summary="获取用户角色关联导入模板",
    description="获取用户角色关联导入模板",
    dependencies=[Depends(AuthPermission(["module_agno_manage:user_roles:download"]))]
)
async def export_user_roles_template_controller() -> StreamingResponse:
    """
    获取用户角色关联导入模板接口
    
    返回:
    - StreamingResponse - 包含用户角色关联导入模板的流式响应
    """
    import_template_result = await AgUserRoleService.import_template_download_user_roles_service()
    log.info('获取用户角色关联导入模板成功')
    return StreamResponse(
        data=bytes2file_response(import_template_result),
        media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        headers={'Content-Disposition': 'attachment; filename=ag_user_roles_template.xlsx'}
    )