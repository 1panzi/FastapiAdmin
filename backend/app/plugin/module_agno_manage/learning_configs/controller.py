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

from .service import AgLearningConfigService
from .schema import AgLearningConfigCreateSchema, AgLearningConfigUpdateSchema, AgLearningConfigQueryParam

AgLearningConfigRouter = APIRouter(prefix='/learning_configs', tags=["学习管理模块"]) 

@AgLearningConfigRouter.get(
    "/detail/{id}",
    summary="获取学习管理详情",
    description="获取学习管理详情"
)
async def get_learning_configs_detail_controller(
    id: int = Path(..., description="ID"),
    auth: AuthSchema = Depends(AuthPermission(["module_agno_manage:learning_configs:query"]))
) -> JSONResponse:
    """
    获取学习管理详情接口
    
    参数:
    - id: int - 数据ID
    - auth: AuthSchema - 认证信息
    
    返回:
    - JSONResponse - 包含学习管理详情的JSON响应
    """
    result_dict = await AgLearningConfigService.detail_learning_configs_service(auth=auth, id=id)
    log.info(f"获取学习管理详情成功 {id}")
    return SuccessResponse(data=result_dict, msg="获取学习管理详情成功")

@AgLearningConfigRouter.get(
    "/list",
    summary="查询学习管理列表",
    description="查询学习管理列表"
)
async def get_learning_configs_list_controller(
    page: PaginationQueryParam = Depends(),
    search: AgLearningConfigQueryParam = Depends(),
    auth: AuthSchema = Depends(AuthPermission(["module_agno_manage:learning_configs:query"]))
) -> JSONResponse:
    """
    查询学习管理列表接口（数据库分页）
    
    参数:
    - page: PaginationQueryParam - 分页参数
    - search: AgLearningConfigQueryParam - 查询参数
    - auth: AuthSchema - 认证信息
    
    返回:
    - JSONResponse - 包含学习管理列表的JSON响应
    """
    result_dict = await AgLearningConfigService.page_learning_configs_service(
        auth=auth,
        page_no=page.page_no if page.page_no is not None else 1,
        page_size=page.page_size if page.page_size is not None else 10,
        search=search,
        order_by=page.order_by
    )
    log.info("查询学习管理列表成功")
    return SuccessResponse(data=result_dict, msg="查询学习管理列表成功")

@AgLearningConfigRouter.post(
    "/create",
    summary="创建学习管理",
    description="创建学习管理"
)
async def create_learning_configs_controller(
    data: AgLearningConfigCreateSchema,
    auth: AuthSchema = Depends(AuthPermission(["module_agno_manage:learning_configs:create"]))
) -> JSONResponse:
    """
    创建学习管理接口
    
    参数:
    - data: AgLearningConfigCreateSchema - 创建数据
    - auth: AuthSchema - 认证信息
    
    返回:
    - JSONResponse - 包含创建学习管理结果的JSON响应
    """
    result_dict = await AgLearningConfigService.create_learning_configs_service(auth=auth, data=data)
    log.info("创建学习管理成功")
    return SuccessResponse(data=result_dict, msg="创建学习管理成功")

@AgLearningConfigRouter.put(
    "/update/{id}",
    summary="修改学习管理",
    description="修改学习管理"
)
async def update_learning_configs_controller(
    data: AgLearningConfigUpdateSchema,
    id: int = Path(..., description="ID"),
    auth: AuthSchema = Depends(AuthPermission(["module_agno_manage:learning_configs:update"]))
) -> JSONResponse:
    """
    修改学习管理接口
    
    参数:
    - id: int - 数据ID
    - data: AgLearningConfigUpdateSchema - 更新数据
    - auth: AuthSchema - 认证信息
    
    返回:
    - JSONResponse - 包含修改学习管理结果的JSON响应
    """
    result_dict = await AgLearningConfigService.update_learning_configs_service(auth=auth, id=id, data=data)
    log.info("修改学习管理成功")
    return SuccessResponse(data=result_dict, msg="修改学习管理成功")

