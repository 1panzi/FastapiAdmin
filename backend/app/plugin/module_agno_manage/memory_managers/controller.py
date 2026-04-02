
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
    AgMemoryManagerCreateSchema,
    AgMemoryManagerQueryParam,
    AgMemoryManagerUpdateSchema,
)
from .service import AgMemoryManagerService

AgMemoryManagerRouter = APIRouter(prefix='/memory_managers', tags=["记忆管理模块"])


@AgMemoryManagerRouter.get(
    "/detail/{id}",
    summary="获取记忆管理详情",
    description="获取记忆管理详情"
)
async def get_memory_managers_detail_controller(
    id: int = Path(..., description="ID"),
    auth: AuthSchema = Depends(AuthPermission(["module_agno_manage:memory_managers:query"]))
) -> JSONResponse:
    """
    获取记忆管理详情接口
    
    参数:
    - id: int - 数据ID
    - auth: AuthSchema - 认证信息
    
    返回:
    - JSONResponse - 包含记忆管理详情的JSON响应
    """
    result_dict = await AgMemoryManagerService.detail_memory_managers_service(auth=auth, id=id)
    log.info(f"获取记忆管理详情成功 {id}")
    return SuccessResponse(data=result_dict, msg="获取记忆管理详情成功")


@AgMemoryManagerRouter.get(
    "/list",
    summary="查询记忆管理列表",
    description="查询记忆管理列表"
)
async def get_memory_managers_list_controller(
    page: PaginationQueryParam = Depends(),
    search: AgMemoryManagerQueryParam = Depends(),
    auth: AuthSchema = Depends(AuthPermission(["module_agno_manage:memory_managers:query"]))
) -> JSONResponse:
    """
    查询记忆管理列表接口（数据库分页）
    
    参数:
    - page: PaginationQueryParam - 分页参数
    - search: AgMemoryManagerQueryParam - 查询参数
    - auth: AuthSchema - 认证信息
    
    返回:
    - JSONResponse - 包含记忆管理列表的JSON响应
    """
    result_dict = await AgMemoryManagerService.page_memory_managers_service(
        auth=auth,
        page_no=page.page_no if page.page_no is not None else 1,
        page_size=page.page_size if page.page_size is not None else 10,
        search=search,
        order_by=page.order_by
    )
    log.info("查询记忆管理列表成功")
    return SuccessResponse(data=result_dict, msg="查询记忆管理列表成功")


@AgMemoryManagerRouter.post(
    "/create",
    summary="创建记忆管理",
    description="创建记忆管理"
)
async def create_memory_managers_controller(
    data: AgMemoryManagerCreateSchema,
    auth: AuthSchema = Depends(AuthPermission(["module_agno_manage:memory_managers:create"]))
) -> JSONResponse:
    """
    创建记忆管理接口
    
    参数:
    - data: AgMemoryManagerCreateSchema - 创建数据
    - auth: AuthSchema - 认证信息
    
    返回:
    - JSONResponse - 包含创建记忆管理结果的JSON响应
    """
    result_dict = await AgMemoryManagerService.create_memory_managers_service(auth=auth, data=data)
    log.info("创建记忆管理成功")
    return SuccessResponse(data=result_dict, msg="创建记忆管理成功")


@AgMemoryManagerRouter.put(
    "/update/{id}",
    summary="修改记忆管理",
    description="修改记忆管理"
)
async def update_memory_managers_controller(
    data: AgMemoryManagerUpdateSchema,
    id: int = Path(..., description="ID"),
    auth: AuthSchema = Depends(AuthPermission(["module_agno_manage:memory_managers:update"]))
) -> JSONResponse:
    """
    修改记忆管理接口
    
    参数:
    - id: int - 数据ID
    - data: AgMemoryManagerUpdateSchema - 更新数据
    - auth: AuthSchema - 认证信息
    
    返回:
    - JSONResponse - 包含修改记忆管理结果的JSON响应
    """
    result_dict = await AgMemoryManagerService.update_memory_managers_service(auth=auth, id=id, data=data)
    log.info("修改记忆管理成功")
    return SuccessResponse(data=result_dict, msg="修改记忆管理成功")


