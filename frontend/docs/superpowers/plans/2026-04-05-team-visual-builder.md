# Team 可视化构建器 Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 新增一个基于 Vue Flow 的 Team 可视化构建页面，支持嵌套 Team 的组织架构图查看与编辑。

**Architecture:** 独立路由页面 `/agno/team-builder`，通过 URL 参数 `?root_id=123` 指定根 Team。从后端递归加载 team_members，转换为 Vue Flow nodes/edges 渲染画布。右侧 400px 面板点击节点后展开，显示 TeamFormFields 组件（从 teams/index.vue 抽出）。保存时串行批量提交。

**Tech Stack:** Vue3 + TypeScript + Element-Plus + `@vue-flow/core` + `@vue-flow/background` + `@vue-flow/controls` + `@vue-flow/minimap`

**Spec:** `docs/superpowers/specs/2026-04-05-team-visual-builder-design.md`

---

## Chunk 1: 依赖安装 + TeamFormFields 组件 + teams/index.vue 改造

### Task 1: 安装 Vue Flow 依赖

**Files:**
- 修改: `package.json` (pnpm 自动)

- [ ] **Step 1: 安装依赖**

```bash
cd /home/rb/pb/project/github/FastapiAdmin/frontend
pnpm add @vue-flow/core @vue-flow/background @vue-flow/controls @vue-flow/minimap
```

- [ ] **Step 2: 验证类型检查通过**

```bash
pnpm ts:check
```
期望：无新增错误

- [ ] **Step 3: 提交**

```bash
git add package.json pnpm-lock.yaml
git commit -m "chore: 安装 vue-flow 相关依赖"
```

---

### Task 2: 创建 TeamFormFields.vue 组件

将 `teams/index.vue` 中编辑弹窗的 `<el-form>` 内容（el-tabs + 所有 tab pane）抽取为独立组件，供 teams/index.vue Dialog 和 team_builder 右侧面板共用。

> **设计说明：** TeamFormFields 只负责 Team 的配置表单字段（5 个 Tab：基本信息、成员协作、历史与记忆、知识库、元数据）。「成员列表」管理 Tab 不在此组件内——它需要访问 team_member 关联数据，属于 team_builder 右侧面板专属逻辑，由 team_builder/index.vue 在 el-tabs 外层额外添加。

**Files:**
- 创建: `src/views/module_agno_manage/teams/components/TeamFormFields.vue`

- [ ] **Step 1: 创建目录并创建组件**

创建 `src/views/module_agno_manage/teams/components/TeamFormFields.vue`，内容如下：

