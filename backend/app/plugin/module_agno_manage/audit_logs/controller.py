
from fastapi import APIRouter, Body, Depends, Path, UploadFile
from fastapi.responses import JSONResponse, StreamingResponse

from app.api.v1.module_system.auth.schema import AuthSchema
from app.common.response import StreamResponse, SuccessResponse
from app.core.base_params import PaginationQueryParam
from app.core.base_schema import BatchSetAvailable
from app.core.dependencies import AuthPermission
from app.core.logger import log
from app.utils.common_util import bytes2file_response

from .schema import AgAuditLogCreateSchema, AgAuditLogQueryParam, AgAuditLogUpdateSchema
from .service import AgAuditLogService

AgAuditLogRouter = APIRouter(prefix='/audit_logs', tags=["审计日志模块"])


@AgAuditLogRouter.get(
    "/detail/{id}",
    summary="获取审计日志详情",
    description="获取审计日志详情"
)
async def get_audit_logs_detail_controller(
    id: int = Path(..., description="ID"),
    auth: AuthSchema = Depends(AuthPermission(["module_agno_manage:audit_logs:query"]))
) -> JSONResponse:
    """
    获取审计日志详情接口
    
    参数:
    - id: int - 数据ID
    - auth: AuthSchema - 认证信息
    
    返回:
    - JSONResponse - 包含审计日志详情的JSON响应
    """
    result_dict = await AgAuditLogService.detail_audit_logs_service(auth=auth, id=id)
    log.info(f"获取审计日志详情成功 {id}")
    return SuccessResponse(data=result_dict, msg="获取审计日志详情成功")


@AgAuditLogRouter.get(
    "/list",
    summary="查询审计日志列表",
    description="查询审计日志列表"
)
async def get_audit_logs_list_controller(
    page: PaginationQueryParam = Depends(),
    search: AgAuditLogQueryParam = Depends(),
    auth: AuthSchema = Depends(AuthPermission(["module_agno_manage:audit_logs:query"]))
) -> JSONResponse:
    """
    查询审计日志列表接口（数据库分页）
    
    参数:
    - page: PaginationQueryParam - 分页参数
    - search: AgAuditLogQueryParam - 查询参数
    - auth: AuthSchema - 认证信息
    
    返回:
    - JSONResponse - 包含审计日志列表的JSON响应
    """
    result_dict = await AgAuditLogService.page_audit_logs_service(
        auth=auth,
        page_no=page.page_no if page.page_no is not None else 1,
        page_size=page.page_size if page.page_size is not None else 10,
        search=search,
        order_by=page.order_by
    )
    log.info("查询审计日志列表成功")
    return SuccessResponse(data=result_dict, msg="查询审计日志列表成功")


@AgAuditLogRouter.post(
    "/create",
    summary="创建审计日志",
    description="创建审计日志"
)
async def create_audit_logs_controller(
    data: AgAuditLogCreateSchema,
    auth: AuthSchema = Depends(AuthPermission(["module_agno_manage:audit_logs:create"]))
) -> JSONResponse:
    """
    创建审计日志接口
    
    参数:
    - data: AgAuditLogCreateSchema - 创建数据
    - auth: AuthSchema - 认证信息
    
    返回:
    - JSONResponse - 包含创建审计日志结果的JSON响应
    """
    result_dict = await AgAuditLogService.create_audit_logs_service(auth=auth, data=data)
    log.info("创建审计日志成功")
    return SuccessResponse(data=result_dict, msg="创建审计日志成功")


@AgAuditLogRouter.put(
    "/update/{id}",
    summary="修改审计日志",
    description="修改审计日志"
)
async def update_audit_logs_controller(
    data: AgAuditLogUpdateSchema,
    id: int = Path(..., description="ID"),
    auth: AuthSchema = Depends(AuthPermission(["module_agno_manage:audit_logs:update"]))
) -> JSONResponse:
    """
    修改审计日志接口
    
    参数:
    - id: int - 数据ID
    - data: AgAuditLogUpdateSchema - 更新数据
    - auth: AuthSchema - 认证信息
    
    返回:
    - JSONResponse - 包含修改审计日志结果的JSON响应
    """
    result_dict = await AgAuditLogService.update_audit_logs_service(auth=auth, id=id, data=data)
    log.info("修改审计日志成功")
    return SuccessResponse(data=result_dict, msg="修改审计日志成功")


