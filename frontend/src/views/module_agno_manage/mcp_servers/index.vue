<!-- MCP服务 -->
<template>
  <div class="app-container">
    <!-- 内容区域 -->
    <el-card class="data-table">
      <template #header>
        <div class="card-header">
          <span>
            MCP服务列表
            <el-tooltip content="MCP服务列表">
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
            <el-form-item label="MCP服务名称" prop="name">
              <el-input v-model="queryFormData.name" placeholder="请输入MCP服务名称" clearable />
            </el-form-item>
            <el-form-item label="传输协议" prop="transport">
              <el-input v-model="queryFormData.transport" placeholder="请输入传输协议" clearable />
            </el-form-item>
            <el-form-item label="stdio启动命令" prop="command">
              <el-input v-model="queryFormData.command" placeholder="请输入stdio启动命令" clearable />
            </el-form-item>
            <el-form-item label="HTTP/SSE服务地址" prop="url">
              <el-input v-model="queryFormData.url" placeholder="请输入HTTP/SSE服务地址" clearable />
            </el-form-item>
            <el-form-item label="环境变量配置" prop="env_config">
              <el-input v-model="queryFormData.env_config" placeholder="请输入环境变量配置" clearable />
            </el-form-item>
            <el-form-item label="仅包含的工具列表" prop="include_tools">
              <el-input v-model="queryFormData.include_tools" placeholder="请输入仅包含的工具列表" clearable />
            </el-form-item>
            <el-form-item label="排除的工具列表" prop="exclude_tools">
              <el-input v-model="queryFormData.exclude_tools" placeholder="请输入排除的工具列表" clearable />
            </el-form-item>
            <el-form-item label="工具名称前缀" prop="tool_name_prefix">
              <el-input v-model="queryFormData.tool_name_prefix" placeholder="请输入工具名称前缀" clearable />
            </el-form-item>
            <el-form-item label="连接超时秒数" prop="timeout_seconds">
              <el-input v-model="queryFormData.timeout_seconds" placeholder="请输入连接超时秒数" clearable />
            </el-form-item>
            <el-form-item label="是否刷新连接" prop="refresh_connection">
              <el-input v-model="queryFormData.refresh_connection" placeholder="请输入是否刷新连接" clearable />
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
                v-hasPerm="['module_agno_manage:mcp_servers:query']"
                type="primary"
                icon="search"
                @click="handleQuery"
              >
                查询
              </el-button>
              <el-button
                v-hasPerm="['module_agno_manage:mcp_servers:query']"
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
                v-hasPerm="['module_agno_manage:mcp_servers:create']"
                type="success"
                icon="plus"
                @click="handleOpenDialog('create')"
              >
                新增
              </el-button>
            </el-col>
            <el-col :span="1.5">
              <el-button
                v-hasPerm="['module_agno_manage:mcp_servers:delete']"
                type="danger"
                icon="delete"
                :disabled="selectIds.length === 0"
                @click="handleDelete(selectIds)"
              >
                批量删除
              </el-button>
            </el-col>
            <el-col :span="1.5">
              <el-dropdown v-hasPerm="['module_agno_manage:mcp_servers:batch']" trigger="click">
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
                  v-hasPerm="['module_agno_manage:mcp_servers:import']"
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
                  v-hasPerm="['module_agno_manage:mcp_servers:export']"
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
                  v-hasPerm="['module_agno_manage:mcp_servers:query']"
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
          label="MCP服务名称"
          prop="name"
          min-width="140"
          show-overflow-tooltip
        />
        <el-table-column
          v-if="tableColumns.find((col) => col.prop === 'transport')?.show"
          label="传输协议"
          prop="transport"
          min-width="140"
          show-overflow-tooltip
        />
        <el-table-column
          v-if="tableColumns.find((col) => col.prop === 'command')?.show"
          label="stdio启动命令"
          prop="command"
          min-width="140"
          show-overflow-tooltip
        />
        <el-table-column
          v-if="tableColumns.find((col) => col.prop === 'url')?.show"
          label="HTTP/SSE服务地址"
          prop="url"
          min-width="140"
          show-overflow-tooltip
        />
        <el-table-column
          v-if="tableColumns.find((col) => col.prop === 'env_config')?.show"
          label="环境变量配置"
          prop="env_config"
          min-width="140"
          show-overflow-tooltip
        />
        <el-table-column
          v-if="tableColumns.find((col) => col.prop === 'include_tools')?.show"
          label="仅包含的工具列表"
          prop="include_tools"
          min-width="140"
          show-overflow-tooltip
        />
        <el-table-column
          v-if="tableColumns.find((col) => col.prop === 'exclude_tools')?.show"
          label="排除的工具列表"
          prop="exclude_tools"
          min-width="140"
          show-overflow-tooltip
        />
        <el-table-column
          v-if="tableColumns.find((col) => col.prop === 'tool_name_prefix')?.show"
          label="工具名称前缀"
          prop="tool_name_prefix"
          min-width="140"
          show-overflow-tooltip
        />
        <el-table-column
          v-if="tableColumns.find((col) => col.prop === 'timeout_seconds')?.show"
          label="连接超时秒数"
          prop="timeout_seconds"
          min-width="140"
          show-overflow-tooltip
        />
        <el-table-column
          v-if="tableColumns.find((col) => col.prop === 'refresh_connection')?.show"
          label="是否刷新连接"
          prop="refresh_connection"
          min-width="140"
          show-overflow-tooltip
        />
        <el-table-column
          v-if="tableColumns.find((col) => col.prop === 'status')?.show"
          label="是否启用"
          prop="status"
          min-width="140"
          show-overflow-tooltip
        />
        <el-table-column
          v-if="tableColumns.find((col) => col.prop === 'status')?.show"
          label="是否启用"
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
              v-hasPerm="['module_agno_manage:mcp_servers:detail']"
              type="info"
              size="small"
              link
              icon="document"
              @click="handleOpenDialog('detail', scope.row.id)"
            >
              详情
            </el-button>
            <el-button
              v-hasPerm="['module_agno_manage:mcp_servers:update']"
              type="primary"
              size="small"
              link
              icon="edit"
              @click="handleOpenDialog('update', scope.row.id)"
            >
              编辑
            </el-button>
            <el-button
              v-hasPerm="['module_agno_manage:mcp_servers:delete']"
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
          <el-descriptions-item label="MCP服务名称" :span="2">
            {{ detailFormData.name }}
          </el-descriptions-item>
          <el-descriptions-item label="传输协议" :span="2">
            {{ detailFormData.transport }}
          </el-descriptions-item>
          <el-descriptions-item label="stdio启动命令" :span="2">
            {{ detailFormData.command }}
          </el-descriptions-item>
          <el-descriptions-item label="HTTP/SSE服务地址" :span="2">
            {{ detailFormData.url }}
          </el-descriptions-item>
          <el-descriptions-item label="环境变量配置" :span="2">
            {{ detailFormData.env_config }}
          </el-descriptions-item>
          <el-descriptions-item label="仅包含的工具列表" :span="2">
            {{ detailFormData.include_tools }}
          </el-descriptions-item>
          <el-descriptions-item label="排除的工具列表" :span="2">
            {{ detailFormData.exclude_tools }}
          </el-descriptions-item>
          <el-descriptions-item label="工具名称前缀" :span="2">
            {{ detailFormData.tool_name_prefix }}
          </el-descriptions-item>
          <el-descriptions-item label="连接超时秒数" :span="2">
            {{ detailFormData.timeout_seconds }}
          </el-descriptions-item>
          <el-descriptions-item label="是否刷新连接" :span="2">
            {{ detailFormData.refresh_connection }}
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
          <el-form-item label="MCP服务名称" prop="name" :required="false">
            <el-input v-model="formData.name" placeholder="请输入MCP服务名称" />
          </el-form-item>
          <el-form-item label="传输协议" prop="transport" :required="false">
            <el-input v-model="formData.transport" placeholder="请输入传输协议" />
          </el-form-item>
          <el-form-item label="stdio启动命令" prop="command" :required="false">
            <el-input v-model="formData.command" placeholder="请输入stdio启动命令" />
          </el-form-item>
          <el-form-item label="HTTP/SSE服务地址" prop="url" :required="false">
            <el-input v-model="formData.url" placeholder="请输入HTTP/SSE服务地址" />
          </el-form-item>
          <el-form-item label="环境变量配置" prop="env_config" :required="false">
            <el-input v-model="formData.env_config" placeholder="请输入环境变量配置" />
          </el-form-item>
          <el-form-item label="仅包含的工具列表" prop="include_tools" :required="false">
            <el-input v-model="formData.include_tools" placeholder="请输入仅包含的工具列表" />
          </el-form-item>
          <el-form-item label="排除的工具列表" prop="exclude_tools" :required="false">
            <el-input v-model="formData.exclude_tools" placeholder="请输入排除的工具列表" />
          </el-form-item>
          <el-form-item label="工具名称前缀" prop="tool_name_prefix" :required="false">
            <el-input v-model="formData.tool_name_prefix" placeholder="请输入工具名称前缀" />
          </el-form-item>
          <el-form-item label="连接超时秒数" prop="timeout_seconds" :required="false">
            <el-input v-model="formData.timeout_seconds" placeholder="请输入连接超时秒数" />
          </el-form-item>
          <el-form-item label="是否刷新连接" prop="refresh_connection" :required="false">
            <el-input v-model="formData.refresh_connection" placeholder="请输入是否刷新连接" />
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
  name: "AgMcpServer",
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
import AgMcpServerAPI, {
  AgMcpServerPageQuery,
  AgMcpServerTable,
  AgMcpServerForm,
} from "@/api/module_agno_manage/mcp_servers";