```vue
<!-- Team 表单字段组件：供 teams/index.vue Dialog 和 team_builder 右侧面板复用 -->
<template>
  <el-form
    ref="formRef"
    :model="formData"
    :rules="rules"
    label-suffix=":"
    label-width="160px"
    label-position="right"
  >
    <el-tabs type="border-card" class="team-form-tabs">
      <!-- ══ Tab 1: 基本信息 ══ -->
      <el-tab-pane label="基本信息">
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="Team名称" prop="name">
              <el-input v-model="formData.name" placeholder="请输入Team名称" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="主模型" prop="model_id" :required="false">
              <LazySelect v-model="formData.model_id" :fetcher="modelFetcher" placeholder="请选择主模型" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="记忆管理器" prop="memory_manager_id" :required="false">
              <LazySelect v-model="formData.memory_manager_id" :fetcher="memoryManagerFetcher" placeholder="请选择记忆管理器" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="协作模式" prop="mode" :required="false">
              <el-select v-model="formData.mode" placeholder="请选择协作模式" clearable style="width: 100%">
                <el-option value="route" label="route（路由）" />
                <el-option value="coordinate" label="coordinate（协调）" />
                <el-option value="collaborate" label="collaborate（协作）" />
                <el-option value="tasks" label="tasks（任务）" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="状态" prop="status" :required="false">
              <el-radio-group v-model="formData.status">
                <el-radio value="0">启用</el-radio>
                <el-radio value="1">停用</el-radio>
              </el-radio-group>
            </el-form-item>
          </el-col>
          <el-col :span="24">
            <el-form-item label="Team指令" prop="instructions" :required="false">
              <el-input v-model="formData.instructions" placeholder="请输入Team指令（system prompt）" type="textarea" :rows="4" />
            </el-form-item>
          </el-col>
          <el-col :span="24">
            <el-form-item label="期望输出格式" prop="expected_output" :required="false">
              <el-input v-model="formData.expected_output" placeholder="请输入期望输出格式说明" type="textarea" :rows="2" />
            </el-form-item>
          </el-col>
          <el-col :span="24">
            <el-form-item label="描述" prop="description" :required="false">
              <el-input v-model="formData.description" :rows="3" :maxlength="100" show-word-limit type="textarea" placeholder="请输入描述" />
            </el-form-item>
          </el-col>
        </el-row>
      </el-tab-pane>

      <!-- ══ Tab 2: 成员协作 ══ -->
      <el-tab-pane label="成员协作">
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="是否直接响应" prop="respond_directly" :required="false">
              <el-select v-model="formData.respond_directly" placeholder="默认" clearable style="width:100%">
                <el-option label="开启" :value="true" />
                <el-option label="关闭" :value="false" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="分发给所有成员" prop="delegate_to_all_members" :required="false">
              <el-select v-model="formData.delegate_to_all_members" placeholder="默认" clearable style="width:100%">
                <el-option label="开启" :value="true" />
                <el-option label="关闭" :value="false" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="为成员决定输入" prop="determine_input_for_members" :required="false">
              <el-select v-model="formData.determine_input_for_members" placeholder="默认" clearable style="width:100%">
                <el-option label="开启" :value="true" />
                <el-option label="关闭" :value="false" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="最大迭代次数" prop="max_iterations" :required="false">
              <el-input-number v-model="formData.max_iterations" :min="1" :precision="0" style="width:100%" placeholder="默认" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="工具调用上限" prop="tool_call_limit" :required="false">
              <el-input-number v-model="formData.tool_call_limit" :min="1" :precision="0" style="width:100%" placeholder="默认" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="输出Markdown" prop="markdown" :required="false">
              <el-select v-model="formData.markdown" placeholder="默认" clearable style="width:100%">
                <el-option label="开启" :value="true" />
                <el-option label="关闭" :value="false" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="流式输出" prop="stream" :required="false">
              <el-select v-model="formData.stream" placeholder="默认" clearable style="width:100%">
                <el-option label="开启" :value="true" />
                <el-option label="关闭" :value="false" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="流式推送事件" prop="stream_events" :required="false">
              <el-select v-model="formData.stream_events" placeholder="默认" clearable style="width:100%">
                <el-option label="开启" :value="true" />
                <el-option label="关闭" :value="false" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="调试模式" prop="debug_mode" :required="false">
              <el-select v-model="formData.debug_mode" placeholder="默认" clearable style="width:100%">
                <el-option label="开启" :value="true" />
                <el-option label="关闭" :value="false" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
      </el-tab-pane>

      <!-- ══ Tab 3: 历史与记忆 ══ -->
      <el-tab-pane label="历史与记忆">
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="传Team历史给成员" prop="add_team_history_to_members" :required="false">
              <el-select v-model="formData.add_team_history_to_members" placeholder="默认" clearable style="width:100%">
                <el-option label="开启" :value="true" />
                <el-option label="关闭" :value="false" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="传给成员历史次数" prop="num_team_history_runs" :required="false">
              <el-input-number v-model="formData.num_team_history_runs" :min="1" :precision="0" style="width:100%" placeholder="默认" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="共享成员交互" prop="share_member_interactions" :required="false">
              <el-select v-model="formData.share_member_interactions" placeholder="默认" clearable style="width:100%">
                <el-option label="开启" :value="true" />
                <el-option label="关闭" :value="false" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="成员工具加入上下文" prop="add_member_tools_to_context" :required="false">
              <el-select v-model="formData.add_member_tools_to_context" placeholder="默认" clearable style="width:100%">
                <el-option label="开启" :value="true" />
                <el-option label="关闭" :value="false" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="读取聊天历史" prop="read_chat_history" :required="false">
              <el-select v-model="formData.read_chat_history" placeholder="默认" clearable style="width:100%">
                <el-option label="开启" :value="true" />
                <el-option label="关闭" :value="false" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="搜索历史会话" prop="search_past_sessions" :required="false">
              <el-select v-model="formData.search_past_sessions" placeholder="默认" clearable style="width:100%">
                <el-option label="开启" :value="true" />
                <el-option label="关闭" :value="false" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="搜索历史会话数量" prop="num_past_sessions_to_search" :required="false">
              <el-input-number v-model="formData.num_past_sessions_to_search" :min="1" :precision="0" style="width:100%" placeholder="默认" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="智能记忆" prop="enable_agentic_memory" :required="false">
              <el-select v-model="formData.enable_agentic_memory" placeholder="默认" clearable style="width:100%">
                <el-option label="开启" :value="true" />
                <el-option label="关闭" :value="false" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="运行后更新记忆" prop="update_memory_on_run" :required="false">
              <el-select v-model="formData.update_memory_on_run" placeholder="默认" clearable style="width:100%">
                <el-option label="开启" :value="true" />
                <el-option label="关闭" :value="false" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="开启会话摘要" prop="enable_session_summaries" :required="false">
              <el-select v-model="formData.enable_session_summaries" placeholder="默认" clearable style="width:100%">
                <el-option label="开启" :value="true" />
                <el-option label="关闭" :value="false" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="摘要加入上下文" prop="add_session_summary_to_context" :required="false">
              <el-select v-model="formData.add_session_summary_to_context" placeholder="默认" clearable style="width:100%">
                <el-option label="开启" :value="true" />
                <el-option label="关闭" :value="false" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
      </el-tab-pane>

      <!-- ══ Tab 4: 知识库 ══ -->
      <el-tab-pane label="知识库">
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="搜索知识库" prop="search_knowledge" :required="false">
              <el-select v-model="formData.search_knowledge" placeholder="默认" clearable style="width:100%">
                <el-option label="开启" :value="true" />
                <el-option label="关闭" :value="false" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="允许更新知识库" prop="update_knowledge" :required="false">
              <el-select v-model="formData.update_knowledge" placeholder="默认" clearable style="width:100%">
                <el-option label="开启" :value="true" />
                <el-option label="关闭" :value="false" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="智能知识过滤" prop="enable_agentic_knowledge_filters" :required="false">
              <el-select v-model="formData.enable_agentic_knowledge_filters" placeholder="默认" clearable style="width:100%">
                <el-option label="开启" :value="true" />
                <el-option label="关闭" :value="false" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="智能状态" prop="enable_agentic_state" :required="false">
              <el-select v-model="formData.enable_agentic_state" placeholder="默认" clearable style="width:100%">
                <el-option label="开启" :value="true" />
                <el-option label="关闭" :value="false" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
      </el-tab-pane>

      <!-- ══ Tab 5: 元数据 ══ -->
      <el-tab-pane label="元数据">
        <el-form-item label="元数据配置" prop="metadata_config" :required="false">
          <DictEditor v-model="formData.metadata_config" />
        </el-form-item>
      </el-tab-pane>
    </el-tabs>
  </el-form>
</template>

<script setup lang="ts">
import { ref } from "vue";
import LazySelect from "@/views/module_agno_manage/components/LazySelect/index.vue";
import DictEditor from "@/views/module_agno_manage/components/DictEditor/index.vue";
import AgModelAPI from "@/api/module_agno_manage/models";
import AgMemoryManagerAPI from "@/api/module_agno_manage/memory_managers";
import type { AgTeamForm } from "@/api/module_agno_manage/teams";

defineOptions({ name: "TeamFormFields", inheritAttrs: false });

const props = defineProps<{
  formData: AgTeamForm;
}>();

// 暴露 formRef 及代理方法，父组件可直接调用 ref.validate() 而无需 ref.formRef.validate()
const formRef = ref();
defineExpose({
  formRef,
  validate: (...args: any[]) => formRef.value?.validate(...args),
  resetFields: () => formRef.value?.resetFields(),
  clearValidate: () => formRef.value?.clearValidate(),
});

const rules = {
  name: [{ required: true, message: "请输入Team名称", trigger: "blur" }],
};

// LazySelect fetchers
const modelFetcher = async (params: { page_no: number; page_size: number; name?: string }) => {
  const res = await AgModelAPI.listAgModel({ ...params });
  const items = (res.data?.data?.items || []).map((item: any) => ({
    value: String(item.id),
    label: item.name || String(item.id),
    raw: item,
  }));
  return { items, total: res.data?.data?.total || 0 };
};

const memoryManagerFetcher = async (params: { page_no: number; page_size: number; name?: string }) => {
  const res = await AgMemoryManagerAPI.listAgMemoryManager({ ...params });
  const items = (res.data?.data?.items || []).map((item: any) => ({
    value: String(item.id),
    label: item.name || String(item.id),
    raw: item,
  }));
  return { items, total: res.data?.data?.total || 0 };
};
</script>

<style lang="scss" scoped>
.team-form-tabs {
  width: 100%;
}
</style>
```

- [ ] **Step 2: 类型检查**

```bash
pnpm ts:check
```
期望：无错误

- [ ] **Step 3: 提交**

```bash
git add src/views/module_agno_manage/teams/components/TeamFormFields.vue
git commit -m "feat(teams): 抽取 TeamFormFields 表单字段组件"
```

---

### Task 3: 修改 teams/index.vue

① 将编辑弹窗中的 `<el-form>` 替换为 `<TeamFormFields>`；② 在操作列新增「可视化」跳转按钮。

**Files:**
- 修改: `src/views/module_agno_manage/teams/index.vue`

- [ ] **Step 1: 在 script 中引入组件和 useRouter**

在 `teams/index.vue` 的 `<script setup>` 顶部引入区域，添加：

```typescript
import { useRouter } from "vue-router";
import TeamFormFields from "./components/TeamFormFields.vue";

const router = useRouter();

function handleOpenVisualBuilder(id: number) {
  router.push(`/agno/team-builder?root_id=${id}`);
}
```

