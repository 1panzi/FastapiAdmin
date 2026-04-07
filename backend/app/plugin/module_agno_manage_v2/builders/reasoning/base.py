"""
ReasoningBuilder — 推理配置 Builder。

agno 的推理能力通过在 Agent 上配置 reasoning=True 以及可选的
reasoning_model 来启用。本 Builder 管理"推理模型"资源（category=reasoning），
供 AgentBuilder 通过 ref 引用。

build() 返回一个 dict（reasoning config），AgentBuilder 在组装 Agent 时直接
传入 reasoning_model 参数；也可直接返回 Model 实例由 AgentBuilder 使用。

build() 为 async，通过 resolver.resolve() 解析 model 依赖。
"""

from typing import Any

from app.plugin.module_agno_manage_v2.core.builder_base import BaseBuilder


class ReasoningBuilder(BaseBuilder):
    """
    推理配置 Builder。

    返回一个包含推理配置的 dict，key 与 agno Agent 构造参数对应：
      - reasoning_model: Model 实例（可为 None，Agent 将使用默认 CoT）
      - min_steps / max_steps：推理步骤范围
      - use_json_mode：是否使用 JSON 模式
      - debug_mode：调试模式
    """

    category = "reasoning"
    type = "base"
    label = "推理配置"
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
            "name": "min_steps",
            "type": "int",
            "required": False,
            "default": 1,
            "order": 2,
        },
        {
            "name": "max_steps",
            "type": "int",
            "required": False,
            "default": 10,
            "order": 3,
        },
        {
            "name": "use_json_mode",
            "type": "bool",
            "required": False,
            "default": False,
            "order": 4,
        },
        {
            "name": "debug_mode",
            "type": "bool",
            "required": False,
            "default": False,
            "order": 5,
        },
    ]

    field_meta = {
        "model": {
            "label": "推理模型",
            "group": "基础配置",
            "span": 24,
            "tooltip": "用于推理的模型（支持原生推理模型如 o1/o3/DeepSeek-R1，或标准 CoT）；留空则 Agent 使用默认 CoT 推理",
        },
        "min_steps": {
            "label": "最少推理步骤",
            "group": "步骤配置",
            "span": 12,
            "min": 1,
            "max": 50,
        },
        "max_steps": {
            "label": "最多推理步骤",
            "group": "步骤配置",
            "span": 12,
            "min": 1,
            "max": 50,
            "tooltip": "推理步骤上限，防止无限循环",
        },
        "use_json_mode": {
            "label": "JSON 模式",
            "group": "高级配置",
            "span": 12,
            "tooltip": "推理输出使用 JSON 格式（适合结构化推理场景）",
        },
        "debug_mode": {"label": "调试模式", "group": "高级配置", "span": 12},
    }

    async def build(self, config: dict, resolver) -> Any:
        """
        返回推理配置 dict，供 AgentBuilder 使用。

        AgentBuilder 可检查 config 中是否有 "reasoning" key：
          reasoning_cfg = await resolver.resolve(config.get("reasoning"))
          # reasoning_cfg 即此处返回的 dict
          agent = Agent(
              reasoning=True,
              reasoning_model=reasoning_cfg.get("reasoning_model"),
              ...
          )
        """
        model = await resolver.resolve(config.get("model"))

        return {
            "reasoning_model": model,
            "min_steps": config.get("min_steps", 1),
            "max_steps": config.get("max_steps", 10),
            "use_json_mode": config.get("use_json_mode", False),
            "debug_mode": config.get("debug_mode", False),
        }
