<!-- workflow管理 -->
<template>
  <div class="app-container">
    <!-- 内容区域 -->
    <el-card class="data-table">
      <template #header>
        <div class="card-header">
          <span>
            workflow管理列表
            <el-tooltip content="workflow管理列表">
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
            <el-form-item label="工作流名称'" prop="name">
              <el-input v-model="queryFormData.name" placeholder="请输入工作流名称'" clearable />
            </el-form-item>
            <el-form-item label="是否开启流式输出" prop="stream">
              <el-input v-model="queryFormData.stream" placeholder="请输入是否开启流式输出" clearable />
            </el-form-item>
            <el-form-item label="是否流式推送事件" prop="stream_events">
              <el-input v-model="queryFormData.stream_events" placeholder="请输入是否流式推送事件" clearable />
            </el-form-item>
            <el-form-item label="是否流式推送执行器事件" prop="stream_executor_events">
              <el-input v-model="queryFormData.stream_executor_events" placeholder="请输入是否流式推送执行器事件" clearable />
            </el-form-item>
            <el-form-item label="是否存储事件" prop="store_events">
              <el-input v-model="queryFormData.store_events" placeholder="请输入是否存储事件" clearable />
            </el-form-item>
            <el-form-item label="是否存储执行器输出" prop="store_executor_outputs">
              <el-input v-model="queryFormData.store_executor_outputs" placeholder="请输入是否存储执行器输出" clearable />
            </el-form-item>
            <el-form-item label="是否将工作流历史传给步骤" prop="add_workflow_history_to_steps">
              <el-input v-model="queryFormData.add_workflow_history_to_steps" placeholder="请输入是否将工作流历史传给步骤" clearable />
            </el-form-item>
            <el-form-item label="传给步骤的历史运行次数" prop="num_history_runs">
              <el-input v-model="queryFormData.num_history_runs" placeholder="请输入传给步骤的历史运行次数" clearable />
            </el-form-item>
            <el-form-item label="是否将会话状态加入上下文" prop="add_session_state_to_context">
              <el-input v-model="queryFormData.add_session_state_to_context" placeholder="请输入是否将会话状态加入上下文" clearable />
            </el-form-item>
            <el-form-item label="是否开启调试模式" prop="debug_mode">
              <el-input v-model="queryFormData.debug_mode" placeholder="请输入是否开启调试模式" clearable />
            </el-form-item>
            <el-form-item label="输入结构体JSON Schema" prop="input_schema">
              <el-input v-model="queryFormData.input_schema" placeholder="请输入输入结构体JSON Schema" clearable />
            </el-form-item>
            <el-form-item label="元数据" prop="metadata">
              <el-input v-model="queryFormData.metadata" placeholder="请输入元数据" clearable />
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
                v-hasPerm="['module_agno_manage:workflows:query']"
                type="primary"
                icon="search"
                @click="handleQuery"
              >
                查询
              </el-button>
              <el-button
                v-hasPerm="['module_agno_manage:workflows:query']"
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
                v-hasPerm="['module_agno_manage:workflows:create']"
                type="success"
                icon="plus"
                @click="handleOpenDialog('create')"
              >
                新增
              </el-button>
            </el-col>
            <el-col :span="1.5">
              <el-button
                v-hasPerm="['module_agno_manage:workflows:delete']"
                type="danger"
                icon="delete"
                :disabled="selectIds.length === 0"
                @click="handleDelete(selectIds)"
              >
                批量删除
              </el-button>
            </el-col>
            <el-col :span="1.5">
              <el-dropdown v-hasPerm="['module_agno_manage:workflows:batch']" trigger="click">
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
                  v-hasPerm="['module_agno_manage:workflows:import']"
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
                  v-hasPerm="['module_agno_manage:workflows:export']"
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
                  v-hasPerm="['module_agno_manage:workflows:query']"
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
          v-if="tableColumns.find((col) => col.prop === 'name')?.show"
          label="工作流名称'"
          prop="name"
          min-width="140"
          show-overflow-tooltip
        />
        <el-table-column
          v-if="tableColumns.find((col) => col.prop === 'stream')?.show"
          label="是否开启流式输出"
          prop="stream"
          min-width="140"
          show-overflow-tooltip
        />
        <el-table-column
          v-if="tableColumns.find((col) => col.prop === 'stream_events')?.show"
          label="是否流式推送事件"
          prop="stream_events"
          min-width="140"
          show-overflow-tooltip
        />
        <el-table-column
          v-if="tableColumns.find((col) => col.prop === 'stream_executor_events')?.show"
          label="是否流式推送执行器事件"
          prop="stream_executor_events"
          min-width="140"
          show-overflow-tooltip
        />
        <el-table-column
          v-if="tableColumns.find((col) => col.prop === 'store_events')?.show"
          label="是否存储事件"
          prop="store_events"
          min-width="140"
          show-overflow-tooltip
        />
        <el-table-column
          v-if="tableColumns.find((col) => col.prop === 'store_executor_outputs')?.show"
          label="是否存储执行器输出"
          prop="store_executor_outputs"
          min-width="140"
          show-overflow-tooltip
        />
        <el-table-column
          v-if="tableColumns.find((col) => col.prop === 'add_workflow_history_to_steps')?.show"
          label="是否将工作流历史传给步骤"
          prop="add_workflow_history_to_steps"
          min-width="140"
          show-overflow-tooltip
        />
        <el-table-column
          v-if="tableColumns.find((col) => col.prop === 'num_history_runs')?.show"
          label="传给步骤的历史运行次数"
          prop="num_history_runs"
          min-width="140"
          show-overflow-tooltip
        />
        <el-table-column
          v-if="tableColumns.find((col) => col.prop === 'add_session_state_to_context')?.show"
          label="是否将会话状态加入上下文"
          prop="add_session_state_to_context"
          min-width="140"
          show-overflow-tooltip
        />
        <el-table-column
          v-if="tableColumns.find((col) => col.prop === 'debug_mode')?.show"
          label="是否开启调试模式"
          prop="debug_mode"
          min-width="140"
          show-overflow-tooltip
        />
        <el-table-column
          v-if="tableColumns.find((col) => col.prop === 'input_schema')?.show"
          label="输入结构体JSON Schema"
          prop="input_schema"
          min-width="140"
          show-overflow-tooltip
        />
        <el-table-column
          v-if="tableColumns.find((col) => col.prop === 'metadata')?.show"
          label="元数据"
          prop="metadata"
          min-width="140"
          show-overflow-tooltip
        />
        <el-table-column
          v-if="tableColumns.find((col) => col.prop === 'status')?.show"
          label=""
          prop="status"
          min-width="140"
          show-overflow-tooltip
        />
        <el-table-column
          v-if="tableColumns.find((col) => col.prop === 'status')?.show"
          label=""
          prop="status"
          min-width="140"
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
          label=""
          prop="description"
          min-width="140"
          show-overflow-tooltip
        />
        <el-table-column
          v-if="tableColumns.find((col) => col.prop === 'created_time')?.show"
          label=""
          prop="created_time"
          min-width="140"
          show-overflow-tooltip
        />
        <el-table-column
          v-if="tableColumns.find((col) => col.prop === 'updated_time')?.show"
          label=""
          prop="updated_time"
          min-width="140"
          show-overflow-tooltip
        />
        <el-table-column
          v-if="tableColumns.find((col) => col.prop === 'created_id')?.show"
          label=""
          prop="created_id"
          min-width="140"
          show-overflow-tooltip
        />
        <el-table-column
          v-if="tableColumns.find((col) => col.prop === 'created_id')?.show"
          label=""
          prop="created_id"
          min-width="140"
          show-overflow-tooltip
        >
          <template #default="scope">
            <el-tag>{{ scope.row.created_by?.name }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column
          v-if="tableColumns.find((col) => col.prop === 'updated_id')?.show"
          label=""
          prop="updated_id"
          min-width="140"
          show-overflow-tooltip
        />
        <el-table-column
          v-if="tableColumns.find((col) => col.prop === 'updated_id')?.show"
          label=""
          prop="updated_id"
          min-width="140"
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
              v-hasPerm="['module_agno_manage:workflows:detail']"
              type="info"
              size="small"
              link
              icon="document"
              @click="handleOpenDialog('detail', scope.row.id)"
            >
              详情
            </el-button>
            <el-button
              v-hasPerm="['module_agno_manage:workflows:update']"
              type="primary"
              size="small"
              link
              icon="edit"
              @click="handleOpenDialog('update', scope.row.id)"
            >
              编辑
            </el-button>
            <el-button
              v-hasPerm="['module_agno_manage:workflows:delete']"
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
          <el-descriptions-item label="" :span="2">
            {{ detailFormData.id }}
          </el-descriptions-item>
          <el-descriptions-item label="" :span="2">
            {{ detailFormData.uuid }}
          </el-descriptions-item>
          <el-descriptions-item label="工作流名称'" :span="2">
            {{ detailFormData.name }}
          </el-descriptions-item>
          <el-descriptions-item label="是否开启流式输出" :span="2">
            {{ detailFormData.stream }}
          </el-descriptions-item>
          <el-descriptions-item label="是否流式推送事件" :span="2">
            {{ detailFormData.stream_events }}
          </el-descriptions-item>
          <el-descriptions-item label="是否流式推送执行器事件" :span="2">
            {{ detailFormData.stream_executor_events }}
          </el-descriptions-item>
          <el-descriptions-item label="是否存储事件" :span="2">
            {{ detailFormData.store_events }}
          </el-descriptions-item>
          <el-descriptions-item label="是否存储执行器输出" :span="2">
            {{ detailFormData.store_executor_outputs }}
          </el-descriptions-item>
          <el-descriptions-item label="是否将工作流历史传给步骤" :span="2">
            {{ detailFormData.add_workflow_history_to_steps }}
          </el-descriptions-item>
          <el-descriptions-item label="传给步骤的历史运行次数" :span="2">
            {{ detailFormData.num_history_runs }}
          </el-descriptions-item>
          <el-descriptions-item label="是否将会话状态加入上下文" :span="2">
            {{ detailFormData.add_session_state_to_context }}
          </el-descriptions-item>
          <el-descriptions-item label="是否开启调试模式" :span="2">
            {{ detailFormData.debug_mode }}
          </el-descriptions-item>
          <el-descriptions-item label="输入结构体JSON Schema" :span="2">
            {{ detailFormData.input_schema }}
          </el-descriptions-item>
          <el-descriptions-item label="元数据" :span="2">
            {{ detailFormData.metadata }}
          </el-descriptions-item>
          <el-descriptions-item label="状态" :span="2">
            <el-tag :type="detailFormData.status == '0' ? 'success' : 'danger'">
              {{ detailFormData.status == "0" ? "启用" : "停用" }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="" :span="2">
            {{ detailFormData.description }}
          </el-descriptions-item>
          <el-descriptions-item label="" :span="2">
            {{ detailFormData.created_time }}
          </el-descriptions-item>
          <el-descriptions-item label="" :span="2">
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
          <el-form-item label="工作流名称'" prop="name" :required="false">
            <el-input v-model="formData.name" placeholder="请输入工作流名称'" />
          </el-form-item>
          <el-form-item label="是否开启流式输出" prop="stream" :required="false">
            <el-input v-model="formData.stream" placeholder="请输入是否开启流式输出" />
          </el-form-item>
          <el-form-item label="是否流式推送事件" prop="stream_events" :required="false">
            <el-input v-model="formData.stream_events" placeholder="请输入是否流式推送事件" />
          </el-form-item>
          <el-form-item label="是否流式推送执行器事件" prop="stream_executor_events" :required="false">
            <el-input v-model="formData.stream_executor_events" placeholder="请输入是否流式推送执行器事件" />
          </el-form-item>
          <el-form-item label="是否存储事件" prop="store_events" :required="false">
            <el-input v-model="formData.store_events" placeholder="请输入是否存储事件" />
          </el-form-item>
          <el-form-item label="是否存储执行器输出" prop="store_executor_outputs" :required="false">
            <el-input v-model="formData.store_executor_outputs" placeholder="请输入是否存储执行器输出" />
          </el-form-item>
          <el-form-item label="是否将工作流历史传给步骤" prop="add_workflow_history_to_steps" :required="false">
            <el-input v-model="formData.add_workflow_history_to_steps" placeholder="请输入是否将工作流历史传给步骤" />
          </el-form-item>
          <el-form-item label="传给步骤的历史运行次数" prop="num_history_runs" :required="false">
            <el-input v-model="formData.num_history_runs" placeholder="请输入传给步骤的历史运行次数" />
          </el-form-item>
          <el-form-item label="是否将会话状态加入上下文" prop="add_session_state_to_context" :required="false">
            <el-input v-model="formData.add_session_state_to_context" placeholder="请输入是否将会话状态加入上下文" />
          </el-form-item>
          <el-form-item label="是否开启调试模式" prop="debug_mode" :required="false">
            <el-input v-model="formData.debug_mode" placeholder="请输入是否开启调试模式" />
          </el-form-item>
          <el-form-item label="输入结构体JSON Schema" prop="input_schema" :required="false">
            <el-input v-model="formData.input_schema" placeholder="请输入输入结构体JSON Schema" />
          </el-form-item>
          <el-form-item label="元数据" prop="metadata" :required="false">
            <el-input v-model="formData.metadata" placeholder="请输入元数据" />
          </el-form-item>
          <el-form-item label="状态" prop="status" :required="true">
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
  name: "AgWorkflow",
  inheritAttrs: false,
});

