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

**status 字段规范**：
- 表单中使用 `el-radio-group`（不用 el-select），`:required="false"`，默认值为 `"0"`（启用）
- `formData` 和 `initialFormData` 中 `status` 初始值设为 `"0"`
- `handleOpenDialog` 新增分支中 `formData.status = "0"`（不得设为 `undefined`）
- 表格列使用 el-tag 渲染（`"0"` → success 绿色"启用"，其他 → info 灰色"停用"）

```vue
<!-- 表单 -->
<el-form-item label="状态" prop="status" :required="false">
  <el-radio-group v-model="formData.status">
    <el-radio value="0">启用</el-radio>
    <el-radio value="1">停用</el-radio>
  </el-radio-group>
</el-form-item>
```

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

### 3. 关联外键字段（ID 关联其他资源）

当字段存储的是另一张表的 ID（如 `embedder_id`、`model_id`、`owner_id`、`resource_id`），必须用下拉选择器而非文本输入框。

**选择方案：**
- **数据量小（≤100条）**：使用 `el-select` + `onMounted` 全量加载（见下方"全量加载模式"）
- **数据量大或不确定**：使用 `LazySelect` 懒加载组件（见下方"懒加载模式"，**推荐**）

---

#### 3a. 全量加载模式（数据量小时使用）

```typescript
// 脚本：声明列表 ref
const embedderList = ref<any[]>([]);

// 脚本：加载列表（onMounted 中调用）
async function loadEmbedderList() {
  const res = await AgEmbedderAPI.listAgEmbedder({ page_no: 1, page_size: 100 });
  embedderList.value = (res.data?.data?.items || []).map((item: any) => ({
    id: item.id,
    name: item.name || `Embedder#${item.id}`,
    provider: item.provider || "",
  }));
}

// 脚本：ID → 名称转换（用于表格列和详情显示）
function getEmbedderName(embedderId?: string): string {
  if (!embedderId) return "-";
  const found = embedderList.value.find((e) => String(e.id) === String(embedderId));
  return found ? found.name : String(embedderId);
}
```

**表单下拉（带 tooltip）：**
```vue
<el-form-item label="关联嵌入模型" prop="embedder_id" :required="false">
  <el-select v-model="formData.embedder_id" placeholder="请选择嵌入模型" clearable filterable style="width: 100%">
    <el-option
      v-for="item in embedderList"
      :key="item.id"
      :label="item.name"
      :value="String(item.id)"
    >
      <el-tooltip
        :content="`ID: ${item.id} | ${item.provider}`"
        placement="right"
        :show-after="300"
        :teleported="true"
        :enterable="false"
      >
        <span style="display: block; width: 100%;">{{ item.name }}</span>
      </el-tooltip>
    </el-option>
  </el-select>
</el-form-item>
```

**搜索表单下拉：**
```vue
<el-form-item label="关联嵌入模型" prop="embedder_id">
  <el-select v-model="queryFormData.embedder_id" placeholder="请选择嵌入模型" clearable filterable style="width: 200px">
    <el-option
      v-for="item in embedderList"
      :key="item.id"
      :label="item.name"
      :value="String(item.id)"
    />
  </el-select>
</el-form-item>
```

**表格列（显示名称而非 ID）：**
```vue
<el-table-column label="关联嵌入模型" prop="embedder_id" min-width="160" show-overflow-tooltip>
  <template #default="scope">
    <span>{{ getEmbedderName(scope.row.embedder_id) }}</span>
  </template>
</el-table-column>
```

**详情展示：**
```vue
<el-descriptions-item label="关联嵌入模型" :span="2">
  {{ getEmbedderName(detailFormData.embedder_id) }}
