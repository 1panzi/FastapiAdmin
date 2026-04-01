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

from .service import AgWorkflowNodeService
from .schema import AgWorkflowNodeCreateSchema, AgWorkflowNodeUpdateSchema, AgWorkflowNodeQueryParam

AgWorkflowNodeRouter = APIRouter(prefix='/workflow_nodes', tags=["工作流节点模块"]) 

@AgWorkflowNodeRouter.get(
    "/detail/{id}",
    summary="获取工作流节点详情",
    description="获取工作流节点详情"
)
async def get_workflow_nodes_detail_controller(
    id: int = Path(..., description="ID"),
    auth: AuthSchema = Depends(AuthPermission(["module_agno_manage:workflow_nodes:query"]))
) -> JSONResponse:
    """
    获取工作流节点详情接口
    
    参数:
    - id: int - 数据ID
    - auth: AuthSchema - 认证信息
    
    返回:
    - JSONResponse - 包含工作流节点详情的JSON响应
    """
    result_dict = await AgWorkflowNodeService.detail_workflow_nodes_service(auth=auth, id=id)
    log.info(f"获取工作流节点详情成功 {id}")
    return SuccessResponse(data=result_dict, msg="获取工作流节点详情成功")

@AgWorkflowNodeRouter.get(
    "/list",
    summary="查询工作流节点列表",
    description="查询工作流节点列表"
)
async def get_workflow_nodes_list_controller(
    page: PaginationQueryParam = Depends(),
    search: AgWorkflowNodeQueryParam = Depends(),
    auth: AuthSchema = Depends(AuthPermission(["module_agno_manage:workflow_nodes:query"]))
) -> JSONResponse:
    """
    查询工作流节点列表接口（数据库分页）
    
    参数:
    - page: PaginationQueryParam - 分页参数
    - search: AgWorkflowNodeQueryParam - 查询参数
    - auth: AuthSchema - 认证信息
    
    返回:
    - JSONResponse - 包含工作流节点列表的JSON响应
    """
    result_dict = await AgWorkflowNodeService.page_workflow_nodes_service(
        auth=auth,
        page_no=page.page_no if page.page_no is not None else 1,
        page_size=page.page_size if page.page_size is not None else 10,
        search=search,
        order_by=page.order_by
    )
    log.info("查询工作流节点列表成功")
    return SuccessResponse(data=result_dict, msg="查询工作流节点列表成功")

@AgWorkflowNodeRouter.post(
    "/create",
    summary="创建工作流节点",
    description="创建工作流节点"
)
async def create_workflow_nodes_controller(
    data: AgWorkflowNodeCreateSchema,
    auth: AuthSchema = Depends(AuthPermission(["module_agno_manage:workflow_nodes:create"]))
) -> JSONResponse:
    """
    创建工作流节点接口
    
    参数:
    - data: AgWorkflowNodeCreateSchema - 创建数据
    - auth: AuthSchema - 认证信息
    
    返回:
    - JSONResponse - 包含创建工作流节点结果的JSON响应
    """
    result_dict = await AgWorkflowNodeService.create_workflow_nodes_service(auth=auth, data=data)
    log.info("创建工作流节点成功")
    return SuccessResponse(data=result_dict, msg="创建工作流节点成功")

@AgWorkflowNodeRouter.put(
    "/update/{id}",
    summary="修改工作流节点",
    description="修改工作流节点"
)
async def update_workflow_nodes_controller(
    data: AgWorkflowNodeUpdateSchema,
    id: int = Path(..., description="ID"),
    auth: AuthSchema = Depends(AuthPermission(["module_agno_manage:workflow_nodes:update"]))
) -> JSONResponse:
    """
    修改工作流节点接口
    
    参数:
    - id: int - 数据ID
    - data: AgWorkflowNodeUpdateSchema - 更新数据
    - auth: AuthSchema - 认证信息
    
    返回:
    - JSONResponse - 包含修改工作流节点结果的JSON响应
    """
    result_dict = await AgWorkflowNodeService.update_workflow_nodes_service(auth=auth, id=id, data=data)
    log.info("修改工作流节点成功")
    return SuccessResponse(data=result_dict, msg="修改工作流节点成功")

