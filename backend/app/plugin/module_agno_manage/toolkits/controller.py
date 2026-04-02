
from fastapi import APIRouter, Body, Depends, Path, Query, UploadFile
from fastapi.responses import JSONResponse, StreamingResponse

from app.api.v1.module_system.auth.schema import AuthSchema
from app.common.response import StreamResponse, SuccessResponse
from app.core.base_params import PaginationQueryParam
from app.core.base_schema import BatchSetAvailable
from app.core.dependencies import AuthPermission
from app.core.logger import log
from app.utils.common_util import bytes2file_response

from .schema import AgToolkitCreateSchema, AgToolkitQueryParam, AgToolkitUpdateSchema
from .service import AgToolkitService

AgToolkitRouter = APIRouter(prefix='/toolkits', tags=["工具管理模块"])


@AgToolkitRouter.get(
    "/detail/{id}",
    summary="获取工具管理详情",
    description="获取工具管理详情"
)
async def get_toolkits_detail_controller(
    id: int = Path(..., description="ID"),
    auth: AuthSchema = Depends(AuthPermission(["module_agno_manage:toolkits:query"]))
) -> JSONResponse:
    """
    获取工具管理详情接口
    
    参数:
    - id: int - 数据ID
    - auth: AuthSchema - 认证信息
    
    返回:
    - JSONResponse - 包含工具管理详情的JSON响应
    """
    result_dict = await AgToolkitService.detail_toolkits_service(auth=auth, id=id)
    log.info(f"获取工具管理详情成功 {id}")
    return SuccessResponse(data=result_dict, msg="获取工具管理详情成功")


@AgToolkitRouter.get(
    "/list",
    summary="查询工具管理列表",
    description="查询工具管理列表"
)
async def get_toolkits_list_controller(
    page: PaginationQueryParam = Depends(),
    search: AgToolkitQueryParam = Depends(),
    auth: AuthSchema = Depends(AuthPermission(["module_agno_manage:toolkits:query"]))
) -> JSONResponse:
    """
    查询工具管理列表接口（数据库分页）
    
    参数:
    - page: PaginationQueryParam - 分页参数
    - search: AgToolkitQueryParam - 查询参数
    - auth: AuthSchema - 认证信息
    
    返回:
    - JSONResponse - 包含工具管理列表的JSON响应
    """
    result_dict = await AgToolkitService.page_toolkits_service(
        auth=auth,
        page_no=page.page_no if page.page_no is not None else 1,
        page_size=page.page_size if page.page_size is not None else 10,
        search=search,
        order_by=page.order_by
    )
    log.info("查询工具管理列表成功")
    return SuccessResponse(data=result_dict, msg="查询工具管理列表成功")


@AgToolkitRouter.post(
    "/create",
    summary="创建工具管理",
    description="创建工具管理"
)
async def create_toolkits_controller(
    data: AgToolkitCreateSchema,
    auth: AuthSchema = Depends(AuthPermission(["module_agno_manage:toolkits:create"]))
) -> JSONResponse:
    """
    创建工具管理接口
    
    参数:
    - data: AgToolkitCreateSchema - 创建数据
    - auth: AuthSchema - 认证信息
    
    返回:
    - JSONResponse - 包含创建工具管理结果的JSON响应
    """
    result_dict = await AgToolkitService.create_toolkits_service(auth=auth, data=data)
    log.info("创建工具管理成功")
    return SuccessResponse(data=result_dict, msg="创建工具管理成功")


@AgToolkitRouter.put(
    "/update/{id}",
    summary="修改工具管理",
    description="修改工具管理"
)
async def update_toolkits_controller(
    data: AgToolkitUpdateSchema,
    id: int = Path(..., description="ID"),
    auth: AuthSchema = Depends(AuthPermission(["module_agno_manage:toolkits:update"]))
) -> JSONResponse:
    """
    修改工具管理接口
    
    参数:
    - id: int - 数据ID
    - data: AgToolkitUpdateSchema - 更新数据
    - auth: AuthSchema - 认证信息
    
    返回:
    - JSONResponse - 包含修改工具管理结果的JSON响应
    """
    result_dict = await AgToolkitService.update_toolkits_service(auth=auth, id=id, data=data)
    log.info("修改工具管理成功")
    return SuccessResponse(data=result_dict, msg="修改工具管理成功")


@AgToolkitRouter.delete(
    "/delete",
    summary="删除工具管理",
    description="删除工具管理"
)
async def delete_toolkits_controller(
    ids: list[int] = Body(..., description="ID列表"),
    auth: AuthSchema = Depends(AuthPermission(["module_agno_manage:toolkits:delete"]))
) -> JSONResponse:
    """
    删除工具管理接口
    
    参数:
    - ids: list[int] - 数据ID列表
    - auth: AuthSchema - 认证信息
    
    返回:
    - JSONResponse - 包含删除工具管理结果的JSON响应
    """
    await AgToolkitService.delete_toolkits_service(auth=auth, ids=ids)
    log.info(f"删除工具管理成功: {ids}")
    return SuccessResponse(msg="删除工具管理成功")


