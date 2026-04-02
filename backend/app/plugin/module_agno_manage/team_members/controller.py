
from fastapi import APIRouter, Body, Depends, Path, UploadFile
from fastapi.responses import JSONResponse, StreamingResponse

from app.api.v1.module_system.auth.schema import AuthSchema
from app.common.response import StreamResponse, SuccessResponse
from app.core.base_params import PaginationQueryParam
from app.core.base_schema import BatchSetAvailable
from app.core.dependencies import AuthPermission
from app.core.logger import log
from app.utils.common_util import bytes2file_response

from .schema import AgTeamMemberCreateSchema, AgTeamMemberQueryParam, AgTeamMemberUpdateSchema
from .service import AgTeamMemberService

AgTeamMemberRouter = APIRouter(prefix='/team_members', tags=["Team成员关系模块"])


@AgTeamMemberRouter.get(
    "/detail/{id}",
    summary="获取Team成员关系详情",
    description="获取Team成员关系详情"
)
async def get_team_members_detail_controller(
    id: int = Path(..., description="ID"),
    auth: AuthSchema = Depends(AuthPermission(["module_agno_manage:team_members:query"]))
) -> JSONResponse:
    """
    获取Team成员关系详情接口
    
    参数:
    - id: int - 数据ID
    - auth: AuthSchema - 认证信息
    
    返回:
    - JSONResponse - 包含Team成员关系详情的JSON响应
    """
    result_dict = await AgTeamMemberService.detail_team_members_service(auth=auth, id=id)
    log.info(f"获取Team成员关系详情成功 {id}")
    return SuccessResponse(data=result_dict, msg="获取Team成员关系详情成功")


@AgTeamMemberRouter.get(
    "/list",
    summary="查询Team成员关系列表",
    description="查询Team成员关系列表"
)
async def get_team_members_list_controller(
    page: PaginationQueryParam = Depends(),
    search: AgTeamMemberQueryParam = Depends(),
    auth: AuthSchema = Depends(AuthPermission(["module_agno_manage:team_members:query"]))
) -> JSONResponse:
    """
    查询Team成员关系列表接口（数据库分页）
    
    参数:
    - page: PaginationQueryParam - 分页参数
    - search: AgTeamMemberQueryParam - 查询参数
    - auth: AuthSchema - 认证信息
    
    返回:
    - JSONResponse - 包含Team成员关系列表的JSON响应
    """
    result_dict = await AgTeamMemberService.page_team_members_service(
        auth=auth,
        page_no=page.page_no if page.page_no is not None else 1,
        page_size=page.page_size if page.page_size is not None else 10,
        search=search,
        order_by=page.order_by
    )
    log.info("查询Team成员关系列表成功")
    return SuccessResponse(data=result_dict, msg="查询Team成员关系列表成功")


@AgTeamMemberRouter.post(
    "/create",
    summary="创建Team成员关系",
    description="创建Team成员关系"
)
async def create_team_members_controller(
    data: AgTeamMemberCreateSchema,
    auth: AuthSchema = Depends(AuthPermission(["module_agno_manage:team_members:create"]))
) -> JSONResponse:
    """
    创建Team成员关系接口
    
    参数:
    - data: AgTeamMemberCreateSchema - 创建数据
    - auth: AuthSchema - 认证信息
    
    返回:
    - JSONResponse - 包含创建Team成员关系结果的JSON响应
    """
    result_dict = await AgTeamMemberService.create_team_members_service(auth=auth, data=data)
    log.info("创建Team成员关系成功")
    return SuccessResponse(data=result_dict, msg="创建Team成员关系成功")


@AgTeamMemberRouter.put(
    "/update/{id}",
    summary="修改Team成员关系",
    description="修改Team成员关系"
)
async def update_team_members_controller(
    data: AgTeamMemberUpdateSchema,
    id: int = Path(..., description="ID"),
    auth: AuthSchema = Depends(AuthPermission(["module_agno_manage:team_members:update"]))
) -> JSONResponse:
    """
    修改Team成员关系接口
    
    参数:
    - id: int - 数据ID
    - data: AgTeamMemberUpdateSchema - 更新数据
    - auth: AuthSchema - 认证信息
    
    返回:
    - JSONResponse - 包含修改Team成员关系结果的JSON响应
    """
    result_dict = await AgTeamMemberService.update_team_members_service(auth=auth, id=id, data=data)
    log.info("修改Team成员关系成功")
    return SuccessResponse(data=result_dict, msg="修改Team成员关系成功")


