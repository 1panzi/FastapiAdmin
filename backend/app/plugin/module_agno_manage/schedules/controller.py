
from fastapi import APIRouter, Body, Depends, Path, UploadFile
from fastapi.responses import JSONResponse, StreamingResponse

from app.api.v1.module_system.auth.schema import AuthSchema
from app.common.response import StreamResponse, SuccessResponse
from app.core.base_params import PaginationQueryParam
from app.core.base_schema import BatchSetAvailable
from app.core.dependencies import AuthPermission
from app.core.logger import log
from app.utils.common_util import bytes2file_response

from .schema import AgScheduleCreateSchema, AgScheduleQueryParam, AgScheduleUpdateSchema
from .service import AgScheduleService

AgScheduleRouter = APIRouter(prefix='/schedules', tags=["定时任务管理模块"])


@AgScheduleRouter.get(
    "/detail/{id}",
    summary="获取定时任务管理详情",
    description="获取定时任务管理详情"
)
async def get_schedules_detail_controller(
    id: int = Path(..., description="ID"),
    auth: AuthSchema = Depends(AuthPermission(["module_agno_manage:schedules:query"]))
) -> JSONResponse:
    """
    获取定时任务管理详情接口
    
    参数:
    - id: int - 数据ID
    - auth: AuthSchema - 认证信息
    
    返回:
    - JSONResponse - 包含定时任务管理详情的JSON响应
    """
    result_dict = await AgScheduleService.detail_schedules_service(auth=auth, id=id)
    log.info(f"获取定时任务管理详情成功 {id}")
    return SuccessResponse(data=result_dict, msg="获取定时任务管理详情成功")


@AgScheduleRouter.get(
    "/list",
    summary="查询定时任务管理列表",
    description="查询定时任务管理列表"
)
async def get_schedules_list_controller(
    page: PaginationQueryParam = Depends(),
    search: AgScheduleQueryParam = Depends(),
    auth: AuthSchema = Depends(AuthPermission(["module_agno_manage:schedules:query"]))
) -> JSONResponse:
    """
    查询定时任务管理列表接口（数据库分页）
    
    参数:
    - page: PaginationQueryParam - 分页参数
    - search: AgScheduleQueryParam - 查询参数
    - auth: AuthSchema - 认证信息
    
    返回:
    - JSONResponse - 包含定时任务管理列表的JSON响应
    """
    result_dict = await AgScheduleService.page_schedules_service(
        auth=auth,
        page_no=page.page_no if page.page_no is not None else 1,
        page_size=page.page_size if page.page_size is not None else 10,
        search=search,
        order_by=page.order_by
    )
    log.info("查询定时任务管理列表成功")
    return SuccessResponse(data=result_dict, msg="查询定时任务管理列表成功")


@AgScheduleRouter.post(
    "/create",
    summary="创建定时任务管理",
    description="创建定时任务管理"
)
async def create_schedules_controller(
    data: AgScheduleCreateSchema,
    auth: AuthSchema = Depends(AuthPermission(["module_agno_manage:schedules:create"]))
) -> JSONResponse:
    """
    创建定时任务管理接口
    
    参数:
    - data: AgScheduleCreateSchema - 创建数据
    - auth: AuthSchema - 认证信息
    
    返回:
    - JSONResponse - 包含创建定时任务管理结果的JSON响应
    """
    result_dict = await AgScheduleService.create_schedules_service(auth=auth, data=data)
    log.info("创建定时任务管理成功")
    return SuccessResponse(data=result_dict, msg="创建定时任务管理成功")


@AgScheduleRouter.put(
    "/update/{id}",
    summary="修改定时任务管理",
    description="修改定时任务管理"
)
async def update_schedules_controller(
    data: AgScheduleUpdateSchema,
    id: int = Path(..., description="ID"),
    auth: AuthSchema = Depends(AuthPermission(["module_agno_manage:schedules:update"]))
) -> JSONResponse:
    """
    修改定时任务管理接口
    
    参数:
    - id: int - 数据ID
    - data: AgScheduleUpdateSchema - 更新数据
    - auth: AuthSchema - 认证信息
    
    返回:
    - JSONResponse - 包含修改定时任务管理结果的JSON响应
    """
    result_dict = await AgScheduleService.update_schedules_service(auth=auth, id=id, data=data)
    log.info("修改定时任务管理成功")
    return SuccessResponse(data=result_dict, msg="修改定时任务管理成功")