- [ ] **Step 2: 替换编辑弹窗中的 `<el-form>` 块**

在 `<!-- 新增、编辑表单 -->` 的 `<template v-else>` 内，将整个 `<el-form ...> ... </el-form>` 替换为：

```vue
<TeamFormFields ref="dataFormRef" :form-data="formData" />
```

- [ ] **Step 3: 修改 handleSubmit 中的 validate 调用**

由于 TeamFormFields 通过 `defineExpose` 代理暴露了 `validate` 方法，`dataFormRef.value.validate(...)` 调用方式保持不变，无需修改 `handleSubmit`。

> 确认 script 中 `handleSubmit` 里所有形如 `dataFormRef.value.validate(async (valid) => {...})` 的调用不需要改动。

- [ ] **Step 4: 在操作列新增「可视化」按钮**

在操作列的「编辑」按钮之后、「删除」按钮之前，添加：

```vue
<el-button
  v-hasPerm="['module_agno_manage:teams:update']"
  type="warning"
  size="small"
  link
  icon="Share"
  @click="handleOpenVisualBuilder(scope.row.id)"
>
  可视化
</el-button>
```

- [ ] **Step 4: 类型检查**

```bash
pnpm ts:check
```
期望：无错误

- [ ] **Step 5: 提交**

```bash
git add src/views/module_agno_manage/teams/index.vue
git commit -m "feat(teams): 引入 TeamFormFields 组件 + 新增可视化跳转按钮"
```

---

## Chunk 2: team_builder — 骨架 + 数据加载 + 自定义节点

### Task 4: 创建 team_builder 骨架页面

**Files:**
- 创建: `src/views/module_agno_manage/team_builder/index.vue`

- [ ] **Step 1: 创建基础骨架**

创建 `src/views/module_agno_manage/team_builder/index.vue`，先建立页面结构（工具栏 + 画布占位 + 右侧面板），不涉及 Vue Flow 具体逻辑：

```vue
<template>
  <div class="team-builder">
    <!-- 工具栏 -->
    <div class="team-builder__toolbar">
      <div class="toolbar-left">
        <span class="toolbar-title">Team 可视化构建器</span>
        <LazySelect
          v-model="rootTeamId"
          :fetcher="teamFetcher"
          placeholder="选择根 Team"
          style="width: 220px"
          @update:model-value="handleRootTeamChange"
        />
      </div>
      <div class="toolbar-right">
        <el-button icon="Plus" @click="handleCreateTeam">新建 Team</el-button>
        <el-button icon="User" @click="handleAddAgentMember">添加 Agent 成员</el-button>
        <el-button type="primary" icon="Check" :loading="saving" @click="handleSave">保存</el-button>
        <el-button icon="ArrowLeft" @click="handleBack">返回列表</el-button>
      </div>
    </div>

    <!-- 主内容区 -->
    <div class="team-builder__main">
      <!-- 画布区 -->
      <div class="team-builder__canvas" :style="{ width: panelVisible ? 'calc(100% - 400px)' : '100%' }">
        <div v-if="!rootTeamId" class="canvas-empty">
          <el-empty description="请在上方选择一个根 Team 开始可视化" />
        </div>
        <!-- Vue Flow 将在 Task 5 中填入 -->
        <div v-else style="width:100%;height:100%;background:#f5f7fa;display:flex;align-items:center;justify-content:center;">
          <span>画布加载中...</span>
        </div>
      </div>

      <!-- 右侧配置面板 -->
      <div v-if="panelVisible" class="team-builder__panel">
        <div class="panel-header">
          <span>{{ selectedNode?.type === 'teamNode' ? 'Team 配置' : 'Agent 成员' }}</span>
          <el-button icon="Close" circle size="small" @click="panelVisible = false" />
        </div>
        <div class="panel-body">
          <!-- 面板内容将在 Task 7 中填入 -->
          <p>节点 ID: {{ selectedNode?.id }}</p>
        </div>
      </div>
    </div>

    <!-- 新建 Team 弹窗 -->
    <el-dialog v-model="createTeamDialog.visible" title="新建 Team" width="400px">
      <el-form :model="createTeamDialog.form" label-width="80px">
        <el-form-item label="名称" required>
          <el-input v-model="createTeamDialog.form.name" placeholder="请输入 Team 名称" />
        </el-form-item>
        <el-form-item label="协作模式">
          <el-select v-model="createTeamDialog.form.mode" style="width:100%">
            <el-option value="route" label="route（路由）" />
            <el-option value="coordinate" label="coordinate（协调）" />
            <el-option value="collaborate" label="collaborate（协作）" />
            <el-option value="tasks" label="tasks（任务）" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="createTeamDialog.visible = false">取消</el-button>
        <el-button type="primary" @click="handleConfirmCreateTeam">确定</el-button>
      </template>
    </el-dialog>

    <!-- 添加 Agent 成员弹窗（工具栏入口） -->
    <el-dialog v-model="addAgentDialog.visible" title="选择 Agent 成员" width="400px">
      <el-form label-width="80px">
        <el-form-item label="Agent" required>
          <LazySelect
            v-model="addAgentDialog.selectedAgentId"
            :fetcher="agentFetcher"
            placeholder="请选择 Agent"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="addAgentDialog.visible = false">取消</el-button>
        <el-button type="primary" @click="handleConfirmAddAgent">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
defineOptions({ name: "AgTeamBuilder", inheritAttrs: false });

import { ref, reactive, onMounted } from "vue";
import { useRoute, useRouter } from "vue-router";
import { ElMessage, ElMessageBox } from "element-plus";
import LazySelect from "@/views/module_agno_manage/components/LazySelect/index.vue";
import AgTeamAPI from "@/api/module_agno_manage/teams";
import AgTeamMemberAPI from "@/api/module_agno_manage/team_members";
import AgAgentAPI from "@/api/module_agno_manage/agents";
import type { AgTeamTable, AgTeamForm } from "@/api/module_agno_manage/teams";
import type { AgTeamMemberTable } from "@/api/module_agno_manage/team_members";

const route = useRoute();
const router = useRouter();

// 根 Team ID（来自 URL 参数或选择器）
const rootTeamId = ref<string | undefined>(
  route.query.root_id ? String(route.query.root_id) : undefined
);

// 右侧面板
const panelVisible = ref(false);
const selectedNode = ref<{ id: string; type: string; data: any } | null>(null);

// 保存状态
const saving = ref(false);

// 新建 Team 弹窗
const createTeamDialog = reactive({
  visible: false,
  form: { name: "", mode: "route" as string },
});

// 添加 Agent 成员弹窗（工具栏「添加 Agent 成员」按钮触发）
const addAgentDialog = reactive({
  visible: false,
  selectedAgentId: undefined as string | undefined,
});

// Team fetcher（LazySelect 用）
const teamFetcher = async (params: { page_no: number; page_size: number; name?: string }) => {
  const res = await AgTeamAPI.listAgTeam({ ...params });
  const items = (res.data?.data?.items || []).map((item: any) => ({
    value: String(item.id),
    label: item.name || String(item.id),
    raw: item,
  }));
  return { items, total: res.data?.data?.total || 0 };
};

function handleRootTeamChange(id: string) {
  router.replace({ query: { root_id: id } });
  loadGraph(id);
}

function handleBack() {
  router.push("/agno/teams");
}

function handleCreateTeam() {
  createTeamDialog.form = { name: "", mode: "route" };
  createTeamDialog.visible = true;
}

// 工具栏「添加 Agent 成员」：弹出 LazySelect 选择已有 Agent，加入当前选中的 Team 节点
// 若当前未选中 TeamNode，提示用户先点击一个 Team 节点
function handleAddAgentMember() {
  if (!selectedNode.value || selectedNode.value.type !== "teamNode") {
    ElMessage.warning("请先在画布中点击一个 Team 节点，再添加 Agent 成员");
    return;
  }
  addAgentDialog.visible = true;
}

// Agent fetcher（用于添加 Agent 成员弹窗的 LazySelect）
const agentFetcher = async (params: { page_no: number; page_size: number; name?: string }) => {
  const res = await AgAgentAPI.listAgAgent({ ...params });
  const items = (res.data?.data?.items || []).map((item: any) => ({
    value: String(item.id),
    label: item.name || String(item.id),
    raw: item,
  }));
  return { items, total: res.data?.data?.total || 0 };
};

// 确认添加 Agent 成员（添加到当前选中的 TeamNode）
function handleConfirmAddAgent() {
  if (!addAgentDialog.selectedAgentId) {
    ElMessage.warning("请选择 Agent");
    return;
  }
  const teamNode = selectedNode.value;
  if (!teamNode || teamNode.type !== "teamNode") return;

  const teamNodeId = teamNode.id;
  const agentId = addAgentDialog.selectedAgentId;
  const agentNodeId = `agent-${agentId}-in-${teamNode.data.team?.id}-${Date.now()}`;

  // 添加 AgentNode 到画布（位置在 Team 节点正下方）
  const teamPos = nodes.value.find((n) => n.id === teamNodeId)?.position || { x: 0, y: 0 };
  addNodes([{
    id: agentNodeId,
    type: "agentNode",
    position: { x: teamPos.x, y: teamPos.y + 180 },
    data: { agentId, member: { member_type: "agent", member_id: agentId, member_order: 99, status: "0" } },
  }]);
  addEdges([{ id: `e-${teamNodeId}-${agentNodeId}`, source: teamNodeId, target: agentNodeId }]);

  // 加入 pendingChanges（Task 8 中 handleSave 使用）
  pendingChanges.value.push({
    type: "addMember",
    payload: {
      team_id: teamNode.data.team?.id ? String(teamNode.data.team.id) : teamNodeId,
      member_type: "agent",
      member_id: agentId,
      member_order: 99,
      status: "0",
    },
  });

  addAgentDialog.visible = false;
  addAgentDialog.selectedAgentId = undefined;
  ElMessage.success("Agent 成员已添加到画布，保存后生效");
}


  if (!createTeamDialog.form.name) {
    ElMessage.warning("请输入 Team 名称");
    return;
  }
  // Task 6 中实现：加入 pendingChanges
  createTeamDialog.visible = false;
  ElMessage.success("已添加到画布（保存后生效）");
}

async function handleSave() {
  // Task 8 中实现
  ElMessage.info("保存功能待实现");
}

// 加载图数据（Task 5 中实现）
async function loadGraph(teamId: string) {
  // 占位
}

onMounted(() => {
  if (rootTeamId.value) {
    loadGraph(rootTeamId.value);
  }
});
</script>

<style lang="scss" scoped>
.team-builder {
  display: flex;
  flex-direction: column;
  height: calc(100vh - 84px);
  background: #fff;

  &__toolbar {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 8px 16px;
    border-bottom: 1px solid #e4e7ed;
    background: #fff;
    flex-shrink: 0;

    .toolbar-left {
      display: flex;
      align-items: center;
      gap: 12px;
    }
    .toolbar-title {
      font-size: 15px;
      font-weight: 600;
      color: #303133;
    }
    .toolbar-right {
      display: flex;
      gap: 8px;
    }
  }

  &__main {
    display: flex;
    flex: 1;
    overflow: hidden;
  }

  &__canvas {
    flex: 1;
    position: relative;
    transition: width 0.2s;
    overflow: hidden;

    .canvas-empty {
      display: flex;
      align-items: center;
      justify-content: center;
      height: 100%;
    }
  }

  &__panel {
    width: 400px;
    flex-shrink: 0;
    border-left: 1px solid #e4e7ed;
    display: flex;
    flex-direction: column;
    overflow: hidden;

    .panel-header {
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 12px 16px;
      border-bottom: 1px solid #e4e7ed;
      font-weight: 600;
    }

    .panel-body {
      flex: 1;
      overflow-y: auto;
      padding: 16px;
    }
  }
}
</style>
```