</el-descriptions-item>
```

**注意事项：**
- `value` 统一用 `String(item.id)`，因为后端返回的 ID 类型可能不一致
- `page_size: 100` 是约定的下拉列表加载上限
- 多个列表可以在 `onMounted` 中用 `Promise.all` 并行加载：
  ```typescript
  await Promise.all([loadEmbedderList(), loadVectordbTypeList()]);
  ```

---

#### 3b. 懒加载模式（数据量大时使用，推荐）

使用封装好的 `LazySelect` 组件（`@/views/module_agno_manage/components/LazySelect/index.vue`），支持滚动触底自动加载下一页、服务端关键字搜索、300ms 防抖。

**⚠️ LazySelect 已知陷阱与修复记录：**

1. **`v-infinite-scroll` 废弃警告**：Element Plus 3.0.0 起废弃该指令。已改用 `IntersectionObserver` 观察底部哨兵 `div`，不要再加回 `v-infinite-scroll`，也不要用 `el-scrollbar` 包裹选项（会破坏 el-select 原生下拉布局导致闪烁）。

2. **每次打开下拉都发请求 + 闪烁**：根本原因是 `el-select` 在 `filterable` 模式下，每次下拉打开时都会调用 `filter-method`（传入当前输入值，通常为 `''`），从而触发重新 fetch。
   **修复**：在 `handleFilter` 中加入 `keyword` 未变化时直接跳过的守卫：
   ```typescript
   function handleFilter(val: string) {
     if (val === keyword.value) return; // ← 关键：相同时跳过，防止打开时误触发
     keyword.value = val;
     if (filterTimer) clearTimeout(filterTimer);
     filterTimer = setTimeout(() => fetchPage(true), 300);
   }
   ```

3. **`IntersectionObserver` 立即触发**：Observer 挂载后会立即执行一次初始可见性检测，若哨兵 div 已在视口内（选项未溢出时），会立即触发 `loadMore`。
   **修复**：在 Observer 回调中用局部 `initialized` 标志跳过首次触发：
   ```typescript
   let initialized = false;
   observer = new IntersectionObserver((entries) => {
     if (!initialized) { initialized = true; return; } // ← 跳过初始检测
     if (entries[0].isIntersecting && !loading.value && !appending.value && !noMore.value) loadMore();
   }, { threshold: 0.1 });
   ```

4. **首次打开下拉有加载闪烁**：下拉打开时 options 为空才开始请求，用户看到"空 → 加载中 → 出现数据"的过程。
   **修复**：使用 `preload` prop，组件挂载时立即预拉取第一页，用户打开下拉时数据已就绪：
   ```vue
   <LazySelect :preload="true" ... />
   ```
   适用场景：父组件通过 `v-if` 控制 LazySelect 的显示（如先选类型再出现选择器），组件挂载即意味着用户需要它，此时预加载合理。默认 `false`，不影响其他使用场景。

5. **翻页时选择框卡顿**：滚动到第 20 条触发翻页时，`loading = true` 导致 input 出现转圈、底部文字抖动，用户感知明显。
   **修复**：区分两种加载状态——`loading`（首次/搜索，显示 input 转圈）和 `appending`（翻页追加，静默）。翻页时仅用 `appending`，底部保持等高占位，新选项悄悄追加，input 不变：
   ```typescript
   const loading = ref(false);    // 首次/搜索加载
   const appending = ref(false);  // 翻页追加（静默）

   async function fetchPage(reset = false) {
     if (loading.value || appending.value) return;
     reset ? (loading.value = true) : (appending.value = true);
     try { ... } finally {
       loading.value = false;
       appending.value = false;
     }
   }
   ```

**前提条件：** 对应列表接口的 `PageQuery` 须支持 `name?: string` 过滤参数。

**脚本：定义 fetcher 函数**
```typescript
import LazySelect from "@/views/module_agno_manage/components/LazySelect/index.vue";

// fetcher：传给 LazySelect 的数据拉取函数
const modelFetcher = async (params: { page_no: number; page_size: number; name?: string }) => {
  const res = await AgModelAPI.listAgModel({ ...params });
  const items = (res.data?.data?.items || []).map((item: any) => ({
    value: String(item.id),   // 必须是 string
    label: item.name || String(item.id),
    raw: item,                // 可选，保留原始数据
  }));
  return { items, total: res.data?.data?.total || 0 };
};
```

**脚本：表格/详情中的名称显示（按需 + cache，同步函数）**
```typescript
// 缓存已查询过的 ID → 名称映射
const modelNameCache = ref<Record<string, string>>({});

