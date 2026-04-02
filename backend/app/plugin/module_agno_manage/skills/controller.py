
from fastapi import APIRouter, Body, Depends, Path, UploadFile
from fastapi.responses import JSONResponse, StreamingResponse

from app.api.v1.module_system.auth.schema import AuthSchema
from app.common.response import StreamResponse, SuccessResponse
from app.core.base_params import PaginationQueryParam
from app.core.base_schema import BatchSetAvailable
from app.core.dependencies import AuthPermission
from app.core.logger import log
from app.utils.common_util import bytes2file_response

from .schema import AgSkillCreateSchema, AgSkillQueryParam, AgSkillUpdateSchema
from .service import AgSkillService

AgSkillRouter = APIRouter(prefix='/skills', tags=["技能管理模块"])


@AgSkillRouter.get(
    "/detail/{id}",
    summary="获取技能管理详情",
    description="获取技能管理详情"
)
async def get_skills_detail_controller(
    id: int = Path(..., description="ID"),
    auth: AuthSchema = Depends(AuthPermission(["module_agno_manage:skills:query"]))
) -> JSONResponse:
    """
    获取技能管理详情接口
    
    参数:
    - id: int - 数据ID
    - auth: AuthSchema - 认证信息
    
    返回:
    - JSONResponse - 包含技能管理详情的JSON响应
    """
    result_dict = await AgSkillService.detail_skills_service(auth=auth, id=id)
    log.info(f"获取技能管理详情成功 {id}")
    return SuccessResponse(data=result_dict, msg="获取技能管理详情成功")


@AgSkillRouter.get(
    "/list",
    summary="查询技能管理列表",
    description="查询技能管理列表"
)
async def get_skills_list_controller(
    page: PaginationQueryParam = Depends(),
    search: AgSkillQueryParam = Depends(),
    auth: AuthSchema = Depends(AuthPermission(["module_agno_manage:skills:query"]))
) -> JSONResponse:
    """
    查询技能管理列表接口（数据库分页）
    
    参数:
    - page: PaginationQueryParam - 分页参数
    - search: AgSkillQueryParam - 查询参数
    - auth: AuthSchema - 认证信息
    
    返回:
    - JSONResponse - 包含技能管理列表的JSON响应
    """
    result_dict = await AgSkillService.page_skills_service(
        auth=auth,
        page_no=page.page_no if page.page_no is not None else 1,
        page_size=page.page_size if page.page_size is not None else 10,
        search=search,
        order_by=page.order_by
    )
    log.info("查询技能管理列表成功")
    return SuccessResponse(data=result_dict, msg="查询技能管理列表成功")


@AgSkillRouter.post(
    "/create",
    summary="创建技能管理",
    description="创建技能管理"
)
async def create_skills_controller(
    data: AgSkillCreateSchema,
    auth: AuthSchema = Depends(AuthPermission(["module_agno_manage:skills:create"]))
) -> JSONResponse:
    """
    创建技能管理接口
    
    参数:
    - data: AgSkillCreateSchema - 创建数据
    - auth: AuthSchema - 认证信息
    
    返回:
    - JSONResponse - 包含创建技能管理结果的JSON响应
    """
    result_dict = await AgSkillService.create_skills_service(auth=auth, data=data)
    log.info("创建技能管理成功")
    return SuccessResponse(data=result_dict, msg="创建技能管理成功")


@AgSkillRouter.put(
    "/update/{id}",
    summary="修改技能管理",
    description="修改技能管理"
)
async def update_skills_controller(
    data: AgSkillUpdateSchema,
    id: int = Path(..., description="ID"),
    auth: AuthSchema = Depends(AuthPermission(["module_agno_manage:skills:update"]))
) -> JSONResponse:
    """
    修改技能管理接口
    
    参数:
    - id: int - 数据ID
    - data: AgSkillUpdateSchema - 更新数据
    - auth: AuthSchema - 认证信息
    
    返回:
    - JSONResponse - 包含修改技能管理结果的JSON响应
    """
    result_dict = await AgSkillService.update_skills_service(auth=auth, id=id, data=data)
    log.info("修改技能管理成功")
    return SuccessResponse(data=result_dict, msg="修改技能管理成功")