import { ref, reactive, onMounted } from "vue";
import { ElMessage, ElMessageBox } from "element-plus";
import { QuestionFilled, ArrowUp, ArrowDown, Check, CircleClose } from "@element-plus/icons-vue";
import { formatToDateTime } from "@/utils/dateUtil";
import { useDictStore } from "@/store";
import { ResultEnum } from "@/enums/api/result.enum";
import DatePicker from "@/components/DatePicker/index.vue";
import type { IContentConfig } from "@/components/CURD/types";
import ImportModal from "@/components/CURD/ImportModal.vue";
import ExportModal from "@/components/CURD/ExportModal.vue";
import AgWorkflowAPI, {
  AgWorkflowPageQuery,
  AgWorkflowTable,
  AgWorkflowForm,
} from "@/api/module_agno_manage/workflows";

const visible = ref(true);
const queryFormRef = ref();
const dataFormRef = ref();
const total = ref(0);
const selectIds = ref<number[]>([]);
const selectionRows = ref<AgWorkflowTable[]>([]);
const loading = ref(false);
const isExpand = ref(false);
const isExpandable = ref(true);

// 分页表单
const pageTableData = ref<AgWorkflowTable[]>([]);

// 表格列配置
const tableColumns = ref([
  { prop: "selection", label: "选择框", show: true },
  { prop: "index", label: "序号", show: true },
  { prop: "name", label: "工作流名称'", show: true },
  { prop: "stream", label: "是否开启流式输出", show: true },
  { prop: "stream_events", label: "是否流式推送事件", show: true },
  { prop: "stream_executor_events", label: "是否流式推送执行器事件", show: true },
  { prop: "store_events", label: "是否存储事件", show: true },
  { prop: "store_executor_outputs", label: "是否存储执行器输出", show: true },
  { prop: "add_workflow_history_to_steps", label: "是否将工作流历史传给步骤", show: true },
  { prop: "num_history_runs", label: "传给步骤的历史运行次数", show: true },
  { prop: "add_session_state_to_context", label: "是否将会话状态加入上下文", show: true },
  { prop: "debug_mode", label: "是否开启调试模式", show: true },
  { prop: "input_schema", label: "输入结构体JSON Schema", show: true },
  { prop: "metadata", label: "元数据", show: true },
  { prop: "status", label: "status", show: true },
  { prop: "description", label: "description", show: true },
  { prop: "created_time", label: "created_time", show: true },
  { prop: "updated_time", label: "updated_time", show: true },
  { prop: "created_id", label: "created_id", show: true },
  { prop: "updated_id", label: "updated_id", show: true },
  { prop: "operation", label: "操作", show: true },
]);

