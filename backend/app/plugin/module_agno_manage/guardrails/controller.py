
from fastapi import APIRouter, Body, Depends, Path, UploadFile
from fastapi.responses import JSONResponse, StreamingResponse

from app.api.v1.module_system.auth.schema import AuthSchema
from app.common.response import StreamResponse, SuccessResponse
from app.core.base_params import PaginationQueryParam
from app.core.base_schema import BatchSetAvailable
from app.core.dependencies import AuthPermission
from app.core.logger import log
from app.utils.common_util import bytes2file_response

from .schema import AgGuardrailCreateSchema, AgGuardrailQueryParam, AgGuardrailUpdateSchema
from .service import AgGuardrailService

AgGuardrailRouter = APIRouter(prefix='/guardrails', tags=["护栏模块"])


@AgGuardrailRouter.get(
    "/detail/{id}",
    summary="获取护栏详情",
    description="获取护栏详情"
)
async def get_guardrails_detail_controller(
    id: int = Path(..., description="ID"),
    auth: AuthSchema = Depends(AuthPermission(["module_agno_manage:guardrails:query"]))
) -> JSONResponse:
    """
    获取护栏详情接口
    
    参数:
    - id: int - 数据ID
    - auth: AuthSchema - 认证信息
    
    返回:
    - JSONResponse - 包含护栏详情的JSON响应
    """
    result_dict = await AgGuardrailService.detail_guardrails_service(auth=auth, id=id)
    log.info(f"获取护栏详情成功 {id}")
    return SuccessResponse(data=result_dict, msg="获取护栏详情成功")


@AgGuardrailRouter.get(
    "/list",
    summary="查询护栏列表",
    description="查询护栏列表"
)
async def get_guardrails_list_controller(
    page: PaginationQueryParam = Depends(),
    search: AgGuardrailQueryParam = Depends(),
    auth: AuthSchema = Depends(AuthPermission(["module_agno_manage:guardrails:query"]))
) -> JSONResponse:
    """
    查询护栏列表接口（数据库分页）
    
    参数:
    - page: PaginationQueryParam - 分页参数
    - search: AgGuardrailQueryParam - 查询参数
    - auth: AuthSchema - 认证信息
    
    返回:
    - JSONResponse - 包含护栏列表的JSON响应
    """
    result_dict = await AgGuardrailService.page_guardrails_service(
        auth=auth,
        page_no=page.page_no if page.page_no is not None else 1,
        page_size=page.page_size if page.page_size is not None else 10,
        search=search,
        order_by=page.order_by
    )
    log.info("查询护栏列表成功")
    return SuccessResponse(data=result_dict, msg="查询护栏列表成功")


@AgGuardrailRouter.post(
    "/create",
    summary="创建护栏",
    description="创建护栏"
)
async def create_guardrails_controller(
    data: AgGuardrailCreateSchema,
    auth: AuthSchema = Depends(AuthPermission(["module_agno_manage:guardrails:create"]))
) -> JSONResponse:
    """
    创建护栏接口
    
    参数:
    - data: AgGuardrailCreateSchema - 创建数据
    - auth: AuthSchema - 认证信息
    
    返回:
    - JSONResponse - 包含创建护栏结果的JSON响应
    """
    result_dict = await AgGuardrailService.create_guardrails_service(auth=auth, data=data)
    log.info("创建护栏成功")
    return SuccessResponse(data=result_dict, msg="创建护栏成功")


@AgGuardrailRouter.put(
    "/update/{id}",
    summary="修改护栏",
    description="修改护栏"
)
async def update_guardrails_controller(
    data: AgGuardrailUpdateSchema,
    id: int = Path(..., description="ID"),
    auth: AuthSchema = Depends(AuthPermission(["module_agno_manage:guardrails:update"]))
) -> JSONResponse:
    """
    修改护栏接口
    
    参数:
    - id: int - 数据ID
    - data: AgGuardrailUpdateSchema - 更新数据
    - auth: AuthSchema - 认证信息
    
    返回:
    - JSONResponse - 包含修改护栏结果的JSON响应
    """
    result_dict = await AgGuardrailService.update_guardrails_service(auth=auth, id=id, data=data)
    log.info("修改护栏成功")
    return SuccessResponse(data=result_dict, msg="修改护栏成功")