@AgWorkflowNodeRouter.delete(
    "/delete",
    summary="删除工作流节点",
    description="删除工作流节点"
)
async def delete_workflow_nodes_controller(
    ids: list[int] = Body(..., description="ID列表"),
    auth: AuthSchema = Depends(AuthPermission(["module_agno_manage:workflow_nodes:delete"]))
) -> JSONResponse:
    """
    删除工作流节点接口
    
    参数:
    - ids: list[int] - 数据ID列表
    - auth: AuthSchema - 认证信息
    
    返回:
    - JSONResponse - 包含删除工作流节点结果的JSON响应
    """
    await AgWorkflowNodeService.delete_workflow_nodes_service(auth=auth, ids=ids)
    log.info(f"删除工作流节点成功: {ids}")
    return SuccessResponse(msg="删除工作流节点成功")

@AgWorkflowNodeRouter.patch(
    "/available/setting",
    summary="批量修改工作流节点状态",
    description="批量修改工作流节点状态"
)
async def batch_set_available_workflow_nodes_controller(
    data: BatchSetAvailable,
    auth: AuthSchema = Depends(AuthPermission(["module_agno_manage:workflow_nodes:patch"]))
) -> JSONResponse:
    """
    批量修改工作流节点状态接口
    
    参数:
    - data: BatchSetAvailable - 批量修改状态数据
    - auth: AuthSchema - 认证信息
    
    返回:
    - JSONResponse - 包含批量修改工作流节点状态结果的JSON响应
    """
    await AgWorkflowNodeService.set_available_workflow_nodes_service(auth=auth, data=data)
    log.info(f"批量修改工作流节点状态成功: {data.ids}")
    return SuccessResponse(msg="批量修改工作流节点状态成功")

@AgWorkflowNodeRouter.post(
    '/export',
    summary="导出工作流节点",
    description="导出工作流节点"
)
async def export_workflow_nodes_list_controller(
    search: AgWorkflowNodeQueryParam = Depends(),
    auth: AuthSchema = Depends(AuthPermission(["module_agno_manage:workflow_nodes:export"]))
) -> StreamingResponse:
    """
    导出工作流节点接口
    
    参数:
    - search: AgWorkflowNodeQueryParam - 查询参数
    - auth: AuthSchema - 认证信息
    
    返回:
    - StreamingResponse - 包含导出工作流节点数据的流式响应
    """
    result_dict_list = await AgWorkflowNodeService.list_workflow_nodes_service(search=search, auth=auth)
    export_result = await AgWorkflowNodeService.batch_export_workflow_nodes_service(obj_list=result_dict_list)
    log.info('导出工作流节点成功')
    return StreamResponse(
        data=bytes2file_response(export_result),
        media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        headers={'Content-Disposition': 'attachment; filename=ag_workflow_nodes.xlsx'}
    )

@AgWorkflowNodeRouter.post(
    '/import',
    summary="导入工作流节点",
    description="导入工作流节点"
)
async def import_workflow_nodes_list_controller(
    file: UploadFile,
    auth: AuthSchema = Depends(AuthPermission(["module_agno_manage:workflow_nodes:import"]))
) -> JSONResponse:
    """
    导入工作流节点接口
    
    参数:
    - file: UploadFile - 上传的Excel文件
    - auth: AuthSchema - 认证信息
    
    返回:
    - JSONResponse - 包含导入工作流节点结果的JSON响应
    """
    batch_import_result = await AgWorkflowNodeService.batch_import_workflow_nodes_service(file=file, auth=auth, update_support=True)
    log.info("导入工作流节点成功")
    return SuccessResponse(data=batch_import_result, msg="导入工作流节点成功")

@AgWorkflowNodeRouter.post(
    '/download/template',
    summary="获取工作流节点导入模板",
    description="获取工作流节点导入模板",
    dependencies=[Depends(AuthPermission(["module_agno_manage:workflow_nodes:download"]))]
)
async def export_workflow_nodes_template_controller() -> StreamingResponse:
    """
    获取工作流节点导入模板接口
    
    返回:
    - StreamingResponse - 包含工作流节点导入模板的流式响应
    """
    import_template_result = await AgWorkflowNodeService.import_template_download_workflow_nodes_service()
    log.info('获取工作流节点导入模板成功')
    return StreamResponse(
        data=bytes2file_response(import_template_result),
        media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        headers={'Content-Disposition': 'attachment; filename=ag_workflow_nodes_template.xlsx'}
    )