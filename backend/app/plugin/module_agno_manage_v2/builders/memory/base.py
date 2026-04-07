"""
MemoryManagerBuilder — MemoryManager Builder。

MemoryManager 依赖：
- model（ref 或 inline）：用于记忆管理的模型
- db：存储后端（通过外部配置，此处用 db_url 字符串配置）
- 各种操作开关（add/update/delete/clear）

build() 为 async，通过 resolver.resolve() 解析 model 依赖。
"""

from typing import Any

from app.plugin.module_agno_manage_v2.core.builder_base import BaseBuilder


class MemoryManagerBuilder(BaseBuilder):
    category = "memory"
    type = "base"
    label = "记忆管理器"
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
            "name": "add_memories",
            "type": "bool",
            "required": False,
            "default": True,
            "order": 2,
        },
        {
            "name": "update_memories",
            "type": "bool",
            "required": False,
            "default": True,
            "order": 3,
        },
        {
            "name": "delete_memories",
            "type": "bool",
            "required": False,
            "default": False,
            "order": 4,
        },
        {
            "name": "clear_memories",
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
            "name": "memory_capture_instructions",
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
            "label": "记忆模型",
            "group": "基础配置",
            "span": 24,
            "tooltip": "用于提取和管理记忆的模型，留空则使用 Agent 的主模型",
        },
        "add_memories": {"label": "允许添加记忆", "group": "操作权限", "span": 12},
        "update_memories": {"label": "允许更新记忆", "group": "操作权限", "span": 12},
        "delete_memories": {"label": "允许删除记忆", "group": "操作权限", "span": 12},
        "clear_memories": {
            "label": "允许清空记忆",
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
        "memory_capture_instructions": {
            "label": "记忆捕获指令",
            "group": "提示词配置",
            "span": 24,
            "placeholder": "留空使用默认记忆捕获指令",
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
        from agno.memory.manager import MemoryManager

        model = await resolver.resolve(config.get("model"))

        return MemoryManager(
            model=model,
            system_message=config.get("system_message") or None,
            memory_capture_instructions=config.get("memory_capture_instructions") or None,
            additional_instructions=config.get("additional_instructions") or None,
            add_memories=config.get("add_memories", True),
            update_memories=config.get("update_memories", True),
            delete_memories=config.get("delete_memories", False),
            clear_memories=config.get("clear_memories", False),
            debug_mode=config.get("debug_mode", False),
        )
