
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
    AgCompressionConfigCreateSchema,
    AgCompressionConfigQueryParam,
    AgCompressionConfigUpdateSchema,
)
from .service import AgCompressionConfigService

AgCompressionConfigRouter = APIRouter(prefix='/compression_configs', tags=["压缩管理器模块"])


@AgCompressionConfigRouter.get(
    "/detail/{id}",
    summary="获取压缩管理器详情",
    description="获取压缩管理器详情"
)
async def get_compression_configs_detail_controller(
    id: int = Path(..., description="ID"),
    auth: AuthSchema = Depends(AuthPermission(["module_agno_manage:compression_configs:query"]))
) -> JSONResponse:
    """
    获取压缩管理器详情接口
    
    参数:
    - id: int - 数据ID
    - auth: AuthSchema - 认证信息
    
    返回:
    - JSONResponse - 包含压缩管理器详情的JSON响应
    """
    result_dict = await AgCompressionConfigService.detail_compression_configs_service(auth=auth, id=id)
    log.info(f"获取压缩管理器详情成功 {id}")
    return SuccessResponse(data=result_dict, msg="获取压缩管理器详情成功")


@AgCompressionConfigRouter.get(
    "/list",
    summary="查询压缩管理器列表",
    description="查询压缩管理器列表"
)
async def get_compression_configs_list_controller(
    page: PaginationQueryParam = Depends(),
    search: AgCompressionConfigQueryParam = Depends(),
    auth: AuthSchema = Depends(AuthPermission(["module_agno_manage:compression_configs:query"]))
) -> JSONResponse:
    """
    查询压缩管理器列表接口（数据库分页）
    
    参数:
    - page: PaginationQueryParam - 分页参数
    - search: AgCompressionConfigQueryParam - 查询参数
    - auth: AuthSchema - 认证信息
    
    返回:
    - JSONResponse - 包含压缩管理器列表的JSON响应
    """
    result_dict = await AgCompressionConfigService.page_compression_configs_service(
        auth=auth,
        page_no=page.page_no if page.page_no is not None else 1,
        page_size=page.page_size if page.page_size is not None else 10,
        search=search,
        order_by=page.order_by
    )
    log.info("查询压缩管理器列表成功")
    return SuccessResponse(data=result_dict, msg="查询压缩管理器列表成功")


@AgCompressionConfigRouter.post(
    "/create",
    summary="创建压缩管理器",
    description="创建压缩管理器"
)
async def create_compression_configs_controller(
    data: AgCompressionConfigCreateSchema,
    auth: AuthSchema = Depends(AuthPermission(["module_agno_manage:compression_configs:create"]))
) -> JSONResponse:
    """
    创建压缩管理器接口
    
    参数:
    - data: AgCompressionConfigCreateSchema - 创建数据
    - auth: AuthSchema - 认证信息
    
    返回:
    - JSONResponse - 包含创建压缩管理器结果的JSON响应
    """
    result_dict = await AgCompressionConfigService.create_compression_configs_service(auth=auth, data=data)
    log.info("创建压缩管理器成功")
    return SuccessResponse(data=result_dict, msg="创建压缩管理器成功")


@AgCompressionConfigRouter.put(
    "/update/{id}",
    summary="修改压缩管理器",
    description="修改压缩管理器"
)
async def update_compression_configs_controller(
    data: AgCompressionConfigUpdateSchema,
    id: int = Path(..., description="ID"),
    auth: AuthSchema = Depends(AuthPermission(["module_agno_manage:compression_configs:update"]))
) -> JSONResponse:
    """
    修改压缩管理器接口
    
    参数:
    - id: int - 数据ID
    - data: AgCompressionConfigUpdateSchema - 更新数据
    - auth: AuthSchema - 认证信息
    
    返回:
    - JSONResponse - 包含修改压缩管理器结果的JSON响应
    """
    result_dict = await AgCompressionConfigService.update_compression_configs_service(auth=auth, id=id, data=data)
    log.info("修改压缩管理器成功")
    return SuccessResponse(data=result_dict, msg="修改压缩管理器成功")


