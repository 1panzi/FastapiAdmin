
from fastapi import APIRouter, Body, Depends, Path, UploadFile
from fastapi.responses import JSONResponse, StreamingResponse

from app.api.v1.module_system.auth.schema import AuthSchema
from app.common.response import StreamResponse, SuccessResponse
from app.core.base_params import PaginationQueryParam
from app.core.base_schema import BatchSetAvailable
from app.core.dependencies import AuthPermission
from app.core.logger import log
from app.utils.common_util import bytes2file_response

from .schema import AgUsageLogCreateSchema, AgUsageLogQueryParam, AgUsageLogUpdateSchema
from .service import AgUsageLogService

AgUsageLogRouter = APIRouter(prefix='/usage_logs', tags=["用量日志模块"])


@AgUsageLogRouter.get(
    "/detail/{id}",
    summary="获取用量日志详情",
    description="获取用量日志详情"
)
async def get_usage_logs_detail_controller(
    id: int = Path(..., description="ID"),
    auth: AuthSchema = Depends(AuthPermission(["module_agno_manage:usage_logs:query"]))
) -> JSONResponse:
    """
    获取用量日志详情接口
    
    参数:
    - id: int - 数据ID
    - auth: AuthSchema - 认证信息
    
    返回:
    - JSONResponse - 包含用量日志详情的JSON响应
    """
    result_dict = await AgUsageLogService.detail_usage_logs_service(auth=auth, id=id)
    log.info(f"获取用量日志详情成功 {id}")
    return SuccessResponse(data=result_dict, msg="获取用量日志详情成功")


@AgUsageLogRouter.get(
    "/list",
    summary="查询用量日志列表",
    description="查询用量日志列表"
)
async def get_usage_logs_list_controller(
    page: PaginationQueryParam = Depends(),
    search: AgUsageLogQueryParam = Depends(),
    auth: AuthSchema = Depends(AuthPermission(["module_agno_manage:usage_logs:query"]))
) -> JSONResponse:
    """
    查询用量日志列表接口（数据库分页）
    
    参数:
    - page: PaginationQueryParam - 分页参数
    - search: AgUsageLogQueryParam - 查询参数
    - auth: AuthSchema - 认证信息
    
    返回:
    - JSONResponse - 包含用量日志列表的JSON响应
    """
    result_dict = await AgUsageLogService.page_usage_logs_service(
        auth=auth,
        page_no=page.page_no if page.page_no is not None else 1,
        page_size=page.page_size if page.page_size is not None else 10,
        search=search,
        order_by=page.order_by
    )
    log.info("查询用量日志列表成功")
    return SuccessResponse(data=result_dict, msg="查询用量日志列表成功")


@AgUsageLogRouter.post(
    "/create",
    summary="创建用量日志",
    description="创建用量日志"
)
async def create_usage_logs_controller(
    data: AgUsageLogCreateSchema,
    auth: AuthSchema = Depends(AuthPermission(["module_agno_manage:usage_logs:create"]))
) -> JSONResponse:
    """
    创建用量日志接口
    
    参数:
    - data: AgUsageLogCreateSchema - 创建数据
    - auth: AuthSchema - 认证信息
    
    返回:
    - JSONResponse - 包含创建用量日志结果的JSON响应
    """
    result_dict = await AgUsageLogService.create_usage_logs_service(auth=auth, data=data)
    log.info("创建用量日志成功")
    return SuccessResponse(data=result_dict, msg="创建用量日志成功")


@AgUsageLogRouter.put(
    "/update/{id}",
    summary="修改用量日志",
    description="修改用量日志"
)
async def update_usage_logs_controller(
    data: AgUsageLogUpdateSchema,
    id: int = Path(..., description="ID"),
    auth: AuthSchema = Depends(AuthPermission(["module_agno_manage:usage_logs:update"]))
) -> JSONResponse:
    """
    修改用量日志接口
    
    参数:
    - id: int - 数据ID
    - data: AgUsageLogUpdateSchema - 更新数据
    - auth: AuthSchema - 认证信息
    
    返回:
    - JSONResponse - 包含修改用量日志结果的JSON响应
    """
    result_dict = await AgUsageLogService.update_usage_logs_service(auth=auth, id=id, data=data)
    log.info("修改用量日志成功")
    return SuccessResponse(data=result_dict, msg="修改用量日志成功")