- [ ] **Step 2: 类型检查**

```bash
pnpm ts:check
```
期望：无错误

- [ ] **Step 3: 提交**

```bash
git add src/views/module_agno_manage/team_builder/index.vue
git commit -m "feat(team-builder): 创建可视化构建器骨架页面"
```

---

### Task 5: 集成 Vue Flow + 数据加载 + buildGraph

**Files:**
- 修改: `src/views/module_agno_manage/team_builder/index.vue`

- [ ] **Step 1: 引入 Vue Flow 和样式**

在 `<script setup>` 中添加 Vue Flow 相关引入：

```typescript
import { VueFlow, useVueFlow, type Node, type Edge } from "@vue-flow/core";
import { Background } from "@vue-flow/background";
import { Controls } from "@vue-flow/controls";
import { MiniMap } from "@vue-flow/minimap";
import "@vue-flow/core/dist/style.css";
import "@vue-flow/core/dist/theme-default.css";
import "@vue-flow/controls/dist/style.css";
import "@vue-flow/minimap/dist/style.css";
```

在 `<script setup>` 中初始化 Vue Flow：

```typescript
const { fitView, addNodes, addEdges, removeNodes, removeEdges, getNodes, getEdges } = useVueFlow();

const nodes = ref<Node[]>([]);
const edges = ref<Edge[]>([]);
```

- [ ] **Step 2: 实现 buildGraph 数据加载函数**

替换 `loadGraph` 占位实现：