// 导出列（不含选择/序号/操作）
const exportColumns = [
  { prop: "name", label: "工作流名称'" },
  { prop: "stream", label: "是否开启流式输出" },
  { prop: "stream_events", label: "是否流式推送事件" },
  { prop: "stream_executor_events", label: "是否流式推送执行器事件" },
  { prop: "store_events", label: "是否存储事件" },
  { prop: "store_executor_outputs", label: "是否存储执行器输出" },
  { prop: "add_workflow_history_to_steps", label: "是否将工作流历史传给步骤" },
  { prop: "num_history_runs", label: "传给步骤的历史运行次数" },
  { prop: "add_session_state_to_context", label: "是否将会话状态加入上下文" },
  { prop: "debug_mode", label: "是否开启调试模式" },
  { prop: "input_schema", label: "输入结构体JSON Schema" },
  { prop: "metadata", label: "元数据" },
  { prop: "status", label: "status" },
  { prop: "description", label: "description" },
  { prop: "created_time", label: "created_time" },
  { prop: "updated_time", label: "updated_time" },
  { prop: "created_id", label: "created_id" },
  { prop: "updated_id", label: "updated_id" },
];

// 导入/导出配置
const curdContentConfig = {
  permPrefix: "module_agno_manage:workflows",
  cols: exportColumns as any,
  importTemplate: () => AgWorkflowAPI.downloadTemplateAgWorkflow(),
  exportsAction: async (params: any) => {
    const query: any = { ...params };
    query.status = "0";
    query.page_no = 1;
    query.page_size = 9999;
    const all: any[] = [];
    while (true) {
      const res = await AgWorkflowAPI.listAgWorkflow(query);
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
const detailFormData = ref<AgWorkflowTable>({});
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
const queryFormData = reactive<AgWorkflowPageQuery>({
  page_no: 1,
  page_size: 10,
  name: undefined,
  stream: undefined,
  stream_events: undefined,
  stream_executor_events: undefined,
  store_events: undefined,
  store_executor_outputs: undefined,
  add_workflow_history_to_steps: undefined,
  num_history_runs: undefined,
  add_session_state_to_context: undefined,
  debug_mode: undefined,
  input_schema: undefined,
  metadata: undefined,
  status: undefined,
  created_time: undefined,
  updated_time: undefined,
  created_id: undefined,
  updated_id: undefined,
});

// 编辑表单
const formData = reactive<AgWorkflowForm>({
  id: undefined,
  name: undefined,
  stream: undefined,
  stream_events: undefined,
  stream_executor_events: undefined,
  store_events: undefined,
  store_executor_outputs: undefined,
  add_workflow_history_to_steps: undefined,
  num_history_runs: undefined,
  add_session_state_to_context: undefined,
  debug_mode: undefined,
  input_schema: undefined,
  metadata: undefined,
  status: undefined,
  description: undefined,
});

// 字典仓库与需要加载的字典类型
const dictStore = useDictStore();
const dictTypes: any = [
];

// 弹窗状态
const dialogVisible = reactive({
  title: "",
  visible: false,
  type: "create" as "create" | "update" | "detail",
});

// 表单验证规则
const rules = reactive({
  id: [{ required: false, message: "请输入id", trigger: "blur" }],
  uuid: [{ required: false, message: "请输入uuid", trigger: "blur" }],
  name: [{ required: false, message: "请输入工作流名称'", trigger: "blur" }],
  stream: [{ required: false, message: "请输入是否开启流式输出", trigger: "blur" }],
  stream_events: [{ required: false, message: "请输入是否流式推送事件", trigger: "blur" }],
  stream_executor_events: [{ required: false, message: "请输入是否流式推送执行器事件", trigger: "blur" }],
  store_events: [{ required: false, message: "请输入是否存储事件", trigger: "blur" }],
  store_executor_outputs: [{ required: false, message: "请输入是否存储执行器输出", trigger: "blur" }],
  add_workflow_history_to_steps: [{ required: false, message: "请输入是否将工作流历史传给步骤", trigger: "blur" }],
  num_history_runs: [{ required: false, message: "请输入传给步骤的历史运行次数", trigger: "blur" }],
  add_session_state_to_context: [{ required: false, message: "请输入是否将会话状态加入上下文", trigger: "blur" }],
  debug_mode: [{ required: false, message: "请输入是否开启调试模式", trigger: "blur" }],
  input_schema: [{ required: true, message: "请输入输入结构体JSON Schema", trigger: "blur" }],
  metadata: [{ required: false, message: "请输入元数据", trigger: "blur" }],
  status: [{ required: false, message: "请输入status", trigger: "blur" }],
  description: [{ required: true, message: "请输入description", trigger: "blur" }],
  created_time: [{ required: false, message: "请输入created_time", trigger: "blur" }],
  updated_time: [{ required: false, message: "请输入updated_time", trigger: "blur" }],
  created_id: [{ required: true, message: "请输入created_id", trigger: "blur" }],
  updated_id: [{ required: true, message: "请输入updated_id", trigger: "blur" }],
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
    const response = await AgWorkflowAPI.listAgWorkflow(queryFormData);
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
const initialFormData: AgWorkflowForm = {
  id: undefined,
  name: undefined,
  stream: undefined,
  stream_events: undefined,
  stream_executor_events: undefined,
  store_events: undefined,
  store_executor_outputs: undefined,
  add_workflow_history_to_steps: undefined,
  num_history_runs: undefined,
  add_session_state_to_context: undefined,
  debug_mode: undefined,
  input_schema: undefined,
  metadata: undefined,
  status: undefined,
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
    const response = await AgWorkflowAPI.detailAgWorkflow(id);
    if (type === "detail") {
      dialogVisible.title = "详情";
      Object.assign(detailFormData.value, response.data.data);
    } else if (type === "update") {
      dialogVisible.title = "修改";
      Object.assign(formData, response.data.data);
    }
  } else {
    dialogVisible.title = "新增AgWorkflow";
    formData.id = undefined;
    formData.name = undefined;
    formData.stream = undefined;
    formData.stream_events = undefined;
    formData.stream_executor_events = undefined;
    formData.store_events = undefined;
    formData.store_executor_outputs = undefined;
    formData.add_workflow_history_to_steps = undefined;
    formData.num_history_runs = undefined;
    formData.add_session_state_to_context = undefined;
    formData.debug_mode = undefined;
    formData.input_schema = undefined;
    formData.metadata = undefined;
    formData.status = undefined;
    formData.description = undefined;
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
          await AgWorkflowAPI.updateAgWorkflow(id, { id, ...submitData });
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
          await AgWorkflowAPI.createAgWorkflow(submitData);
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
        await AgWorkflowAPI.deleteAgWorkflow(ids);
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
          await AgWorkflowAPI.batchAgWorkflow({ ids: selectIds.value, status });
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
    const response = await AgWorkflowAPI.importAgWorkflow(formData);
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
  // 预加载字典数据
  if (dictTypes.length > 0) {
    await dictStore.getDict(dictTypes);
  }
  loadingData();
});
</script>

<style lang="scss" scoped></style>