@AgCompressionConfigRouter.delete(
    "/delete",
    summary="删除压缩管理器",
    description="删除压缩管理器"
)
async def delete_compression_configs_controller(
    ids: list[int] = Body(..., description="ID列表"),
    auth: AuthSchema = Depends(AuthPermission(["module_agno_manage:compression_configs:delete"]))
) -> JSONResponse:
    """
    删除压缩管理器接口
    
    参数:
    - ids: list[int] - 数据ID列表
    - auth: AuthSchema - 认证信息
    
    返回:
    - JSONResponse - 包含删除压缩管理器结果的JSON响应
    """
    await AgCompressionConfigService.delete_compression_configs_service(auth=auth, ids=ids)
    log.info(f"删除压缩管理器成功: {ids}")
    return SuccessResponse(msg="删除压缩管理器成功")


@AgCompressionConfigRouter.patch(
    "/available/setting",
    summary="批量修改压缩管理器状态",
    description="批量修改压缩管理器状态"
)
async def batch_set_available_compression_configs_controller(
    data: BatchSetAvailable,
    auth: AuthSchema = Depends(AuthPermission(["module_agno_manage:compression_configs:patch"]))
) -> JSONResponse:
    """
    批量修改压缩管理器状态接口
    
    参数:
    - data: BatchSetAvailable - 批量修改状态数据
    - auth: AuthSchema - 认证信息
    
    返回:
    - JSONResponse - 包含批量修改压缩管理器状态结果的JSON响应
    """
    await AgCompressionConfigService.set_available_compression_configs_service(auth=auth, data=data)
    log.info(f"批量修改压缩管理器状态成功: {data.ids}")
    return SuccessResponse(msg="批量修改压缩管理器状态成功")


@AgCompressionConfigRouter.post(
    '/export',
    summary="导出压缩管理器",
    description="导出压缩管理器"
)
async def export_compression_configs_list_controller(
    search: AgCompressionConfigQueryParam = Depends(),
    auth: AuthSchema = Depends(AuthPermission(["module_agno_manage:compression_configs:export"]))
) -> StreamingResponse:
    """
    导出压缩管理器接口
    
    参数:
    - search: AgCompressionConfigQueryParam - 查询参数
    - auth: AuthSchema - 认证信息
    
    返回:
    - StreamingResponse - 包含导出压缩管理器数据的流式响应
    """
    result_dict_list = await AgCompressionConfigService.list_compression_configs_service(search=search, auth=auth)
    export_result = await AgCompressionConfigService.batch_export_compression_configs_service(obj_list=result_dict_list)
    log.info('导出压缩管理器成功')
    return StreamResponse(
        data=bytes2file_response(export_result),
        media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        headers={'Content-Disposition': 'attachment; filename=ag_compression_configs.xlsx'}
    )


@AgCompressionConfigRouter.post(
    '/import',
    summary="导入压缩管理器",
    description="导入压缩管理器"
)
async def import_compression_configs_list_controller(
    file: UploadFile,
    auth: AuthSchema = Depends(AuthPermission(["module_agno_manage:compression_configs:import"]))
) -> JSONResponse:
    """
    导入压缩管理器接口
    
    参数:
    - file: UploadFile - 上传的Excel文件
    - auth: AuthSchema - 认证信息
    
    返回:
    - JSONResponse - 包含导入压缩管理器结果的JSON响应
    """
    batch_import_result = await AgCompressionConfigService.batch_import_compression_configs_service(file=file, auth=auth, update_support=True)
    log.info("导入压缩管理器成功")
    return SuccessResponse(data=batch_import_result, msg="导入压缩管理器成功")


@AgCompressionConfigRouter.post(
    '/download/template',
    summary="获取压缩管理器导入模板",
    description="获取压缩管理器导入模板",
    dependencies=[Depends(AuthPermission(["module_agno_manage:compression_configs:download"]))]
)
async def export_compression_configs_template_controller() -> StreamingResponse:
    """
    获取压缩管理器导入模板接口
    
    返回:
    - StreamingResponse - 包含压缩管理器导入模板的流式响应
    """
    import_template_result = await AgCompressionConfigService.import_template_download_compression_configs_service()
    log.info('获取压缩管理器导入模板成功')
    return StreamResponse(
        data=bytes2file_response(import_template_result),
        media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        headers={'Content-Disposition': 'attachment; filename=ag_compression_configs_template.xlsx'}
    )
