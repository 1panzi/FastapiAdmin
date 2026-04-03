# CLAUDE.md

本文件为 Claude Code（claude.ai/code）在此仓库中工作时提供指导。

## 语言要求

**所有回复必须使用中文。** 无论用户使用何种语言提问，均以中文回答。

## 工作范围

主要工作目录：
- `src/api/module_agno_manage/` — API 请求层（TypeScript）
- `src/views/module_agno_manage/` — Vue3 页面组件

除非明确指示，不得修改这两个目录以外的文件。

## 常用命令

```bash
# 开发
pnpm dev           # 启动开发服务器（Vite）
pnpm build         # 类型检查 + 生产构建
pnpm ts:check      # 仅执行 TypeScript 类型检查
pnpm lint          # 运行全部 lint（eslint + prettier + stylelint）
pnpm commit        # 使用 commitizen 提交（规范化 commit）
```

包管理器：**pnpm**（强制使用，禁止使用 npm/yarn）。

## 架构概览

本项目是基于 **Vue3 + TypeScript + Element-Plus** 的后台管理面板前端，用于管理基于 Agno 框架构建的 AI Agent。

### 模块结构

`module_agno_manage` 模块负责管理 Agno AI Agent 的所有资源：

| 资源 | 用途 |
|---|---|
| `models` | LLM 模型配置（provider、api_key、base_url） |
| `agents` | AI Agent 定义（50+ 配置字段） |
| `teams` | 多 Agent 群组 |
| `workflows` / `workflow_nodes` | 工作流自动化 |
| `knowledge_bases` / `documents` | RAG 知识库 |
| `toolkits` / `mcp_servers` | Agent 能力扩展 |
| `skills` | Agent 动作定义 |
| `embedders` / `vectordbs` | 向量嵌入与向量存储 |
| `memory_managers` | Agent 记忆配置 |
| `provider` | 只读 LLM 提供商元数据（用作下拉选项数据源） |
| `*_configs` | 专项配置：reasoning、compression、culture、learning、sess_summary |
| `roles` / `user_roles` | RBAC 权限管理 |
| `audit_logs` / `usage_logs` | 可观测性日志 |

### API 层规范（`src/api/module_agno_manage/*.ts`）

每个资源导出一个带类型的 API 对象，包含以下端点：

```typescript
const AgXxxAPI = {
  listAgXxx(query: AgXxxPageQuery)            // GET /agno_manage/xxx/list
  detailAgXxx(id: number)                     // GET /agno_manage/xxx/detail/{id}
  createAgXxx(body: AgXxxForm)                // POST /agno_manage/xxx/create
  updateAgXxx(id: number, body: AgXxxForm)    // PUT /agno_manage/xxx/update/{id}
  deleteAgXxx(ids: number[])                  // DELETE /agno_manage/xxx/delete
  batchAgXxx(body: BatchType)                 // PATCH /agno_manage/xxx/available/setting
  exportAgXxx(query)                          // POST /agno_manage/xxx/export → Blob
  downloadTemplateAgXxx()                     // POST /agno_manage/xxx/download/template → Blob
  importAgXxx(body: FormData)                 // POST /agno_manage/xxx/import
}
```

每个文件导出 3 个 TypeScript 接口：
- `AgXxxPageQuery`（继承 `PageQuery`）— 搜索/过滤参数，全部可选，支持 `created_time?: string[]` 和 `updated_time?: string[]` 日期范围
- `AgXxxTable`（继承 `BaseType`）— 列表展示，包含 `created_by?: CommonType` 和 `updated_by?: CommonType`
- `AgXxxForm`（继承 `BaseFormType`）— 新增/编辑表单字段

特例：`provider.ts` 为只读（无 CRUD），返回 `Provider[]`，用于填充模型提供商下拉框。

### 视图层规范（`src/views/module_agno_manage/*/index.vue`）

所有视图遵循统一结构：

**模板区域（按顺序）：**
1. 搜索表单（可折叠，展开后显示高级字段：日期范围 + 用户选择器）
2. 工具栏：左侧（新增、批量删除、更多下拉含批量启用/停用）+ 右侧（导入、导出、搜索显示/隐藏、刷新、列显隐）
3. `<el-table>`，通过 `tableColumns` ref 控制列的显示/隐藏
4. `<pagination>` 组件置于 `#footer` 插槽
5. `<el-dialog>` 用于新增/编辑/详情（详情用 `<el-descriptions>`，表单用 `<el-form>`）
6. `<ImportModal>` 和 `<ExportModal>` 组件

**关键脚本规范：**
- `queryFormData` reactive 对象 — 绑定搜索表单及分页（`page_no`、`page_size`）
- `formData` reactive 对象 — 绑定新增/编辑弹窗表单
- `detailFormData` ref — 绑定详情弹窗（只读）
- `tableColumns` ref 数组 — 控制列的显示/隐藏
- `loadingData()` — 获取列表，更新 `pageTableData` 和 `total`
- `handleOpenDialog(type, id?)` — 打开弹窗，如传入 id 则先获取详情
- `handleSubmit()` — 校验表单，根据 `formData.id` 判断调用新增或更新
- 权限指令格式：`v-hasPerm="['module_agno_manage:{resource}:{action}']"`，action 包括：`query`、`create`、`update`、`delete`、`detail`、`export`、`import`、`batch`