@AgUsageLogRouter.delete(
    "/delete",
    summary="删除用量日志",
    description="删除用量日志"
)
async def delete_usage_logs_controller(
    ids: list[int] = Body(..., description="ID列表"),
    auth: AuthSchema = Depends(AuthPermission(["module_agno_manage:usage_logs:delete"]))
) -> JSONResponse:
    """
    删除用量日志接口
    
    参数:
    - ids: list[int] - 数据ID列表
    - auth: AuthSchema - 认证信息
    
    返回:
    - JSONResponse - 包含删除用量日志结果的JSON响应
    """
    await AgUsageLogService.delete_usage_logs_service(auth=auth, ids=ids)
    log.info(f"删除用量日志成功: {ids}")
    return SuccessResponse(msg="删除用量日志成功")


@AgUsageLogRouter.patch(
    "/available/setting",
    summary="批量修改用量日志状态",
    description="批量修改用量日志状态"
)
async def batch_set_available_usage_logs_controller(
    data: BatchSetAvailable,
    auth: AuthSchema = Depends(AuthPermission(["module_agno_manage:usage_logs:patch"]))
) -> JSONResponse:
    """
    批量修改用量日志状态接口
    
    参数:
    - data: BatchSetAvailable - 批量修改状态数据
    - auth: AuthSchema - 认证信息
    
    返回:
    - JSONResponse - 包含批量修改用量日志状态结果的JSON响应
    """
    await AgUsageLogService.set_available_usage_logs_service(auth=auth, data=data)
    log.info(f"批量修改用量日志状态成功: {data.ids}")
    return SuccessResponse(msg="批量修改用量日志状态成功")


@AgUsageLogRouter.post(
    '/export',
    summary="导出用量日志",
    description="导出用量日志"
)
async def export_usage_logs_list_controller(
    search: AgUsageLogQueryParam = Depends(),
    auth: AuthSchema = Depends(AuthPermission(["module_agno_manage:usage_logs:export"]))
) -> StreamingResponse:
    """
    导出用量日志接口
    
    参数:
    - search: AgUsageLogQueryParam - 查询参数
    - auth: AuthSchema - 认证信息
    
    返回:
    - StreamingResponse - 包含导出用量日志数据的流式响应
    """
    result_dict_list = await AgUsageLogService.list_usage_logs_service(search=search, auth=auth)
    export_result = await AgUsageLogService.batch_export_usage_logs_service(obj_list=result_dict_list)
    log.info('导出用量日志成功')
    return StreamResponse(
        data=bytes2file_response(export_result),
        media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        headers={'Content-Disposition': 'attachment; filename=ag_usage_logs.xlsx'}
    )


@AgUsageLogRouter.post(
    '/import',
    summary="导入用量日志",
    description="导入用量日志"
)
async def import_usage_logs_list_controller(
    file: UploadFile,
    auth: AuthSchema = Depends(AuthPermission(["module_agno_manage:usage_logs:import"]))
) -> JSONResponse:
    """
    导入用量日志接口
    
    参数:
    - file: UploadFile - 上传的Excel文件
    - auth: AuthSchema - 认证信息
    
    返回:
    - JSONResponse - 包含导入用量日志结果的JSON响应
    """
    batch_import_result = await AgUsageLogService.batch_import_usage_logs_service(file=file, auth=auth, update_support=True)
    log.info("导入用量日志成功")
    return SuccessResponse(data=batch_import_result, msg="导入用量日志成功")


@AgUsageLogRouter.post(
    '/download/template',
    summary="获取用量日志导入模板",
    description="获取用量日志导入模板",
    dependencies=[Depends(AuthPermission(["module_agno_manage:usage_logs:download"]))]
)
async def export_usage_logs_template_controller() -> StreamingResponse:
    """
    获取用量日志导入模板接口
    
    返回:
    - StreamingResponse - 包含用量日志导入模板的流式响应
    """
    import_template_result = await AgUsageLogService.import_template_download_usage_logs_service()
    log.info('获取用量日志导入模板成功')
    return StreamResponse(
        data=bytes2file_response(import_template_result),
        media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        headers={'Content-Disposition': 'attachment; filename=ag_usage_logs_template.xlsx'}
    )
