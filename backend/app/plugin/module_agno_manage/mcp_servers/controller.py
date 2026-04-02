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

from .service import AgMcpServerService
from .schema import AgMcpServerCreateSchema, AgMcpServerUpdateSchema, AgMcpServerQueryParam

AgMcpServerRouter = APIRouter(prefix='/mcp_servers', tags=["MCP服务模块"]) 

@AgMcpServerRouter.get(
    "/detail/{id}",
    summary="获取MCP服务详情",
    description="获取MCP服务详情"
)
async def get_mcp_servers_detail_controller(
    id: int = Path(..., description="ID"),
    auth: AuthSchema = Depends(AuthPermission(["module_agno_manage:mcp_servers:query"]))
) -> JSONResponse:
    """
    获取MCP服务详情接口
    
    参数:
    - id: int - 数据ID
    - auth: AuthSchema - 认证信息
    
    返回:
    - JSONResponse - 包含MCP服务详情的JSON响应
    """
    result_dict = await AgMcpServerService.detail_mcp_servers_service(auth=auth, id=id)
    log.info(f"获取MCP服务详情成功 {id}")
    return SuccessResponse(data=result_dict, msg="获取MCP服务详情成功")

@AgMcpServerRouter.get(
    "/list",
    summary="查询MCP服务列表",
    description="查询MCP服务列表"
)
async def get_mcp_servers_list_controller(
    page: PaginationQueryParam = Depends(),
    search: AgMcpServerQueryParam = Depends(),
    auth: AuthSchema = Depends(AuthPermission(["module_agno_manage:mcp_servers:query"]))
) -> JSONResponse:
    """
    查询MCP服务列表接口（数据库分页）
    
    参数:
    - page: PaginationQueryParam - 分页参数
    - search: AgMcpServerQueryParam - 查询参数
    - auth: AuthSchema - 认证信息
    
    返回:
    - JSONResponse - 包含MCP服务列表的JSON响应
    """
    result_dict = await AgMcpServerService.page_mcp_servers_service(
        auth=auth,
        page_no=page.page_no if page.page_no is not None else 1,
        page_size=page.page_size if page.page_size is not None else 10,
        search=search,
        order_by=page.order_by
    )
    log.info("查询MCP服务列表成功")
    return SuccessResponse(data=result_dict, msg="查询MCP服务列表成功")

@AgMcpServerRouter.post(
    "/create",
    summary="创建MCP服务",
    description="创建MCP服务"
)
async def create_mcp_servers_controller(
    data: AgMcpServerCreateSchema,
    auth: AuthSchema = Depends(AuthPermission(["module_agno_manage:mcp_servers:create"]))
) -> JSONResponse:
    """
    创建MCP服务接口
    
    参数:
    - data: AgMcpServerCreateSchema - 创建数据
    - auth: AuthSchema - 认证信息
    
    返回:
    - JSONResponse - 包含创建MCP服务结果的JSON响应
    """
    result_dict = await AgMcpServerService.create_mcp_servers_service(auth=auth, data=data)
    log.info("创建MCP服务成功")
    return SuccessResponse(data=result_dict, msg="创建MCP服务成功")

@AgMcpServerRouter.put(
    "/update/{id}",
    summary="修改MCP服务",
    description="修改MCP服务"
)
async def update_mcp_servers_controller(
    data: AgMcpServerUpdateSchema,
    id: int = Path(..., description="ID"),
    auth: AuthSchema = Depends(AuthPermission(["module_agno_manage:mcp_servers:update"]))
) -> JSONResponse:
    """
    修改MCP服务接口
    
    参数:
    - id: int - 数据ID
    - data: AgMcpServerUpdateSchema - 更新数据
    - auth: AuthSchema - 认证信息
    
    返回:
    - JSONResponse - 包含修改MCP服务结果的JSON响应
    """
    result_dict = await AgMcpServerService.update_mcp_servers_service(auth=auth, id=id, data=data)
    log.info("修改MCP服务成功")
    return SuccessResponse(data=result_dict, msg="修改MCP服务成功")