@AgSkillRouter.delete(
    "/delete",
    summary="删除技能管理",
    description="删除技能管理"
)
async def delete_skills_controller(
    ids: list[int] = Body(..., description="ID列表"),
    auth: AuthSchema = Depends(AuthPermission(["module_agno_manage:skills:delete"]))
) -> JSONResponse:
    """
    删除技能管理接口
    
    参数:
    - ids: list[int] - 数据ID列表
    - auth: AuthSchema - 认证信息
    
    返回:
    - JSONResponse - 包含删除技能管理结果的JSON响应
    """
    await AgSkillService.delete_skills_service(auth=auth, ids=ids)
    log.info(f"删除技能管理成功: {ids}")
    return SuccessResponse(msg="删除技能管理成功")


@AgSkillRouter.patch(
    "/available/setting",
    summary="批量修改技能管理状态",
    description="批量修改技能管理状态"
)
async def batch_set_available_skills_controller(
    data: BatchSetAvailable,
    auth: AuthSchema = Depends(AuthPermission(["module_agno_manage:skills:patch"]))
) -> JSONResponse:
    """
    批量修改技能管理状态接口
    
    参数:
    - data: BatchSetAvailable - 批量修改状态数据
    - auth: AuthSchema - 认证信息
    
    返回:
    - JSONResponse - 包含批量修改技能管理状态结果的JSON响应
    """
    await AgSkillService.set_available_skills_service(auth=auth, data=data)
    log.info(f"批量修改技能管理状态成功: {data.ids}")
    return SuccessResponse(msg="批量修改技能管理状态成功")


@AgSkillRouter.post(
    '/export',
    summary="导出技能管理",
    description="导出技能管理"
)
async def export_skills_list_controller(
    search: AgSkillQueryParam = Depends(),
    auth: AuthSchema = Depends(AuthPermission(["module_agno_manage:skills:export"]))
) -> StreamingResponse:
    """
    导出技能管理接口
    
    参数:
    - search: AgSkillQueryParam - 查询参数
    - auth: AuthSchema - 认证信息
    
    返回:
    - StreamingResponse - 包含导出技能管理数据的流式响应
    """
    result_dict_list = await AgSkillService.list_skills_service(search=search, auth=auth)
    export_result = await AgSkillService.batch_export_skills_service(obj_list=result_dict_list)
    log.info('导出技能管理成功')
    return StreamResponse(
        data=bytes2file_response(export_result),
        media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        headers={'Content-Disposition': 'attachment; filename=ag_skills.xlsx'}
    )


@AgSkillRouter.post(
    '/import',
    summary="导入技能管理",
    description="导入技能管理"
)
async def import_skills_list_controller(
    file: UploadFile,
    auth: AuthSchema = Depends(AuthPermission(["module_agno_manage:skills:import"]))
) -> JSONResponse:
    """
    导入技能管理接口
    
    参数:
    - file: UploadFile - 上传的Excel文件
    - auth: AuthSchema - 认证信息
    
    返回:
    - JSONResponse - 包含导入技能管理结果的JSON响应
    """
    batch_import_result = await AgSkillService.batch_import_skills_service(file=file, auth=auth, update_support=True)
    log.info("导入技能管理成功")
    return SuccessResponse(data=batch_import_result, msg="导入技能管理成功")


@AgSkillRouter.post(
    '/download/template',
    summary="获取技能管理导入模板",
    description="获取技能管理导入模板",
    dependencies=[Depends(AuthPermission(["module_agno_manage:skills:download"]))]
)
async def export_skills_template_controller() -> StreamingResponse:
    """
    获取技能管理导入模板接口
    
    返回:
    - StreamingResponse - 包含技能管理导入模板的流式响应
    """
    import_template_result = await AgSkillService.import_template_download_skills_service()
    log.info('获取技能管理导入模板成功')
    return StreamResponse(
        data=bytes2file_response(import_template_result),
        media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        headers={'Content-Disposition': 'attachment; filename=ag_skills_template.xlsx'}
    )