```typescript
// 递归加载所有 team_members（BFS，防止无限递归）
// 同时收集所有子 Team 的完整 AgTeamTable 数据（teamDataMap）
async function fetchAllMembers(
  teamIds: string[],
  visited: Set<string>,
  rootTeam: AgTeamTable
): Promise<{ membersMap: Map<string, AgTeamMemberTable[]>; teamDataMap: Map<string, AgTeamTable> }> {
  const membersMap = new Map<string, AgTeamMemberTable[]>();
  const teamDataMap = new Map<string, AgTeamTable>();
  // 根 Team 自身已有完整数据，先存入
  teamDataMap.set(String(rootTeam.id), rootTeam);

  const queue = [...teamIds];

  while (queue.length > 0) {
    const id = queue.shift()!;
    if (visited.has(id)) continue;
    visited.add(id);

    try {
      const res = await AgTeamMemberAPI.listAgTeamMember({
        team_id: id,
        page_no: 1,
        page_size: 200,
      });
      const members = res.data?.data?.items || [];
      membersMap.set(id, members);

      // 将子 Team ID 加入队列，并异步加载子 Team 完整数据
      for (const m of members) {
        if (m.member_type === "team" && m.member_id) {
          const childId = String(m.member_id);
          if (!visited.has(childId)) {
            queue.push(childId);
            // 并发加载子 Team 完整详情（非阻塞，结果会在该轮循环后可用）
            AgTeamAPI.detailAgTeam(Number(childId))
              .then((r) => { if (r.data?.data) teamDataMap.set(childId, r.data.data); })
              .catch(() => {});
          }
        }
      }
    } catch (e) {
      membersMap.set(id, []);
    }
  }
  return { membersMap, teamDataMap };
}

// 根据 teams + members 构建 nodes + edges
function buildGraph(
  rootTeam: AgTeamTable,
  membersMap: Map<string, AgTeamMemberTable[]>,
  teamDataMap: Map<string, AgTeamTable>
): { nodes: Node[]; edges: Edge[] } {
  const resultNodes: Node[] = [];
  const resultEdges: Edge[] = [];

  // 用于记录已创建的节点，防止重复
  const createdNodeIds = new Set<string>();

  // 布局：简单瀑布式自动布局（x从左，y按层递增）
  // 注意：此为初始自动布局，用户可在画布中自由拖拽节点调整位置。
  // 复杂嵌套场景（多个平级子 Team）下 x 轴可能出现重叠，拖拽后位置不保存，刷新页面恢复。
  const X_GAP = 280;
  const Y_GAP = 160;
  let colCounter = 0;

  function addTeamNode(team: AgTeamTable, depth: number, col: number) {
    const nodeId = `team-${team.id}`;
    if (createdNodeIds.has(nodeId)) return;
    createdNodeIds.add(nodeId);

    resultNodes.push({
      id: nodeId,
      type: "teamNode",
      position: { x: col * X_GAP, y: depth * Y_GAP },
      data: { team, members: membersMap.get(String(team.id)) || [] },
    });

    const members = membersMap.get(String(team.id)) || [];
    let childCol = col;

    for (const member of members) {
      const memberId = String(member.member_id);

      if (member.member_type === "agent") {
        const agentNodeId = `agent-${memberId}-in-${team.id}`;
        if (!createdNodeIds.has(agentNodeId)) {
          createdNodeIds.add(agentNodeId);
          resultNodes.push({
            id: agentNodeId,
            type: "agentNode",
            position: { x: childCol * X_GAP, y: (depth + 1) * Y_GAP },
            data: { member, agentId: memberId },
          });
          childCol++;
        }
        resultEdges.push({
          id: `e-${nodeId}-${agentNodeId}`,
          source: nodeId,
          target: agentNodeId,
          animated: false,
        });
      } else if (member.member_type === "team") {
        // 子 Team 从 teamDataMap 中取完整数据（fetchAllMembers 阶段已收集）
        const subTeamNodeId = `team-${memberId}`;
        const subTeamData = teamDataMap.get(memberId) || { id: Number(memberId), name: `Team#${memberId}` } as AgTeamTable;

        addTeamNode(subTeamData, depth + 1, childCol);
        childCol++;

        resultEdges.push({
          id: `e-${nodeId}-${subTeamNodeId}`,
          source: nodeId,
          target: subTeamNodeId,
          animated: false,
          style: { stroke: "#409eff" },
        });
      }
    }
  }

  addTeamNode(rootTeam, 0, 0);
  return { nodes: resultNodes, edges: resultEdges };
}

async function loadGraph(teamId: string) {
  const res = await AgTeamAPI.detailAgTeam(Number(teamId));
  const rootTeam = res.data?.data;
  if (!rootTeam) {
    ElMessage.error("Team 不存在");
    return;
  }

  const visited = new Set<string>();
  // fetchAllMembers 同时返回 teamDataMap（子 Team 完整数据）
  const { membersMap, teamDataMap } = await fetchAllMembers([teamId], visited, rootTeam);

  const { nodes: newNodes, edges: newEdges } = buildGraph(rootTeam, membersMap, teamDataMap);
  nodes.value = newNodes;
  edges.value = newEdges;

  // 等待下一帧再居中
  setTimeout(() => fitView({ padding: 0.2 }), 100);
}
```

- [ ] **Step 3: 替换画布区域模板（使用真实 VueFlow）**

将模板中的画布占位 div 替换为：

```vue
<VueFlow
  v-else
  v-model:nodes="nodes"
  v-model:edges="edges"
  :node-types="nodeTypes"
  fit-view-on-init
  @node-click="handleNodeClick"
  @connect="handleConnect"
  @edge-remove="handleEdgeRemove"
>
  <Background />
  <Controls />
  <MiniMap />
</VueFlow>
```

在 script 中声明 nodeTypes（先用默认节点，Task 6 再换自定义）：

```typescript
const nodeTypes = {};  // Task 6 中填入自定义节点类型

function handleNodeClick(_: MouseEvent, node: Node) {
  selectedNode.value = { id: node.id, type: node.type!, data: node.data };
  panelVisible.value = true;
}

function handleConnect(params: any) {
  // Task 6 中实现连线逻辑
}

function handleEdgeRemove(removedEdges: Edge[]) {
  // Task 8 中实现断线逻辑（参数命名为 removedEdges，避免遮蔽外层 edges ref）
}
```

- [ ] **Step 4: 类型检查**

```bash
pnpm ts:check
```
期望：无错误

- [ ] **Step 5: 提交**

```bash
git add src/views/module_agno_manage/team_builder/index.vue
git commit -m "feat(team-builder): 集成 Vue Flow，实现数据加载和 buildGraph"
```

---

### Task 6: 创建自定义节点组件

**Files:**
- 创建: `src/views/module_agno_manage/team_builder/nodes/TeamNode.vue`
- 创建: `src/views/module_agno_manage/team_builder/nodes/AgentNode.vue`

- [ ] **Step 1: 创建 TeamNode.vue**

```vue
<template>
  <div class="team-node" :class="`mode-${data.team?.mode || 'default'}`">
    <Handle type="target" :position="Position.Left" />
    <div class="team-node__header">
      <span class="team-node__icon">🏢</span>
      <span class="team-node__name">{{ data.team?.name || 'Team' }}</span>
      <el-tag size="small" :type="modeTagType" class="team-node__mode">
        {{ data.team?.mode || '-' }}
      </el-tag>
    </div>
    <div class="team-node__body">
      <div class="team-node__meta">成员: {{ data.members?.length || 0 }} 个</div>
    </div>
    <Handle type="source" :position="Position.Bottom" />
  </div>
</template>

<script setup lang="ts">
import { computed } from "vue";
import { Handle, Position } from "@vue-flow/core";

const props = defineProps<{
  data: {
    team: any;
    members: any[];
  };
}>();

const modeTagType = computed(() => {
  const map: Record<string, string> = {
    route: "",
    coordinate: "warning",
    collaborate: "success",
    tasks: "info",
  };
  return (map[props.data.team?.mode] ?? "") as any;
});
</script>

