<!-- 资源绑定关系 -->
<template>
  <div class="app-container">
    <!-- 内容区域 -->
    <el-card class="data-table">
      <template #header>
        <div class="card-header">
          <span>
            资源绑定关系列表
            <el-tooltip content="资源绑定关系列表">
              <QuestionFilled class="w-4 h-4 mx-1" />
            </el-tooltip>
          </span>
        </div>

        <!-- 搜索区域 -->
        <div v-show="visible" class="search-container">
          <el-form
            ref="queryFormRef"
            :model="queryFormData"
            label-suffix=":"
            :inline="true"
            @submit.prevent="handleQuery"
          >
            <el-form-item label="拥有者类型" prop="owner_type">
              <el-select v-model="queryFormData.owner_type" placeholder="请选择拥有者类型" clearable style="width: 170px">
                <el-option
                  v-for="opt in ownerTypeOptions"
                  :key="opt.value"
                  :value="opt.value"
                  :label="opt.label"
                />
              </el-select>
            </el-form-item>
            <el-form-item label="拥有者ID" prop="owner_id">
              <el-input-number v-model="queryFormData.owner_id" placeholder="请输入拥有者ID" clearable :controls="false" style="width: 170px" />
            </el-form-item>
            <el-form-item label="资源类型" prop="resource_type">
              <el-select v-model="queryFormData.resource_type" placeholder="请选择资源类型" clearable style="width: 170px">
                <el-option
                  v-for="opt in allResourceTypeOptions"
                  :key="opt.value"
                  :value="opt.value"
                  :label="opt.label"
                />
              </el-select>
            </el-form-item>
            <el-form-item label="资源ID" prop="resource_id">
              <el-input-number v-model="queryFormData.resource_id" placeholder="请输入资源ID" clearable :controls="false" style="width: 170px" />
            </el-form-item>
            <el-form-item label="优先级" prop="priority">
              <el-input-number v-model="queryFormData.priority" placeholder="请输入优先级" clearable :controls="false" style="width: 170px" />
            </el-form-item>
            <el-form-item prop="status" label="状态">
              <el-select
                v-model="queryFormData.status"
                placeholder="请选择状态"
                style="width: 170px"
                clearable
              >
                <el-option value="0" label="启用" />
                <el-option value="1" label="停用" />
              </el-select>
            </el-form-item>
            <el-form-item v-if="isExpand" prop="created_time" label="创建时间">
              <DatePicker
                v-model="createdDateRange"
                @update:model-value="handleCreatedDateRangeChange"
              />
            </el-form-item>
            <el-form-item v-if="isExpand" prop="updated_time" label="更新时间">
              <DatePicker
                v-model="updatedDateRange"
                @update:model-value="handleUpdatedDateRangeChange"
              />
            </el-form-item>
            <el-form-item v-if="isExpand" prop="created_id" label="创建人">
              <UserTableSelect
                v-model="queryFormData.created_id"
                @confirm-click="handleConfirm"
                @clear-click="handleQuery"
              />
            </el-form-item>
            <el-form-item v-if="isExpand" prop="updated_id" label="更新人">
              <UserTableSelect
                v-model="queryFormData.updated_id"
                @confirm-click="handleConfirm"
                @clear-click="handleQuery"
              />
            </el-form-item>
            <!-- 查询、重置、展开/收起按钮 -->
            <el-form-item>
              <el-button
                v-hasPerm="['module_agno_manage:bindings:query']"
                type="primary"
                icon="search"
                @click="handleQuery"
              >
                查询
              </el-button>
              <el-button
                v-hasPerm="['module_agno_manage:bindings:query']"
                icon="refresh"
                @click="handleResetQuery"
              >
                重置
              </el-button>
              <!-- 展开/收起 -->
              <template v-if="isExpandable">
                <el-link 
                  class="ml-3"
                  type="primary"
                  underline="never"
                  @click="isExpand = !isExpand"
                >
                  {{ isExpand ? "收起" : "展开" }}
                  <el-icon>
                    <template v-if="isExpand">
                      <ArrowUp />
                    </template>
                    <template v-else>
                      <ArrowDown />
                    </template>
                  </el-icon>
                </el-link>
              </template>
            </el-form-item>
          </el-form>
        </div>
      </template>

      <!-- 功能区域 -->
      <div class="data-table__toolbar">
        <div class="data-table__toolbar--left">
          <el-row :gutter="10">
            <el-col :span="1.5">
              <el-button
                v-hasPerm="['module_agno_manage:bindings:create']"
                type="success"
                icon="plus"
                @click="handleOpenDialog('create')"
              >
                新增
              </el-button>
            </el-col>
            <el-col :span="1.5">
              <el-button
                v-hasPerm="['module_agno_manage:bindings:delete']"
                type="danger"
                icon="delete"
                :disabled="selectIds.length === 0"
                @click="handleDelete(selectIds)"
              >
                批量删除
              </el-button>
            </el-col>
            <el-col :span="1.5">
              <el-dropdown v-hasPerm="['module_agno_manage:bindings:batch']" trigger="click">
                <el-button type="default" :disabled="selectIds.length === 0" icon="ArrowDown">
                  更多
                </el-button>
                <template #dropdown>
                  <el-dropdown-menu>
                    <el-dropdown-item :icon="Check" @click="handleMoreClick('0')">
                      批量启用
                    </el-dropdown-item>
                    <el-dropdown-item :icon="CircleClose" @click="handleMoreClick('1')">
                      批量停用
                    </el-dropdown-item>
                  </el-dropdown-menu>
                </template>
              </el-dropdown>
            </el-col>
          </el-row>
        </div>
        <div class="data-table__toolbar--right">
          <el-row :gutter="10">
            <el-col :span="1.5">
              <el-tooltip content="导入">
                <el-button
                  v-hasPerm="['module_agno_manage:bindings:import']"
                  type="success"
                  icon="upload"
                  circle
                  @click="handleOpenImportDialog"
                />
              </el-tooltip>
            </el-col>
            <el-col :span="1.5">
              <el-tooltip content="导出">
                <el-button
                  v-hasPerm="['module_agno_manage:bindings:export']"
                  type="warning"
                  icon="download"
                  circle
                  @click="handleOpenExportsModal"
                />
              </el-tooltip>
            </el-col>
            <el-col :span="1.5">
              <el-tooltip content="搜索显示/隐藏">
                <el-button
                  v-hasPerm="['*:*:*']"
                  type="info"
                  icon="search"
                  circle
                  @click="visible = !visible"
                />
              </el-tooltip>
            </el-col>
            <el-col :span="1.5">
              <el-tooltip content="刷新">
                <el-button
                  v-hasPerm="['module_agno_manage:bindings:query']"
                  type="primary"
                  icon="refresh"
                  circle
                  @click="handleRefresh"
                />
              </el-tooltip>
            </el-col>
            <el-col :span="1.5">
              <el-popover placement="bottom" trigger="click">
                <template #reference>
                  <el-button type="danger" icon="operation" circle></el-button>
                </template>
                <el-scrollbar max-height="350px">
                  <template v-for="column in tableColumns" :key="column.prop">
                    <el-checkbox v-if="column.prop" v-model="column.show" :label="column.label" />
                  </template>
                </el-scrollbar>
              </el-popover>
            </el-col>
          </el-row>
        </div>
      </div>

      <!-- 表格区域：系统配置列表 -->
      <el-table
        ref="tableRef"
        v-loading="loading"
        :data="pageTableData"
        highlight-current-row
        class="data-table__content"
        border
        stripe
        @selection-change="handleSelectionChange"
      >
        <template #empty>
          <el-empty :image-size="80" description="暂无数据" />
        </template>
        <el-table-column
          v-if="tableColumns.find((col) => col.prop === 'selection')?.show"
          type="selection"
          min-width="55"
          align="center"
        />
        <el-table-column
          v-if="tableColumns.find((col) => col.prop === 'index')?.show"
          fixed
          label="序号"
          min-width="60"
        >
          <template #default="scope">
            {{ (queryFormData.page_no - 1) * queryFormData.page_size + scope.$index + 1 }}
          </template>
        </el-table-column>
        <el-table-column
          v-if="tableColumns.find((col) => col.prop === 'owner_type')?.show"
          label="拥有者类型"
          prop="owner_type"
          min-width="120"
          show-overflow-tooltip
        />
        <el-table-column
          v-if="tableColumns.find((col) => col.prop === 'owner_id')?.show"
          label="拥有者ID"
          prop="owner_id"
          min-width="100"
          show-overflow-tooltip
        />
        <el-table-column
          v-if="tableColumns.find((col) => col.prop === 'resource_type')?.show"
          label="资源类型"
          prop="resource_type"
          min-width="120"
          show-overflow-tooltip
        />
        <el-table-column
          v-if="tableColumns.find((col) => col.prop === 'resource_id')?.show"
          label="资源ID"
          prop="resource_id"
          min-width="100"
          show-overflow-tooltip
        />
        <el-table-column
          v-if="tableColumns.find((col) => col.prop === 'priority')?.show"
          label="优先级"
          prop="priority"
          min-width="100"
          show-overflow-tooltip
        />
        <el-table-column
          v-if="tableColumns.find((col) => col.prop === 'config_override')?.show"
          label="配置覆盖"
          prop="config_override"
          min-width="200"
          show-overflow-tooltip
        >
          <template #default="scope">
            <pre v-if="scope.row.config_override" style="margin: 0; font-size: 12px">{{ JSON.stringify(scope.row.config_override, null, 2) }}</pre>
            <span v-else>-</span>
          </template>
        </el-table-column>
        <el-table-column
          v-if="tableColumns.find((col) => col.prop === 'status')?.show"
          label="状态(原始值)"
          prop="status"
          min-width="100"
          show-overflow-tooltip
        />
        <el-table-column
          v-if="tableColumns.find((col) => col.prop === 'status')?.show"
          label="状态"
          prop="status"
          min-width="100"
          show-overflow-tooltip
        >
          <template #default="scope">
            <el-tag :type="scope.row.status == '0' ? 'success' : 'info'">
              {{ scope.row.status == "0" ? "启用" : "停用" }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column
          v-if="tableColumns.find((col) => col.prop === 'description')?.show"
          label="描述"
          prop="description"
          min-width="140"
          show-overflow-tooltip
        />
        <el-table-column
          v-if="tableColumns.find((col) => col.prop === 'created_time')?.show"
          label="创建时间"
          prop="created_time"
          min-width="160"
          show-overflow-tooltip
        />
        <el-table-column
          v-if="tableColumns.find((col) => col.prop === 'updated_time')?.show"
          label="更新时间"
          prop="updated_time"
          min-width="160"
          show-overflow-tooltip
        />
        <el-table-column
          v-if="tableColumns.find((col) => col.prop === 'created_id')?.show"
          label="创建人ID"
          prop="created_id"
          min-width="100"
          show-overflow-tooltip
        />
        <el-table-column
          v-if="tableColumns.find((col) => col.prop === 'created_id')?.show"
          label="创建人"
          prop="created_id"
          min-width="120"
          show-overflow-tooltip
        >
          <template #default="scope">
            <el-tag>{{ scope.row.created_by?.name }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column
          v-if="tableColumns.find((col) => col.prop === 'updated_id')?.show"
          label="更新人ID"
          prop="updated_id"
          min-width="100"
          show-overflow-tooltip
        />
        <el-table-column
          v-if="tableColumns.find((col) => col.prop === 'updated_id')?.show"
          label="更新人"
          prop="updated_id"
          min-width="120"
          show-overflow-tooltip
        >
          <template #default="scope">
            <el-tag>{{ scope.row.updated_by?.name }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column
          v-if="tableColumns.find((col) => col.prop === 'operation')?.show"
          fixed="right"
          label="操作"
          align="center"
          min-width="180"
        >
          <template #default="scope">
            <el-button
              v-hasPerm="['module_agno_manage:bindings:detail']"
              type="info"
              size="small"
              link
              icon="document"
              @click="handleOpenDialog('detail', scope.row.id)"
            >
              详情
            </el-button>
            <el-button
              v-hasPerm="['module_agno_manage:bindings:update']"
              type="primary"
              size="small"
              link
              icon="edit"
              @click="handleOpenDialog('update', scope.row.id)"
            >
              编辑
            </el-button>
            <el-button
              v-hasPerm="['module_agno_manage:bindings:delete']"
              type="danger"
              size="small"
              link
              icon="delete"
              @click="handleDelete([scope.row.id])"
            >
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页区域 -->
      <template #footer>
        <pagination
          v-model:total="total"
          v-model:page="queryFormData.page_no"
          v-model:limit="queryFormData.page_size"
          @pagination="loadingData"
        />
      </template>
    </el-card>

    <!-- 弹窗区域 -->
    <el-dialog
      v-model="dialogVisible.visible"
      :title="dialogVisible.title"
      @close="handleCloseDialog"
    >
      <!-- 详情 -->
      <template v-if="dialogVisible.type === 'detail'">
        <el-descriptions :column="4" border>
          <el-descriptions-item label="ID" :span="2">
            {{ detailFormData.id }}
          </el-descriptions-item>
          <el-descriptions-item label="UUID" :span="2">
            {{ detailFormData.uuid }}
          </el-descriptions-item>
          <el-descriptions-item label="拥有者类型" :span="2">
            {{ detailFormData.owner_type }}
          </el-descriptions-item>
          <el-descriptions-item label="拥有者ID" :span="2">
            {{ detailFormData.owner_id }}
          </el-descriptions-item>
          <el-descriptions-item label="资源类型" :span="2">
            {{ detailFormData.resource_type }}
          </el-descriptions-item>
          <el-descriptions-item label="资源ID" :span="2">
            {{ detailFormData.resource_id }}
          </el-descriptions-item>
          <el-descriptions-item label="优先级" :span="2">
            {{ detailFormData.priority }}
          </el-descriptions-item>
          <el-descriptions-item label="配置覆盖" :span="4">
            <pre v-if="detailFormData.config_override" style="margin: 0; white-space: pre-wrap; font-size: 12px">{{ JSON.stringify(detailFormData.config_override, null, 2) }}</pre>
            <span v-else>-</span>
          </el-descriptions-item>
          <el-descriptions-item label="状态" :span="2">
            <el-tag :type="detailFormData.status == '0' ? 'success' : 'danger'">
              {{ detailFormData.status == "0" ? "启用" : "停用" }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="描述" :span="2">
            {{ detailFormData.description }}
          </el-descriptions-item>
          <el-descriptions-item label="创建时间" :span="2">
            {{ detailFormData.created_time }}
          </el-descriptions-item>
          <el-descriptions-item label="更新时间" :span="2">
            {{ detailFormData.updated_time }}
          </el-descriptions-item>
          <el-descriptions-item label="创建人" :span="2">
            {{ detailFormData.created_by?.name }}
          </el-descriptions-item>
          <el-descriptions-item label="更新人" :span="2">
            {{ detailFormData.updated_by?.name }}
          </el-descriptions-item>
        </el-descriptions>
      </template>

      <!-- 新增、编辑表单 -->
      <template v-else>
        <el-form
          ref="dataFormRef"
          :model="formData"
          :rules="rules"
          label-suffix=":"
          label-width="auto"
          label-position="right"
        >
          <el-form-item label="拥有者类型" prop="owner_type" :required="false">
            <el-select v-model="formData.owner_type" placeholder="请选择拥有者类型" clearable style="width: 100%" @change="handleOwnerTypeChange">
              <el-option
                v-for="opt in ownerTypeOptions"
                :key="opt.value"
                :value="opt.value"
                :label="opt.label"
              />
            </el-select>
          </el-form-item>
          <el-form-item label="拥有者ID" prop="owner_id" :required="false">
            <LazySelect
              v-if="formData.owner_type"
              :key="`owner-${formData.owner_type}`"
              :model-value="formData.owner_id !== undefined ? String(formData.owner_id) : undefined"
              @update:model-value="(v) => (formData.owner_id = v ? Number(v) : undefined)"
              :fetcher="ownerFetcher"
              :preload="true"
              placeholder="请选择拥有者"
              style="width: 100%"
            />
            <el-text v-else size="small" type="info">请先选择拥有者类型</el-text>
          </el-form-item>
          <el-form-item label="资源类型" prop="resource_type" :required="false">
            <el-select v-model="formData.resource_type" placeholder="请选择资源类型" clearable style="width: 100%" @change="handleResourceTypeChange">
              <el-option
                v-for="opt in resourceTypeOptions"
                :key="opt.value"
                :value="opt.value"
                :label="opt.label"
              />
            </el-select>
          </el-form-item>
          <el-form-item label="资源ID" prop="resource_id" :required="false">
            <LazySelect
              v-if="formData.resource_type"
              :key="`resource-${formData.owner_type}-${formData.resource_type}`"
              :model-value="formData.resource_id !== undefined ? String(formData.resource_id) : undefined"
              @update:model-value="(v) => (formData.resource_id = v ? Number(v) : undefined)"
              :fetcher="resourceFetcher"
              :preload="true"
              placeholder="请选择资源"
              style="width: 100%"
            />
            <el-text v-else size="small" type="info">请先选择资源类型</el-text>
          </el-form-item>
          <el-form-item label="优先级" prop="priority" :required="false">
            <el-input-number v-model="formData.priority" placeholder="请输入优先级（数字越小优先级越高）" :min="0" style="width: 100%" />
          </el-form-item>
          <el-form-item label="配置覆盖" prop="config_override" :required="false">
            <!-- param_schema 引导面板：仅 toolkit 类型资源且有 schema 时显示 -->
            <div v-if="currentParamSchema.length > 0" style="width: 100%; margin-bottom: 8px;">
              <el-text type="info" size="small" style="display: block; margin-bottom: 6px;">
                可配置参数（点击 + 快速填入）：
              </el-text>
              <el-space wrap>
                <el-tooltip
                  v-for="field in currentParamSchema"
                  :key="field.name"
                  :content="`类型: ${field.type} | 默认: ${field.default ?? '无'} | ${field.required ? '必填' : '可选'}`"
                  placement="top"
                  :show-after="200"
                >
                  <el-tag
                    :type="field.required ? 'danger' : 'info'"
                    style="cursor: pointer;"
                    @click="applySchemaField(field)"
                  >
                    + {{ field.name }}
                  </el-tag>
                </el-tooltip>
              </el-space>
            </div>
            <DictEditor v-model="formData.config_override" />
          </el-form-item>
          <el-form-item label="状态" prop="status" :required="false">
            <el-radio-group v-model="formData.status">
              <el-radio value="0">启用</el-radio>
              <el-radio value="1">停用</el-radio>
            </el-radio-group>
          </el-form-item>
          <el-form-item label="描述" prop="description">
            <el-input
              v-model="formData.description"
              :rows="4"
              :maxlength="100"
              show-word-limit
              type="textarea"
              placeholder="请输入描述"
            />
          </el-form-item>
        </el-form>
      </template>

      <template #footer>
        <div class="dialog-footer">
          <!-- 详情弹窗不需要确定按钮的提交逻辑 -->
          <el-button @click="handleCloseDialog">取消</el-button>
          <el-button v-if="dialogVisible.type !== 'detail'" type="primary" @click="handleSubmit">
            确定
          </el-button>
          <el-button v-else type="primary" @click="handleCloseDialog">确定</el-button>
        </div>
      </template>
    </el-dialog>

    <!-- 导入弹窗 -->
    <ImportModal
      v-model="importDialogVisible"
      :content-config="curdContentConfig"
      :loading="uploadLoading"
      @upload="handleUpload"
    />

    <!-- 导出弹窗 -->
    <ExportModal
      v-model="exportsDialogVisible"
      :content-config="curdContentConfig"
      :query-params="queryFormData"
      :page-data="pageTableData"
      :selection-data="selectionRows"
    />
  </div>
</template>

<script setup lang="ts">
defineOptions({
  name: "AgBinding",
  inheritAttrs: false,
});

import { ref, reactive, onMounted, watch, computed } from "vue";
import { ElMessage, ElMessageBox } from "element-plus";
import { QuestionFilled, ArrowUp, ArrowDown, Check, CircleClose } from "@element-plus/icons-vue";
import { formatToDateTime } from "@/utils/dateUtil";
import { useDictStore } from "@/store";
import { ResultEnum } from "@/enums/api/result.enum";
import DatePicker from "@/components/DatePicker/index.vue";
import type { IContentConfig } from "@/components/CURD/types";
import ImportModal from "@/components/CURD/ImportModal.vue";
import ExportModal from "@/components/CURD/ExportModal.vue";
import request from "@/utils/request";
import AgBindingAPI, {
  AgBindingPageQuery,
  AgBindingTable,
  AgBindingForm,
  BindingMeta,
} from "@/api/module_agno_manage/bindings";
import DictEditor from "@/views/module_agno_manage/components/DictEditor/index.vue";
import LazySelect from "@/views/module_agno_manage/components/LazySelect/index.vue";

const visible = ref(false);
const queryFormRef = ref();
const dataFormRef = ref();
const total = ref(0);
const selectIds = ref<number[]>([]);
const selectionRows = ref<AgBindingTable[]>([]);
const loading = ref(false);
const isExpand = ref(false);
const isExpandable = ref(true);

// 分页表单
const pageTableData = ref<AgBindingTable[]>([]);

// 动态选择器数据
const bindingMeta = ref<BindingMeta>({});

// 从 meta 派生：所有 owner 类型选项
const ownerTypeOptions = computed(() =>
  Object.entries(bindingMeta.value).map(([value, info]) => ({ value, label: info.label }))
);

// 从 meta 派生：当前 owner 下可绑资源类型选项
const resourceTypeOptions = computed(() => {
  const ownerType = formData.owner_type;
  if (!ownerType || !bindingMeta.value[ownerType]) return [];
  return Object.entries(bindingMeta.value[ownerType].allowed_resources).map(([value, info]) => ({
    value,
    label: info.label,
  }));
});

// 搜索栏用：所有可能的资源类型（去重）
const allResourceTypeOptions = computed(() => {
  const map = new Map<string, string>();
  for (const owner of Object.values(bindingMeta.value)) {
    for (const [key, info] of Object.entries(owner.allowed_resources)) {
      if (!map.has(key)) map.set(key, info.label);
    }
  }
  return Array.from(map.entries()).map(([value, label]) => ({ value, label }));
});

// 将 schema 中某个字段的默认值填入 config_override
function applySchemaField(field: { name: string; type: string; default: any }) {
  if (!formData.config_override) formData.config_override = {};
  formData.config_override[field.name] = field.default ?? (field.type === 'bool' ? false : field.type === 'int' || field.type === 'float' ? 0 : '');
  // 触发响应式更新
  formData.config_override = { ...formData.config_override };
}

// 表格列配置
const tableColumns = ref([
  { prop: "selection", label: "选择框", show: true },
  { prop: "index", label: "序号", show: true },
  { prop: "owner_type", label: "拥有者类型", show: true },
  { prop: "owner_id", label: "拥有者ID", show: true },
  { prop: "resource_type", label: "资源类型", show: true },
  { prop: "resource_id", label: "资源ID", show: true },
  { prop: "priority", label: "优先级", show: true },
  { prop: "config_override", label: "配置覆盖", show: true },
  { prop: "status", label: "状态", show: true },
  { prop: "description", label: "描述", show: true },
  { prop: "created_time", label: "创建时间", show: true },
  { prop: "updated_time", label: "更新时间", show: true },
  { prop: "created_id", label: "创建人", show: true },
  { prop: "updated_id", label: "更新人", show: true },
  { prop: "operation", label: "操作", show: true },
]);

// 导出列（不含选择/序号/操作）
const exportColumns = [
  { prop: "owner_type", label: "拥有者类型" },
  { prop: "owner_id", label: "拥有者ID" },
  { prop: "resource_type", label: "资源类型" },
  { prop: "resource_id", label: "资源ID" },
  { prop: "priority", label: "优先级" },
  { prop: "config_override", label: "配置覆盖" },
  { prop: "status", label: "状态" },
  { prop: "description", label: "描述" },
  { prop: "created_time", label: "创建时间" },
  { prop: "updated_time", label: "更新时间" },
  { prop: "created_id", label: "创建人" },
  { prop: "updated_id", label: "更新人" },
];

// 导入/导出配置
const curdContentConfig = {
  permPrefix: "module_agno_manage:bindings",
  cols: exportColumns as any,
  importTemplate: () => AgBindingAPI.downloadTemplateAgBinding(),
  exportsAction: async (params: any) => {
    const query: any = { ...params };
    query.status = "0";
    query.page_no = 1;
    query.page_size = 100;
    const all: any[] = [];
    while (true) {
      const res = await AgBindingAPI.listAgBinding(query);
      const items = res.data?.data?.items || [];
      const total = res.data?.data?.total || 0;
      all.push(...items);
      if (all.length >= total || items.length === 0) break;
      query.page_no += 1;
    }
    return all;
  },
} as unknown as IContentConfig;

// 详情表单
const detailFormData = ref<AgBindingTable>({});
// 日期范围临时变量
const createdDateRange = ref<[Date, Date] | []>([]);
// 更新时间范围临时变量
const updatedDateRange = ref<[Date, Date] | []>([]);

// 处理创建时间范围变化
function handleCreatedDateRangeChange(range: [Date, Date]) {
  createdDateRange.value = range;
  if (range && range.length === 2) {
    queryFormData.created_time = [formatToDateTime(range[0]), formatToDateTime(range[1])];
  } else {
    queryFormData.created_time = undefined;
  }
}

// 处理更新时间范围变化
function handleUpdatedDateRangeChange(range: [Date, Date]) {
  updatedDateRange.value = range;
  if (range && range.length === 2) {
    queryFormData.updated_time = [formatToDateTime(range[0]), formatToDateTime(range[1])];
  } else {
    queryFormData.updated_time = undefined;
  }
}

// 分页查询参数
const queryFormData = reactive<AgBindingPageQuery>({
  page_no: 1,
  page_size: 10,
  owner_type: undefined,
  owner_id: undefined,
  resource_type: undefined,
  resource_id: undefined,
  priority: undefined,
  status: undefined,
  created_time: undefined,
  updated_time: undefined,
  created_id: undefined,
  updated_id: undefined,
});

// 编辑表单
const formData = reactive<AgBindingForm>({
  id: undefined,
  owner_type: undefined,
  owner_id: undefined,
  resource_type: undefined,
  resource_id: undefined,
  priority: undefined,
  config_override: undefined,
  status: "0",
  description: undefined,
});

// 字典仓库与需要加载的字典类型
const dictStore = useDictStore();
const dictTypes: any = [
];

// 当前资源的 param_schema（仅 toolkit 有）
const currentParamSchema = ref<Array<{ name: string; type: string; default: any; required: boolean }>>([]);

// resource_id 变化时，按需请求 param_schema
watch(
  () => formData.resource_id,
  async (newId) => {
    currentParamSchema.value = [];
    if (!newId || !formData.resource_type || !formData.owner_type) return;
    const resourceInfo = bindingMeta.value[formData.owner_type]?.allowed_resources[formData.resource_type];
    if (!resourceInfo) return;
    try {
      const res = await request({ url: `${resourceInfo.api_path}/detail/${newId}`, method: "get" });
      currentParamSchema.value = (res as any).data?.data?.param_schema || [];
    } catch {
      // 无 param_schema，忽略
    }
  }
);

// 拥有者懒加载 fetcher
const ownerFetcher = computed(() => {
  const ownerType = formData.owner_type;
  if (!ownerType || !bindingMeta.value[ownerType]) {
    return async () => ({ items: [], total: 0 });
  }
  const apiPath = bindingMeta.value[ownerType].api_path;
  return async (params: { page_no: number; page_size: number; name?: string }) => {
    const res = await request({ url: `${apiPath}/list`, method: "get", params });
    const items = ((res as any).data?.data?.items || []).map((item: any) => ({
      value: String(item.id),
      label: item.name || `${ownerType}#${item.id}`,
      raw: item,
    }));
    return { items, total: (res as any).data?.data?.total || 0 };
  };
});

// 资源懒加载 fetcher
const resourceFetcher = computed(() => {
  const ownerType = formData.owner_type;
  const resourceType = formData.resource_type;
  if (!ownerType || !resourceType || !bindingMeta.value[ownerType]?.allowed_resources[resourceType]) {
    return async () => ({ items: [], total: 0 });
  }
  const apiPath = bindingMeta.value[ownerType].allowed_resources[resourceType].api_path;
  return async (params: { page_no: number; page_size: number; name?: string }) => {
    const res = await request({ url: `${apiPath}/list`, method: "get", params });
    const items = ((res as any).data?.data?.items || []).map((item: any) => ({
      value: String(item.id),
      label: item.name || `${resourceType}#${item.id}`,
      raw: item,
    }));
    return { items, total: (res as any).data?.data?.total || 0 };
  };
});

// 弹窗状态
const dialogVisible = reactive({
  title: "",
  visible: false,
  type: "create" as "create" | "update" | "detail",
});

// 表单验证规则
const rules = reactive({
  owner_type: [{ required: false, message: "请选择拥有者类型", trigger: "change" }],
  owner_id: [{ required: false, message: "请选择拥有者", trigger: "change" }],
  resource_type: [{ required: false, message: "请选择资源类型", trigger: "change" }],
  resource_id: [{ required: false, message: "请选择资源", trigger: "change" }],
  priority: [{ required: false, message: "请输入优先级", trigger: "blur" }],
  config_override: [{ required: false, trigger: "blur" }],
  status: [{ required: false, message: "请选择状态", trigger: "change" }],
  description: [{ required: false, message: "请输入描述", trigger: "blur" }],
});

// 导入弹窗显示状态
const importDialogVisible = ref(false);
const uploadLoading = ref(false);

// 导出弹窗显示状态
const exportsDialogVisible = ref(false);

// 打开导入弹窗
function handleOpenImportDialog() {
  importDialogVisible.value = true;
}

// 打开导出弹窗
function handleOpenExportsModal() {
  exportsDialogVisible.value = true;
}

// 列表刷新
async function handleRefresh() {
  await loadingData();
}

// 加载表格数据
async function loadingData() {
  loading.value = true;
  try {
    const response = await AgBindingAPI.listAgBinding(queryFormData);
    pageTableData.value = response.data.data.items;
    total.value = response.data.data.total;
  } catch (error: any) {
    console.error(error);
  } finally {
    loading.value = false;
  }
}

// 查询（重置页码后获取数据）
async function handleQuery() {
  queryFormData.page_no = 1;
  loadingData();
}

// 选择创建人后触发查询
function handleConfirm() {
  handleQuery();
}

// 拥有者类型变更时重置拥有者ID
function handleOwnerTypeChange(_type: string) {
  formData.owner_id = undefined;
}

// 资源类型变更时重置资源ID
function handleResourceTypeChange(_type: string) {
  formData.resource_id = undefined;
}

// 重置查询
async function handleResetQuery() {
  queryFormRef.value.resetFields();
  queryFormData.page_no = 1;
  // 重置日期范围选择器
  createdDateRange.value = [];
  updatedDateRange.value = [];
  queryFormData.created_time = undefined;
  queryFormData.updated_time = undefined;
  loadingData();
}

// 定义初始表单数据常量
const initialFormData: AgBindingForm = {
  id: undefined,
  owner_type: undefined,
  owner_id: undefined,
  resource_type: undefined,
  resource_id: undefined,
  priority: undefined,
  config_override: undefined,
  status: "0",
  description: undefined,
};

// 重置表单
async function resetForm() {
  if (dataFormRef.value) {
    dataFormRef.value.resetFields();
    dataFormRef.value.clearValidate();
  }
  // 完全重置 formData 为初始状态
  Object.assign(formData, initialFormData);
}

// 行复选框选中项变化
async function handleSelectionChange(selection: any) {
  selectIds.value = selection.map((item: any) => item.id);
  selectionRows.value = selection;
}

// 关闭弹窗
async function handleCloseDialog() {
  dialogVisible.visible = false;
  resetForm();
}

// 打开弹窗
async function handleOpenDialog(type: "create" | "update" | "detail", id?: number) {
  dialogVisible.type = type;
  if (id) {
    const response = await AgBindingAPI.detailAgBinding(id);
    if (type === "detail") {
      dialogVisible.title = "详情";
      Object.assign(detailFormData.value, response.data.data);
    } else if (type === "update") {
      dialogVisible.title = "修改";
      Object.assign(formData, response.data.data);
      // LazySelect 会在下拉打开时自动请求，无需预加载列表
    }
  } else {
    dialogVisible.title = "新增绑定关系";
    Object.assign(formData, initialFormData);
    currentParamSchema.value = [];
  }
  dialogVisible.visible = true;
}

// 提交表单（防抖）
async function handleSubmit() {
  // 表单校验
  dataFormRef.value.validate(async (valid: any) => {
    if (valid) {
      loading.value = true;
      // 根据弹窗传入的参数(deatil\create\update)判断走什么逻辑
      const submitData = { ...formData };
      const id = formData.id;
      if (id) {
        try {
          await AgBindingAPI.updateAgBinding(id, { id, ...submitData });
          dialogVisible.visible = false;
          resetForm();
          handleCloseDialog();
          handleResetQuery();
        } catch (error: any) {
          console.error(error);
        } finally {
          loading.value = false;
        }
      } else {
        try {
          await AgBindingAPI.createAgBinding(submitData);
          dialogVisible.visible = false;
          resetForm();
          handleCloseDialog();
          handleResetQuery();
        } catch (error: any) {
          console.error(error);
        } finally {
          loading.value = false;
        }
      }
    }
  });
}

// 删除、批量删除
async function handleDelete(ids: number[]) {
  ElMessageBox.confirm("确认删除该项数据?", "警告", {
    confirmButtonText: "确定",
    cancelButtonText: "取消",
    type: "warning",
  })
    .then(async () => {
      try {
        loading.value = true;
        await AgBindingAPI.deleteAgBinding(ids);
        handleResetQuery();
      } catch (error: any) {
        console.error(error);
      } finally {
        loading.value = false;
      }
    })
    .catch(() => {
      ElMessageBox.close();
    });
}

// 批量启用/停用
async function handleMoreClick(status: string) {
  if (selectIds.value.length) {
    ElMessageBox.confirm(`确认${status === "0" ? "启用" : "停用"}该项数据?`, "警告", {
      confirmButtonText: "确定",
      cancelButtonText: "取消",
      type: "warning",
    })
      .then(async () => {
        try {
          loading.value = true;
          await AgBindingAPI.batchAgBinding({ ids: selectIds.value, status });
          handleResetQuery();
        } catch (error: any) {
          console.error(error);
        } finally {
          loading.value = false;
        }
      })
      .catch(() => {
        ElMessageBox.close();
      });
  }
}

// 处理上传
const handleUpload = async (formData: FormData) => {
  try {
    uploadLoading.value = true;
    const response = await AgBindingAPI.importAgBinding(formData);
    if (response.data.code === ResultEnum.SUCCESS) {
      ElMessage.success(`${response.data.msg}，${response.data.data}`);
      importDialogVisible.value = false;
      await handleQuery();
    }
  } catch (error: any) {
    console.error(error);
  } finally {
    uploadLoading.value = false;
  }
};

onMounted(async () => {
  // 加载绑定元数据
  try {
    const res = await AgBindingAPI.getBindingMeta();
    bindingMeta.value = res.data.data;
  } catch (e) {
    console.error("加载绑定元数据失败", e);
  }
  // 预加载字典数据
  if (dictTypes.length > 0) {
    await dictStore.getDict(dictTypes);
  }
  loadingData();
});
</script>

<style lang="scss" scoped></style>
