
from fastapi import APIRouter, Body, Depends, Path, UploadFile
from fastapi.responses import JSONResponse, StreamingResponse

from app.api.v1.module_system.auth.schema import AuthSchema
from app.common.response import StreamResponse, SuccessResponse
from app.core.base_params import PaginationQueryParam
from app.core.base_schema import BatchSetAvailable
from app.core.dependencies import AuthPermission
from app.core.logger import log
from app.utils.common_util import bytes2file_response

from .schema import AgBindingCreateSchema, AgBindingQueryParam, AgBindingUpdateSchema
from .service import AgBindingService

AgBindingRouter = APIRouter(prefix='/bindings', tags=["资源绑定关系模块"])

# 拥有者类型 → 可绑资源类型的静态元数据
# api_path 供前端动态发起列表查询
BINDING_META: dict = {
    "agent": {
        "label": "Agent",
        "api_path": "/agno_manage/agents",
        "allowed_resources": {
            "toolkit":   {"label": "Toolkit",    "api_path": "/agno_manage/toolkits"},
            "skill":     {"label": "Skill",      "api_path": "/agno_manage/skills"},
            "mcp":       {"label": "MCP Server", "api_path": "/agno_manage/mcp_servers"},
            "knowledge": {"label": "知识库",      "api_path": "/agno_manage/knowledge_bases"},
            "hook":      {"label": "Hook",       "api_path": "/agno_manage/hooks"},
            "guardrail": {"label": "Guardrail",  "api_path": "/agno_manage/guardrails"},
        },
    },
    "team": {
        "label": "Team",
        "api_path": "/agno_manage/teams",
        "allowed_resources": {
            "toolkit":   {"label": "Toolkit",    "api_path": "/agno_manage/toolkits"},
            "skill":     {"label": "Skill",      "api_path": "/agno_manage/skills"},
            "mcp":       {"label": "MCP Server", "api_path": "/agno_manage/mcp_servers"},
            "knowledge": {"label": "知识库",      "api_path": "/agno_manage/knowledge_bases"},
            "hook":      {"label": "Hook",       "api_path": "/agno_manage/hooks"},
            "guardrail": {"label": "Guardrail",  "api_path": "/agno_manage/guardrails"},
        },
    },
    "knowledge": {
        "label": "知识库",
        "api_path": "/agno_manage/knowledge_bases",
        "allowed_resources": {
            "reader": {"label": "Reader", "api_path": "/agno_manage/readers"},
        },
    },
}


@AgBindingRouter.get(
    "/meta",
    summary="获取绑定关系元数据",
    description="返回拥有者类型及其可绑定资源类型的映射关系（含前端所需 api_path）"
)
async def get_bindings_meta_controller(
    auth: AuthSchema = Depends(AuthPermission(["module_agno_manage:bindings:query"]))
) -> JSONResponse:
    return SuccessResponse(data=BINDING_META, msg="获取绑定元数据成功")


@AgBindingRouter.get(
    "/detail/{id}",
    summary="获取资源绑定关系详情",
    description="获取资源绑定关系详情"
)
async def get_bindings_detail_controller(
    id: int = Path(..., description="ID"),
    auth: AuthSchema = Depends(AuthPermission(["module_agno_manage:bindings:query"]))
) -> JSONResponse:
    """
    获取资源绑定关系详情接口
    
    参数:
    - id: int - 数据ID
    - auth: AuthSchema - 认证信息
    
    返回:
    - JSONResponse - 包含资源绑定关系详情的JSON响应
    """
    result_dict = await AgBindingService.detail_bindings_service(auth=auth, id=id)
    log.info(f"获取资源绑定关系详情成功 {id}")
    return SuccessResponse(data=result_dict, msg="获取资源绑定关系详情成功")


@AgBindingRouter.get(
    "/list",
    summary="查询资源绑定关系列表",
    description="查询资源绑定关系列表"
)
async def get_bindings_list_controller(
    page: PaginationQueryParam = Depends(),
    search: AgBindingQueryParam = Depends(),
    auth: AuthSchema = Depends(AuthPermission(["module_agno_manage:bindings:query"]))
) -> JSONResponse:
    """
    查询资源绑定关系列表接口（数据库分页）
    
    参数:
    - page: PaginationQueryParam - 分页参数
    - search: AgBindingQueryParam - 查询参数
    - auth: AuthSchema - 认证信息
    
    返回:
    - JSONResponse - 包含资源绑定关系列表的JSON响应
    """
    result_dict = await AgBindingService.page_bindings_service(
        auth=auth,
        page_no=page.page_no if page.page_no is not None else 1,
        page_size=page.page_size if page.page_size is not None else 10,
        search=search,
        order_by=page.order_by
    )
    log.info("查询资源绑定关系列表成功")
    return SuccessResponse(data=result_dict, msg="查询资源绑定关系列表成功")


@AgBindingRouter.post(
    "/create",
    summary="创建资源绑定关系",
    description="创建资源绑定关系"
)
async def create_bindings_controller(
    data: AgBindingCreateSchema,
    auth: AuthSchema = Depends(AuthPermission(["module_agno_manage:bindings:create"]))
) -> JSONResponse:
    """
    创建资源绑定关系接口
    
    参数:
    - data: AgBindingCreateSchema - 创建数据
    - auth: AuthSchema - 认证信息
    
    返回:
    - JSONResponse - 包含创建资源绑定关系结果的JSON响应
    """
    result_dict = await AgBindingService.create_bindings_service(auth=auth, data=data)
    log.info("创建资源绑定关系成功")
    return SuccessResponse(data=result_dict, msg="创建资源绑定关系成功")