@AgAuditLogRouter.delete(
    "/delete",
    summary="删除审计日志",
    description="删除审计日志"
)
async def delete_audit_logs_controller(
    ids: list[int] = Body(..., description="ID列表"),
    auth: AuthSchema = Depends(AuthPermission(["module_agno_manage:audit_logs:delete"]))
) -> JSONResponse:
    """
    删除审计日志接口
    
    参数:
    - ids: list[int] - 数据ID列表
    - auth: AuthSchema - 认证信息
    
    返回:
    - JSONResponse - 包含删除审计日志结果的JSON响应
    """
    await AgAuditLogService.delete_audit_logs_service(auth=auth, ids=ids)
    log.info(f"删除审计日志成功: {ids}")
    return SuccessResponse(msg="删除审计日志成功")


@AgAuditLogRouter.patch(
    "/available/setting",
    summary="批量修改审计日志状态",
    description="批量修改审计日志状态"
)
async def batch_set_available_audit_logs_controller(
    data: BatchSetAvailable,
    auth: AuthSchema = Depends(AuthPermission(["module_agno_manage:audit_logs:patch"]))
) -> JSONResponse:
    """
    批量修改审计日志状态接口
    
    参数:
    - data: BatchSetAvailable - 批量修改状态数据
    - auth: AuthSchema - 认证信息
    
    返回:
    - JSONResponse - 包含批量修改审计日志状态结果的JSON响应
    """
    await AgAuditLogService.set_available_audit_logs_service(auth=auth, data=data)
    log.info(f"批量修改审计日志状态成功: {data.ids}")
    return SuccessResponse(msg="批量修改审计日志状态成功")


@AgAuditLogRouter.post(
    '/export',
    summary="导出审计日志",
    description="导出审计日志"
)
async def export_audit_logs_list_controller(
    search: AgAuditLogQueryParam = Depends(),
    auth: AuthSchema = Depends(AuthPermission(["module_agno_manage:audit_logs:export"]))
) -> StreamingResponse:
    """
    导出审计日志接口
    
    参数:
    - search: AgAuditLogQueryParam - 查询参数
    - auth: AuthSchema - 认证信息
    
    返回:
    - StreamingResponse - 包含导出审计日志数据的流式响应
    """
    result_dict_list = await AgAuditLogService.list_audit_logs_service(search=search, auth=auth)
    export_result = await AgAuditLogService.batch_export_audit_logs_service(obj_list=result_dict_list)
    log.info('导出审计日志成功')
    return StreamResponse(
        data=bytes2file_response(export_result),
        media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        headers={'Content-Disposition': 'attachment; filename=ag_audit_logs.xlsx'}
    )


@AgAuditLogRouter.post(
    '/import',
    summary="导入审计日志",
    description="导入审计日志"
)
async def import_audit_logs_list_controller(
    file: UploadFile,
    auth: AuthSchema = Depends(AuthPermission(["module_agno_manage:audit_logs:import"]))
) -> JSONResponse:
    """
    导入审计日志接口
    
    参数:
    - file: UploadFile - 上传的Excel文件
    - auth: AuthSchema - 认证信息
    
    返回:
    - JSONResponse - 包含导入审计日志结果的JSON响应
    """
    batch_import_result = await AgAuditLogService.batch_import_audit_logs_service(file=file, auth=auth, update_support=True)
    log.info("导入审计日志成功")
    return SuccessResponse(data=batch_import_result, msg="导入审计日志成功")


@AgAuditLogRouter.post(
    '/download/template',
    summary="获取审计日志导入模板",
    description="获取审计日志导入模板",
    dependencies=[Depends(AuthPermission(["module_agno_manage:audit_logs:download"]))]
)
async def export_audit_logs_template_controller() -> StreamingResponse:
    """
    获取审计日志导入模板接口
    
    返回:
    - StreamingResponse - 包含审计日志导入模板的流式响应
    """
    import_template_result = await AgAuditLogService.import_template_download_audit_logs_service()
    log.info('获取审计日志导入模板成功')
    return StreamResponse(
        data=bytes2file_response(import_template_result),
        media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        headers={'Content-Disposition': 'attachment; filename=ag_audit_logs_template.xlsx'}
    )