// 同步函数：首次调用时异步填充 cache，响应式触发重渲染
function getModelName(id?: string | number): string {
  if (!id) return "-";
  const key = String(id);
  if (modelNameCache.value[key]) return modelNameCache.value[key];
  // 触发异步填充，不阻塞模板渲染
  AgModelAPI.detailAgModel(Number(id))
    .then((res) => {
      modelNameCache.value[key] = res.data?.data?.name || key;
    })
    .catch(() => {
      modelNameCache.value[key] = key;
    });
  return key; // 首次渲染暂显 ID，异步回来后自动刷新
}
```

**表单（搜索区 + 新增/编辑区）：**
```vue
<!-- 搜索表单 -->
<el-form-item label="主模型" prop="model_id">
  <LazySelect
    v-model="queryFormData.model_id"
    :fetcher="modelFetcher"
    placeholder="请选择主模型"
    style="width: 200px"
  />
</el-form-item>

<!-- 新增/编辑表单 -->
<el-form-item label="主模型" prop="model_id" :required="false">
  <LazySelect
    v-model="formData.model_id"
    :fetcher="modelFetcher"
    placeholder="请选择主模型"
  />
</el-form-item>
```

**表格列（显示名称而非 ID）：**
```vue
<el-table-column label="主模型" prop="model_id" min-width="160" show-overflow-tooltip>
  <template #default="scope">
    <span>{{ getModelName(scope.row.model_id) }}</span>
  </template>
</el-table-column>
```

**详情展示：**
```vue
<el-descriptions-item label="主模型" :span="2">
  {{ getModelName(detailFormData.model_id) }}
</el-descriptions-item>
```

**onMounted 无需预加载**（LazySelect 在下拉打开时自动请求）：
```typescript
onMounted(async () => {
  if (dictTypes.length > 0) await dictStore.getDict(dictTypes);
  loadingData(); // 无需 loadModelList()
});
```

**LazySelect Props 说明：**
| Prop | 类型 | 说明 |
|---|---|---|
| `modelValue` | `string` | 绑定值（`v-model`） |
| `fetcher` | `Function` | 必填，签名见上方 |
| `placeholder` | `string` | 占位文本 |
| `clearable` | `boolean` | 是否可清空，默认 `true` |
| `pageSize` | `number` | 每页条数，默认 `20` |
| `initialLabel` | `string` | 编辑场景回显标签（可选） |
| `preload` | `boolean` | 挂载时立即预拉取第一页，消除首次打开的加载闪烁，默认 `false` |

### 4. 枚举类型下拉（来自后端 /agno/types 接口）

当后端提供枚举类型列表接口（如向量库类型、embedder provider 类型），在 API 文件中添加对应方法，并在视图中动态加载。

**API 文件中添加类型接口：**
```typescript
// 获取类型列表
agnoTypes() {
  return request<ApiResponse<AgXxxType[]>>({
    url: `${API_PATH}/agno/types`,
    method: "get",
  });
},
```

**类型声明：**
```typescript
export interface AgXxxType {
  db_type: string;      // 存储值（如 "pgvector"）
  label: string;        // 显示标签（如 "PostgreSQL + pgvector"）
  description: string;  // 描述
  config_example: Record<string, any>;  // 配置示例（可用于自动填入）
  // ...其他字段
}
```

**视图脚本：**
```typescript
const vectordbTypeList = ref<AgVectordbType[]>([]);

async function loadVectordbTypeList() {
  const res = await AgVectordbAPI.agnoTypes();
  vectordbTypeList.value = res.data?.data || [];
}

// 获取显示标签
function getProviderLabel(dbType?: string): string {
  if (!dbType) return "-";
  const found = vectordbTypeList.value.find((t) => t.db_type === dbType);
  return found ? found.label : dbType;
}

