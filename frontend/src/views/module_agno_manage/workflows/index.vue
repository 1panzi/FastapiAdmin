<!-- workflow管理 -->
<template>
  <div class="app-container">
    <!-- 内容区域 -->
    <el-card class="data-table">
      <template #header>
        <div class="card-header">
          <span>
            工作流管理列表
            <el-tooltip content="工作流管理列表">
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
            <el-form-item label="工作流名称" prop="name">
              <el-input v-model="queryFormData.name" placeholder="请输入工作流名称" clearable />
            </el-form-item>
            <el-form-item label="流式输出" prop="stream">
              <el-select v-model="queryFormData.stream" placeholder="请选择" style="width: 120px" clearable>
                <el-option :value="'true'" label="是" />
                <el-option :value="'false'" label="否" />
              </el-select>
            </el-form-item>
            <el-form-item label="调试模式" prop="debug_mode">
              <el-select v-model="queryFormData.debug_mode" placeholder="请选择" style="width: 120px" clearable>
                <el-option :value="'true'" label="是" />
                <el-option :value="'false'" label="否" />
              </el-select>
            </el-form-item>
            <el-form-item prop="status" label="状态">
              <el-select
                v-model="queryFormData.status"
                placeholder="请选择状态"
                style="width: 120px"
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
              <template v-if="isExpandable">
                <el-link
                  class="ml-3"
                  type="primary"
                  underline="never"
                  @click="isExpand = !isExpand"
                >
                  {{ isExpand ? "收起" : "展开" }}
                  <el-icon>
                    <template v-if="isExpand"><ArrowUp /></template>
                    <template v-else><ArrowDown /></template>
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
                    <el-dropdown-item :icon="Check" @click="handleMoreClick('0')">批量启用</el-dropdown-item>
                    <el-dropdown-item :icon="CircleClose" @click="handleMoreClick('1')">批量停用</el-dropdown-item>
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
                <el-button type="info" icon="search" circle @click="visible = !visible" />
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

      <!-- 表格区域 -->
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
          label="工作流名称"
          prop="name"
          min-width="160"
          show-overflow-tooltip
        />
        <el-table-column
          v-if="tableColumns.find((col) => col.prop === 'stream')?.show"
          label="流式输出"
          prop="stream"
          min-width="100"
        >
          <template #default="scope">
            <el-tag :type="scope.row.stream === true ? 'success' : scope.row.stream === false ? 'danger' : undefined">
              {{ scope.row.stream === true ? '是' : scope.row.stream === false ? '否' : '默认' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column
          v-if="tableColumns.find((col) => col.prop === 'stream_events')?.show"
          label="流式推送事件"
          prop="stream_events"
          min-width="120"
        >
          <template #default="scope">
            <el-tag :type="scope.row.stream_events === true ? 'success' : scope.row.stream_events === false ? 'danger' : undefined">
              {{ scope.row.stream_events === true ? '是' : scope.row.stream_events === false ? '否' : '默认' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column
          v-if="tableColumns.find((col) => col.prop === 'stream_executor_events')?.show"
          label="流式推送执行器事件"
          prop="stream_executor_events"
          min-width="150"
        >
          <template #default="scope">
            <el-tag :type="scope.row.stream_executor_events === true ? 'success' : scope.row.stream_executor_events === false ? 'danger' : undefined">
              {{ scope.row.stream_executor_events === true ? '是' : scope.row.stream_executor_events === false ? '否' : '默认' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column
          v-if="tableColumns.find((col) => col.prop === 'store_events')?.show"
          label="存储事件"
          prop="store_events"
          min-width="100"
        >
          <template #default="scope">
            <el-tag :type="scope.row.store_events === true ? 'success' : scope.row.store_events === false ? 'danger' : undefined">
              {{ scope.row.store_events === true ? '是' : scope.row.store_events === false ? '否' : '默认' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column
          v-if="tableColumns.find((col) => col.prop === 'store_executor_outputs')?.show"
          label="存储执行器输出"
          prop="store_executor_outputs"
          min-width="130"
        >
          <template #default="scope">
            <el-tag :type="scope.row.store_executor_outputs === true ? 'success' : scope.row.store_executor_outputs === false ? 'danger' : undefined">
              {{ scope.row.store_executor_outputs === true ? '是' : scope.row.store_executor_outputs === false ? '否' : '默认' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column
          v-if="tableColumns.find((col) => col.prop === 'add_workflow_history_to_steps')?.show"
          label="传历史给步骤"
          prop="add_workflow_history_to_steps"
          min-width="120"
        >
          <template #default="scope">
            <el-tag :type="scope.row.add_workflow_history_to_steps === true ? 'success' : scope.row.add_workflow_history_to_steps === false ? 'danger' : undefined">
              {{ scope.row.add_workflow_history_to_steps === true ? '是' : scope.row.add_workflow_history_to_steps === false ? '否' : '默认' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column
          v-if="tableColumns.find((col) => col.prop === 'num_history_runs')?.show"
          label="历史运行次数"
          prop="num_history_runs"
          min-width="120"
          show-overflow-tooltip
        />
        <el-table-column
          v-if="tableColumns.find((col) => col.prop === 'add_session_state_to_context')?.show"
          label="会话状态加入上下文"
          prop="add_session_state_to_context"
          min-width="150"
        >
          <template #default="scope">
            <el-tag :type="scope.row.add_session_state_to_context === true ? 'success' : scope.row.add_session_state_to_context === false ? 'danger' : undefined">
              {{ scope.row.add_session_state_to_context === true ? '是' : scope.row.add_session_state_to_context === false ? '否' : '默认' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column
          v-if="tableColumns.find((col) => col.prop === 'debug_mode')?.show"
          label="调试模式"
          prop="debug_mode"
          min-width="100"
        >
          <template #default="scope">
            <el-tag :type="scope.row.debug_mode === true ? 'success' : scope.row.debug_mode === false ? 'danger' : undefined">
              {{ scope.row.debug_mode === true ? '是' : scope.row.debug_mode === false ? '否' : '默认' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column
          v-if="tableColumns.find((col) => col.prop === 'status')?.show"
          label="状态原始值"
          prop="status"
          min-width="100"
          show-overflow-tooltip
        />
        <el-table-column
          v-if="tableColumns.find((col) => col.prop === 'status')?.show"
          label="状态"
          prop="status"
          min-width="80"
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
          min-width="160"
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
      width="800px"
      @close="handleCloseDialog"
    >
      <!-- 详情 -->
      <template v-if="dialogVisible.type === 'detail'">
        <el-descriptions :column="4" border>
          <el-descriptions-item label="ID" :span="2">{{ detailFormData.id }}</el-descriptions-item>
          <el-descriptions-item label="UUID" :span="2">{{ detailFormData.uuid }}</el-descriptions-item>
          <el-descriptions-item label="工作流名称" :span="2">{{ detailFormData.name }}</el-descriptions-item>
          <el-descriptions-item label="状态" :span="2">
            <el-tag :type="detailFormData.status == '0' ? 'success' : 'info'">
              {{ detailFormData.status == "0" ? "启用" : "停用" }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="流式输出" :span="2">
            <el-tag :type="detailFormData.stream === true ? 'success' : detailFormData.stream === false ? 'danger' : undefined">
              {{ detailFormData.stream === true ? '是' : detailFormData.stream === false ? '否' : '默认' }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="流式推送事件" :span="2">
            <el-tag :type="detailFormData.stream_events === true ? 'success' : detailFormData.stream_events === false ? 'danger' : undefined">
              {{ detailFormData.stream_events === true ? '是' : detailFormData.stream_events === false ? '否' : '默认' }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="流式推送执行器事件" :span="2">
            <el-tag :type="detailFormData.stream_executor_events === true ? 'success' : detailFormData.stream_executor_events === false ? 'danger' : undefined">
              {{ detailFormData.stream_executor_events === true ? '是' : detailFormData.stream_executor_events === false ? '否' : '默认' }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="存储事件" :span="2">
            <el-tag :type="detailFormData.store_events === true ? 'success' : detailFormData.store_events === false ? 'danger' : undefined">
              {{ detailFormData.store_events === true ? '是' : detailFormData.store_events === false ? '否' : '默认' }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="存储执行器输出" :span="2">
            <el-tag :type="detailFormData.store_executor_outputs === true ? 'success' : detailFormData.store_executor_outputs === false ? 'danger' : undefined">
              {{ detailFormData.store_executor_outputs === true ? '是' : detailFormData.store_executor_outputs === false ? '否' : '默认' }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="传历史给步骤" :span="2">
            <el-tag :type="detailFormData.add_workflow_history_to_steps === true ? 'success' : detailFormData.add_workflow_history_to_steps === false ? 'danger' : undefined">
              {{ detailFormData.add_workflow_history_to_steps === true ? '是' : detailFormData.add_workflow_history_to_steps === false ? '否' : '默认' }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="历史运行次数" :span="2">{{ detailFormData.num_history_runs }}</el-descriptions-item>
          <el-descriptions-item label="会话状态加入上下文" :span="2">
            <el-tag :type="detailFormData.add_session_state_to_context === true ? 'success' : detailFormData.add_session_state_to_context === false ? 'danger' : undefined">
              {{ detailFormData.add_session_state_to_context === true ? '是' : detailFormData.add_session_state_to_context === false ? '否' : '默认' }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="调试模式" :span="2">
            <el-tag :type="detailFormData.debug_mode === true ? 'success' : detailFormData.debug_mode === false ? 'danger' : undefined">
              {{ detailFormData.debug_mode === true ? '是' : detailFormData.debug_mode === false ? '否' : '默认' }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="输入结构体Schema" :span="4">
            <pre style="margin: 0; white-space: pre-wrap; font-size: 12px">{{ JSON.stringify(detailFormData.input_schema, null, 2) }}</pre>
          </el-descriptions-item>
          <el-descriptions-item label="元数据配置" :span="4">
            <pre style="margin: 0; white-space: pre-wrap; font-size: 12px">{{ JSON.stringify(detailFormData.metadata_config, null, 2) }}</pre>
          </el-descriptions-item>
          <el-descriptions-item label="描述" :span="4">{{ detailFormData.description }}</el-descriptions-item>
          <el-descriptions-item label="创建时间" :span="2">{{ detailFormData.created_time }}</el-descriptions-item>
          <el-descriptions-item label="更新时间" :span="2">{{ detailFormData.updated_time }}</el-descriptions-item>
          <el-descriptions-item label="创建人" :span="2">{{ detailFormData.created_by?.name }}</el-descriptions-item>
          <el-descriptions-item label="更新人" :span="2">{{ detailFormData.updated_by?.name }}</el-descriptions-item>
        </el-descriptions>
      </template>

      <!-- 新增、编辑表单 -->
      <template v-else>
        <el-form
          ref="dataFormRef"
          :model="formData"
          :rules="rules"
          label-suffix=":"
          label-width="160px"
          label-position="right"
        >
          <el-tabs type="border-card">
            <!-- Tab1: 基本信息 -->
            <el-tab-pane label="基本信息">
              <el-form-item label="工作流名称" prop="name" :required="false">
                <el-input v-model="formData.name" placeholder="请输入工作流名称" />
              </el-form-item>
              <el-form-item label="状态" prop="status" :required="false">
                <el-radio-group v-model="formData.status">
                  <el-radio value="0">启用</el-radio>
                  <el-radio value="1">停用</el-radio>
                </el-radio-group>
              </el-form-item>
              <el-form-item label="描述" prop="description" :required="false">
                <el-input
                  v-model="formData.description"
                  :rows="4"
                  :maxlength="200"
                  show-word-limit
                  type="textarea"
                  placeholder="请输入描述"
                />
              </el-form-item>
            </el-tab-pane>

            <!-- Tab2: 流式与存储 -->
            <el-tab-pane label="流式与存储">
              <el-form-item label="流式输出" prop="stream" :required="false">
                <el-select v-model="formData.stream" placeholder="默认" clearable style="width: 100%">
                  <el-option label="开启" :value="true" />
                  <el-option label="关闭" :value="false" />
                </el-select>
              </el-form-item>
              <el-form-item label="流式推送事件" prop="stream_events" :required="false">
                <el-select v-model="formData.stream_events" placeholder="默认" clearable style="width: 100%">
                  <el-option label="开启" :value="true" />
                  <el-option label="关闭" :value="false" />
                </el-select>
              </el-form-item>
              <el-form-item label="流式推送执行器事件" prop="stream_executor_events" :required="false">
                <el-select v-model="formData.stream_executor_events" placeholder="默认" clearable style="width: 100%">
                  <el-option label="开启" :value="true" />
                  <el-option label="关闭" :value="false" />
                </el-select>
              </el-form-item>
              <el-form-item label="存储事件" prop="store_events" :required="false">
                <el-select v-model="formData.store_events" placeholder="默认" clearable style="width: 100%">
                  <el-option label="开启" :value="true" />
                  <el-option label="关闭" :value="false" />
                </el-select>
              </el-form-item>
              <el-form-item label="存储执行器输出" prop="store_executor_outputs" :required="false">
                <el-select v-model="formData.store_executor_outputs" placeholder="默认" clearable style="width: 100%">
                  <el-option label="开启" :value="true" />
                  <el-option label="关闭" :value="false" />
                </el-select>
              </el-form-item>
            </el-tab-pane>

            <!-- Tab3: 历史与上下文 -->
            <el-tab-pane label="历史与上下文">
              <el-form-item label="传历史给步骤" prop="add_workflow_history_to_steps" :required="false">
                <el-select v-model="formData.add_workflow_history_to_steps" placeholder="默认" clearable style="width: 100%">
                  <el-option label="开启" :value="true" />
                  <el-option label="关闭" :value="false" />
                </el-select>
              </el-form-item>
              <el-form-item label="历史运行次数" prop="num_history_runs" :required="false">
                <el-input-number v-model="formData.num_history_runs" :min="0" placeholder="请输入历史运行次数" style="width: 100%" />
              </el-form-item>
              <el-form-item label="会话状态加入上下文" prop="add_session_state_to_context" :required="false">
                <el-select v-model="formData.add_session_state_to_context" placeholder="默认" clearable style="width: 100%">
                  <el-option label="开启" :value="true" />
                  <el-option label="关闭" :value="false" />
                </el-select>
              </el-form-item>
            </el-tab-pane>

            <!-- Tab4: 调试与Schema -->
            <el-tab-pane label="调试与Schema">
              <el-form-item label="调试模式" prop="debug_mode" :required="false">
                <el-select v-model="formData.debug_mode" placeholder="默认" clearable style="width: 100%">
                  <el-option label="开启" :value="true" />
                  <el-option label="关闭" :value="false" />
                </el-select>
              </el-form-item>
              <el-form-item label="输入结构体Schema" prop="input_schema" :required="false">
                <DictEditor v-model="formData.input_schema" />
              </el-form-item>
              <el-form-item label="元数据配置" prop="metadata_config" :required="false">
                <DictEditor v-model="formData.metadata_config" />
              </el-form-item>
            </el-tab-pane>
          </el-tabs>
        </el-form>
      </template>

      <template #footer>
        <div class="dialog-footer">
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
import DictEditor from "@/views/module_agno_manage/components/DictEditor/index.vue";
import AgWorkflowAPI, {
  AgWorkflowPageQuery,
  AgWorkflowTable,
  AgWorkflowForm,
} from "@/api/module_agno_manage/workflows";

const visible = ref(false);
const queryFormRef = ref();
const dataFormRef = ref();
const total = ref(0);
const selectIds = ref<number[]>([]);
const selectionRows = ref<AgWorkflowTable[]>([]);
const loading = ref(false);
const isExpand = ref(false);
const isExpandable = ref(true);

const pageTableData = ref<AgWorkflowTable[]>([]);

const tableColumns = ref([
  { prop: "selection", label: "选择框", show: true },
  { prop: "index", label: "序号", show: true },
  { prop: "name", label: "工作流名称", show: true },
  { prop: "stream", label: "流式输出", show: true },
  { prop: "stream_events", label: "流式推送事件", show: false },
  { prop: "stream_executor_events", label: "流式推送执行器事件", show: false },
  { prop: "store_events", label: "存储事件", show: false },
  { prop: "store_executor_outputs", label: "存储执行器输出", show: false },
  { prop: "add_workflow_history_to_steps", label: "传历史给步骤", show: false },
  { prop: "num_history_runs", label: "历史运行次数", show: false },
  { prop: "add_session_state_to_context", label: "会话状态加入上下文", show: false },
  { prop: "debug_mode", label: "调试模式", show: true },
  { prop: "status", label: "状态", show: true },
  { prop: "description", label: "描述", show: true },
  { prop: "created_time", label: "创建时间", show: true },
  { prop: "updated_time", label: "更新时间", show: false },
  { prop: "created_id", label: "创建人", show: true },
  { prop: "updated_id", label: "更新人", show: false },
  { prop: "operation", label: "操作", show: true },
]);

const exportColumns = [
  { prop: "name", label: "工作流名称" },
  { prop: "stream", label: "流式输出" },
  { prop: "stream_events", label: "流式推送事件" },
  { prop: "stream_executor_events", label: "流式推送执行器事件" },
  { prop: "store_events", label: "存储事件" },
  { prop: "store_executor_outputs", label: "存储执行器输出" },
  { prop: "add_workflow_history_to_steps", label: "传历史给步骤" },
  { prop: "num_history_runs", label: "历史运行次数" },
  { prop: "add_session_state_to_context", label: "会话状态加入上下文" },
  { prop: "debug_mode", label: "调试模式" },
  { prop: "status", label: "状态" },
  { prop: "description", label: "描述" },
  { prop: "created_time", label: "创建时间" },
  { prop: "updated_time", label: "更新时间" },
  { prop: "created_id", label: "创建人ID" },
  { prop: "updated_id", label: "更新人ID" },
];

const curdContentConfig = {
  permPrefix: "module_agno_manage:workflows",
  cols: exportColumns as any,
  importTemplate: () => AgWorkflowAPI.downloadTemplateAgWorkflow(),
  exportsAction: async (params: any) => {
    const query: any = { ...params };
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

const detailFormData = ref<AgWorkflowTable>({});
const createdDateRange = ref<[Date, Date] | []>([]);
const updatedDateRange = ref<[Date, Date] | []>([]);

function handleCreatedDateRangeChange(range: [Date, Date]) {
  createdDateRange.value = range;
  if (range && range.length === 2) {
    queryFormData.created_time = [formatToDateTime(range[0]), formatToDateTime(range[1])];
  } else {
    queryFormData.created_time = undefined;
  }
}

function handleUpdatedDateRangeChange(range: [Date, Date]) {
  updatedDateRange.value = range;
  if (range && range.length === 2) {
    queryFormData.updated_time = [formatToDateTime(range[0]), formatToDateTime(range[1])];
  } else {
    queryFormData.updated_time = undefined;
  }
}

const queryFormData = reactive<AgWorkflowPageQuery>({
  page_no: 1,
  page_size: 10,
  name: undefined,
  stream: undefined,
  debug_mode: undefined,
  status: undefined,
  created_time: undefined,
  updated_time: undefined,
  created_id: undefined,
  updated_id: undefined,
});

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
  metadata_config: undefined,
  status: "0",
  description: undefined,
};

const formData = reactive<AgWorkflowForm>({ ...initialFormData });

const dictStore = useDictStore();
const dictTypes: any = [];

const dialogVisible = reactive({
  title: "",
  visible: false,
  type: "create" as "create" | "update" | "detail",
});

const rules = reactive({
  name: [{ required: false, message: "请输入工作流名称", trigger: "blur" }],
  status: [{ required: false, message: "请选择状态", trigger: "change" }],
});

const importDialogVisible = ref(false);
const uploadLoading = ref(false);
const exportsDialogVisible = ref(false);

function handleOpenImportDialog() {
  importDialogVisible.value = true;
}

function handleOpenExportsModal() {
  exportsDialogVisible.value = true;
}

async function handleRefresh() {
  await loadingData();
}

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

async function handleQuery() {
  queryFormData.page_no = 1;
  loadingData();
}

function handleConfirm() {
  handleQuery();
}

async function handleResetQuery() {
  queryFormRef.value.resetFields();
  queryFormData.page_no = 1;
  createdDateRange.value = [];
  updatedDateRange.value = [];
  queryFormData.created_time = undefined;
  queryFormData.updated_time = undefined;
  loadingData();
}

async function resetForm() {
  if (dataFormRef.value) {
    dataFormRef.value.resetFields();
    dataFormRef.value.clearValidate();
  }
  Object.assign(formData, initialFormData);
}

async function handleSelectionChange(selection: any) {
  selectIds.value = selection.map((item: any) => item.id);
  selectionRows.value = selection;
}

async function handleCloseDialog() {
  dialogVisible.visible = false;
  resetForm();
}

async function handleOpenDialog(type: "create" | "update" | "detail", id?: number) {
  dialogVisible.type = type;
  if (id) {
    const response = await AgWorkflowAPI.detailAgWorkflow(id);
    if (type === "detail") {
      dialogVisible.title = "详情";
      Object.assign(detailFormData.value, response.data.data);
    } else if (type === "update") {
      dialogVisible.title = "修改";
      Object.assign(formData, initialFormData, response.data.data);
    }
  } else {
    dialogVisible.title = "新增工作流";
    Object.assign(formData, initialFormData);
    formData.status = "0";
  }
  dialogVisible.visible = true;
}

async function handleSubmit() {
  dataFormRef.value.validate(async (valid: any) => {
    if (valid) {
      loading.value = true;
      const submitData = { ...formData };
      const id = formData.id;
      if (id) {
        try {
          await AgWorkflowAPI.updateAgWorkflow(id, { id, ...submitData });
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
  if (dictTypes.length > 0) {
    await dictStore.getDict(dictTypes);
  }
  loadingData();
});
</script>

<style lang="scss" scoped></style>
