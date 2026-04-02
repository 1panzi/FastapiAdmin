
from fastapi import APIRouter, Body, Depends, Path, UploadFile
from fastapi.responses import JSONResponse, StreamingResponse

from app.api.v1.module_system.auth.schema import AuthSchema
from app.common.response import StreamResponse, SuccessResponse
from app.core.base_params import PaginationQueryParam
from app.core.base_schema import BatchSetAvailable
from app.core.dependencies import AuthPermission
from app.core.logger import log
from app.utils.common_util import bytes2file_response

from .schema import AgWorkflowCreateSchema, AgWorkflowQueryParam, AgWorkflowUpdateSchema
from .service import AgWorkflowService

AgWorkflowRouter = APIRouter(prefix='/workflows', tags=["workflow管理模块"])


@AgWorkflowRouter.get(
    "/detail/{id}",
    summary="获取workflow管理详情",
    description="获取workflow管理详情"
)
async def get_workflows_detail_controller(
    id: int = Path(..., description="ID"),
    auth: AuthSchema = Depends(AuthPermission(["module_agno_manage:workflows:query"]))
) -> JSONResponse:
    """
    获取workflow管理详情接口
    
    参数:
    - id: int - 数据ID
    - auth: AuthSchema - 认证信息
    
    返回:
    - JSONResponse - 包含workflow管理详情的JSON响应
    """
    result_dict = await AgWorkflowService.detail_workflows_service(auth=auth, id=id)
    log.info(f"获取workflow管理详情成功 {id}")
    return SuccessResponse(data=result_dict, msg="获取workflow管理详情成功")


@AgWorkflowRouter.get(
    "/list",
    summary="查询workflow管理列表",
    description="查询workflow管理列表"
)
async def get_workflows_list_controller(
    page: PaginationQueryParam = Depends(),
    search: AgWorkflowQueryParam = Depends(),
    auth: AuthSchema = Depends(AuthPermission(["module_agno_manage:workflows:query"]))
) -> JSONResponse:
    """
    查询workflow管理列表接口（数据库分页）
    
    参数:
    - page: PaginationQueryParam - 分页参数
    - search: AgWorkflowQueryParam - 查询参数
    - auth: AuthSchema - 认证信息
    
    返回:
    - JSONResponse - 包含workflow管理列表的JSON响应
    """
    result_dict = await AgWorkflowService.page_workflows_service(
        auth=auth,
        page_no=page.page_no if page.page_no is not None else 1,
        page_size=page.page_size if page.page_size is not None else 10,
        search=search,
        order_by=page.order_by
    )
    log.info("查询workflow管理列表成功")
    return SuccessResponse(data=result_dict, msg="查询workflow管理列表成功")


@AgWorkflowRouter.post(
    "/create",
    summary="创建workflow管理",
    description="创建workflow管理"
)
async def create_workflows_controller(
    data: AgWorkflowCreateSchema,
    auth: AuthSchema = Depends(AuthPermission(["module_agno_manage:workflows:create"]))
) -> JSONResponse:
    """
    创建workflow管理接口
    
    参数:
    - data: AgWorkflowCreateSchema - 创建数据
    - auth: AuthSchema - 认证信息
    
    返回:
    - JSONResponse - 包含创建workflow管理结果的JSON响应
    """
    result_dict = await AgWorkflowService.create_workflows_service(auth=auth, data=data)
    log.info("创建workflow管理成功")
    return SuccessResponse(data=result_dict, msg="创建workflow管理成功")


@AgWorkflowRouter.put(
    "/update/{id}",
    summary="修改workflow管理",
    description="修改workflow管理"
)
async def update_workflows_controller(
    data: AgWorkflowUpdateSchema,
    id: int = Path(..., description="ID"),
    auth: AuthSchema = Depends(AuthPermission(["module_agno_manage:workflows:update"]))
) -> JSONResponse:
    """
    修改workflow管理接口
    
    参数:
    - id: int - 数据ID
    - data: AgWorkflowUpdateSchema - 更新数据
    - auth: AuthSchema - 认证信息
    
    返回:
    - JSONResponse - 包含修改workflow管理结果的JSON响应
    """
    result_dict = await AgWorkflowService.update_workflows_service(auth=auth, id=id, data=data)
    log.info("修改workflow管理成功")
    return SuccessResponse(data=result_dict, msg="修改workflow管理成功")