@AgGuardrailRouter.delete(
    "/delete",
    summary="删除护栏",
    description="删除护栏"
)
async def delete_guardrails_controller(
    ids: list[int] = Body(..., description="ID列表"),
    auth: AuthSchema = Depends(AuthPermission(["module_agno_manage:guardrails:delete"]))
) -> JSONResponse:
    """
    删除护栏接口
    
    参数:
    - ids: list[int] - 数据ID列表
    - auth: AuthSchema - 认证信息
    
    返回:
    - JSONResponse - 包含删除护栏结果的JSON响应
    """
    await AgGuardrailService.delete_guardrails_service(auth=auth, ids=ids)
    log.info(f"删除护栏成功: {ids}")
    return SuccessResponse(msg="删除护栏成功")


@AgGuardrailRouter.patch(
    "/available/setting",
    summary="批量修改护栏状态",
    description="批量修改护栏状态"
)
async def batch_set_available_guardrails_controller(
    data: BatchSetAvailable,
    auth: AuthSchema = Depends(AuthPermission(["module_agno_manage:guardrails:patch"]))
) -> JSONResponse:
    """
    批量修改护栏状态接口
    
    参数:
    - data: BatchSetAvailable - 批量修改状态数据
    - auth: AuthSchema - 认证信息
    
    返回:
    - JSONResponse - 包含批量修改护栏状态结果的JSON响应
    """
    await AgGuardrailService.set_available_guardrails_service(auth=auth, data=data)
    log.info(f"批量修改护栏状态成功: {data.ids}")
    return SuccessResponse(msg="批量修改护栏状态成功")


@AgGuardrailRouter.post(
    '/export',
    summary="导出护栏",
    description="导出护栏"
)
async def export_guardrails_list_controller(
    search: AgGuardrailQueryParam = Depends(),
    auth: AuthSchema = Depends(AuthPermission(["module_agno_manage:guardrails:export"]))
) -> StreamingResponse:
    """
    导出护栏接口
    
    参数:
    - search: AgGuardrailQueryParam - 查询参数
    - auth: AuthSchema - 认证信息
    
    返回:
    - StreamingResponse - 包含导出护栏数据的流式响应
    """
    result_dict_list = await AgGuardrailService.list_guardrails_service(search=search, auth=auth)
    export_result = await AgGuardrailService.batch_export_guardrails_service(obj_list=result_dict_list)
    log.info('导出护栏成功')
    return StreamResponse(
        data=bytes2file_response(export_result),
        media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        headers={'Content-Disposition': 'attachment; filename=ag_guardrails.xlsx'}
    )


@AgGuardrailRouter.post(
    '/import',
    summary="导入护栏",
    description="导入护栏"
)
async def import_guardrails_list_controller(
    file: UploadFile,
    auth: AuthSchema = Depends(AuthPermission(["module_agno_manage:guardrails:import"]))
) -> JSONResponse:
    """
    导入护栏接口
    
    参数:
    - file: UploadFile - 上传的Excel文件
    - auth: AuthSchema - 认证信息
    
    返回:
    - JSONResponse - 包含导入护栏结果的JSON响应
    """
    batch_import_result = await AgGuardrailService.batch_import_guardrails_service(file=file, auth=auth, update_support=True)
    log.info("导入护栏成功")
    return SuccessResponse(data=batch_import_result, msg="导入护栏成功")


@AgGuardrailRouter.post(
    '/download/template',
    summary="获取护栏导入模板",
    description="获取护栏导入模板",
    dependencies=[Depends(AuthPermission(["module_agno_manage:guardrails:download"]))]
)
async def export_guardrails_template_controller() -> StreamingResponse:
    """
    获取护栏导入模板接口
    
    返回:
    - StreamingResponse - 包含护栏导入模板的流式响应
    """
    import_template_result = await AgGuardrailService.import_template_download_guardrails_service()
    log.info('获取护栏导入模板成功')
    return StreamResponse(
        data=bytes2file_response(import_template_result),
        media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        headers={'Content-Disposition': 'attachment; filename=ag_guardrails_template.xlsx'}
    )


@AgGuardrailRouter.get(
    "/agno/guardrail_types",
    summary="获取 Agno Guardrail 类型列表",
)
async def get_agno_guardrail_types_controller(
    auth: AuthSchema = Depends(AuthPermission(["module_agno_manage:guardrails:query"]))
):
    result = AgGuardrailService.list_agno_guardrail_types_service()
    return SuccessResponse(data=result, msg="获取 Guardrail 类型列表成功")
