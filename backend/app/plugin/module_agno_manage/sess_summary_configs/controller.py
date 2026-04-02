
from fastapi import APIRouter, Body, Depends, Path, UploadFile
from fastapi.responses import JSONResponse, StreamingResponse

from app.api.v1.module_system.auth.schema import AuthSchema
from app.common.response import StreamResponse, SuccessResponse
from app.core.base_params import PaginationQueryParam
from app.core.base_schema import BatchSetAvailable
from app.core.dependencies import AuthPermission
from app.core.logger import log
from app.utils.common_util import bytes2file_response

from .schema import (
    AgSessSummaryConfigCreateSchema,
    AgSessSummaryConfigQueryParam,
    AgSessSummaryConfigUpdateSchema,
)
from .service import AgSessSummaryConfigService

AgSessSummaryConfigRouter = APIRouter(prefix='/sess_summary_configs', tags=["会话摘要配置模块"])


@AgSessSummaryConfigRouter.get(
    "/detail/{id}",
    summary="获取会话摘要配置详情",
    description="获取会话摘要配置详情"
)
async def get_sess_summary_configs_detail_controller(
    id: int = Path(..., description="ID"),
    auth: AuthSchema = Depends(AuthPermission(["module_agno_manage:sess_summary_configs:query"]))
) -> JSONResponse:
    """
    获取会话摘要配置详情接口
    
    参数:
    - id: int - 数据ID
    - auth: AuthSchema - 认证信息
    
    返回:
    - JSONResponse - 包含会话摘要配置详情的JSON响应
    """
    result_dict = await AgSessSummaryConfigService.detail_sess_summary_configs_service(auth=auth, id=id)
    log.info(f"获取会话摘要配置详情成功 {id}")
    return SuccessResponse(data=result_dict, msg="获取会话摘要配置详情成功")


@AgSessSummaryConfigRouter.get(
    "/list",
    summary="查询会话摘要配置列表",
    description="查询会话摘要配置列表"
)
async def get_sess_summary_configs_list_controller(
    page: PaginationQueryParam = Depends(),
    search: AgSessSummaryConfigQueryParam = Depends(),
    auth: AuthSchema = Depends(AuthPermission(["module_agno_manage:sess_summary_configs:query"]))
) -> JSONResponse:
    """
    查询会话摘要配置列表接口（数据库分页）
    
    参数:
    - page: PaginationQueryParam - 分页参数
    - search: AgSessSummaryConfigQueryParam - 查询参数
    - auth: AuthSchema - 认证信息
    
    返回:
    - JSONResponse - 包含会话摘要配置列表的JSON响应
    """
    result_dict = await AgSessSummaryConfigService.page_sess_summary_configs_service(
        auth=auth,
        page_no=page.page_no if page.page_no is not None else 1,
        page_size=page.page_size if page.page_size is not None else 10,
        search=search,
        order_by=page.order_by
    )
    log.info("查询会话摘要配置列表成功")
    return SuccessResponse(data=result_dict, msg="查询会话摘要配置列表成功")


@AgSessSummaryConfigRouter.post(
    "/create",
    summary="创建会话摘要配置",
    description="创建会话摘要配置"
)
async def create_sess_summary_configs_controller(
    data: AgSessSummaryConfigCreateSchema,
    auth: AuthSchema = Depends(AuthPermission(["module_agno_manage:sess_summary_configs:create"]))
) -> JSONResponse:
    """
    创建会话摘要配置接口
    
    参数:
    - data: AgSessSummaryConfigCreateSchema - 创建数据
    - auth: AuthSchema - 认证信息
    
    返回:
    - JSONResponse - 包含创建会话摘要配置结果的JSON响应
    """
    result_dict = await AgSessSummaryConfigService.create_sess_summary_configs_service(auth=auth, data=data)
    log.info("创建会话摘要配置成功")
    return SuccessResponse(data=result_dict, msg="创建会话摘要配置成功")


@AgSessSummaryConfigRouter.put(
    "/update/{id}",
    summary="修改会话摘要配置",
    description="修改会话摘要配置"
)
async def update_sess_summary_configs_controller(
    data: AgSessSummaryConfigUpdateSchema,
    id: int = Path(..., description="ID"),
    auth: AuthSchema = Depends(AuthPermission(["module_agno_manage:sess_summary_configs:update"]))
) -> JSONResponse:
    """
    修改会话摘要配置接口
    
    参数:
    - id: int - 数据ID
    - data: AgSessSummaryConfigUpdateSchema - 更新数据
    - auth: AuthSchema - 认证信息
    
    返回:
    - JSONResponse - 包含修改会话摘要配置结果的JSON响应
    """
    result_dict = await AgSessSummaryConfigService.update_sess_summary_configs_service(auth=auth, id=id, data=data)
    log.info("修改会话摘要配置成功")
    return SuccessResponse(data=result_dict, msg="修改会话摘要配置成功")