const visible = ref(true);
const queryFormRef = ref();
const dataFormRef = ref();
const total = ref(0);
const selectIds = ref<number[]>([]);
const selectionRows = ref<AgMcpServerTable[]>([]);
const loading = ref(false);
const isExpand = ref(false);
const isExpandable = ref(true);

// 分页表单
const pageTableData = ref<AgMcpServerTable[]>([]);

// 表格列配置
const tableColumns = ref([
  { prop: "selection", label: "选择框", show: true },
  { prop: "index", label: "序号", show: true },
  { prop: "name", label: "MCP服务名称", show: true },
  { prop: "transport", label: "传输协议", show: true },
  { prop: "command", label: "stdio启动命令", show: true },
  { prop: "url", label: "HTTP/SSE服务地址", show: true },
  { prop: "env_config", label: "环境变量配置", show: true },
  { prop: "include_tools", label: "仅包含的工具列表", show: true },
  { prop: "exclude_tools", label: "排除的工具列表", show: true },
  { prop: "tool_name_prefix", label: "工具名称前缀", show: true },
  { prop: "timeout_seconds", label: "连接超时秒数", show: true },
  { prop: "refresh_connection", label: "是否刷新连接", show: true },
  { prop: "status", label: "是否启用", show: true },
  { prop: "description", label: "description", show: true },
  { prop: "created_time", label: "created_time", show: true },
  { prop: "updated_time", label: "updated_time", show: true },
  { prop: "created_id", label: "created_id", show: true },
  { prop: "updated_id", label: "updated_id", show: true },
  { prop: "operation", label: "操作", show: true },
]);

