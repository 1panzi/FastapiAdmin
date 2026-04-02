
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
    AgCultureConfigCreateSchema,
    AgCultureConfigQueryParam,
    AgCultureConfigUpdateSchema,
)
from .service import AgCultureConfigService

AgCultureConfigRouter = APIRouter(prefix='/culture_configs', tags=["文化配置模块"])


@AgCultureConfigRouter.get(
    "/detail/{id}",
    summary="获取文化配置详情",
    description="获取文化配置详情"
)
async def get_culture_configs_detail_controller(
    id: int = Path(..., description="ID"),
    auth: AuthSchema = Depends(AuthPermission(["module_agno_manage:culture_configs:query"]))
) -> JSONResponse:
    """
    获取文化配置详情接口
    
    参数:
    - id: int - 数据ID
    - auth: AuthSchema - 认证信息
    
    返回:
    - JSONResponse - 包含文化配置详情的JSON响应
    """
    result_dict = await AgCultureConfigService.detail_culture_configs_service(auth=auth, id=id)
    log.info(f"获取文化配置详情成功 {id}")
    return SuccessResponse(data=result_dict, msg="获取文化配置详情成功")


@AgCultureConfigRouter.get(
    "/list",
    summary="查询文化配置列表",
    description="查询文化配置列表"
)
async def get_culture_configs_list_controller(
    page: PaginationQueryParam = Depends(),
    search: AgCultureConfigQueryParam = Depends(),
    auth: AuthSchema = Depends(AuthPermission(["module_agno_manage:culture_configs:query"]))
) -> JSONResponse:
    """
    查询文化配置列表接口（数据库分页）
    
    参数:
    - page: PaginationQueryParam - 分页参数
    - search: AgCultureConfigQueryParam - 查询参数
    - auth: AuthSchema - 认证信息
    
    返回:
    - JSONResponse - 包含文化配置列表的JSON响应
    """
    result_dict = await AgCultureConfigService.page_culture_configs_service(
        auth=auth,
        page_no=page.page_no if page.page_no is not None else 1,
        page_size=page.page_size if page.page_size is not None else 10,
        search=search,
        order_by=page.order_by
    )
    log.info("查询文化配置列表成功")
    return SuccessResponse(data=result_dict, msg="查询文化配置列表成功")


@AgCultureConfigRouter.post(
    "/create",
    summary="创建文化配置",
    description="创建文化配置"
)
async def create_culture_configs_controller(
    data: AgCultureConfigCreateSchema,
    auth: AuthSchema = Depends(AuthPermission(["module_agno_manage:culture_configs:create"]))
) -> JSONResponse:
    """
    创建文化配置接口
    
    参数:
    - data: AgCultureConfigCreateSchema - 创建数据
    - auth: AuthSchema - 认证信息
    
    返回:
    - JSONResponse - 包含创建文化配置结果的JSON响应
    """
    result_dict = await AgCultureConfigService.create_culture_configs_service(auth=auth, data=data)
    log.info("创建文化配置成功")
    return SuccessResponse(data=result_dict, msg="创建文化配置成功")


@AgCultureConfigRouter.put(
    "/update/{id}",
    summary="修改文化配置",
    description="修改文化配置"
)
async def update_culture_configs_controller(
    data: AgCultureConfigUpdateSchema,
    id: int = Path(..., description="ID"),
    auth: AuthSchema = Depends(AuthPermission(["module_agno_manage:culture_configs:update"]))
) -> JSONResponse:
    """
    修改文化配置接口
    
    参数:
    - id: int - 数据ID
    - data: AgCultureConfigUpdateSchema - 更新数据
    - auth: AuthSchema - 认证信息
    
    返回:
    - JSONResponse - 包含修改文化配置结果的JSON响应
    """
    result_dict = await AgCultureConfigService.update_culture_configs_service(auth=auth, id=id, data=data)
    log.info("修改文化配置成功")
    return SuccessResponse(data=result_dict, msg="修改文化配置成功")