@AgScheduleRouter.delete(
    "/delete",
    summary="删除定时任务管理",
    description="删除定时任务管理"
)
async def delete_schedules_controller(
    ids: list[int] = Body(..., description="ID列表"),
    auth: AuthSchema = Depends(AuthPermission(["module_agno_manage:schedules:delete"]))
) -> JSONResponse:
    """
    删除定时任务管理接口
    
    参数:
    - ids: list[int] - 数据ID列表
    - auth: AuthSchema - 认证信息
    
    返回:
    - JSONResponse - 包含删除定时任务管理结果的JSON响应
    """
    await AgScheduleService.delete_schedules_service(auth=auth, ids=ids)
    log.info(f"删除定时任务管理成功: {ids}")
    return SuccessResponse(msg="删除定时任务管理成功")


@AgScheduleRouter.patch(
    "/available/setting",
    summary="批量修改定时任务管理状态",
    description="批量修改定时任务管理状态"
)
async def batch_set_available_schedules_controller(
    data: BatchSetAvailable,
    auth: AuthSchema = Depends(AuthPermission(["module_agno_manage:schedules:patch"]))
) -> JSONResponse:
    """
    批量修改定时任务管理状态接口
    
    参数:
    - data: BatchSetAvailable - 批量修改状态数据
    - auth: AuthSchema - 认证信息
    
    返回:
    - JSONResponse - 包含批量修改定时任务管理状态结果的JSON响应
    """
    await AgScheduleService.set_available_schedules_service(auth=auth, data=data)
    log.info(f"批量修改定时任务管理状态成功: {data.ids}")
    return SuccessResponse(msg="批量修改定时任务管理状态成功")


@AgScheduleRouter.post(
    '/export',
    summary="导出定时任务管理",
    description="导出定时任务管理"
)
async def export_schedules_list_controller(
    search: AgScheduleQueryParam = Depends(),
    auth: AuthSchema = Depends(AuthPermission(["module_agno_manage:schedules:export"]))
) -> StreamingResponse:
    """
    导出定时任务管理接口
    
    参数:
    - search: AgScheduleQueryParam - 查询参数
    - auth: AuthSchema - 认证信息
    
    返回:
    - StreamingResponse - 包含导出定时任务管理数据的流式响应
    """
    result_dict_list = await AgScheduleService.list_schedules_service(search=search, auth=auth)
    export_result = await AgScheduleService.batch_export_schedules_service(obj_list=result_dict_list)
    log.info('导出定时任务管理成功')
    return StreamResponse(
        data=bytes2file_response(export_result),
        media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        headers={'Content-Disposition': 'attachment; filename=ag_schedules.xlsx'}
    )


@AgScheduleRouter.post(
    '/import',
    summary="导入定时任务管理",
    description="导入定时任务管理"
)
async def import_schedules_list_controller(
    file: UploadFile,
    auth: AuthSchema = Depends(AuthPermission(["module_agno_manage:schedules:import"]))
) -> JSONResponse:
    """
    导入定时任务管理接口
    
    参数:
    - file: UploadFile - 上传的Excel文件
    - auth: AuthSchema - 认证信息
    
    返回:
    - JSONResponse - 包含导入定时任务管理结果的JSON响应
    """
    batch_import_result = await AgScheduleService.batch_import_schedules_service(file=file, auth=auth, update_support=True)
    log.info("导入定时任务管理成功")
    return SuccessResponse(data=batch_import_result, msg="导入定时任务管理成功")


@AgScheduleRouter.post(
    '/download/template',
    summary="获取定时任务管理导入模板",
    description="获取定时任务管理导入模板",
    dependencies=[Depends(AuthPermission(["module_agno_manage:schedules:download"]))]
)
async def export_schedules_template_controller() -> StreamingResponse:
    """
    获取定时任务管理导入模板接口
    
    返回:
    - StreamingResponse - 包含定时任务管理导入模板的流式响应
    """
    import_template_result = await AgScheduleService.import_template_download_schedules_service()
    log.info('获取定时任务管理导入模板成功')
    return StreamResponse(
        data=bytes2file_response(import_template_result),
        media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        headers={'Content-Disposition': 'attachment; filename=ag_schedules_template.xlsx'}
    )
