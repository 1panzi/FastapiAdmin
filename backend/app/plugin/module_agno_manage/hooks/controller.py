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

from .service import AgHookService
from .schema import AgHookCreateSchema, AgHookUpdateSchema, AgHookQueryParam

AgHookRouter = APIRouter(prefix='/hooks', tags=["hook模块"]) 

@AgHookRouter.get(
    "/detail/{id}",
    summary="获取hook详情",
    description="获取hook详情"
)
async def get_hooks_detail_controller(
    id: int = Path(..., description="ID"),
    auth: AuthSchema = Depends(AuthPermission(["module_agno_manage:hooks:query"]))
) -> JSONResponse:
    """
    获取hook详情接口
    
    参数:
    - id: int - 数据ID
    - auth: AuthSchema - 认证信息
    
    返回:
    - JSONResponse - 包含hook详情的JSON响应
    """
    result_dict = await AgHookService.detail_hooks_service(auth=auth, id=id)
    log.info(f"获取hook详情成功 {id}")
    return SuccessResponse(data=result_dict, msg="获取hook详情成功")

@AgHookRouter.get(
    "/list",
    summary="查询hook列表",
    description="查询hook列表"
)
async def get_hooks_list_controller(
    page: PaginationQueryParam = Depends(),
    search: AgHookQueryParam = Depends(),
    auth: AuthSchema = Depends(AuthPermission(["module_agno_manage:hooks:query"]))
) -> JSONResponse:
    """
    查询hook列表接口（数据库分页）
    
    参数:
    - page: PaginationQueryParam - 分页参数
    - search: AgHookQueryParam - 查询参数
    - auth: AuthSchema - 认证信息
    
    返回:
    - JSONResponse - 包含hook列表的JSON响应
    """
    result_dict = await AgHookService.page_hooks_service(
        auth=auth,
        page_no=page.page_no if page.page_no is not None else 1,
        page_size=page.page_size if page.page_size is not None else 10,
        search=search,
        order_by=page.order_by
    )
    log.info("查询hook列表成功")
    return SuccessResponse(data=result_dict, msg="查询hook列表成功")

@AgHookRouter.post(
    "/create",
    summary="创建hook",
    description="创建hook"
)
async def create_hooks_controller(
    data: AgHookCreateSchema,
    auth: AuthSchema = Depends(AuthPermission(["module_agno_manage:hooks:create"]))
) -> JSONResponse:
    """
    创建hook接口
    
    参数:
    - data: AgHookCreateSchema - 创建数据
    - auth: AuthSchema - 认证信息
    
    返回:
    - JSONResponse - 包含创建hook结果的JSON响应
    """
    result_dict = await AgHookService.create_hooks_service(auth=auth, data=data)
    log.info("创建hook成功")
    return SuccessResponse(data=result_dict, msg="创建hook成功")

@AgHookRouter.put(
    "/update/{id}",
    summary="修改hook",
    description="修改hook"
)
async def update_hooks_controller(
    data: AgHookUpdateSchema,
    id: int = Path(..., description="ID"),
    auth: AuthSchema = Depends(AuthPermission(["module_agno_manage:hooks:update"]))
) -> JSONResponse:
    """
    修改hook接口
    
    参数:
    - id: int - 数据ID
    - data: AgHookUpdateSchema - 更新数据
    - auth: AuthSchema - 认证信息
    
    返回:
    - JSONResponse - 包含修改hook结果的JSON响应
    """
    result_dict = await AgHookService.update_hooks_service(auth=auth, id=id, data=data)
    log.info("修改hook成功")
    return SuccessResponse(data=result_dict, msg="修改hook成功")

@AgHookRouter.delete(
    "/delete",
    summary="删除hook",
    description="删除hook"
)
async def delete_hooks_controller(
    ids: list[int] = Body(..., description="ID列表"),
    auth: AuthSchema = Depends(AuthPermission(["module_agno_manage:hooks:delete"]))
) -> JSONResponse:
    """
    删除hook接口
    
    参数:
    - ids: list[int] - 数据ID列表
    - auth: AuthSchema - 认证信息
    
    返回:
    - JSONResponse - 包含删除hook结果的JSON响应
    """
    await AgHookService.delete_hooks_service(auth=auth, ids=ids)
    log.info(f"删除hook成功: {ids}")
    return SuccessResponse(msg="删除hook成功")

@AgHookRouter.patch(
    "/available/setting",
    summary="批量修改hook状态",
    description="批量修改hook状态"
)
async def batch_set_available_hooks_controller(
    data: BatchSetAvailable,
    auth: AuthSchema = Depends(AuthPermission(["module_agno_manage:hooks:patch"]))
) -> JSONResponse:
    """
    批量修改hook状态接口
    
    参数:
    - data: BatchSetAvailable - 批量修改状态数据
    - auth: AuthSchema - 认证信息
    
    返回:
    - JSONResponse - 包含批量修改hook状态结果的JSON响应
    """
    await AgHookService.set_available_hooks_service(auth=auth, data=data)
    log.info(f"批量修改hook状态成功: {data.ids}")
    return SuccessResponse(msg="批量修改hook状态成功")

@AgHookRouter.post(
    '/export',
    summary="导出hook",
    description="导出hook"
)
async def export_hooks_list_controller(
    search: AgHookQueryParam = Depends(),
    auth: AuthSchema = Depends(AuthPermission(["module_agno_manage:hooks:export"]))
) -> StreamingResponse:
    """
    导出hook接口
    
    参数:
    - search: AgHookQueryParam - 查询参数
    - auth: AuthSchema - 认证信息
    
    返回:
    - StreamingResponse - 包含导出hook数据的流式响应
    """
    result_dict_list = await AgHookService.list_hooks_service(search=search, auth=auth)
    export_result = await AgHookService.batch_export_hooks_service(obj_list=result_dict_list)
    log.info('导出hook成功')
    return StreamResponse(
        data=bytes2file_response(export_result),
        media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        headers={'Content-Disposition': 'attachment; filename=ag_hooks.xlsx'}
    )

@AgHookRouter.post(
    '/import',
    summary="导入hook",
    description="导入hook"
)
async def import_hooks_list_controller(
    file: UploadFile,
    auth: AuthSchema = Depends(AuthPermission(["module_agno_manage:hooks:import"]))
) -> JSONResponse:
    """
    导入hook接口
    
    参数:
    - file: UploadFile - 上传的Excel文件
    - auth: AuthSchema - 认证信息
    
    返回:
    - JSONResponse - 包含导入hook结果的JSON响应
    """
    batch_import_result = await AgHookService.batch_import_hooks_service(file=file, auth=auth, update_support=True)
    log.info("导入hook成功")
    return SuccessResponse(data=batch_import_result, msg="导入hook成功")

@AgHookRouter.post(
    '/download/template',
    summary="获取hook导入模板",
    description="获取hook导入模板",
    dependencies=[Depends(AuthPermission(["module_agno_manage:hooks:download"]))]
)
async def export_hooks_template_controller() -> StreamingResponse:
    """
    获取hook导入模板接口
    
    返回:
    - StreamingResponse - 包含hook导入模板的流式响应
    """
    import_template_result = await AgHookService.import_template_download_hooks_service()
    log.info('获取hook导入模板成功')
    return StreamResponse(
        data=bytes2file_response(import_template_result),
        media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        headers={'Content-Disposition': 'attachment; filename=ag_hooks_template.xlsx'}
    )