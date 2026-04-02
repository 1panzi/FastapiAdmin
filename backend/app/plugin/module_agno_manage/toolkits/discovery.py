"""
工具自动发现模块。

- scan_agno_tools()   扫描 agno.tools 包下所有 Toolkit 子类
- scan_custom_tools() 扫描 custom/ 目录下所有 Toolkit 子类

返回格式统一为 DiscoveredTool TypedDict，供 startup.py upsert 入库。
"""

import importlib
import importlib.util
import inspect
import pkgutil
from pathlib import Path
from typing import Any, TypedDict

from app.core.logger import log

# agno_catalog 作为 category/description 补充来源
from .agno_catalog import _CATALOG

# 构建 catalog 快速查找索引：module_path+class_name → info
_CATALOG_INDEX: dict[str, dict] = {
    f"{t['module_path']}.{t['class_name']}": t for t in _CATALOG
}

CUSTOM_TOOLS_DIR = Path(__file__).parent / "custom"

# 简单类型映射
_SIMPLE_TYPES = {
    "str": "str",
    "int": "int",
    "float": "float",
    "bool": "bool",
    "list": "list",
    "dict": "dict",
}


class ParamInfo(TypedDict):
    name: str
    type: str       # "str" / "int" / "float" / "bool" / "list" / "dict" / "object"
    default: Any    # 简单类型值或 None
    required: bool


class DiscoveredTool(TypedDict):
    name: str
    type: str           # 固定 "toolkit"
    module_path: str
    class_name: str
    category: str
    description: str
    tool_from: str      # "agno" | "custom"
    param_schema: list[ParamInfo]


def _normalize_type(hint) -> str:
    """把类型注解转成简洁字符串，复杂类型统一返回 'object'。"""
    if hint is inspect.Parameter.empty or hint is None:
        return "object"

    # 已经是基础类型
    if hint in (str, int, float, bool, list, dict):
        return hint.__name__

    hint_str = str(hint)

    # Optional[X] / X | None → 取内层类型
    for prefix in ("typing.Optional[", "Optional["):
        if hint_str.startswith(prefix):
            inner = hint_str[len(prefix):].rstrip("]")
            return _SIMPLE_TYPES.get(inner, "object") + " | None"

    # Union[X, None] 形式
    if "| None" in hint_str or "None |" in hint_str:
        core = hint_str.replace("| None", "").replace("None |", "").strip()
        # 去掉 typing. 前缀
        core = core.replace("typing.", "").strip()
        return _SIMPLE_TYPES.get(core, "object") + " | None"

    # 基础类型字符串
    clean = hint_str.replace("typing.", "").replace("<class '", "").rstrip("'>")
    return _SIMPLE_TYPES.get(clean, "object")


def extract_param_schema(cls) -> list[ParamInfo]:
    """从类 __init__ 签名提取参数信息（名称、类型、默认值、是否必填）。"""
    try:
        sig = inspect.signature(cls.__init__)
        hints = getattr(cls.__init__, "__annotations__", {})
    except (ValueError, TypeError):
        return []

    params: list[ParamInfo] = []
    for name, param in sig.parameters.items():
        if name == "self":
            continue
        if param.kind in (param.VAR_POSITIONAL, param.VAR_KEYWORD):
            continue

        type_str = _normalize_type(hints.get(name, inspect.Parameter.empty))

        if param.default is inspect.Parameter.empty:
            default = None
            required = True
        else:
            dv = param.default
            default = dv if isinstance(dv, (str, int, float, bool, type(None))) else str(dv)
            required = False

        params.append(ParamInfo(name=name, type=type_str, default=default, required=required))

    return params


def _get_toolkit_base():
    """懒加载 Toolkit 基类，避免 import 时 agno 未安装报错。"""
    try:
        from agno.tools.toolkit import Toolkit
        return Toolkit
    except ImportError:
        return None


def _extract_classes_from_module(module, toolkit_base, module_path: str, tool_from: str) -> list[DiscoveredTool]:
    """从已导入的 module 中提取所有 Toolkit 子类。"""
    results: list[DiscoveredTool] = []
    for attr_name in dir(module):
        obj = getattr(module, attr_name, None)
        if (
            obj is None
            or not inspect.isclass(obj)
            or obj is toolkit_base
            or not issubclass(obj, toolkit_base)
            or obj.__module__ != module.__name__
        ):
            continue

        key = f"{module_path}.{attr_name}"
        catalog_info = _CATALOG_INDEX.get(key, {})
        results.append(DiscoveredTool(
            name=catalog_info.get("name") or attr_name,
            type="toolkit",
            module_path=module_path,
            class_name=attr_name,
            category=catalog_info.get("category") or "其他",
            description=catalog_info.get("description") or (inspect.getdoc(obj) or "")[:255],
            tool_from=tool_from,
            param_schema=extract_param_schema(obj),
        ))
    return results


def scan_agno_tools() -> list[DiscoveredTool]:
    """扫描 agno.tools 包，返回所有 Toolkit 子类信息。"""
    toolkit_base = _get_toolkit_base()
    if toolkit_base is None:
        log.warning("[Discovery] agno 未安装，跳过 agno 工具扫描")
        return []

    try:
        import agno.tools as agno_tools_pkg
    except ImportError:
        log.warning("[Discovery] agno.tools 导入失败，跳过扫描")
        return []

    results: list[DiscoveredTool] = []
    for module_info in pkgutil.iter_modules(agno_tools_pkg.__path__, prefix="agno.tools."):
        try:
            mod = importlib.import_module(module_info.name)
            results.extend(_extract_classes_from_module(mod, toolkit_base, module_info.name, "agno"))
        except Exception as e:
            log.debug(f"[Discovery] 跳过 {module_info.name}: {e}")

    log.info(f"[Discovery] agno 工具扫描完成，发现 {len(results)} 个 Toolkit")
    return results


def scan_custom_tools() -> list[DiscoveredTool]:
    """扫描 custom/ 目录，返回所有 Toolkit 子类信息。"""
    toolkit_base = _get_toolkit_base()
    if toolkit_base is None:
        log.warning("[Discovery] agno 未安装，跳过 custom 工具扫描")
        return []

    if not CUSTOM_TOOLS_DIR.exists():
        return []

    results: list[DiscoveredTool] = []
    for py_file in CUSTOM_TOOLS_DIR.glob("*.py"):
        if py_file.name.startswith("_"):
            continue
        module_path = f"app.plugin.module_agno_manage.toolkits.custom.{py_file.stem}"
        try:
            spec = importlib.util.spec_from_file_location(module_path, py_file)
            if spec is None or spec.loader is None:
                continue
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            results.extend(_extract_classes_from_module(mod, toolkit_base, module_path, "custom"))
        except Exception as e:
            log.warning(f"[Discovery] 加载 custom 工具 {py_file.name} 失败: {e}")

    log.info(f"[Discovery] custom 工具扫描完成，发现 {len(results)} 个 Toolkit")
    return results


def scan_all_tools() -> list[DiscoveredTool]:
    """扫描全部工具（agno + custom）。"""
    return scan_agno_tools() + scan_custom_tools()