@AgLearningConfigRouter.delete(
    "/delete",
    summary="删除学习管理",
    description="删除学习管理"
)
async def delete_learning_configs_controller(
    ids: list[int] = Body(..., description="ID列表"),
    auth: AuthSchema = Depends(AuthPermission(["module_agno_manage:learning_configs:delete"]))
) -> JSONResponse:
    """
    删除学习管理接口
    
    参数:
    - ids: list[int] - 数据ID列表
    - auth: AuthSchema - 认证信息
    
    返回:
    - JSONResponse - 包含删除学习管理结果的JSON响应
    """
    await AgLearningConfigService.delete_learning_configs_service(auth=auth, ids=ids)
    log.info(f"删除学习管理成功: {ids}")
    return SuccessResponse(msg="删除学习管理成功")

@AgLearningConfigRouter.patch(
    "/available/setting",
    summary="批量修改学习管理状态",
    description="批量修改学习管理状态"
)
async def batch_set_available_learning_configs_controller(
    data: BatchSetAvailable,
    auth: AuthSchema = Depends(AuthPermission(["module_agno_manage:learning_configs:patch"]))
) -> JSONResponse:
    """
    批量修改学习管理状态接口
    
    参数:
    - data: BatchSetAvailable - 批量修改状态数据
    - auth: AuthSchema - 认证信息
    
    返回:
    - JSONResponse - 包含批量修改学习管理状态结果的JSON响应
    """
    await AgLearningConfigService.set_available_learning_configs_service(auth=auth, data=data)
    log.info(f"批量修改学习管理状态成功: {data.ids}")
    return SuccessResponse(msg="批量修改学习管理状态成功")

@AgLearningConfigRouter.post(
    '/export',
    summary="导出学习管理",
    description="导出学习管理"
)
async def export_learning_configs_list_controller(
    search: AgLearningConfigQueryParam = Depends(),
    auth: AuthSchema = Depends(AuthPermission(["module_agno_manage:learning_configs:export"]))
) -> StreamingResponse:
    """
    导出学习管理接口
    
    参数:
    - search: AgLearningConfigQueryParam - 查询参数
    - auth: AuthSchema - 认证信息
    
    返回:
    - StreamingResponse - 包含导出学习管理数据的流式响应
    """
    result_dict_list = await AgLearningConfigService.list_learning_configs_service(search=search, auth=auth)
    export_result = await AgLearningConfigService.batch_export_learning_configs_service(obj_list=result_dict_list)
    log.info('导出学习管理成功')
    return StreamResponse(
        data=bytes2file_response(export_result),
        media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        headers={'Content-Disposition': 'attachment; filename=ag_learning_configs.xlsx'}
    )

@AgLearningConfigRouter.post(
    '/import',
    summary="导入学习管理",
    description="导入学习管理"
)
async def import_learning_configs_list_controller(
    file: UploadFile,
    auth: AuthSchema = Depends(AuthPermission(["module_agno_manage:learning_configs:import"]))
) -> JSONResponse:
    """
    导入学习管理接口
    
    参数:
    - file: UploadFile - 上传的Excel文件
    - auth: AuthSchema - 认证信息
    
    返回:
    - JSONResponse - 包含导入学习管理结果的JSON响应
    """
    batch_import_result = await AgLearningConfigService.batch_import_learning_configs_service(file=file, auth=auth, update_support=True)
    log.info("导入学习管理成功")
    return SuccessResponse(data=batch_import_result, msg="导入学习管理成功")

@AgLearningConfigRouter.post(
    '/download/template',
    summary="获取学习管理导入模板",
    description="获取学习管理导入模板",
    dependencies=[Depends(AuthPermission(["module_agno_manage:learning_configs:download"]))]
)
async def export_learning_configs_template_controller() -> StreamingResponse:
    """
    获取学习管理导入模板接口
    
    返回:
    - StreamingResponse - 包含学习管理导入模板的流式响应
    """
    import_template_result = await AgLearningConfigService.import_template_download_learning_configs_service()
    log.info('获取学习管理导入模板成功')
    return StreamResponse(
        data=bytes2file_response(import_template_result),
        media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        headers={'Content-Disposition': 'attachment; filename=ag_learning_configs_template.xlsx'}
    )