@AgWorkflowRouter.delete(
    "/delete",
    summary="删除workflow管理",
    description="删除workflow管理"
)
async def delete_workflows_controller(
    ids: list[int] = Body(..., description="ID列表"),
    auth: AuthSchema = Depends(AuthPermission(["module_agno_manage:workflows:delete"]))
) -> JSONResponse:
    """
    删除workflow管理接口
    
    参数:
    - ids: list[int] - 数据ID列表
    - auth: AuthSchema - 认证信息
    
    返回:
    - JSONResponse - 包含删除workflow管理结果的JSON响应
    """
    await AgWorkflowService.delete_workflows_service(auth=auth, ids=ids)
    log.info(f"删除workflow管理成功: {ids}")
    return SuccessResponse(msg="删除workflow管理成功")


@AgWorkflowRouter.patch(
    "/available/setting",
    summary="批量修改workflow管理状态",
    description="批量修改workflow管理状态"
)
async def batch_set_available_workflows_controller(
    data: BatchSetAvailable,
    auth: AuthSchema = Depends(AuthPermission(["module_agno_manage:workflows:patch"]))
) -> JSONResponse:
    """
    批量修改workflow管理状态接口
    
    参数:
    - data: BatchSetAvailable - 批量修改状态数据
    - auth: AuthSchema - 认证信息
    
    返回:
    - JSONResponse - 包含批量修改workflow管理状态结果的JSON响应
    """
    await AgWorkflowService.set_available_workflows_service(auth=auth, data=data)
    log.info(f"批量修改workflow管理状态成功: {data.ids}")
    return SuccessResponse(msg="批量修改workflow管理状态成功")


@AgWorkflowRouter.post(
    '/export',
    summary="导出workflow管理",
    description="导出workflow管理"
)
async def export_workflows_list_controller(
    search: AgWorkflowQueryParam = Depends(),
    auth: AuthSchema = Depends(AuthPermission(["module_agno_manage:workflows:export"]))
) -> StreamingResponse:
    """
    导出workflow管理接口
    
    参数:
    - search: AgWorkflowQueryParam - 查询参数
    - auth: AuthSchema - 认证信息
    
    返回:
    - StreamingResponse - 包含导出workflow管理数据的流式响应
    """
    result_dict_list = await AgWorkflowService.list_workflows_service(search=search, auth=auth)
    export_result = await AgWorkflowService.batch_export_workflows_service(obj_list=result_dict_list)
    log.info('导出workflow管理成功')
    return StreamResponse(
        data=bytes2file_response(export_result),
        media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        headers={'Content-Disposition': 'attachment; filename=ag_workflows.xlsx'}
    )


@AgWorkflowRouter.post(
    '/import',
    summary="导入workflow管理",
    description="导入workflow管理"
)
async def import_workflows_list_controller(
    file: UploadFile,
    auth: AuthSchema = Depends(AuthPermission(["module_agno_manage:workflows:import"]))
) -> JSONResponse:
    """
    导入workflow管理接口
    
    参数:
    - file: UploadFile - 上传的Excel文件
    - auth: AuthSchema - 认证信息
    
    返回:
    - JSONResponse - 包含导入workflow管理结果的JSON响应
    """
    batch_import_result = await AgWorkflowService.batch_import_workflows_service(file=file, auth=auth, update_support=True)
    log.info("导入workflow管理成功")
    return SuccessResponse(data=batch_import_result, msg="导入workflow管理成功")


@AgWorkflowRouter.post(
    '/download/template',
    summary="获取workflow管理导入模板",
    description="获取workflow管理导入模板",
    dependencies=[Depends(AuthPermission(["module_agno_manage:workflows:download"]))]
)
async def export_workflows_template_controller() -> StreamingResponse:
    """
    获取workflow管理导入模板接口
    
    返回:
    - StreamingResponse - 包含workflow管理导入模板的流式响应
    """
    import_template_result = await AgWorkflowService.import_template_download_workflows_service()
    log.info('获取workflow管理导入模板成功')
    return StreamResponse(
        data=bytes2file_response(import_template_result),
        media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        headers={'Content-Disposition': 'attachment; filename=ag_workflows_template.xlsx'}
    )
