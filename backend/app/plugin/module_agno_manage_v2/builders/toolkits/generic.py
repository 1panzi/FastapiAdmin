"""
GenericToolkitBuilder — 统一处理所有 agno 内置工具。

通过 TOOLKIT_CATALOG 按 type_key 找到 module_path + class_name，
懒加载目标类并自动反射 schema，无需为每个工具写独立 Builder。

schema 构建优先级：
1. 反射 agno 工具类 __init__ 签名
2. catalog 中声明的 extra_fields 覆盖/追加（优先级更高）
"""

import importlib
from typing import Any

from app.core.logger import log
from app.plugin.module_agno_manage_v2.builders.toolkits.base import BaseToolkitBuilder
from app.plugin.module_agno_manage_v2.builders.toolkits.catalog import TOOLKIT_CATALOG
from app.plugin.module_agno_manage_v2.core.builder_base import generate_schema_from_class


class GenericToolkitBuilder(BaseToolkitBuilder):
    """动态加载 agno 内置工具的通用 Builder。"""

    def __init__(self, type_key: str):
        info = TOOLKIT_CATALOG[type_key]
        self.type = type_key
        self.label = info["name"]
        self._module_path: str = info["module_path"]
        self._class_name: str = info["class_name"]
        self._agno_cls = None
        self.extra_fields: list[dict] = info.get("extra_fields", [])

    def _load_class(self):
        if self._agno_cls is None:
            mod = importlib.import_module(self._module_path)
            self._agno_cls = getattr(mod, self._class_name)
        return self._agno_cls

    @property
    def schema(self) -> list[dict]:
        fields: dict[str, dict] = {}
        # 1. 反射 agno 工具类
        try:
            for f in generate_schema_from_class(self._load_class()):
                fields[f["name"]] = f
        except Exception as e:
            log.debug(f"[GenericToolkitBuilder] schema 反射失败 {self.type}: {e}")
        # 2. catalog extra_fields 覆盖/追加
        for f in self.extra_fields:
            fields[f["name"]] = {**fields.get(f["name"], {}), **f}
        return list(fields.values())

    def build(self, config: dict, resolver) -> Any:
        cls = self._load_class()
        param_map = TOOLKIT_CATALOG[self.type].get("param_map", {})
        mapped_config = {param_map.get(k, k): v for k, v in config.items()}
        return cls(**mapped_config)
