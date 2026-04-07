"""
CultureManagerBuilder — CultureManager Builder。

CultureManager 是 agno 实验性功能，用于捕获和管理文化知识。
与 MemoryManager 类似，但专注于文化层面的知识积累。

build() 为 async，通过 resolver.resolve() 解析 model 依赖。
"""

from typing import Any

from app.plugin.module_agno_manage_v2.core.builder_base import BaseBuilder


class CultureManagerBuilder(BaseBuilder):
    category = "culture"
    type = "base"
    label = "文化管理器"
    agno_class = None

    extra_fields = [
        {
            "name": "model",
            "type": "ref_or_inline",
            "required": False,
            "order": 1,
            "source": "model",
        },
        {
            "name": "add_knowledge",
            "type": "bool",
            "required": False,
            "default": True,
            "order": 2,
        },
        {
            "name": "update_knowledge",
            "type": "bool",
            "required": False,
            "default": True,
            "order": 3,
        },
        {
            "name": "delete_knowledge",
            "type": "bool",
            "required": False,
            "default": False,
            "order": 4,
        },
        {
            "name": "clear_knowledge",
            "type": "bool",
            "required": False,
            "default": False,
            "order": 5,
        },
        {
            "name": "system_message",
            "type": "str",
            "required": False,
            "order": 6,
        },
        {
            "name": "culture_capture_instructions",
            "type": "str",
            "required": False,
            "order": 7,
        },
        {
            "name": "additional_instructions",
            "type": "str",
            "required": False,
            "order": 8,
        },
        {
            "name": "debug_mode",
            "type": "bool",
            "required": False,
            "default": False,
            "order": 9,
        },
    ]

    field_meta = {
        "model": {
            "label": "文化模型",
            "group": "基础配置",
            "span": 24,
            "tooltip": "用于提取和管理文化知识的模型（实验性功能）",
        },
        "add_knowledge": {"label": "允许添加知识", "group": "操作权限", "span": 12},
        "update_knowledge": {"label": "允许更新知识", "group": "操作权限", "span": 12},
        "delete_knowledge": {"label": "允许删除知识", "group": "操作权限", "span": 12},
        "clear_knowledge": {
            "label": "允许清空知识",
            "group": "操作权限",
            "span": 12,
            "tooltip": "危险操作，谨慎开启",
        },
        "system_message": {
            "label": "系统提示词",
            "group": "提示词配置",
            "span": 24,
            "placeholder": "留空使用默认系统提示词",
        },
        "culture_capture_instructions": {
            "label": "文化捕获指令",
            "group": "提示词配置",
            "span": 24,
            "placeholder": "留空使用默认文化捕获指令",
        },
        "additional_instructions": {
            "label": "附加指令",
            "group": "提示词配置",
            "span": 24,
            "placeholder": "附加到默认系统提示词后的额外指令",
        },
        "debug_mode": {"label": "调试模式", "group": "其他", "span": 12},
    }

    async def build(self, config: dict, resolver) -> Any:
        from agno.culture.manager import CultureManager

        model = await resolver.resolve(config.get("model"))

        return CultureManager(
            model=model,
            system_message=config.get("system_message") or None,
            culture_capture_instructions=config.get("culture_capture_instructions") or None,
            additional_instructions=config.get("additional_instructions") or None,
            add_knowledge=config.get("add_knowledge", True),
            update_knowledge=config.get("update_knowledge", True),
            delete_knowledge=config.get("delete_knowledge", False),
            clear_knowledge=config.get("clear_knowledge", False),
            debug_mode=config.get("debug_mode", False),
        )