// 选择类型后自动填入 config_example（仅当 config 为空时）
function handleProviderChange(dbType: string) {
  const found = vectordbTypeList.value.find((t) => t.db_type === dbType);
  if (found?.config_example && !formData.config) {
    formData.config = { ...found.config_example };
  }
}
```

**表单下拉（带描述 tooltip）：**
```vue
<el-select v-model="formData.provider" placeholder="请选择类型" clearable style="width: 100%" @change="handleProviderChange">
  <el-option
    v-for="item in vectordbTypeList"
    :key="item.db_type"
    :label="item.label"
    :value="item.db_type"
  >
    <el-tooltip :content="item.description" placement="right" :show-after="300" :teleported="true" :enterable="false">
      <span style="display: block; width: 100%;">{{ item.label }}</span>
    </el-tooltip>
  </el-option>
</el-select>
```

### models 视图特殊说明
- `providerList` 在 `onMounted` 时通过 `ProviderAPI.listProvider({})` 加载
- 提供商在 UI 中显示 `Provider.label`，存储值为 `Provider.provider`（字符串 key）
- `curdContentConfig` 将 ImportModal/ExportModal 与 API 方法绑定

### embedders 视图特殊说明

嵌入器提供商接口返回的字段比 models 的提供商更丰富，需要利用这些字段驱动表单行为：

**独立 API 文件**：`src/api/module_agno_manage/embedder_providers.ts`（不复用 provider.ts），接口路径 `GET /agno_manage/embedders/agno/providers`。

**`EmbedderProvider` 关键字段：**
- `needs_api_key: boolean` — 是否需要 API 密钥，决定表单字段是否显示
- `needs_base_url: boolean` — 是否需要自定义端点，决定表单字段是否显示
- `base_url_label: string` — 端点地址的业务名称（如"Azure 端点地址"），用作表单 label 和 placeholder
- `popular_models: string[]` — 推荐模型列表，用于 model_id 的下拉候选
- `default_dimensions: number | null` — 默认向量维度，用于 dimensions 字段的 placeholder 提示

**表单联动模式（computed + @change）：**
```typescript
// 当前提供商对象（computed）
const currentProvider = computed(() =>
  providerList.value.find((p) => p.provider === formData.provider) ?? null
);

// 推荐模型列表（computed）
const currentProviderModels = computed(() =>
  currentProvider.value?.popular_models ?? []
);

// 切换提供商时清空依赖字段
function handleProviderChange() {
  formData.model_id = undefined;
  formData.api_key = undefined;
  formData.base_url = undefined;
  formData.dimensions = undefined;
}
```

**model_id 使用 el-select（filterable + allow-create）而非文本输入：**
```vue
<el-select
  v-model="formData.model_id"
  placeholder="请输入或选择嵌入模型标识"
  filterable
  allow-create
  default-first-option
  style="width: 100%"
>
  <el-option v-for="model in currentProviderModels" :key="model" :label="model" :value="model" />
</el-select>
```

**api_key / base_url 动态显示/隐藏：**
```vue
<!-- api_key：未选择提供商时默认显示，选择后按 needs_api_key 决定 -->
<el-form-item
  v-if="!formData.provider || currentProvider?.needs_api_key !== false"
  label="API密钥"
  prop="api_key"
  :required="currentProvider?.needs_api_key === true"
>
  <el-input v-model="formData.api_key" placeholder="请输入API密钥" />
</el-form-item>

<!-- base_url：label 和 placeholder 随提供商变化 -->
<el-form-item
  v-if="!formData.provider || currentProvider?.needs_base_url !== false"
  :label="currentProvider?.base_url_label || '自定义端点地址'"
  prop="base_url"
  :required="currentProvider?.needs_base_url === true"
>
  <el-input
    v-model="formData.base_url"
    :placeholder="currentProvider?.base_url_label ? `请输入${currentProvider.base_url_label}` : '请输入自定义端点地址'"
  />
</el-form-item>
```

**dimensions placeholder 显示默认值：**
```vue
<el-input
  v-model="formData.dimensions"
  :placeholder="currentProvider?.default_dimensions ? `默认 ${currentProvider.default_dimensions}，可不填` : '请输入向量维度（可选）'"