// 导出列（不含选择/序号/操作）
const exportColumns = [
  { prop: "name", label: "MCP服务名称" },
  { prop: "transport", label: "传输协议" },
  { prop: "command", label: "stdio启动命令" },
  { prop: "url", label: "HTTP/SSE服务地址" },
  { prop: "env_config", label: "环境变量配置" },
  { prop: "include_tools", label: "仅包含的工具列表" },
  { prop: "exclude_tools", label: "排除的工具列表" },
  { prop: "tool_name_prefix", label: "工具名称前缀" },
  { prop: "timeout_seconds", label: "连接超时秒数" },
  { prop: "refresh_connection", label: "是否刷新连接" },
  { prop: "status", label: "是否启用" },
  { prop: "description", label: "description" },
  { prop: "created_time", label: "created_time" },
  { prop: "updated_time", label: "updated_time" },
  { prop: "created_id", label: "created_id" },
  { prop: "updated_id", label: "updated_id" },
];

// 导入/导出配置
const curdContentConfig = {
  permPrefix: "module_agno_manage:mcp_servers",
  cols: exportColumns as any,
  importTemplate: () => AgMcpServerAPI.downloadTemplateAgMcpServer(),
  exportsAction: async (params: any) => {
    const query: any = { ...params };
    query.status = "0";
    query.page_no = 1;
    query.page_size = 9999;
    const all: any[] = [];
    while (true) {
      const res = await AgMcpServerAPI.listAgMcpServer(query);
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
const detailFormData = ref<AgMcpServerTable>({});
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
const queryFormData = reactive<AgMcpServerPageQuery>({
  page_no: 1,
  page_size: 10,
  name: undefined,
  transport: undefined,
  command: undefined,
  url: undefined,
  env_config: undefined,
  include_tools: undefined,
  exclude_tools: undefined,
  tool_name_prefix: undefined,
  timeout_seconds: undefined,
  refresh_connection: undefined,
  status: undefined,
  created_time: undefined,
  updated_time: undefined,
  created_id: undefined,
  updated_id: undefined,
});

// 编辑表单
const formData = reactive<AgMcpServerForm>({
  id: undefined,
  name: undefined,
  transport: undefined,
  command: undefined,
  url: undefined,
  env_config: undefined,
  include_tools: undefined,
  exclude_tools: undefined,
  tool_name_prefix: undefined,
  timeout_seconds: undefined,
  refresh_connection: undefined,
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
  name: [{ required: false, message: "请输入MCP服务名称", trigger: "blur" }],
  transport: [{ required: false, message: "请输入传输协议", trigger: "blur" }],
  command: [{ required: true, message: "请输入stdio启动命令", trigger: "blur" }],
  url: [{ required: true, message: "请输入HTTP/SSE服务地址", trigger: "blur" }],
  env_config: [{ required: false, message: "请输入环境变量配置", trigger: "blur" }],
  include_tools: [{ required: true, message: "请输入仅包含的工具列表", trigger: "blur" }],
  exclude_tools: [{ required: true, message: "请输入排除的工具列表", trigger: "blur" }],
  tool_name_prefix: [{ required: true, message: "请输入工具名称前缀", trigger: "blur" }],
  timeout_seconds: [{ required: false, message: "请输入连接超时秒数", trigger: "blur" }],
  refresh_connection: [{ required: false, message: "请输入是否刷新连接", trigger: "blur" }],
  status: [{ required: false, message: "请输入是否启用", trigger: "blur" }],
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
    const response = await AgMcpServerAPI.listAgMcpServer(queryFormData);
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
const initialFormData: AgMcpServerForm = {
  id: undefined,
  name: undefined,
  transport: undefined,
  command: undefined,
  url: undefined,
  env_config: undefined,
  include_tools: undefined,
  exclude_tools: undefined,
  tool_name_prefix: undefined,
  timeout_seconds: undefined,
  refresh_connection: undefined,
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
    const response = await AgMcpServerAPI.detailAgMcpServer(id);
    if (type === "detail") {
      dialogVisible.title = "详情";
      Object.assign(detailFormData.value, response.data.data);
    } else if (type === "update") {
      dialogVisible.title = "修改";
      Object.assign(formData, response.data.data);
    }
  } else {
    dialogVisible.title = "新增AgMcpServer";
    formData.id = undefined;
    formData.name = undefined;
    formData.transport = undefined;
    formData.command = undefined;
    formData.url = undefined;
    formData.env_config = undefined;
    formData.include_tools = undefined;
    formData.exclude_tools = undefined;
    formData.tool_name_prefix = undefined;
    formData.timeout_seconds = undefined;
    formData.refresh_connection = undefined;
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
          await AgMcpServerAPI.updateAgMcpServer(id, { id, ...submitData });
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
          await AgMcpServerAPI.createAgMcpServer(submitData);
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
        await AgMcpServerAPI.deleteAgMcpServer(ids);
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
          await AgMcpServerAPI.batchAgMcpServer({ ids: selectIds.value, status });
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
    const response = await AgMcpServerAPI.importAgMcpServer(formData);
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