@AgMcpServerRouter.delete(
    "/delete",
    summary="删除MCP服务",
    description="删除MCP服务"
)
async def delete_mcp_servers_controller(
    ids: list[int] = Body(..., description="ID列表"),
    auth: AuthSchema = Depends(AuthPermission(["module_agno_manage:mcp_servers:delete"]))
) -> JSONResponse:
    """
    删除MCP服务接口
    
    参数:
    - ids: list[int] - 数据ID列表
    - auth: AuthSchema - 认证信息
    
    返回:
    - JSONResponse - 包含删除MCP服务结果的JSON响应
    """
    await AgMcpServerService.delete_mcp_servers_service(auth=auth, ids=ids)
    log.info(f"删除MCP服务成功: {ids}")
    return SuccessResponse(msg="删除MCP服务成功")

@AgMcpServerRouter.patch(
    "/available/setting",
    summary="批量修改MCP服务状态",
    description="批量修改MCP服务状态"
)
async def batch_set_available_mcp_servers_controller(
    data: BatchSetAvailable,
    auth: AuthSchema = Depends(AuthPermission(["module_agno_manage:mcp_servers:patch"]))
) -> JSONResponse:
    """
    批量修改MCP服务状态接口
    
    参数:
    - data: BatchSetAvailable - 批量修改状态数据
    - auth: AuthSchema - 认证信息
    
    返回:
    - JSONResponse - 包含批量修改MCP服务状态结果的JSON响应
    """
    await AgMcpServerService.set_available_mcp_servers_service(auth=auth, data=data)
    log.info(f"批量修改MCP服务状态成功: {data.ids}")
    return SuccessResponse(msg="批量修改MCP服务状态成功")

@AgMcpServerRouter.post(
    '/export',
    summary="导出MCP服务",
    description="导出MCP服务"
)
async def export_mcp_servers_list_controller(
    search: AgMcpServerQueryParam = Depends(),
    auth: AuthSchema = Depends(AuthPermission(["module_agno_manage:mcp_servers:export"]))
) -> StreamingResponse:
    """
    导出MCP服务接口
    
    参数:
    - search: AgMcpServerQueryParam - 查询参数
    - auth: AuthSchema - 认证信息
    
    返回:
    - StreamingResponse - 包含导出MCP服务数据的流式响应
    """
    result_dict_list = await AgMcpServerService.list_mcp_servers_service(search=search, auth=auth)
    export_result = await AgMcpServerService.batch_export_mcp_servers_service(obj_list=result_dict_list)
    log.info('导出MCP服务成功')
    return StreamResponse(
        data=bytes2file_response(export_result),
        media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        headers={'Content-Disposition': 'attachment; filename=ag_mcp_servers.xlsx'}
    )

@AgMcpServerRouter.post(
    '/import',
    summary="导入MCP服务",
    description="导入MCP服务"
)
async def import_mcp_servers_list_controller(
    file: UploadFile,
    auth: AuthSchema = Depends(AuthPermission(["module_agno_manage:mcp_servers:import"]))
) -> JSONResponse:
    """
    导入MCP服务接口
    
    参数:
    - file: UploadFile - 上传的Excel文件
    - auth: AuthSchema - 认证信息
    
    返回:
    - JSONResponse - 包含导入MCP服务结果的JSON响应
    """
    batch_import_result = await AgMcpServerService.batch_import_mcp_servers_service(file=file, auth=auth, update_support=True)
    log.info("导入MCP服务成功")
    return SuccessResponse(data=batch_import_result, msg="导入MCP服务成功")

@AgMcpServerRouter.post(
    '/download/template',
    summary="获取MCP服务导入模板",
    description="获取MCP服务导入模板",
    dependencies=[Depends(AuthPermission(["module_agno_manage:mcp_servers:download"]))]
)
async def export_mcp_servers_template_controller() -> StreamingResponse:
    """
    获取MCP服务导入模板接口
    
    返回:
    - StreamingResponse - 包含MCP服务导入模板的流式响应
    """
    import_template_result = await AgMcpServerService.import_template_download_mcp_servers_service()
    log.info('获取MCP服务导入模板成功')
    return StreamResponse(
        data=bytes2file_response(import_template_result),
        media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        headers={'Content-Disposition': 'attachment; filename=ag_mcp_servers_template.xlsx'}
    )

@AgMcpServerRouter.get(
    "/agno/server_types",
    summary="获取 MCP Server 类型列表",
)
async def get_agno_mcp_server_types_controller(
    auth: AuthSchema = Depends(AuthPermission(["module_agno_manage:mcp_servers:query"]))
):
    result = AgMcpServerService.list_agno_server_types_service()
    return SuccessResponse(data=result, msg="获取 MCP Server 类型列表成功")