# 设计讨论记录

## 一、v1 vs v2 总体评估

### 结论：选 v2

| 维度 | v1 | v2 |
|------|----|----|
| 表数量 | 20+ 张（每种资源一张） | 1 张 `ag_resources` |
| 模块数量 | 28 个（每种资源一套 model/schema/repo/service/router） | 1 个通用 `resource/` 模块 |
| 新增资源类型 | 加表 + 加模块 + 改 registry if/elif | 加一个 Builder 文件 |
| 前端表单 | 每种资源硬编码一个表单组件 | 一个通用组件，Schema API 驱动 |
| 可覆盖字段声明 | 各模块分散维护 `OVERRIDE_FIELDS` | Builder 类里的 `override_schema`，集中 |

---

## 二、v1 的核心问题：共享 Model 影响所有 Agent

v1 中 Model 是共享实例：

```
ag_models: { gpt-4o, temperature=0.7 }
    ├── Agent A
    ├── Agent B  ← 修改 temperature → 所有人受影响
    └── Agent C
```

**解决方案：参数覆盖 + 绑定**

`ag_bindings` 表加 `config_override` 字段（已实现）：

```
ag_bindings:
┌──────────┬──────────┬──────────────────────────────────┐
│ agent_id │ model_id │ config_override                  │
├──────────┼──────────┼──────────────────────────────────┤
│ agent_A  │ gpt-4o   │ { "temperature": 0.3 }           │
│ agent_B  │ gpt-4o   │ {}  ← 用 model 默认值            │
│ agent_C  │ gpt-4o   │ { "temperature": 0.9 }           │
└──────────┴──────────┴──────────────────────────────────┘
```

Runtime resolve：

```python
base = registry._model_cache[binding.resource_id]
override = binding.config_override or {}
return base.copy(update=override)  # 合并覆盖，互不影响
```

---

## 三、v2 天生支持 override_schema

v2 的 Builder 在声明创建字段（`schema`）的同时，可以声明允许覆盖的字段（`override_schema`）：

```python
class OpenAIBuilder(BaseBuilder):

    schema = [
        {"name": "api_key",    "type": "password", ...},
        {"name": "temperature","type": "float",    ...},
        ...
    ]

    # 绑定时允许 per-agent 覆盖的字段
    override_schema = [
        {"name": "temperature", "type": "float", "min": 0, "max": 2},
        {"name": "max_tokens",  "type": "int",   "min": 1          },
        {"name": "top_p",       "type": "float", "min": 0, "max": 1},
    ]
```

接口：

```
GET /agno_manage/v2/schema?category=model&type=openai&scope=override
```

前端渲染「覆盖参数」表单时，直接调此接口，无需硬编码任何字段。

---

## 四、热插拔支持

### v2 的热插拔方式

v2 通过"重建 Agent 实例 + replace"实现热插拔：

```python
async def update(uuid, body, db, registry):
    row = await crud.update(uuid, body, db)
    if row.category in ("agent", "team"):
        obj = builder_registry[...].build(row.config, resolver)
        registry.replace_agent(uuid, obj)   # 原子替换，正在执行的 run 继续跑完
```

Agent 是纯 Python 对象，重建耗时毫秒级，代价极低。

### 各操作是否需要重建 Agent

| 操作 | 是否需要重建 |
|------|-------------|
| 改 model 的 api_key | ❌ registry 原地换，所有 agent 自动感知 |
| 改 agent 的 instructions | ✅ 核心属性，需重建 |
| 给 agent 加/减工具（改绑定） | ❌ bindings 走 lambda resolve |
| 改 toolkit 参数 | ❌ registry 原地换 |

---

## 五、聊天窗口实时控制知识库

**场景**：用户在聊天窗口随时勾选/取消知识库，立即生效。

**结论**：不应改 `ag_bindings` 表，应直接在 run 请求里传参。

```json
POST /agents/{id}/runs
{
  "message": "帮我查一下...",
  "knowledge_refs": ["knowledge-uuid-D", "knowledge-uuid-E"]
}
```

| 方式 | 实时生效 | 影响其他用户 | 页面刷新后 |
|------|----------|-------------|-----------|
| 改绑定表 | ✅ | ⚠️ 影响所有人 | 持久保留 |
| run 请求传参 | ✅ | ❌ 不影响 | 恢复默认 ✅ |

`ag_bindings` 管理**默认绑定**，临时勾选直接传参，两者分工明确。

---

## 六、v2 ref 系统的级联能力

v2 的 `config` 中通过 `ref` 声明依赖：

```json
{
  "category": "agent",
  "config": {
    "model":     { "ref": "model-uuid-A" },
    "tools":     [{ "ref": "toolkit-uuid-C" }],
    "knowledge": [{ "ref": "knowledge-uuid-D" }]
  }
}
```

形成**显式依赖图**，带来以下能力：

1. **级联更新**：改了某个 model，自动找到所有依赖它的 agent 重建
2. **影响范围可视化**：「此 Model 被 5 个 Agent 使用」，删除前预警
3. **运行时动态组合**：前端传 ref 列表，后端动态 resolve，不绑死
4. **资源复用统计**：发现从未被 ref 的资源，提示清理

v1 用裸 `resource_id`，无法做反向查找，ref 依赖完全不透明。

---

## 七、前端构建优势

v2 前端只需一个通用动态表单组件：

```vue
<!-- DynamicResourceForm.vue -->
<template>
  <FormItem v-for="field in schema" :key="field.name" :field="field" v-model="form[field.name]" />
</template>

<script setup>
const schema = await fetch(`/agno_manage/v2/schema?category=${category}&type=${type}`)
// 后端加新 provider → 前端自动出现对应表单，零改动
</script>
```

**后端加新资源类型 → 前端零改动**，完全由 Schema API 驱动。

---

## 八、最终架构定位

```
ag_resources（统一 CRUD + Schema 驱动）
ag_bindings（默认绑定关系 + config_override 参数覆盖）

RuntimeRegistry
    ├── _model_cache[uuid]      → 原地替换，所有 agent 自动感知
    ├── _toolkit_map[uuid]      → 原地替换
    ├── _mcp_cache[uuid]        → LRU
    ├── _knowledge_cache[uuid]  → LRU
    └── agents[]                → ref 系统 + 按需重建

聊天运行时
    └── run 请求传参            → 临时覆盖，不写 DB
```