@AgSessSummaryConfigRouter.delete(
    "/delete",
    summary="删除会话摘要配置",
    description="删除会话摘要配置"
)
async def delete_sess_summary_configs_controller(
    ids: list[int] = Body(..., description="ID列表"),
    auth: AuthSchema = Depends(AuthPermission(["module_agno_manage:sess_summary_configs:delete"]))
) -> JSONResponse:
    """
    删除会话摘要配置接口
    
    参数:
    - ids: list[int] - 数据ID列表
    - auth: AuthSchema - 认证信息
    
    返回:
    - JSONResponse - 包含删除会话摘要配置结果的JSON响应
    """
    await AgSessSummaryConfigService.delete_sess_summary_configs_service(auth=auth, ids=ids)
    log.info(f"删除会话摘要配置成功: {ids}")
    return SuccessResponse(msg="删除会话摘要配置成功")


@AgSessSummaryConfigRouter.patch(
    "/available/setting",
    summary="批量修改会话摘要配置状态",
    description="批量修改会话摘要配置状态"
)
async def batch_set_available_sess_summary_configs_controller(
    data: BatchSetAvailable,
    auth: AuthSchema = Depends(AuthPermission(["module_agno_manage:sess_summary_configs:patch"]))
) -> JSONResponse:
    """
    批量修改会话摘要配置状态接口
    
    参数:
    - data: BatchSetAvailable - 批量修改状态数据
    - auth: AuthSchema - 认证信息
    
    返回:
    - JSONResponse - 包含批量修改会话摘要配置状态结果的JSON响应
    """
    await AgSessSummaryConfigService.set_available_sess_summary_configs_service(auth=auth, data=data)
    log.info(f"批量修改会话摘要配置状态成功: {data.ids}")
    return SuccessResponse(msg="批量修改会话摘要配置状态成功")


@AgSessSummaryConfigRouter.post(
    '/export',
    summary="导出会话摘要配置",
    description="导出会话摘要配置"
)
async def export_sess_summary_configs_list_controller(
    search: AgSessSummaryConfigQueryParam = Depends(),
    auth: AuthSchema = Depends(AuthPermission(["module_agno_manage:sess_summary_configs:export"]))
) -> StreamingResponse:
    """
    导出会话摘要配置接口
    
    参数:
    - search: AgSessSummaryConfigQueryParam - 查询参数
    - auth: AuthSchema - 认证信息
    
    返回:
    - StreamingResponse - 包含导出会话摘要配置数据的流式响应
    """
    result_dict_list = await AgSessSummaryConfigService.list_sess_summary_configs_service(search=search, auth=auth)
    export_result = await AgSessSummaryConfigService.batch_export_sess_summary_configs_service(obj_list=result_dict_list)
    log.info('导出会话摘要配置成功')
    return StreamResponse(
        data=bytes2file_response(export_result),
        media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        headers={'Content-Disposition': 'attachment; filename=ag_sess_summary_configs.xlsx'}
    )


@AgSessSummaryConfigRouter.post(
    '/import',
    summary="导入会话摘要配置",
    description="导入会话摘要配置"
)
async def import_sess_summary_configs_list_controller(
    file: UploadFile,
    auth: AuthSchema = Depends(AuthPermission(["module_agno_manage:sess_summary_configs:import"]))
) -> JSONResponse:
    """
    导入会话摘要配置接口
    
    参数:
    - file: UploadFile - 上传的Excel文件
    - auth: AuthSchema - 认证信息
    
    返回:
    - JSONResponse - 包含导入会话摘要配置结果的JSON响应
    """
    batch_import_result = await AgSessSummaryConfigService.batch_import_sess_summary_configs_service(file=file, auth=auth, update_support=True)
    log.info("导入会话摘要配置成功")
    return SuccessResponse(data=batch_import_result, msg="导入会话摘要配置成功")


@AgSessSummaryConfigRouter.post(
    '/download/template',
    summary="获取会话摘要配置导入模板",
    description="获取会话摘要配置导入模板",
    dependencies=[Depends(AuthPermission(["module_agno_manage:sess_summary_configs:download"]))]
)
async def export_sess_summary_configs_template_controller() -> StreamingResponse:
    """
    获取会话摘要配置导入模板接口
    
    返回:
    - StreamingResponse - 包含会话摘要配置导入模板的流式响应
    """
    import_template_result = await AgSessSummaryConfigService.import_template_download_sess_summary_configs_service()
    log.info('获取会话摘要配置导入模板成功')
    return StreamResponse(
        data=bytes2file_response(import_template_result),
        media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        headers={'Content-Disposition': 'attachment; filename=ag_sess_summary_configs_template.xlsx'}
    )