@AgMemoryManagerRouter.delete(
    "/delete",
    summary="删除记忆管理",
    description="删除记忆管理"
)
async def delete_memory_managers_controller(
    ids: list[int] = Body(..., description="ID列表"),
    auth: AuthSchema = Depends(AuthPermission(["module_agno_manage:memory_managers:delete"]))
) -> JSONResponse:
    """
    删除记忆管理接口
    
    参数:
    - ids: list[int] - 数据ID列表
    - auth: AuthSchema - 认证信息
    
    返回:
    - JSONResponse - 包含删除记忆管理结果的JSON响应
    """
    await AgMemoryManagerService.delete_memory_managers_service(auth=auth, ids=ids)
    log.info(f"删除记忆管理成功: {ids}")
    return SuccessResponse(msg="删除记忆管理成功")


@AgMemoryManagerRouter.patch(
    "/available/setting",
    summary="批量修改记忆管理状态",
    description="批量修改记忆管理状态"
)
async def batch_set_available_memory_managers_controller(
    data: BatchSetAvailable,
    auth: AuthSchema = Depends(AuthPermission(["module_agno_manage:memory_managers:patch"]))
) -> JSONResponse:
    """
    批量修改记忆管理状态接口
    
    参数:
    - data: BatchSetAvailable - 批量修改状态数据
    - auth: AuthSchema - 认证信息
    
    返回:
    - JSONResponse - 包含批量修改记忆管理状态结果的JSON响应
    """
    await AgMemoryManagerService.set_available_memory_managers_service(auth=auth, data=data)
    log.info(f"批量修改记忆管理状态成功: {data.ids}")
    return SuccessResponse(msg="批量修改记忆管理状态成功")


@AgMemoryManagerRouter.post(
    '/export',
    summary="导出记忆管理",
    description="导出记忆管理"
)
async def export_memory_managers_list_controller(
    search: AgMemoryManagerQueryParam = Depends(),
    auth: AuthSchema = Depends(AuthPermission(["module_agno_manage:memory_managers:export"]))
) -> StreamingResponse:
    """
    导出记忆管理接口
    
    参数:
    - search: AgMemoryManagerQueryParam - 查询参数
    - auth: AuthSchema - 认证信息
    
    返回:
    - StreamingResponse - 包含导出记忆管理数据的流式响应
    """
    result_dict_list = await AgMemoryManagerService.list_memory_managers_service(search=search, auth=auth)
    export_result = await AgMemoryManagerService.batch_export_memory_managers_service(obj_list=result_dict_list)
    log.info('导出记忆管理成功')
    return StreamResponse(
        data=bytes2file_response(export_result),
        media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        headers={'Content-Disposition': 'attachment; filename=ag_memory_managers.xlsx'}
    )


@AgMemoryManagerRouter.post(
    '/import',
    summary="导入记忆管理",
    description="导入记忆管理"
)
async def import_memory_managers_list_controller(
    file: UploadFile,
    auth: AuthSchema = Depends(AuthPermission(["module_agno_manage:memory_managers:import"]))
) -> JSONResponse:
    """
    导入记忆管理接口
    
    参数:
    - file: UploadFile - 上传的Excel文件
    - auth: AuthSchema - 认证信息
    
    返回:
    - JSONResponse - 包含导入记忆管理结果的JSON响应
    """
    batch_import_result = await AgMemoryManagerService.batch_import_memory_managers_service(file=file, auth=auth, update_support=True)
    log.info("导入记忆管理成功")
    return SuccessResponse(data=batch_import_result, msg="导入记忆管理成功")


@AgMemoryManagerRouter.post(
    '/download/template',
    summary="获取记忆管理导入模板",
    description="获取记忆管理导入模板",
    dependencies=[Depends(AuthPermission(["module_agno_manage:memory_managers:download"]))]
)
async def export_memory_managers_template_controller() -> StreamingResponse:
    """
    获取记忆管理导入模板接口
    
    返回:
    - StreamingResponse - 包含记忆管理导入模板的流式响应
    """
    import_template_result = await AgMemoryManagerService.import_template_download_memory_managers_service()
    log.info('获取记忆管理导入模板成功')
    return StreamResponse(
        data=bytes2file_response(import_template_result),
        media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        headers={'Content-Disposition': 'attachment; filename=ag_memory_managers_template.xlsx'}
    )