/>
```

### vectordbs 视图特殊说明
- `embedder_id` 使用关联外键下拉，从 `AgEmbedderAPI.listAgEmbedder` 加载
- `provider`（向量库类型）使用枚举下拉，从 `AgVectordbAPI.agnoTypes()` 加载，选择后自动填入 `config_example`
- 接口路径：`GET /agno_manage/vectordbs/agno/types`

### knowledge_bases 视图特殊说明

知识库列表页在常规 CRUD 基础上，通过 **`el-drawer`** 实现子资源（文档）管理，无需跳转页面。

#### 文档管理抽屉

操作列有「文档」按钮，点击后打开右侧抽屉，展示该知识库下所有文档并提供完整操作：

| 功能 | API 方法 | 说明 |
|---|---|---|
| 上传文件 | `uploadKBDoc(kb_id, FormData)` | 文件 + 可选 name/description，后端异步向量化 |
| 插入 URL / 文本 | `insertKBDoc(kb_id, KBDocInsertBody)` | type 可选 `url` 或 `text`，后端异步向量化 |
| 查询文档列表 | `listKBDocs(kb_id, query)` | 分页，支持 `page_no`/`page_size` |
| 删除文档 | `deleteKBDoc(kb_id, doc_id)` | 同时删除向量数据 |
| 重新向量化 | `reprocessKBDoc(kb_id, doc_id)` | 状态回退为 pending 后重新处理 |
| 向量检索 | `searchKB(kb_id, {query, limit})` | 返回 `KBSearchResult[]`，含 content 和 reranking_score |

以上 6 个方法均在 `src/api/module_agno_manage/knowledge_bases.ts` 中定义，并附带 3 个 TS 类型：

```typescript
interface AgKBDocumentItem { id, uuid, kb_id, name, storage_type, storage_path,
  doc_status, error_msg, content_id, metadata_config, description,
  created_time, updated_time }

interface KBDocInsertBody { url?, text_content?, name?, description?, metadata_config? }

interface KBSearchResult { name?, content?, meta_data?, reranking_score? }
```

#### doc_status 映射

| 值 | 标签 | tag type |
|---|---|---|
| `pending` | 待处理 | warning |
| `processing` | 处理中 | info |
| `completed` | 已完成 | success |
| `failed` | 失败 | danger |

辅助函数 `docStatusTagType(status)` 和 `docStatusLabel(status)` 已在 script 中定义，可直接复用于类似场景。

#### 抽屉开启状态管理

```typescript
const docDrawer = reactive({ visible: false, kbId: 0, kbName: '' });
// 打开时重置所有子状态再调用 loadKBDocs()
function handleOpenDocDrawer(row: AgKnowledgeBaseTable) { ... }
```

`el-drawer` 使用 `:destroy-on-close="true"`，关闭后状态自动销毁，无需手动清理。

## 开发计划

视图完善的优先级顺序：

1. **models**（`src/views/module_agno_manage/models/`）— ✅ 已完成
2. **toolkits**（`src/views/module_agno_manage/toolkits/`）— 完善表单字段
3. **mcp_servers** — 完善表单字段
4. **skills** — 完善表单字段
5. **knowledge_bases** — ✅ 已完成（含文档管理抽屉：上传文件 / 插入URL·文本 / 向量检索 / 重新向量化 / 删除，详见「knowledge_bases 视图特殊说明」）
6. **embedders** — ✅ 已完成
7. **reasoning_configs** — ✅ 已完成（bool 三态 select、model_id 关联下拉、数字字段 input-number）
8. **hooks** — ✅ 已完成（hook_type 枚举 select、run_in_background 三态 select、status 非必须 select）
9. **guardrails** — ✅ 已完成（type 枚举 select、hook_type 枚举 select、status 非必须 select）
10. **memory_managers** — ✅ 已完成（model_id 关联模型下拉、bool 四字段三态 select、文本字段 textarea）
11. **learning_configs** — ✅ 已完成（model_id 关联模型下拉、六个 JSON 字段 DictEditor、搜索表单删除 JSON 字段）
12. **compression_configs** — ✅ 已完成（model_id 关联模型下拉、整数字段 input-number、指令字段 textarea）
13. **agents** — 大型复杂表单（50+ 字段）
14. **teams** — ✅ 已完成（LazySelect 懒加载 model_id/memory_manager_id、布尔三态 select、整数 input-number、DictEditor、el-tabs 分组表单）
15. **workflows** / **workflow_nodes** — 工作流自动化

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