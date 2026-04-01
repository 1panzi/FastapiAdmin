<!-- 定时任务管理 -->
<template>
  <div class="app-container">
    <!-- 内容区域 -->
    <el-card class="data-table">
      <template #header>
        <div class="card-header">
          <span>
            定时任务管理列表
            <el-tooltip content="定时任务管理列表">
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
            <el-form-item label="定时任务名称" prop="name">
              <el-input v-model="queryFormData.name" placeholder="请输入定时任务名称" clearable />
            </el-form-item>
            <el-form-item label="触发目标AgentID" prop="agent_id">
              <el-input v-model="queryFormData.agent_id" placeholder="请输入触发目标AgentID" clearable />
            </el-form-item>
            <el-form-item label="触发目标TeamID" prop="team_id">
              <el-input v-model="queryFormData.team_id" placeholder="请输入触发目标TeamID" clearable />
            </el-form-item>
            <el-form-item label="触发时传入的消息/参数" prop="payload">
              <el-input v-model="queryFormData.payload" placeholder="请输入触发时传入的消息/参数" clearable />
            </el-form-item>
            <el-form-item label="Cron表达式" prop="cron_expr">
              <el-input v-model="queryFormData.cron_expr" placeholder="请输入Cron表达式" clearable />
            </el-form-item>
            <el-form-item label="时区" prop="timezone">
              <el-input v-model="queryFormData.timezone" placeholder="请输入时区" clearable />
            </el-form-item>
            <el-form-item label="任务超时秒数" prop="timeout_seconds">
              <el-input v-model="queryFormData.timeout_seconds" placeholder="请输入任务超时秒数" clearable />
            </el-form-item>
            <el-form-item label="失败最大重试次数" prop="max_retries">
              <el-input v-model="queryFormData.max_retries" placeholder="请输入失败最大重试次数" clearable />
            </el-form-item>
            <el-form-item label="重试间隔秒数" prop="retry_delay_seconds">
              <el-input v-model="queryFormData.retry_delay_seconds" placeholder="请输入重试间隔秒数" clearable />
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
                v-hasPerm="['module_agno_manage:schedules:query']"
                type="primary"
                icon="search"
                @click="handleQuery"
              >
                查询
              </el-button>
              <el-button
                v-hasPerm="['module_agno_manage:schedules:query']"
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
                v-hasPerm="['module_agno_manage:schedules:create']"
                type="success"
                icon="plus"
                @click="handleOpenDialog('create')"
              >
                新增
              </el-button>
            </el-col>
            <el-col :span="1.5">
              <el-button
                v-hasPerm="['module_agno_manage:schedules:delete']"
                type="danger"
                icon="delete"
                :disabled="selectIds.length === 0"
                @click="handleDelete(selectIds)"
              >
                批量删除
              </el-button>
            </el-col>
            <el-col :span="1.5">
              <el-dropdown v-hasPerm="['module_agno_manage:schedules:batch']" trigger="click">
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
                  v-hasPerm="['module_agno_manage:schedules:import']"
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
                  v-hasPerm="['module_agno_manage:schedules:export']"
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
                  v-hasPerm="['module_agno_manage:schedules:query']"
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
          label="定时任务名称"
          prop="name"
          min-width="140"
          show-overflow-tooltip
        />
        <el-table-column
          v-if="tableColumns.find((col) => col.prop === 'agent_id')?.show"
          label="触发目标AgentID"
          prop="agent_id"
          min-width="140"
          show-overflow-tooltip
        />
        <el-table-column
          v-if="tableColumns.find((col) => col.prop === 'team_id')?.show"
          label="触发目标TeamID"
          prop="team_id"
          min-width="140"
          show-overflow-tooltip
        />
        <el-table-column
          v-if="tableColumns.find((col) => col.prop === 'payload')?.show"
          label="触发时传入的消息/参数"
          prop="payload"
          min-width="140"
          show-overflow-tooltip
        />
        <el-table-column
          v-if="tableColumns.find((col) => col.prop === 'cron_expr')?.show"
          label="Cron表达式"
          prop="cron_expr"
          min-width="140"
          show-overflow-tooltip
        />
        <el-table-column
          v-if="tableColumns.find((col) => col.prop === 'timezone')?.show"
          label="时区"
          prop="timezone"
          min-width="140"
          show-overflow-tooltip
        />
        <el-table-column
          v-if="tableColumns.find((col) => col.prop === 'timeout_seconds')?.show"
          label="任务超时秒数"
          prop="timeout_seconds"
          min-width="140"
          show-overflow-tooltip
        />
        <el-table-column
          v-if="tableColumns.find((col) => col.prop === 'max_retries')?.show"
          label="失败最大重试次数"
          prop="max_retries"
          min-width="140"
          show-overflow-tooltip
        />
        <el-table-column
          v-if="tableColumns.find((col) => col.prop === 'retry_delay_seconds')?.show"
          label="重试间隔秒数"
          prop="retry_delay_seconds"
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
              v-hasPerm="['module_agno_manage:schedules:detail']"
              type="info"
              size="small"
              link
              icon="document"
              @click="handleOpenDialog('detail', scope.row.id)"
            >
              详情
            </el-button>
            <el-button
              v-hasPerm="['module_agno_manage:schedules:update']"
              type="primary"
              size="small"
              link
              icon="edit"
              @click="handleOpenDialog('update', scope.row.id)"
            >
              编辑
            </el-button>
            <el-button
              v-hasPerm="['module_agno_manage:schedules:delete']"
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
          <el-descriptions-item label="定时任务名称" :span="2">
            {{ detailFormData.name }}
          </el-descriptions-item>
          <el-descriptions-item label="触发目标AgentID" :span="2">
            {{ detailFormData.agent_id }}
          </el-descriptions-item>
          <el-descriptions-item label="触发目标TeamID" :span="2">
            {{ detailFormData.team_id }}
          </el-descriptions-item>
          <el-descriptions-item label="触发时传入的消息/参数" :span="2">
            {{ detailFormData.payload }}
          </el-descriptions-item>
          <el-descriptions-item label="Cron表达式" :span="2">
            {{ detailFormData.cron_expr }}
          </el-descriptions-item>
          <el-descriptions-item label="时区" :span="2">
            {{ detailFormData.timezone }}
          </el-descriptions-item>
          <el-descriptions-item label="任务超时秒数" :span="2">
            {{ detailFormData.timeout_seconds }}
          </el-descriptions-item>
          <el-descriptions-item label="失败最大重试次数" :span="2">
            {{ detailFormData.max_retries }}
          </el-descriptions-item>
          <el-descriptions-item label="重试间隔秒数" :span="2">
            {{ detailFormData.retry_delay_seconds }}
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
          <el-form-item label="定时任务名称" prop="name" :required="false">
            <el-input v-model="formData.name" placeholder="请输入定时任务名称" />
          </el-form-item>
          <el-form-item label="触发目标AgentID" prop="agent_id" :required="false">
            <el-input v-model="formData.agent_id" placeholder="请输入触发目标AgentID" />
          </el-form-item>
          <el-form-item label="触发目标TeamID" prop="team_id" :required="false">
            <el-input v-model="formData.team_id" placeholder="请输入触发目标TeamID" />
          </el-form-item>
          <el-form-item label="触发时传入的消息/参数" prop="payload" :required="false">
            <el-input v-model="formData.payload" placeholder="请输入触发时传入的消息/参数" />
          </el-form-item>
          <el-form-item label="Cron表达式" prop="cron_expr" :required="false">
            <el-input v-model="formData.cron_expr" placeholder="请输入Cron表达式" />
          </el-form-item>
          <el-form-item label="时区" prop="timezone" :required="false">
            <el-input v-model="formData.timezone" placeholder="请输入时区" />
          </el-form-item>
          <el-form-item label="任务超时秒数" prop="timeout_seconds" :required="false">
            <el-input v-model="formData.timeout_seconds" placeholder="请输入任务超时秒数" />
          </el-form-item>
          <el-form-item label="失败最大重试次数" prop="max_retries" :required="false">
            <el-input v-model="formData.max_retries" placeholder="请输入失败最大重试次数" />
          </el-form-item>
          <el-form-item label="重试间隔秒数" prop="retry_delay_seconds" :required="false">
            <el-input v-model="formData.retry_delay_seconds" placeholder="请输入重试间隔秒数" />
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
  name: "AgSchedule",
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
import AgScheduleAPI, {
  AgSchedulePageQuery,
  AgScheduleTable,
  AgScheduleForm,
} from "@/api/module_agno_manage/schedules";