<style lang="scss" scoped>
.team-node {
  background: #fff;
  border: 2px solid #409eff;
  border-radius: 8px;
  min-width: 200px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  cursor: pointer;

  &__header {
    display: flex;
    align-items: center;
    gap: 6px;
    padding: 8px 12px;
    background: #ecf5ff;
    border-radius: 6px 6px 0 0;
  }

  &__name {
    font-weight: 600;
    font-size: 13px;
    flex: 1;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }

  &__body {
    padding: 8px 12px;
  }

  &__meta {
    font-size: 12px;
    color: #909399;
  }

  &.mode-coordinate {
    border-color: #e6a23c;
    .team-node__header { background: #fdf6ec; }
  }

  &.mode-collaborate {
    border-color: #67c23a;
    .team-node__header { background: #f0f9eb; }
  }

  &.mode-tasks {
    border-color: #909399;
    .team-node__header { background: #f4f4f5; }
  }
}
</style>
```

- [ ] **Step 2: 创建 AgentNode.vue**

AgentNode 在 `onMounted` 中自行异步加载 Agent 名称，不依赖父组件传入，组件自治。

```vue
<template>
  <div class="agent-node">
    <Handle type="target" :position="Position.Left" />
    <div class="agent-node__header">
      <span class="agent-node__icon">🤖</span>
      <span class="agent-node__name">{{ displayName }}</span>
    </div>
    <div v-if="data.member?.role" class="agent-node__body">
      <span class="agent-node__role">{{ data.member.role }}</span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from "vue";
import { Handle, Position } from "@vue-flow/core";
import AgAgentAPI from "@/api/module_agno_manage/agents";

const props = defineProps<{
  data: {
    agentId: string;
    agentName?: string;
    member: any;
  };
}>();

// 初始显示父组件传入的 agentName（可能是 ID 占位），异步加载后更新
const displayName = ref(props.data.agentName || props.data.agentId);

onMounted(async () => {
  if (props.data.agentName && !props.data.agentName.startsWith("Agent#")) return; // 已有真实名称
  try {
    const res = await AgAgentAPI.detailAgAgent(Number(props.data.agentId));
    const name = res.data?.data?.name;
    if (name) displayName.value = name;
  } catch {
    // 保持 ID 占位
  }
});
</script>

<style lang="scss" scoped>
.agent-node {
  background: #fff;
  border: 2px solid #67c23a;
  border-radius: 8px;
  min-width: 160px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  cursor: pointer;

  &__header {
    display: flex;
    align-items: center;
    gap: 6px;
    padding: 8px 12px;
    background: #f0f9eb;
    border-radius: 6px 6px 0 0;
  }

  &__name {
    font-size: 13px;
    font-weight: 500;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }

  &__body {
    padding: 6px 12px;
  }

  &__role {
    font-size: 11px;
    color: #909399;
  }
}
</style>
```

- [ ] **Step 3: 在 team_builder/index.vue 中注册自定义节点**

在 `<script setup>` 中引入并注册：

```typescript
import TeamNode from "./nodes/TeamNode.vue";
import AgentNode from "./nodes/AgentNode.vue";

// 替换之前的空对象
const nodeTypes = {
  teamNode: markRaw(TeamNode),
  agentNode: markRaw(AgentNode),
};
```

同时在顶部引入 `markRaw`：
```typescript
import { ref, reactive, onMounted, markRaw } from "vue";
```

**agentName 使用异步按需加载 + cache 模式（参考 CLAUDE.md `getModelName` 规范）**，不阻塞画布渲染：

```typescript
// Agent 名称缓存（id → name），响应式，变化后自动触发节点重渲染
const agentNameCache = ref<Record<string, string>>({});

// 同步函数：首次调用时异步填充 cache，返回当前已知的名称（或 ID 占位）
function getAgentName(agentId: string): string {
  const key = agentId;
  if (agentNameCache.value[key]) return agentNameCache.value[key];
  // 触发异步填充，不阻塞当前渲染
  AgAgentAPI.detailAgAgent(Number(agentId))
    .then((res) => {
      agentNameCache.value[key] = res.data?.data?.name || key;
    })
    .catch(() => {
      agentNameCache.value[key] = key;
    });
  return key; // 首次返回 ID 占位，异步回来后触发响应式更新
}
```

在 `buildGraph` 中，AgentNode 的 data 使用 `getAgentName`（同步调用），初始渲染显示 ID，名称加载后自动刷新：

```typescript
// AgentNode data 中传入 getAgentName 函数引用（通过 provide/inject 或直接在 index.vue script 中调用）
// 由于 buildGraph 在 index.vue 内定义，可以直接引用 getAgentName
data: { member, agentId: memberId, agentName: getAgentName(memberId) },
```

> **注意**：`agentNameCache` 是响应式的，但 Vue Flow 的节点 data 变化不会自动触发节点重渲染。若需要显示最新名称，在 AgentNode.vue 中通过 `inject` 接收 `agentNameCache`，或直接在 AgentNode.vue 中自行发起 detailAgAgent 请求（推荐后者，组件自治）。AgentNode.vue 可以在 `onMounted` 时根据 `props.data.agentId` 异步填充 `agentName`，并用本地 ref 存储，避免与父组件耦合。

- [ ] **Step 4: 类型检查**

```bash
pnpm ts:check
```
期望：无错误

- [ ] **Step 5: 提交**

```bash
git add src/views/module_agno_manage/team_builder/nodes/
git add src/views/module_agno_manage/team_builder/index.vue
git commit -m "feat(team-builder): 添加自定义 TeamNode 和 AgentNode 组件"
```

---

## Chunk 3: 右侧面板 + 交互逻辑 + 保存流程

### Task 7: 实现右侧配置面板

**Files:**
- 修改: `src/views/module_agno_manage/team_builder/index.vue`

- [ ] **Step 1: 完善右侧 TeamNode 面板**

将 `panel-body` 中的占位内容替换为真实面板。点击 TeamNode 时展示两个 Tab：

```vue
<!-- 右侧配置面板 -->
<div v-if="panelVisible" class="team-builder__panel">
  <div class="panel-header">
    <span>{{ selectedNode?.type === 'teamNode' ? '📋 Team 配置' : '🤖 Agent 成员' }}</span>
    <el-button icon="Close" circle size="small" @click="panelVisible = false" />
  </div>
  <div class="panel-body">
    <!-- TeamNode 面板 -->
    <template v-if="selectedNode?.type === 'teamNode'">
      <el-tabs v-model="panelActiveTab">
        <el-tab-pane label="Team 配置" name="config">
          <TeamFormFields
            v-if="selectedTeamForm"
            ref="panelFormRef"
            :form-data="selectedTeamForm"
          />
        </el-tab-pane>
        <el-tab-pane label="成员列表" name="members">
          <div v-for="m in selectedNodeMembers" :key="m.id" class="member-item">
            <span class="member-icon">{{ m.member_type === 'agent' ? '🤖' : '🏢' }}</span>
            <span class="member-name">{{ getMemberDisplayName(m) }}</span>
            <div class="member-actions">
              <el-input-number
                v-model="m.member_order"
                :min="1"
                :precision="0"
                size="small"
                style="width: 80px"
                @change="markMemberChanged(m)"
              />
              <el-button
                type="danger"
                size="small"
                icon="Delete"
                circle
                @click="handleRemoveMember(m)"
              />
            </div>
          </div>
          <div style="margin-top: 12px;">
            <el-button icon="Plus" @click="handleAddMember">添加成员</el-button>
          </div>
        </el-tab-pane>
      </el-tabs>
      <div style="margin-top: 12px; text-align: right;">
        <el-button type="primary" size="small" @click="handlePanelSaveTeamConfig">应用配置</el-button>
      </div>
    </template>

    <!-- AgentNode 面板 -->
    <template v-else-if="selectedNode?.type === 'agentNode'">
      <el-form label-width="90px" label-suffix=":">
        <el-form-item label="角色描述">
          <el-input v-model="selectedNode.data.member.role" type="textarea" :rows="2" />
        </el-form-item>
        <el-form-item label="排序">
          <el-input-number v-model="selectedNode.data.member.member_order" :min="1" :precision="0" style="width:100%" />
        </el-form-item>
        <el-form-item label="状态">
          <el-radio-group v-model="selectedNode.data.member.status">
            <el-radio value="0">启用</el-radio>
            <el-radio value="1">停用</el-radio>
          </el-radio-group>
        </el-form-item>
      </el-form>
      <div style="margin-top: 12px; text-align: right;">
        <el-button type="primary" size="small" @click="handlePanelSaveMemberConfig">应用配置</el-button>
      </div>
    </template>
  </div>
</div>
```

在 script 中添加面板相关状态和函数：

```typescript
import TeamFormFields from "../teams/components/TeamFormFields.vue";
import type { AgTeamForm } from "@/api/module_agno_manage/teams";

const panelActiveTab = ref("config");
const panelFormRef = ref();
const selectedTeamForm = ref<AgTeamForm | null>(null);
const selectedNodeMembers = ref<AgTeamMemberTable[]>([]);

// 点击节点时填充面板数据
function handleNodeClick(_: MouseEvent, node: Node) {
  selectedNode.value = { id: node.id, type: node.type!, data: node.data };
  panelVisible.value = true;
  panelActiveTab.value = "config";

  if (node.type === "teamNode") {
    // 复制 team 数据到表单
    selectedTeamForm.value = { ...node.data.team } as AgTeamForm;
    selectedNodeMembers.value = [...(node.data.members || [])];
  }
}

// 获取成员显示名称（从节点数据中查）
function getMemberDisplayName(member: AgTeamMemberTable): string {
  const id = String(member.member_id);
  if (member.member_type === "agent") {
    // 从 nodes 中查找对应 agentNode 的 agentName
    const agentNode = nodes.value.find(
      (n) => n.type === "agentNode" && n.data.agentId === id && n.id.includes(`in-${selectedNode.value?.data.team?.id}`)
    );
    return agentNode?.data.agentName || `Agent#${id}`;
  }
  // 子 Team：从 nodes 中找 teamNode
  const teamNode = nodes.value.find((n) => n.id === `team-${id}`);
  return teamNode?.data.team?.name || `Team#${id}`;
}

function markMemberChanged(member: AgTeamMemberTable) {
  // 加入 pendingChanges（Task 8 实现）
}

function handleRemoveMember(member: AgTeamMemberTable) {
  // 从画布和 pendingChanges 移除（Task 8 实现）
  ElMessage.info("移除操作将在保存时生效");
}

function handleAddMember() {
  // 打开选择器（简化版：弹出对话框选 Agent 或 Team）
  ElMessage.info("请在画布中拖拽连线以添加成员");
}

function handlePanelSaveTeamConfig() {
  // 将 selectedTeamForm 的变更写入 pendingChanges（Task 8 实现）
  ElMessage.success("配置已暂存，点击工具栏「保存」提交");
}

function handlePanelSaveMemberConfig() {
  ElMessage.success("成员配置已暂存，点击工具栏「保存」提交");
}
```

- [ ] **Step 2: 类型检查**

```bash
pnpm ts:check
```
期望：无错误

- [ ] **Step 3: 提交**

```bash
git add src/views/module_agno_manage/team_builder/index.vue
git commit -m "feat(team-builder): 实现右侧配置面板（Team配置 + 成员列表）"
```

---

### Task 8: 实现连线、循环引用检测、新建 Team 节点和保存流程

**Files:**
- 修改: `src/views/module_agno_manage/team_builder/index.vue`

- [ ] **Step 1: 实现 pendingChanges 数据结构**

在 script 中添加：

```typescript
// 变更队列
interface PendingChange {
  type:
    | "createTeam"    // 新建 Team（临时 id → 真实 id）
    | "updateTeam"    // 更新 Team 配置
    | "addMember"     // 新建 team_member
    | "removeMember"; // 删除 team_member
  payload: any;
  // 临时 id（仅 createTeam 使用）
  tmpId?: string;
}

const pendingChanges = ref<PendingChange[]>([]);

// 临时 ID 计数
let tmpCounter = 0;
function genTmpId(): string {
  return `tmp_${Date.now()}_${tmpCounter++}`;
}
```

- [ ] **Step 2: 实现循环引用检测**

```typescript
function wouldCreateCycle(sourceId: string, targetId: string): boolean {
  // BFS 可达性检测：从 targetId 出发，若能到达 sourceId，则判定为循环
  // （spec 描述为 DFS，BFS 与 DFS 在可达性检测上语义等价，此处选用 BFS 实现）
  const visited = new Set<string>();
  const queue = [targetId];
  while (queue.length > 0) {
    const curr = queue.shift()!;
    if (curr === sourceId) return true;
    if (visited.has(curr)) continue;
    visited.add(curr);
    // 找出所有以 curr 为 source 的 edge 的 target
    const children = edges.value
      .filter((e) => e.source === curr)
      .map((e) => e.target);
    queue.push(...children);
  }
  return false;
}
```

- [ ] **Step 3: 实现连线和断线处理**

```typescript
function handleConnect(params: { source: string; target: string }) {
  const { source, target } = params;

  // 只允许 teamNode → agentNode 或 teamNode → teamNode
  const sourceNode = nodes.value.find((n) => n.id === source);
  const targetNode = nodes.value.find((n) => n.id === target);
  if (!sourceNode || sourceNode.type !== "teamNode") {
    ElMessage.warning("只能从 Team 节点连出");
    return;
  }

  // 循环引用检测
  if (targetNode?.type === "teamNode" && wouldCreateCycle(source, target)) {
    ElMessage.error("不能创建循环引用：该连线会形成嵌套环");
    return;
  }

  // 创建边
  const edgeId = `e-${source}-${target}-${Date.now()}`;
  addEdges([{ id: edgeId, source, target }]);

  // 加入 pendingChanges
  const teamId = source.replace("team-", "");
  const memberId = target.replace("team-", "").replace("agent-", "").split("-in-")[0];
  const memberType = targetNode?.type === "teamNode" ? "team" : "agent";

  pendingChanges.value.push({
    type: "addMember",
    payload: {
      team_id: teamId,
      member_type: memberType,
      member_id: memberId,
      member_order: 99,
      status: "0",
    },
  });
}

function handleEdgeRemove(removedEdges: Edge[]) {
  for (const edge of removedEdges) {
    const teamId = edge.source.replace("team-", "");
    const target = edge.target;
    const memberId = target.replace("team-", "").replace("agent-", "").split("-in-")[0];
    const memberType = target.startsWith("team-") ? "team" : "agent";

    pendingChanges.value.push({
      type: "removeMember",
      payload: { team_id: teamId, member_id: memberId, member_type: memberType },
    });
  }
}

// 右侧面板「删除成员」按钮：从成员列表和 pendingChanges 中记录删除操作
function handleRemoveMember(member: AgTeamMemberTable) {
  // 从面板成员列表中移除（即时 UI 反馈）
  selectedNodeMembers.value = selectedNodeMembers.value.filter((m) => m.id !== member.id);
  // 加入 pendingChanges，保存时执行实际删除
  pendingChanges.value.push({
    type: "removeMember",
    payload: {
      team_id: String(selectedNode.value?.data.team?.id),
      member_id: String(member.member_id),
      member_type: member.member_type,
    },
  });
  ElMessage.success("已标记删除，保存后生效");
}
```

- [ ] **Step 4: 实现新建 Team 节点**

```typescript
async function handleConfirmCreateTeam() {
  if (!createTeamDialog.form.name) {
    ElMessage.warning("请输入 Team 名称");
    return;
  }

  const tmpId = genTmpId();
  const newNode: Node = {
    id: tmpId,
    type: "teamNode",
    position: { x: 300, y: 300 },
    data: {
      team: { id: null, name: createTeamDialog.form.name, mode: createTeamDialog.form.mode },
      members: [],
      tmpId, // 标记为临时节点
    },
  };

  addNodes([newNode]);

  pendingChanges.value.push({
    type: "createTeam",
    tmpId,
    payload: {
      name: createTeamDialog.form.name,
      mode: createTeamDialog.form.mode,
      status: "0",
    },
  });

  createTeamDialog.visible = false;
  ElMessage.success("Team 节点已添加到画布，保存后生效");
}
```

- [ ] **Step 5: 实现保存流程**

```typescript
async function handleSave() {
  if (pendingChanges.value.length === 0) {
    ElMessage.info("没有待保存的变更");
    return;
  }

  saving.value = true;
  try {
    // 临时 id → 真实 id 映射（用于后续 addMember）
    const tmpToRealId = new Map<string, string>();

    // Step 1: 创建新 Team（串行，保证 ID 可用）
    const createChanges = pendingChanges.value.filter((c) => c.type === "createTeam");
    for (const change of createChanges) {
      const res = await AgTeamAPI.createAgTeam(change.payload);
      const realId = String(res.data?.data?.id || res.data?.data);
      if (change.tmpId) tmpToRealId.set(change.tmpId, realId);
    }

    // Step 2: 更新 Team 配置
    const updateChanges = pendingChanges.value.filter((c) => c.type === "updateTeam");
    await Promise.all(
      updateChanges.map((c) => AgTeamAPI.updateAgTeam(Number(c.payload.id), c.payload))
    );

    // Step 3: 删除成员关系（需要先查到 member record id）
    // 前提：AgTeamMemberAPI.listAgTeamMember 支持按 team_id + member_id + member_type 过滤
    // （对照 src/api/module_agno_manage/team_members.ts 中 AgTeamMemberPageQuery 确认字段存在）
    const removeChanges = pendingChanges.value.filter((c) => c.type === "removeMember");
    for (const change of removeChanges) {
      const res = await AgTeamMemberAPI.listAgTeamMember({
        team_id: change.payload.team_id,
        member_id: change.payload.member_id,
        member_type: change.payload.member_type,
        page_no: 1,
        page_size: 10,
      });
      const records = res.data?.data?.items || [];
      if (records.length > 0) {
        await AgTeamMemberAPI.deleteAgTeamMember(records.map((r: any) => r.id));
      }
    }

    // Step 4: 新建成员关系（替换 tmpId 为真实 id）
    const addChanges = pendingChanges.value.filter((c) => c.type === "addMember");
    for (const change of addChanges) {
      const payload = { ...change.payload };
      // 替换 team_id 中的 tmpId
      if (tmpToRealId.has(payload.team_id)) payload.team_id = tmpToRealId.get(payload.team_id)!;
      // 替换 member_id 中的 tmpId
      if (tmpToRealId.has(payload.member_id)) payload.member_id = tmpToRealId.get(payload.member_id)!;
      await AgTeamMemberAPI.createAgTeamMember(payload);
    }

    pendingChanges.value = [];
    ElMessage.success("保存成功");

    // 刷新画布
    if (rootTeamId.value) await loadGraph(rootTeamId.value);
  } catch (e: any) {
    ElMessage.error(`保存失败: ${e?.message || "未知错误"}`);
  } finally {
    saving.value = false;
  }
}
```

- [ ] **Step 6: 类型检查**

```bash
pnpm ts:check
```
期望：无错误

- [ ] **Step 7: 提交**

```bash
git add src/views/module_agno_manage/team_builder/index.vue
git commit -m "feat(team-builder): 实现连线、循环检测、新建节点和批量保存流程"
```

---

### Task 9: 注册路由（后端菜单）+ 手动验收

**Files:**
- 无需修改前端路由文件（动态路由由后端菜单控制）

- [ ] **Step 1: 在后端管理系统中添加菜单**

登录后台 → 系统管理 → 菜单管理 → 新增：

| 字段 | 值 |
|---|---|
| 菜单类型 | 菜单 |
| 菜单名称 | Team 可视化 |
| 路由路径 | `agno/team-builder` |
| 组件路径 | `module_agno_manage/team_builder/index` |
| 上级菜单 | （选择 Agno 管理菜单组） |
| 是否隐藏 | 否 |

- [ ] **Step 2: 启动开发服务器验证**

```bash
pnpm dev
```

手动验收清单：
- [ ] teams/index.vue 操作列出现「可视化」按钮
- [ ] 点击「可视化」跳转到 `/agno/team-builder?root_id=xxx`
- [ ] 画布中正确渲染 TeamNode 和 AgentNode，Agent 节点名称异步加载后正确显示
- [ ] 点击节点后右侧面板展开，显示 Team 配置 Tab 和成员列表 Tab
- [ ] 工具栏「新建 Team」弹窗可用，确认后节点出现在画布
- [ ] 工具栏「添加 Agent 成员」弹窗可用，选择后 AgentNode 出现在当前选中 Team 下方
- [ ] 画布连线触发循环引用检测（自连/环路被拒绝并弹出 error 提示）
- [ ] 断开画布连线后 pendingChanges 中有 removeMember 条目
- [ ] 右侧面板「删除成员」按钮点击后成员从面板列表消失，pendingChanges 中有 removeMember 条目
- [ ] 点击「保存」串行提交变更，成功后刷新画布

- [ ] **Step 3: 最终提交**

```bash
git add .
git commit -m "feat(team-builder): Team 可视化构建器完成"
```
