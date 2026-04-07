"""
Builder 基类 + generate_schema_from_class

提供：
- generate_schema_from_class(cls) -> list[dict]
  从 Agno 类的 __init__ 签名自动提取字段定义
- BaseBuilder(ABC)
  Builder 抽象基类，负责 schema 反射与 build 接口
"""

import inspect
from abc import ABC, abstractmethod
from typing import Any


def generate_schema_from_class(cls) -> list[dict]:
    """
    从 Agno 类的 __init__ 签名自动提取字段定义。

    过滤规则：
    - 跳过 self
    - 跳过 _ 开头的参数（内部参数）
    - 跳过 model_ 开头的参数（Pydantic 内部）

    类型推断：int/float/bool/str，其余兜底为 str。
    """
    try:
        sig = inspect.signature(cls.__init__)
    except (ValueError, TypeError):
        return []

    fields = []
    for name, param in sig.parameters.items():
        if name == "self":
            continue
        if name.startswith("_"):
            continue
        if name.startswith("model_"):
            continue

        field: dict = {"name": name}

        # 自动推断类型
        ann = param.annotation
        if ann is int:
            field["type"] = "int"
        elif ann is float:
            field["type"] = "float"
        elif ann is bool:
            field["type"] = "bool"
        elif ann is str:
            field["type"] = "str"
        else:
            field["type"] = "str"  # 兜底

        # 自动提取默认值
        if param.default != inspect.Parameter.empty:
            field["default"] = param.default
            field["required"] = False
        else:
            field["required"] = True

        fields.append(field)
    return fields


class BaseBuilder(ABC):
    """
    Builder 抽象基类。

    子类约定：
    - category: str     资源大类（如 "model", "reader"）
    - type: str         具体类型（如 "openai", "pdf"）
    - label: str        前端显示名称
    - agno_class        指向 Agno 类，用于自动反射字段
    - extra_fields      子类专属字段（手动定义或覆盖已有字段）
    - field_meta        UI 元数据补充（label/group/span/tooltip/约束等）

    schema property 构建顺序：
      1. 沿 MRO 反射所有基类的 agno_class（父类先填，子类不覆盖已有）
      2. extra_fields 覆盖/追加（merge，不是替换）
      3. 沿 MRO（reversed）合并所有层级的 field_meta（子类覆盖父类）
      4. 按 order 排序
    """

    category: str = ""
    type: str = ""
    label: str = ""

    agno_class = None  # 指向 Agno 类，自动反射字段

    # 子类专属字段（手动定义或覆盖已有字段）
    extra_fields: list[dict] = []

    # UI 元数据补充（label/group/span/tooltip/约束等）
    field_meta: dict[str, dict] = {}

    @property
    def schema(self) -> list[dict]:
        fields: dict[str, dict] = {}

        # 1. 沿 MRO 反射所有基类的 agno_class（父类先填，子类不覆盖已有）
        for parent in type(self).__mro__:
            if hasattr(parent, "agno_class") and parent.agno_class is not None:
                for f in generate_schema_from_class(parent.agno_class):
                    if f["name"] not in fields:
                        fields[f["name"]] = f

        # 2. extra_fields 覆盖/追加（merge，不是替换）
        for f in self.extra_fields:
            fields[f["name"]] = {**fields.get(f["name"], {}), **f}

        # 3. 沿 MRO（reversed）合并所有层级的 field_meta（子类覆盖父类）
        for parent in reversed(type(self).__mro__):
            if hasattr(parent, "field_meta"):
                for name, meta in parent.field_meta.items():
                    if name in fields:
                        fields[name].update(meta)

        return sorted(fields.values(), key=lambda x: x.get("order", 99))

    @abstractmethod
    def build(self, config: dict, resolver) -> Any:
        """接收展开后的 config dict，返回 Agno 对象。"""
        ...
