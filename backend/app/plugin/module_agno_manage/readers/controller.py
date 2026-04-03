# -*- coding: utf-8 -*-

from fastapi import APIRouter, Depends, UploadFile, Body, Path, Query
from fastapi.responses import StreamingResponse, JSONResponse

from app.api.v1.module_system.auth.schema import AuthSchema
from app.common.response import SuccessResponse, StreamResponse
from app.core.dependencies import AuthPermission
from app.core.base_params import PaginationQueryParam
from app.utils.common_util import bytes2file_response
from app.core.logger import log
from app.core.base_schema import BatchSetAvailable

from .service import AgReaderService
from .schema import AgReaderCreateSchema, AgReaderUpdateSchema, AgReaderQueryParam

AgReaderRouter = APIRouter(prefix='/readers', tags=["reader管理模块"]) 

@AgReaderRouter.get(
    "/detail/{id}",
    summary="获取reader管理详情",
    description="获取reader管理详情"
)
async def get_readers_detail_controller(
    id: int = Path(..., description="ID"),
    auth: AuthSchema = Depends(AuthPermission(["module_agno_manage:readers:query"]))
) -> JSONResponse:
    """
    获取reader管理详情接口
    
    参数:
    - id: int - 数据ID
    - auth: AuthSchema - 认证信息
    
    返回:
    - JSONResponse - 包含reader管理详情的JSON响应
    """
    result_dict = await AgReaderService.detail_readers_service(auth=auth, id=id)
    log.info(f"获取reader管理详情成功 {id}")
    return SuccessResponse(data=result_dict, msg="获取reader管理详情成功")

@AgReaderRouter.get(
    "/list",
    summary="查询reader管理列表",
    description="查询reader管理列表"
)
async def get_readers_list_controller(
    page: PaginationQueryParam = Depends(),
    search: AgReaderQueryParam = Depends(),
    auth: AuthSchema = Depends(AuthPermission(["module_agno_manage:readers:query"]))
) -> JSONResponse:
    """
    查询reader管理列表接口（数据库分页）
    
    参数:
    - page: PaginationQueryParam - 分页参数
    - search: AgReaderQueryParam - 查询参数
    - auth: AuthSchema - 认证信息
    
    返回:
    - JSONResponse - 包含reader管理列表的JSON响应
    """
    result_dict = await AgReaderService.page_readers_service(
        auth=auth,
        page_no=page.page_no if page.page_no is not None else 1,
        page_size=page.page_size if page.page_size is not None else 10,
        search=search,
        order_by=page.order_by
    )
    log.info("查询reader管理列表成功")
    return SuccessResponse(data=result_dict, msg="查询reader管理列表成功")

@AgReaderRouter.post(
    "/create",
    summary="创建reader管理",
    description="创建reader管理"
)
async def create_readers_controller(
    data: AgReaderCreateSchema,
    auth: AuthSchema = Depends(AuthPermission(["module_agno_manage:readers:create"]))
) -> JSONResponse:
    """
    创建reader管理接口
    
    参数:
    - data: AgReaderCreateSchema - 创建数据
    - auth: AuthSchema - 认证信息
    
    返回:
    - JSONResponse - 包含创建reader管理结果的JSON响应
    """
    result_dict = await AgReaderService.create_readers_service(auth=auth, data=data)
    log.info("创建reader管理成功")
    return SuccessResponse(data=result_dict, msg="创建reader管理成功")

@AgReaderRouter.put(
    "/update/{id}",
    summary="修改reader管理",
    description="修改reader管理"
)
async def update_readers_controller(
    data: AgReaderUpdateSchema,
    id: int = Path(..., description="ID"),
    auth: AuthSchema = Depends(AuthPermission(["module_agno_manage:readers:update"]))
) -> JSONResponse:
    """
    修改reader管理接口
    
    参数:
    - id: int - 数据ID
    - data: AgReaderUpdateSchema - 更新数据
    - auth: AuthSchema - 认证信息
    
    返回:
    - JSONResponse - 包含修改reader管理结果的JSON响应
    """
    result_dict = await AgReaderService.update_readers_service(auth=auth, id=id, data=data)
    log.info("修改reader管理成功")
    return SuccessResponse(data=result_dict, msg="修改reader管理成功")

@AgReaderRouter.delete(
    "/delete",
    summary="删除reader管理",
    description="删除reader管理"
)
async def delete_readers_controller(
    ids: list[int] = Body(..., description="ID列表"),
    auth: AuthSchema = Depends(AuthPermission(["module_agno_manage:readers:delete"]))
) -> JSONResponse:
    """
    删除reader管理接口
    
    参数:
    - ids: list[int] - 数据ID列表
    - auth: AuthSchema - 认证信息
    
    返回:
    - JSONResponse - 包含删除reader管理结果的JSON响应
    """
    await AgReaderService.delete_readers_service(auth=auth, ids=ids)
    log.info(f"删除reader管理成功: {ids}")
    return SuccessResponse(msg="删除reader管理成功")

@AgReaderRouter.patch(
    "/available/setting",
    summary="批量修改reader管理状态",
    description="批量修改reader管理状态"
)
async def batch_set_available_readers_controller(
    data: BatchSetAvailable,
    auth: AuthSchema = Depends(AuthPermission(["module_agno_manage:readers:patch"]))
) -> JSONResponse:
    """
    批量修改reader管理状态接口
    
    参数:
    - data: BatchSetAvailable - 批量修改状态数据
    - auth: AuthSchema - 认证信息
    
    返回:
    - JSONResponse - 包含批量修改reader管理状态结果的JSON响应
    """
    await AgReaderService.set_available_readers_service(auth=auth, data=data)
    log.info(f"批量修改reader管理状态成功: {data.ids}")
    return SuccessResponse(msg="批量修改reader管理状态成功")