@AgCultureConfigRouter.delete(
    "/delete",
    summary="删除文化配置",
    description="删除文化配置"
)
async def delete_culture_configs_controller(
    ids: list[int] = Body(..., description="ID列表"),
    auth: AuthSchema = Depends(AuthPermission(["module_agno_manage:culture_configs:delete"]))
) -> JSONResponse:
    """
    删除文化配置接口
    
    参数:
    - ids: list[int] - 数据ID列表
    - auth: AuthSchema - 认证信息
    
    返回:
    - JSONResponse - 包含删除文化配置结果的JSON响应
    """
    await AgCultureConfigService.delete_culture_configs_service(auth=auth, ids=ids)
    log.info(f"删除文化配置成功: {ids}")
    return SuccessResponse(msg="删除文化配置成功")


@AgCultureConfigRouter.patch(
    "/available/setting",
    summary="批量修改文化配置状态",
    description="批量修改文化配置状态"
)
async def batch_set_available_culture_configs_controller(
    data: BatchSetAvailable,
    auth: AuthSchema = Depends(AuthPermission(["module_agno_manage:culture_configs:patch"]))
) -> JSONResponse:
    """
    批量修改文化配置状态接口
    
    参数:
    - data: BatchSetAvailable - 批量修改状态数据
    - auth: AuthSchema - 认证信息
    
    返回:
    - JSONResponse - 包含批量修改文化配置状态结果的JSON响应
    """
    await AgCultureConfigService.set_available_culture_configs_service(auth=auth, data=data)
    log.info(f"批量修改文化配置状态成功: {data.ids}")
    return SuccessResponse(msg="批量修改文化配置状态成功")


@AgCultureConfigRouter.post(
    '/export',
    summary="导出文化配置",
    description="导出文化配置"
)
async def export_culture_configs_list_controller(
    search: AgCultureConfigQueryParam = Depends(),
    auth: AuthSchema = Depends(AuthPermission(["module_agno_manage:culture_configs:export"]))
) -> StreamingResponse:
    """
    导出文化配置接口
    
    参数:
    - search: AgCultureConfigQueryParam - 查询参数
    - auth: AuthSchema - 认证信息
    
    返回:
    - StreamingResponse - 包含导出文化配置数据的流式响应
    """
    result_dict_list = await AgCultureConfigService.list_culture_configs_service(search=search, auth=auth)
    export_result = await AgCultureConfigService.batch_export_culture_configs_service(obj_list=result_dict_list)
    log.info('导出文化配置成功')
    return StreamResponse(
        data=bytes2file_response(export_result),
        media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        headers={'Content-Disposition': 'attachment; filename=ag_culture_configs.xlsx'}
    )


@AgCultureConfigRouter.post(
    '/import',
    summary="导入文化配置",
    description="导入文化配置"
)
async def import_culture_configs_list_controller(
    file: UploadFile,
    auth: AuthSchema = Depends(AuthPermission(["module_agno_manage:culture_configs:import"]))
) -> JSONResponse:
    """
    导入文化配置接口
    
    参数:
    - file: UploadFile - 上传的Excel文件
    - auth: AuthSchema - 认证信息
    
    返回:
    - JSONResponse - 包含导入文化配置结果的JSON响应
    """
    batch_import_result = await AgCultureConfigService.batch_import_culture_configs_service(file=file, auth=auth, update_support=True)
    log.info("导入文化配置成功")
    return SuccessResponse(data=batch_import_result, msg="导入文化配置成功")


@AgCultureConfigRouter.post(
    '/download/template',
    summary="获取文化配置导入模板",
    description="获取文化配置导入模板",
    dependencies=[Depends(AuthPermission(["module_agno_manage:culture_configs:download"]))]
)
async def export_culture_configs_template_controller() -> StreamingResponse:
    """
    获取文化配置导入模板接口
    
    返回:
    - StreamingResponse - 包含文化配置导入模板的流式响应
    """
    import_template_result = await AgCultureConfigService.import_template_download_culture_configs_service()
    log.info('获取文化配置导入模板成功')
    return StreamResponse(
        data=bytes2file_response(import_template_result),
        media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        headers={'Content-Disposition': 'attachment; filename=ag_culture_configs_template.xlsx'}
    )
