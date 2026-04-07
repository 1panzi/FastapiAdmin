"""
Catalog Controller — 暴露 builder_registry 中的 Schema 信息。

提供两个端点：
  GET /v2/schema?category=<cat>         列出该大类支持的所有 type
  GET /v2/schema?category=<cat>&type=<t> 返回指定 (category, type) 的 fields schema
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import JSONResponse

from app.api.v1.module_system.auth.schema import AuthSchema
from app.common.response import SuccessResponse
from app.core.dependencies import AuthPermission
from app.core.logger import log
from app.plugin.module_agno_manage_v2.core.builder_registry import builder_registry

CatalogRouter = APIRouter(prefix="/v2/schema", tags=["V2-Schema目录"])


@CatalogRouter.get(
    "",
    summary="获取资源 Schema",
    description=(
        "当不传 type 时返回该 category 支持的所有类型列表；"
        "传入 type 时返回该 (category, type) 的字段 schema（fields）"
    ),
)
async def get_schema_controller(
    category: str | None = Query(None, description="资源大类，如 model/reader/agent/team"),
    type: str | None = Query(None, description="具体类型，如 openai/pdf/base；不传则返回类型列表"),
    auth: AuthSchema = Depends(AuthPermission(["module_agno_manage:v2:query"])),
) -> JSONResponse:
    """
    获取资源 Schema 接口

    参数:
    - category: str — 资源大类
    - type: str | None — 具体类型；不传时返回该 category 下所有类型列表
    - auth: AuthSchema — 认证信息

    返回:
    - JSONResponse — Schema 信息
    """
    if category is None:
        cat = [k[0] for k, v in builder_registry.items()]
        cat = list(set(cat))
        return SuccessResponse(
            data={"category": cat},
            msg="获取分类列表成功",
        )

    if type is None:
        # 返回该 category 支持的所有 type 列表
        types = [
            {"type": k[1], "label": getattr(v, "label", k[1])}
            for k, v in builder_registry.items()
            if k[0] == category
        ]
        log.info(f"查询 category={category} 类型列表成功，共 {len(types)} 个")
        return SuccessResponse(
            data={"category": category, "types": types},
            msg="获取类型列表成功",
        )

    builder = builder_registry.get((category, type))
    if not builder:
        raise HTTPException(
            status_code=404,
            detail=f"不支持的类型: {category}/{type}",
        )

    log.info(f"查询 schema category={category} type={type} 成功")
    return SuccessResponse(
        data={
            "category": category,
            "type": type,
            "label": getattr(builder, "label", type),
            "fields": builder.schema,
        },
        msg="获取 Schema 成功",
    )