@AgReaderRouter.post(
    '/export',
    summary="导出reader管理",
    description="导出reader管理"
)
async def export_readers_list_controller(
    search: AgReaderQueryParam = Depends(),
    auth: AuthSchema = Depends(AuthPermission(["module_agno_manage:readers:export"]))
) -> StreamingResponse:
    """
    导出reader管理接口
    
    参数:
    - search: AgReaderQueryParam - 查询参数
    - auth: AuthSchema - 认证信息
    
    返回:
    - StreamingResponse - 包含导出reader管理数据的流式响应
    """
    result_dict_list = await AgReaderService.list_readers_service(search=search, auth=auth)
    export_result = await AgReaderService.batch_export_readers_service(obj_list=result_dict_list)
    log.info('导出reader管理成功')
    return StreamResponse(
        data=bytes2file_response(export_result),
        media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        headers={'Content-Disposition': 'attachment; filename=ag_readers.xlsx'}
    )

@AgReaderRouter.post(
    '/import',
    summary="导入reader管理",
    description="导入reader管理"
)
async def import_readers_list_controller(
    file: UploadFile,
    auth: AuthSchema = Depends(AuthPermission(["module_agno_manage:readers:import"]))
) -> JSONResponse:
    """
    导入reader管理接口
    
    参数:
    - file: UploadFile - 上传的Excel文件
    - auth: AuthSchema - 认证信息
    
    返回:
    - JSONResponse - 包含导入reader管理结果的JSON响应
    """
    batch_import_result = await AgReaderService.batch_import_readers_service(file=file, auth=auth, update_support=True)
    log.info("导入reader管理成功")
    return SuccessResponse(data=batch_import_result, msg="导入reader管理成功")

@AgReaderRouter.post(
    '/download/template',
    summary="获取reader管理导入模板",
    description="获取reader管理导入模板",
    dependencies=[Depends(AuthPermission(["module_agno_manage:readers:download"]))]
)
async def export_readers_template_controller() -> StreamingResponse:
    """
    获取reader管理导入模板接口

    返回:
    - StreamingResponse - 包含reader管理导入模板的流式响应
    """
    import_template_result = await AgReaderService.import_template_download_readers_service()
    log.info('获取reader管理导入模板成功')
    return StreamResponse(
        data=bytes2file_response(import_template_result),
        media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        headers={'Content-Disposition': 'attachment; filename=ag_readers_template.xlsx'}
    )


@AgReaderRouter.get(
    "/agno/reader_types",
    summary="获取支持的Reader类型列表",
    description="返回所有支持的 reader_type 元数据，含默认策略、专属参数 schema，供前端动态渲染表单"
)
async def get_reader_types_controller() -> JSONResponse:
    result = AgReaderService.list_reader_types_service()
    return SuccessResponse(data=result, msg="获取Reader类型列表成功")


@AgReaderRouter.get(
    "/agno/reader_types/{reader_type}",
    summary="获取指定Reader类型的元数据",
    description="返回指定 reader_type 的详细元数据，含专属参数 schema"
)
async def get_reader_type_info_controller(
    reader_type: str = Path(..., description="Reader类型，如 pdf/csv/website")
) -> JSONResponse:
    result = AgReaderService.get_reader_info_service(reader_type)
    if result is None:
        return SuccessResponse(data=None, msg=f"未找到Reader类型: {reader_type}")
    return SuccessResponse(data=result, msg="获取Reader类型信息成功")


@AgReaderRouter.get(
    "/agno/reader_types/{reader_type}/chunking_strategies",
    summary="获取指定Reader类型支持的Chunking策略",
    description="直接调用 Agno reader 类的 get_supported_chunking_strategies()，返回该 reader_type 支持的策略名列表"
)
async def get_reader_supported_strategies_controller(
    reader_type: str = Path(..., description="Reader类型，如 pdf/csv/website")
) -> JSONResponse:
    result = AgReaderService.get_supported_strategies_service(reader_type)
    return SuccessResponse(data=result, msg="获取支持策略列表成功")


@AgReaderRouter.get(
    "/agno/chunking_strategies",
    summary="获取全部Chunking策略列表",
    description="返回所有 chunking 策略元数据，含各策略的参数 schema"
)
async def get_chunking_strategies_controller() -> JSONResponse:
    result = AgReaderService.list_chunking_strategies_service()
    return SuccessResponse(data=result, msg="获取Chunking策略列表成功")


@AgReaderRouter.get(
    "/agno/chunking_strategies/{strategy}",
    summary="获取指定Chunking策略的详细参数",
    description="返回指定策略的完整 param_schema，如 FixedSizeChunker / SemanticChunker"
)
async def get_chunking_strategy_detail_controller(
    strategy: str = Path(..., description="策略名，如 FixedSizeChunker / SemanticChunker")
) -> JSONResponse:
    result = AgReaderService.get_chunking_strategy_info_service(strategy)
    if result is None:
        return SuccessResponse(data=None, msg=f"未找到Chunking策略: {strategy}")
    return SuccessResponse(data=result, msg="获取Chunking策略详情成功")