const visible = ref(true);
const queryFormRef = ref();
const dataFormRef = ref();
const total = ref(0);
const selectIds = ref<number[]>([]);
const selectionRows = ref<AgScheduleTable[]>([]);
const loading = ref(false);
const isExpand = ref(false);
const isExpandable = ref(true);

// 分页表单
const pageTableData = ref<AgScheduleTable[]>([]);

// 表格列配置
const tableColumns = ref([
  { prop: "selection", label: "选择框", show: true },
  { prop: "index", label: "序号", show: true },
  { prop: "name", label: "定时任务名称", show: true },
  { prop: "agent_id", label: "触发目标AgentID", show: true },
  { prop: "team_id", label: "触发目标TeamID", show: true },
  { prop: "payload", label: "触发时传入的消息/参数", show: true },
  { prop: "cron_expr", label: "Cron表达式（如0 9 * * 1-5）", show: true },
  { prop: "timezone", label: "时区（如Asia/Shanghai）", show: true },
  { prop: "timeout_seconds", label: "任务超时秒数", show: true },
  { prop: "max_retries", label: "失败最大重试次数", show: true },
  { prop: "retry_delay_seconds", label: "重试间隔秒数", show: true },
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
  { prop: "name", label: "定时任务名称" },
  { prop: "agent_id", label: "触发目标AgentID" },
  { prop: "team_id", label: "触发目标TeamID" },
  { prop: "payload", label: "触发时传入的消息/参数" },
  { prop: "cron_expr", label: "Cron表达式（如0 9 * * 1-5）" },
  { prop: "timezone", label: "时区（如Asia/Shanghai）" },
  { prop: "timeout_seconds", label: "任务超时秒数" },
  { prop: "max_retries", label: "失败最大重试次数" },
  { prop: "retry_delay_seconds", label: "重试间隔秒数" },
  { prop: "status", label: "status" },
  { prop: "description", label: "description" },
  { prop: "created_time", label: "created_time" },
  { prop: "updated_time", label: "updated_time" },
  { prop: "created_id", label: "created_id" },
  { prop: "updated_id", label: "updated_id" },
];

// 导入/导出配置
const curdContentConfig = {
  permPrefix: "module_agno_manage:schedules",
  cols: exportColumns as any,
  importTemplate: () => AgScheduleAPI.downloadTemplateAgSchedule(),
  exportsAction: async (params: any) => {
    const query: any = { ...params };
    query.status = "0";
    query.page_no = 1;
    query.page_size = 9999;
    const all: any[] = [];
    while (true) {
      const res = await AgScheduleAPI.listAgSchedule(query);
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
const detailFormData = ref<AgScheduleTable>({});
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
const queryFormData = reactive<AgSchedulePageQuery>({
  page_no: 1,
  page_size: 10,
  name: undefined,
  agent_id: undefined,
  team_id: undefined,
  payload: undefined,
  cron_expr: undefined,
  timezone: undefined,
  timeout_seconds: undefined,
  max_retries: undefined,
  retry_delay_seconds: undefined,
  status: undefined,
  created_time: undefined,
  updated_time: undefined,
  created_id: undefined,
  updated_id: undefined,
});

// 编辑表单
const formData = reactive<AgScheduleForm>({
  id: undefined,
  name: undefined,
  agent_id: undefined,
  team_id: undefined,
  payload: undefined,
  cron_expr: undefined,
  timezone: undefined,
  timeout_seconds: undefined,
  max_retries: undefined,
  retry_delay_seconds: undefined,
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
  name: [{ required: false, message: "请输入定时任务名称", trigger: "blur" }],
  agent_id: [{ required: true, message: "请输入触发目标AgentID", trigger: "blur" }],
  team_id: [{ required: true, message: "请输入触发目标TeamID", trigger: "blur" }],
  payload: [{ required: false, message: "请输入触发时传入的消息/参数", trigger: "blur" }],
  cron_expr: [{ required: false, message: "请输入Cron表达式（如0 9 * * 1-5）", trigger: "blur" }],
  timezone: [{ required: false, message: "请输入时区（如Asia/Shanghai）", trigger: "blur" }],
  timeout_seconds: [{ required: false, message: "请输入任务超时秒数", trigger: "blur" }],
  max_retries: [{ required: false, message: "请输入失败最大重试次数", trigger: "blur" }],
  retry_delay_seconds: [{ required: false, message: "请输入重试间隔秒数", trigger: "blur" }],
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
    const response = await AgScheduleAPI.listAgSchedule(queryFormData);
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
const initialFormData: AgScheduleForm = {
  id: undefined,
  name: undefined,
  agent_id: undefined,
  team_id: undefined,
  payload: undefined,
  cron_expr: undefined,
  timezone: undefined,
  timeout_seconds: undefined,
  max_retries: undefined,
  retry_delay_seconds: undefined,
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
    const response = await AgScheduleAPI.detailAgSchedule(id);
    if (type === "detail") {
      dialogVisible.title = "详情";
      Object.assign(detailFormData.value, response.data.data);
    } else if (type === "update") {
      dialogVisible.title = "修改";
      Object.assign(formData, response.data.data);
    }
  } else {
    dialogVisible.title = "新增AgSchedule";
    formData.id = undefined;
    formData.name = undefined;
    formData.agent_id = undefined;
    formData.team_id = undefined;
    formData.payload = undefined;
    formData.cron_expr = undefined;
    formData.timezone = undefined;
    formData.timeout_seconds = undefined;
    formData.max_retries = undefined;
    formData.retry_delay_seconds = undefined;
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
          await AgScheduleAPI.updateAgSchedule(id, { id, ...submitData });
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
          await AgScheduleAPI.createAgSchedule(submitData);
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
        await AgScheduleAPI.deleteAgSchedule(ids);
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
          await AgScheduleAPI.batchAgSchedule({ ids: selectIds.value, status });
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
    const response = await AgScheduleAPI.importAgSchedule(formData);
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