@AgBindingRouter.put(
    "/update/{id}",
    summary="修改资源绑定关系",
    description="修改资源绑定关系"
)
async def update_bindings_controller(
    data: AgBindingUpdateSchema,
    id: int = Path(..., description="ID"),
    auth: AuthSchema = Depends(AuthPermission(["module_agno_manage:bindings:update"]))
) -> JSONResponse:
    """
    修改资源绑定关系接口
    
    参数:
    - id: int - 数据ID
    - data: AgBindingUpdateSchema - 更新数据
    - auth: AuthSchema - 认证信息
    
    返回:
    - JSONResponse - 包含修改资源绑定关系结果的JSON响应
    """
    result_dict = await AgBindingService.update_bindings_service(auth=auth, id=id, data=data)
    log.info("修改资源绑定关系成功")
    return SuccessResponse(data=result_dict, msg="修改资源绑定关系成功")


@AgBindingRouter.delete(
    "/delete",
    summary="删除资源绑定关系",
    description="删除资源绑定关系"
)
async def delete_bindings_controller(
    ids: list[int] = Body(..., description="ID列表"),
    auth: AuthSchema = Depends(AuthPermission(["module_agno_manage:bindings:delete"]))
) -> JSONResponse:
    """
    删除资源绑定关系接口
    
    参数:
    - ids: list[int] - 数据ID列表
    - auth: AuthSchema - 认证信息
    
    返回:
    - JSONResponse - 包含删除资源绑定关系结果的JSON响应
    """
    await AgBindingService.delete_bindings_service(auth=auth, ids=ids)
    log.info(f"删除资源绑定关系成功: {ids}")
    return SuccessResponse(msg="删除资源绑定关系成功")


@AgBindingRouter.patch(
    "/available/setting",
    summary="批量修改资源绑定关系状态",
    description="批量修改资源绑定关系状态"
)
async def batch_set_available_bindings_controller(
    data: BatchSetAvailable,
    auth: AuthSchema = Depends(AuthPermission(["module_agno_manage:bindings:patch"]))
) -> JSONResponse:
    """
    批量修改资源绑定关系状态接口
    
    参数:
    - data: BatchSetAvailable - 批量修改状态数据
    - auth: AuthSchema - 认证信息
    
    返回:
    - JSONResponse - 包含批量修改资源绑定关系状态结果的JSON响应
    """
    await AgBindingService.set_available_bindings_service(auth=auth, data=data)
    log.info(f"批量修改资源绑定关系状态成功: {data.ids}")
    return SuccessResponse(msg="批量修改资源绑定关系状态成功")


@AgBindingRouter.post(
    '/export',
    summary="导出资源绑定关系",
    description="导出资源绑定关系"
)
async def export_bindings_list_controller(
    search: AgBindingQueryParam = Depends(),
    auth: AuthSchema = Depends(AuthPermission(["module_agno_manage:bindings:export"]))
) -> StreamingResponse:
    """
    导出资源绑定关系接口
    
    参数:
    - search: AgBindingQueryParam - 查询参数
    - auth: AuthSchema - 认证信息
    
    返回:
    - StreamingResponse - 包含导出资源绑定关系数据的流式响应
    """
    result_dict_list = await AgBindingService.list_bindings_service(search=search, auth=auth)
    export_result = await AgBindingService.batch_export_bindings_service(obj_list=result_dict_list)
    log.info('导出资源绑定关系成功')
    return StreamResponse(
        data=bytes2file_response(export_result),
        media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        headers={'Content-Disposition': 'attachment; filename=ag_bindings.xlsx'}
    )


@AgBindingRouter.post(
    '/import',
    summary="导入资源绑定关系",
    description="导入资源绑定关系"
)
async def import_bindings_list_controller(
    file: UploadFile,
    auth: AuthSchema = Depends(AuthPermission(["module_agno_manage:bindings:import"]))
) -> JSONResponse:
    """
    导入资源绑定关系接口
    
    参数:
    - file: UploadFile - 上传的Excel文件
    - auth: AuthSchema - 认证信息
    
    返回:
    - JSONResponse - 包含导入资源绑定关系结果的JSON响应
    """
    batch_import_result = await AgBindingService.batch_import_bindings_service(file=file, auth=auth, update_support=True)
    log.info("导入资源绑定关系成功")
    return SuccessResponse(data=batch_import_result, msg="导入资源绑定关系成功")


@AgBindingRouter.post(
    '/download/template',
    summary="获取资源绑定关系导入模板",
    description="获取资源绑定关系导入模板",
    dependencies=[Depends(AuthPermission(["module_agno_manage:bindings:download"]))]
)
async def export_bindings_template_controller() -> StreamingResponse:
    """
    获取资源绑定关系导入模板接口
    
    返回:
    - StreamingResponse - 包含资源绑定关系导入模板的流式响应
    """
    import_template_result = await AgBindingService.import_template_download_bindings_service()
    log.info('获取资源绑定关系导入模板成功')
    return StreamResponse(
        data=bytes2file_response(import_template_result),
        media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        headers={'Content-Disposition': 'attachment; filename=ag_bindings_template.xlsx'}
    )