@AgToolkitRouter.patch(
    "/available/setting",
    summary="批量修改工具管理状态",
    description="批量修改工具管理状态"
)
async def batch_set_available_toolkits_controller(
    data: BatchSetAvailable,
    auth: AuthSchema = Depends(AuthPermission(["module_agno_manage:toolkits:patch"]))
) -> JSONResponse:
    """
    批量修改工具管理状态接口
    
    参数:
    - data: BatchSetAvailable - 批量修改状态数据
    - auth: AuthSchema - 认证信息
    
    返回:
    - JSONResponse - 包含批量修改工具管理状态结果的JSON响应
    """
    await AgToolkitService.set_available_toolkits_service(auth=auth, data=data)
    log.info(f"批量修改工具管理状态成功: {data.ids}")
    return SuccessResponse(msg="批量修改工具管理状态成功")


@AgToolkitRouter.post(
    '/export',
    summary="导出工具管理",
    description="导出工具管理"
)
async def export_toolkits_list_controller(
    search: AgToolkitQueryParam = Depends(),
    auth: AuthSchema = Depends(AuthPermission(["module_agno_manage:toolkits:export"]))
) -> StreamingResponse:
    """
    导出工具管理接口
    
    参数:
    - search: AgToolkitQueryParam - 查询参数
    - auth: AuthSchema - 认证信息
    
    返回:
    - StreamingResponse - 包含导出工具管理数据的流式响应
    """
    result_dict_list = await AgToolkitService.list_toolkits_service(search=search, auth=auth)
    export_result = await AgToolkitService.batch_export_toolkits_service(obj_list=result_dict_list)
    log.info('导出工具管理成功')
    return StreamResponse(
        data=bytes2file_response(export_result),
        media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        headers={'Content-Disposition': 'attachment; filename=ag_toolkits.xlsx'}
    )


@AgToolkitRouter.post(
    '/import',
    summary="导入工具管理",
    description="导入工具管理"
)
async def import_toolkits_list_controller(
    file: UploadFile,
    auth: AuthSchema = Depends(AuthPermission(["module_agno_manage:toolkits:import"]))
) -> JSONResponse:
    """
    导入工具管理接口
    
    参数:
    - file: UploadFile - 上传的Excel文件
    - auth: AuthSchema - 认证信息
    
    返回:
    - JSONResponse - 包含导入工具管理结果的JSON响应
    """
    batch_import_result = await AgToolkitService.batch_import_toolkits_service(file=file, auth=auth, update_support=True)
    log.info("导入工具管理成功")
    return SuccessResponse(data=batch_import_result, msg="导入工具管理成功")


@AgToolkitRouter.post(
    '/download/template',
    summary="获取工具管理导入模板",
    description="获取工具管理导入模板",
    dependencies=[Depends(AuthPermission(["module_agno_manage:toolkits:download"]))]
)
async def export_toolkits_template_controller() -> StreamingResponse:
    """
    获取工具管理导入模板接口
    
    返回:
    - StreamingResponse - 包含工具管理导入模板的流式响应
    """
    import_template_result = await AgToolkitService.import_template_download_toolkits_service()
    log.info('获取工具管理导入模板成功')
    return StreamResponse(
        data=bytes2file_response(import_template_result),
        media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        headers={'Content-Disposition': 'attachment; filename=ag_toolkits_template.xlsx'}
    )


@AgToolkitRouter.get(
    "/agno/catalog",
    summary="获取 Agno 内置工具目录",
    description="返回所有可用的 Agno 内置工具列表，供创建 toolkit 时选择 module_path + class_name"
)
async def get_agno_catalog_controller(
    category: str | None = Query(None, description="按分类过滤（如 搜索、数据库）"),
    keyword: str | None = Query(None, description="关键词搜索"),
    auth: AuthSchema = Depends(AuthPermission(["module_agno_manage:toolkits:query"]))
) -> JSONResponse:
    result = AgToolkitService.list_agno_catalog_service(category=category, keyword=keyword)
    return SuccessResponse(data=result, msg="获取 Agno 工具目录成功")


@AgToolkitRouter.get(
    "/agno/categories",
    summary="获取 Agno 工具分类列表",
    description="返回所有工具分类"
)
async def get_agno_categories_controller(
    auth: AuthSchema = Depends(AuthPermission(["module_agno_manage:toolkits:query"]))
) -> JSONResponse:
    result = AgToolkitService.list_agno_categories_service()
    return SuccessResponse(data=result, msg="获取工具分类成功")