**tableColumns 规范**：每项格式为 `{ prop, label, show: true }`，`prop` 与 `AgXxxTable` 字段名对应。`status`、`created_id`、`updated_id` 存在重复列是有意为之——一列显示原始值，一列通过 slot 模板渲染（如标签/用户名）。

### 字段类型处理规范

#### 1. 布尔字段（三态：true/false/null）

**类型定义：**
- `AgXxxTable` 接口：`fieldName?: boolean | null`
- `AgXxxForm` 接口：`fieldName?: boolean | null`

**表单组件（编辑/新增）：**
```vue
<el-select v-model="formData.fieldName" placeholder="默认" clearable style="width:100%">
  <el-option label="开启" :value="true" />
  <el-option label="关闭" :value="false" />
</el-select>
```
- `clearable` 属性允许清空选择，返回 `null`（表示使用默认值）
- 三个状态：`true`（开启）、`false`（关闭）、`null`（默认/未设置）

**表格展示：**
```vue
<el-table-column label="字段名" prop="fieldName" min-width="100">
  <template #default="scope">
    <el-tag :type="scope.row.fieldName === true ? 'success' : scope.row.fieldName === false ? 'danger' : undefined">
      {{ scope.row.fieldName === true ? '是' : scope.row.fieldName === false ? '否' : '默认' }}
    </el-tag>
  </template>
</el-table-column>
```

**详情展示：**
```vue
<el-descriptions-item label="字段名" :span="2">
  <el-tag :type="detailFormData.fieldName === true ? 'success' : detailFormData.fieldName === false ? 'danger' : undefined">
    {{ detailFormData.fieldName === true ? '是' : detailFormData.fieldName === false ? '否' : '默认' }}
  </el-tag>
</el-descriptions-item>
```

**搜索表单：**
```vue
<el-select v-model="queryFormData.fieldName" placeholder="请选择" style="width: 120px" clearable>
  <el-option :value="'true'" label="是" />
  <el-option :value="'false'" label="否" />
</el-select>
```
注意：搜索表单中使用字符串 `'true'` 和 `'false'`，因为查询参数会被序列化为 URL 参数。

#### 2. Record 字段（字典/对象类型）

**类型定义：**
- `AgXxxTable` 接口：`fieldName?: Record<string, any> | null`
- `AgXxxForm` 接口：`fieldName?: Record<string, any>`（不带 `| null`）

**表单组件（编辑/新增）：**
```vue
<el-form-item label="字段名" prop="fieldName">
  <DictEditor v-model="formData.fieldName" />
</el-form-item>
```
使用 `@/views/module_agno_manage/components/DictEditor/index.vue` 组件。

**详情展示：**
```vue
<el-descriptions-item label="字段名" :span="4">
  <pre style="margin: 0; white-space: pre-wrap; font-size: 12px">{{ JSON.stringify(detailFormData.fieldName, null, 2) }}</pre>
</el-descriptions-item>
```

**搜索表单：**
Record 类型字段通常不在搜索表单中出现。

### models 视图特殊说明
- `providerList` 在 `onMounted` 时通过 `ProviderAPI.listProvider({})` 加载
- 提供商在 UI 中显示 `Provider.label`，存储值为 `Provider.provider`（字符串 key）
- `curdContentConfig` 将 ImportModal/ExportModal 与 API 方法绑定

## 开发计划

视图完善的优先级顺序：

1. **models**（`src/views/module_agno_manage/models/`）— ✅ 已完成
2. **toolkits**（`src/views/module_agno_manage/toolkits/`）— 完善表单字段
3. **mcp_servers** — 完善表单字段
4. **skills** — 完善表单字段
5. **knowledge_bases** — 完善表单字段
6. **embedders** — 完善表单字段
7. **agents** — 大型复杂表单（50+ 字段）
8. **teams** — 多 Agent 群组配置
9. **workflows** / **workflow_nodes** — 工作流自动化

每个视图完善时需检查以下内容：
- `tableColumns` 的 `label` 全部填写完整（初始生成时很多为空字符串 `""`）
- 表单字段与 `AgXxxForm` 接口完全对应
- 详情弹窗 `<el-descriptions>` 展示所有相关字段
- 校验规则 `required` 设置正确（不应将所有字段都标记为必填）
- 关联字段（如 model_id、embedder_id 等）使用合适的选择器组件，而非普通文本输入框


## AGNO相关的开发要求：
1 接口文件存放位置：src/api/module_agno_manage/agno/xxx.ts 如agent.ts session.ts
2 界面文件存放未知：src/views/module_agno_manage/agno/xxx/index.vue 如agno/agent/index.vue 
3 接口文件编写格式参照：src/api/module_agno_manage/下的其他ts文件。
4 agno的openapi.json文件在：agnoopenapi.json中。
你可以使用curl来测试这些接口：
我已经启动了一个agno的服务，测试的地址为：http://192.168.81.15:9008/
你可以发送如下的请求，来查看的实际的返回结果：
```bash
curl -X 'GET' \
  'http://192.168.81.15:9008/agents' \
  -H 'accept: application/json'
```