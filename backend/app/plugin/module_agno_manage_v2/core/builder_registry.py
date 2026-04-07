"""
全局 Builder 注册表。

key = (category, type) tuple
value = BaseBuilder 实例

当前为空注册表，由 Task 3 填充各 Builder。
"""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.plugin.module_agno_manage_v2.core.builder_base import BaseBuilder

# 注册表：(category, type) -> Builder 实例
# 例如：("model", "openai") -> OpenAIModelBuilder()
builder_registry: dict[tuple[str, str], "BaseBuilder"] = {}
