from fastapi import APIRouter, Body, Depends, Path
from fastapi.responses import JSONResponse

from app.api.v1.module_system.auth.schema import AuthSchema
from app.common.response import SuccessResponse
from app.core.base_params import PaginationQueryParam
from app.core.base_schema import BatchSetAvailable
from app.core.dependencies import AuthPermission
from app.core.logger import log

from .schema import AgResourceCreateSchema, AgResourceQueryParam, AgResourceUpdateSchema
from .service import AgResourceService

AgResourceRouter = APIRouter(prefix="/v2/resources", tags=["V2-资源管理"])


@AgResourceRouter.get(
    "/detail/{id}",
    summary="获取资源详情",
    description="获取资源详情，config 字段会用 builder schema 默认值补全",
)
async def get_resource_detail_controller(
    id: int = Path(..., description="ID"),
    auth: AuthSchema = Depends(AuthPermission(["module_agno_manage:v2:query"])),
) -> JSONResponse:
    """
    获取资源详情接口

    参数:
    - id: int — 数据 ID
    - auth: AuthSchema — 认证信息

    返回:
    - JSONResponse — 包含资源详情的 JSON 响应
    """
    result = await AgResourceService.detail_resources_service(auth=auth, id=id)
    log.info(f"获取资源详情成功 {id}")
    return SuccessResponse(data=result, msg="获取资源详情成功")


@AgResourceRouter.get(
    "/list",
    summary="查询资源列表",
    description="分页查询资源列表",
)
async def get_resource_list_controller(
    page: PaginationQueryParam = Depends(),
    search: AgResourceQueryParam = Depends(),
    auth: AuthSchema = Depends(AuthPermission(["module_agno_manage:v2:query"])),
) -> JSONResponse:
    """
    查询资源列表接口（数据库分页）

    参数:
    - page: PaginationQueryParam — 分页参数
    - search: AgResourceQueryParam — 查询参数
    - auth: AuthSchema — 认证信息

    返回:
    - JSONResponse — 包含资源列表的 JSON 响应
    """
    result = await AgResourceService.page_resources_service(
        auth=auth,
        page_no=page.page_no if page.page_no is not None else 1,
        page_size=page.page_size if page.page_size is not None else 10,
        search=search,
        order_by=page.order_by,
    )
    log.info("查询资源列表成功")
    return SuccessResponse(data=result, msg="查询资源列表成功")


@AgResourceRouter.post(
    "/create",
    summary="创建资源",
    description="创建资源，agent/team 同步注册到 RuntimeRegistry",
)
async def create_resource_controller(
    data: AgResourceCreateSchema,
    auth: AuthSchema = Depends(AuthPermission(["module_agno_manage:v2:create"])),
) -> JSONResponse:
    """
    创建资源接口

    参数:
    - data: AgResourceCreateSchema — 创建数据
    - auth: AuthSchema — 认证信息

    返回:
    - JSONResponse — 包含创建资源结果的 JSON 响应
    """
    result = await AgResourceService.create_resource_service(auth=auth, data=data)
    log.info("创建资源成功")
    return SuccessResponse(data=result, msg="创建资源成功")


@AgResourceRouter.put(
    "/update/{id}",
    summary="修改资源",
    description="修改资源，agent/team 同步重建 RuntimeRegistry 中的实例",
)
async def update_resource_controller(
    data: AgResourceUpdateSchema,
    id: int = Path(..., description="ID"),
    auth: AuthSchema = Depends(AuthPermission(["module_agno_manage:v2:update"])),
) -> JSONResponse:
    """
    修改资源接口

    参数:
    - id: int — 数据 ID
    - data: AgResourceUpdateSchema — 更新数据
    - auth: AuthSchema — 认证信息

    返回:
    - JSONResponse — 包含修改资源结果的 JSON 响应
    """
    result = await AgResourceService.update_resource_service(auth=auth, id=id, data=data)
    log.info(f"修改资源成功 {id}")
    return SuccessResponse(data=result, msg="修改资源成功")


@AgResourceRouter.delete(
    "/delete",
    summary="删除资源",
    description="批量删除资源，agent/team 同步从 RuntimeRegistry 移除",
)
async def delete_resource_controller(
    ids: list[int] = Body(..., description="ID 列表"),
    auth: AuthSchema = Depends(AuthPermission(["module_agno_manage:v2:delete"])),
) -> JSONResponse:
    """
    删除资源接口

    参数:
    - ids: list[int] — 数据 ID 列表
    - auth: AuthSchema — 认证信息

    返回:
    - JSONResponse — 包含删除资源结果的 JSON 响应
    """
    await AgResourceService.delete_resource_service(auth=auth, ids=ids)
    log.info(f"删除资源成功: {ids}")
    return SuccessResponse(msg="删除资源成功")


@AgResourceRouter.patch(
    "/available/setting",
    summary="批量修改资源状态",
    description="批量启用/禁用资源，agent/team 同步更新 RuntimeRegistry",
)
async def set_available_resource_controller(
    data: BatchSetAvailable,
    auth: AuthSchema = Depends(AuthPermission(["module_agno_manage:v2:patch"])),
) -> JSONResponse:
    """
    批量修改资源状态接口

    参数:
    - data: BatchSetAvailable — 批量修改状态数据
    - auth: AuthSchema — 认证信息

    返回:
    - JSONResponse — 包含批量修改资源状态结果的 JSON 响应
    """
    await AgResourceService.set_available_resource_service(
        auth=auth, ids=data.ids, status=data.status
    )
    log.info(f"批量修改资源状态成功: {data.ids}")
    return SuccessResponse(msg="批量修改资源状态成功")