@AgTeamMemberRouter.delete(
    "/delete",
    summary="删除Team成员关系",
    description="删除Team成员关系"
)
async def delete_team_members_controller(
    ids: list[int] = Body(..., description="ID列表"),
    auth: AuthSchema = Depends(AuthPermission(["module_agno_manage:team_members:delete"]))
) -> JSONResponse:
    """
    删除Team成员关系接口
    
    参数:
    - ids: list[int] - 数据ID列表
    - auth: AuthSchema - 认证信息
    
    返回:
    - JSONResponse - 包含删除Team成员关系结果的JSON响应
    """
    await AgTeamMemberService.delete_team_members_service(auth=auth, ids=ids)
    log.info(f"删除Team成员关系成功: {ids}")
    return SuccessResponse(msg="删除Team成员关系成功")


@AgTeamMemberRouter.patch(
    "/available/setting",
    summary="批量修改Team成员关系状态",
    description="批量修改Team成员关系状态"
)
async def batch_set_available_team_members_controller(
    data: BatchSetAvailable,
    auth: AuthSchema = Depends(AuthPermission(["module_agno_manage:team_members:patch"]))
) -> JSONResponse:
    """
    批量修改Team成员关系状态接口
    
    参数:
    - data: BatchSetAvailable - 批量修改状态数据
    - auth: AuthSchema - 认证信息
    
    返回:
    - JSONResponse - 包含批量修改Team成员关系状态结果的JSON响应
    """
    await AgTeamMemberService.set_available_team_members_service(auth=auth, data=data)
    log.info(f"批量修改Team成员关系状态成功: {data.ids}")
    return SuccessResponse(msg="批量修改Team成员关系状态成功")


@AgTeamMemberRouter.post(
    '/export',
    summary="导出Team成员关系",
    description="导出Team成员关系"
)
async def export_team_members_list_controller(
    search: AgTeamMemberQueryParam = Depends(),
    auth: AuthSchema = Depends(AuthPermission(["module_agno_manage:team_members:export"]))
) -> StreamingResponse:
    """
    导出Team成员关系接口
    
    参数:
    - search: AgTeamMemberQueryParam - 查询参数
    - auth: AuthSchema - 认证信息
    
    返回:
    - StreamingResponse - 包含导出Team成员关系数据的流式响应
    """
    result_dict_list = await AgTeamMemberService.list_team_members_service(search=search, auth=auth)
    export_result = await AgTeamMemberService.batch_export_team_members_service(obj_list=result_dict_list)
    log.info('导出Team成员关系成功')
    return StreamResponse(
        data=bytes2file_response(export_result),
        media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        headers={'Content-Disposition': 'attachment; filename=ag_team_members.xlsx'}
    )


@AgTeamMemberRouter.post(
    '/import',
    summary="导入Team成员关系",
    description="导入Team成员关系"
)
async def import_team_members_list_controller(
    file: UploadFile,
    auth: AuthSchema = Depends(AuthPermission(["module_agno_manage:team_members:import"]))
) -> JSONResponse:
    """
    导入Team成员关系接口
    
    参数:
    - file: UploadFile - 上传的Excel文件
    - auth: AuthSchema - 认证信息
    
    返回:
    - JSONResponse - 包含导入Team成员关系结果的JSON响应
    """
    batch_import_result = await AgTeamMemberService.batch_import_team_members_service(file=file, auth=auth, update_support=True)
    log.info("导入Team成员关系成功")
    return SuccessResponse(data=batch_import_result, msg="导入Team成员关系成功")


@AgTeamMemberRouter.post(
    '/download/template',
    summary="获取Team成员关系导入模板",
    description="获取Team成员关系导入模板",
    dependencies=[Depends(AuthPermission(["module_agno_manage:team_members:download"]))]
)
async def export_team_members_template_controller() -> StreamingResponse:
    """
    获取Team成员关系导入模板接口
    
    返回:
    - StreamingResponse - 包含Team成员关系导入模板的流式响应
    """
    import_template_result = await AgTeamMemberService.import_template_download_team_members_service()
    log.info('获取Team成员关系导入模板成功')
    return StreamResponse(
        data=bytes2file_response(import_template_result),
        media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        headers={'Content-Disposition': 'attachment; filename=ag_team_members_template.xlsx'}
    )
