<!-- 工作流节点管理 -->
<template>
  <div class="app-container">
    <el-card class="data-table">
      <template #header>
        <div class="card-header">
          <span>
            工作流节点列表
            <el-tooltip content="工作流节点列表">
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
            <el-form-item label="所属工作流" prop="workflow_id">
              <LazySelect
                v-model="queryFormData.workflow_id"
                :fetcher="workflowFetcher"
                placeholder="请选择工作流"
                style="width: 200px"
              />
            </el-form-item>
            <el-form-item label="节点名称" prop="name">
              <el-input v-model="queryFormData.name" placeholder="请输入节点名称" clearable />
            </el-form-item>
            <el-form-item label="节点类型" prop="node_type">
              <el-select v-model="queryFormData.node_type" placeholder="请选择" style="width: 140px" clearable>
                <el-option value="step" label="step（步骤）" />
                <el-option value="condition" label="condition（条件）" />
                <el-option value="loop" label="loop（循环）" />
                <el-option value="parallel" label="parallel（并行）" />
                <el-option value="router" label="router（路由）" />
              </el-select>
            </el-form-item>
            <el-form-item label="执行器类型" prop="executor_type">
              <el-select v-model="queryFormData.executor_type" placeholder="请选择" style="width: 140px" clearable>
                <el-option value="agent" label="agent（Agent）" />
                <el-option value="team" label="team（Team）" />
                <el-option value="custom" label="custom（自定义）" />
              </el-select>
            </el-form-item>
            <el-form-item prop="status" label="状态">
              <el-select v-model="queryFormData.status" placeholder="请选择状态" style="width: 120px" clearable>
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
            <el-form-item>
              <el-button
                v-hasPerm="['module_agno_manage:workflow_nodes:query']"
                type="primary"
                icon="search"
                @click="handleQuery"
              >
                查询
              </el-button>
              <el-button
                v-hasPerm="['module_agno_manage:workflow_nodes:query']"
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
                v-hasPerm="['module_agno_manage:workflow_nodes:create']"
                type="success"
                icon="plus"
                @click="handleOpenDialog('create')"
              >
                新增
              </el-button>
            </el-col>
            <el-col :span="1.5">
              <el-button
                v-hasPerm="['module_agno_manage:workflow_nodes:delete']"
                type="danger"
                icon="delete"
                :disabled="selectIds.length === 0"
                @click="handleDelete(selectIds)"
              >
                批量删除
              </el-button>
            </el-col>
            <el-col :span="1.5">
              <el-dropdown v-hasPerm="['module_agno_manage:workflow_nodes:batch']" trigger="click">
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
                  v-hasPerm="['module_agno_manage:workflow_nodes:import']"
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
                  v-hasPerm="['module_agno_manage:workflow_nodes:export']"
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
                  v-hasPerm="['module_agno_manage:workflow_nodes:query']"
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
          v-if="tableColumns.find((col) => col.prop === 'workflow_id')?.show"
          label="所属工作流"
          prop="workflow_id"
          min-width="160"
          show-overflow-tooltip
        >
          <template #default="scope">
            <span>{{ getWorkflowName(scope.row.workflow_id) }}</span>
          </template>
        </el-table-column>
        <el-table-column
          v-if="tableColumns.find((col) => col.prop === 'parent_node_id')?.show"
          label="父节点"
          prop="parent_node_id"
          min-width="160"
          show-overflow-tooltip
        >
          <template #default="scope">
            <span>{{ scope.row.parent_node_id ? getNodeName(scope.row.parent_node_id) : '（顶层节点）' }}</span>
          </template>
        </el-table-column>
        <el-table-column
          v-if="tableColumns.find((col) => col.prop === 'node_order')?.show"
          label="节点顺序"
          prop="node_order"
          min-width="90"
          show-overflow-tooltip
        />
        <el-table-column
          v-if="tableColumns.find((col) => col.prop === 'node_type')?.show"
          label="节点类型"
          prop="node_type"
          min-width="100"
          show-overflow-tooltip
        />
        <el-table-column
          v-if="tableColumns.find((col) => col.prop === 'name')?.show"
          label="节点名称"
          prop="name"
          min-width="160"
          show-overflow-tooltip
        />
        <el-table-column
          v-if="tableColumns.find((col) => col.prop === 'executor_type')?.show"
          label="执行器类型"
          prop="executor_type"
          min-width="100"
          show-overflow-tooltip
        />
        <el-table-column
          v-if="tableColumns.find((col) => col.prop === 'agent_id')?.show"
          label="关联Agent"
          prop="agent_id"
          min-width="160"
          show-overflow-tooltip
        >
          <template #default="scope">
            <span>{{ getAgentName(scope.row.agent_id) }}</span>
          </template>
        </el-table-column>
        <el-table-column
          v-if="tableColumns.find((col) => col.prop === 'team_id')?.show"
          label="关联Team"
          prop="team_id"
          min-width="160"
          show-overflow-tooltip
        >
          <template #default="scope">
            <span>{{ getTeamName(scope.row.team_id) }}</span>
          </template>
        </el-table-column>
        <el-table-column
          v-if="tableColumns.find((col) => col.prop === 'add_workflow_history')?.show"
          label="传入工作流历史"
          prop="add_workflow_history"
          min-width="130"
        >
          <template #default="scope">
            <el-tag :type="scope.row.add_workflow_history === true ? 'success' : scope.row.add_workflow_history === false ? 'danger' : undefined">
              {{ scope.row.add_workflow_history === true ? '是' : scope.row.add_workflow_history === false ? '否' : '默认' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column
          v-if="tableColumns.find((col) => col.prop === 'max_retries')?.show"
          label="最大重试次数"
          prop="max_retries"
          min-width="110"
          show-overflow-tooltip
        />
        <el-table-column
          v-if="tableColumns.find((col) => col.prop === 'skip_on_failure')?.show"
          label="失败时跳过"
          prop="skip_on_failure"
          min-width="110"
        >
          <template #default="scope">
            <el-tag :type="scope.row.skip_on_failure === true ? 'success' : scope.row.skip_on_failure === false ? 'danger' : undefined">
              {{ scope.row.skip_on_failure === true ? '是' : scope.row.skip_on_failure === false ? '否' : '默认' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column
          v-if="tableColumns.find((col) => col.prop === 'requires_confirmation')?.show"
          label="需要用户确认"
          prop="requires_confirmation"
          min-width="120"
        >
          <template #default="scope">
            <el-tag :type="scope.row.requires_confirmation === true ? 'success' : scope.row.requires_confirmation === false ? 'danger' : undefined">
              {{ scope.row.requires_confirmation === true ? '是' : scope.row.requires_confirmation === false ? '否' : '默认' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column
          v-if="tableColumns.find((col) => col.prop === 'requires_user_input')?.show"
          label="需要用户输入"
          prop="requires_user_input"
          min-width="120"
        >
          <template #default="scope">
            <el-tag :type="scope.row.requires_user_input === true ? 'success' : scope.row.requires_user_input === false ? 'danger' : undefined">
              {{ scope.row.requires_user_input === true ? '是' : scope.row.requires_user_input === false ? '否' : '默认' }}
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
              v-hasPerm="['module_agno_manage:workflow_nodes:detail']"
              type="info"
              size="small"
              link
              icon="document"
              @click="handleOpenDialog('detail', scope.row.id)"
            >
              详情
            </el-button>
            <el-button
              v-hasPerm="['module_agno_manage:workflow_nodes:update']"
              type="primary"
              size="small"
              link
              icon="edit"
              @click="handleOpenDialog('update', scope.row.id)"
            >
              编辑
            </el-button>
            <el-button
              v-hasPerm="['module_agno_manage:workflow_nodes:delete']"
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
      width="860px"
      @close="handleCloseDialog"
    >
      <!-- 详情 -->
      <template v-if="dialogVisible.type === 'detail'">
        <el-descriptions :column="4" border>
          <el-descriptions-item label="ID" :span="2">{{ detailFormData.id }}</el-descriptions-item>
          <el-descriptions-item label="UUID" :span="2">{{ detailFormData.uuid }}</el-descriptions-item>
          <el-descriptions-item label="所属工作流" :span="2">{{ getWorkflowName(detailFormData.workflow_id) }}</el-descriptions-item>
          <el-descriptions-item label="父节点" :span="2">{{ detailFormData.parent_node_id ? getNodeName(detailFormData.parent_node_id) : '（顶层节点）' }}</el-descriptions-item>
          <el-descriptions-item label="节点顺序" :span="2">{{ detailFormData.node_order }}</el-descriptions-item>
          <el-descriptions-item label="节点类型" :span="2">{{ detailFormData.node_type }}</el-descriptions-item>
          <el-descriptions-item label="节点名称" :span="2">{{ detailFormData.name }}</el-descriptions-item>
          <el-descriptions-item label="状态" :span="2">
            <el-tag :type="detailFormData.status == '0' ? 'success' : 'info'">
              {{ detailFormData.status == "0" ? "启用" : "停用" }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="执行器类型" :span="2">{{ detailFormData.executor_type }}</el-descriptions-item>
          <el-descriptions-item label="关联Agent" :span="2">{{ getAgentName(detailFormData.agent_id) }}</el-descriptions-item>
          <el-descriptions-item label="关联Team" :span="2">{{ getTeamName(detailFormData.team_id) }}</el-descriptions-item>
          <el-descriptions-item label="自定义执行器模块" :span="2">{{ detailFormData.executor_module }}</el-descriptions-item>
          <el-descriptions-item label="传入工作流历史" :span="2">
            <el-tag :type="detailFormData.add_workflow_history === true ? 'success' : detailFormData.add_workflow_history === false ? 'danger' : undefined">
              {{ detailFormData.add_workflow_history === true ? '是' : detailFormData.add_workflow_history === false ? '否' : '默认' }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="历史运行次数" :span="2">{{ detailFormData.num_history_runs }}</el-descriptions-item>
          <el-descriptions-item label="严格校验输入" :span="2">
            <el-tag :type="detailFormData.strict_input_validation === true ? 'success' : detailFormData.strict_input_validation === false ? 'danger' : undefined">
              {{ detailFormData.strict_input_validation === true ? '是' : detailFormData.strict_input_validation === false ? '否' : '默认' }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="最大重试次数" :span="2">{{ detailFormData.max_retries }}</el-descriptions-item>
          <el-descriptions-item label="失败时跳过" :span="2">
            <el-tag :type="detailFormData.skip_on_failure === true ? 'success' : detailFormData.skip_on_failure === false ? 'danger' : undefined">
              {{ detailFormData.skip_on_failure === true ? '是' : detailFormData.skip_on_failure === false ? '否' : '默认' }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="条件评估器类型" :span="2">{{ detailFormData.evaluator_type }}</el-descriptions-item>
          <el-descriptions-item label="条件评估器值" :span="4">{{ detailFormData.evaluator_value }}</el-descriptions-item>
          <el-descriptions-item label="分支标记" :span="2">{{ detailFormData.branch }}</el-descriptions-item>
          <el-descriptions-item label="循环最大迭代次数" :span="2">{{ detailFormData.max_iterations }}</el-descriptions-item>
          <el-descriptions-item label="循环终止条件类型" :span="2">{{ detailFormData.end_condition_type }}</el-descriptions-item>
          <el-descriptions-item label="循环终止条件值" :span="2">{{ detailFormData.end_condition_value }}</el-descriptions-item>
          <el-descriptions-item label="传递迭代输出" :span="2">
            <el-tag :type="detailFormData.forward_iteration_output === true ? 'success' : detailFormData.forward_iteration_output === false ? 'danger' : undefined">
              {{ detailFormData.forward_iteration_output === true ? '是' : detailFormData.forward_iteration_output === false ? '否' : '默认' }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="路由选择器类型" :span="2">{{ detailFormData.selector_type }}</el-descriptions-item>
          <el-descriptions-item label="路由选择器值" :span="4">{{ detailFormData.selector_value }}</el-descriptions-item>
          <el-descriptions-item label="允许多路由选择" :span="2">
            <el-tag :type="detailFormData.allow_multiple_selections === true ? 'success' : detailFormData.allow_multiple_selections === false ? 'danger' : undefined">
              {{ detailFormData.allow_multiple_selections === true ? '是' : detailFormData.allow_multiple_selections === false ? '否' : '默认' }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="需要用户确认" :span="2">
            <el-tag :type="detailFormData.requires_confirmation === true ? 'success' : detailFormData.requires_confirmation === false ? 'danger' : undefined">
              {{ detailFormData.requires_confirmation === true ? '是' : detailFormData.requires_confirmation === false ? '否' : '默认' }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="确认提示消息" :span="4">{{ detailFormData.confirmation_message }}</el-descriptions-item>
          <el-descriptions-item label="需要用户输入" :span="2">
            <el-tag :type="detailFormData.requires_user_input === true ? 'success' : detailFormData.requires_user_input === false ? 'danger' : undefined">
              {{ detailFormData.requires_user_input === true ? '是' : detailFormData.requires_user_input === false ? '否' : '默认' }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="用户输入提示" :span="2">{{ detailFormData.user_input_message }}</el-descriptions-item>
          <el-descriptions-item label="用户输入Schema" :span="4">
            <pre style="margin: 0; white-space: pre-wrap; font-size: 12px">{{ JSON.stringify(detailFormData.user_input_schema, null, 2) }}</pre>
          </el-descriptions-item>
          <el-descriptions-item label="拒绝时处理策略" :span="2">{{ detailFormData.on_reject }}</el-descriptions-item>
          <el-descriptions-item label="出错时处理策略" :span="2">{{ detailFormData.on_error }}</el-descriptions-item>
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
              <el-form-item label="所属工作流" prop="workflow_id" :required="false">
                <LazySelect
                  v-model="workflowIdStr"
                  :fetcher="workflowFetcher"
                  placeholder="请选择工作流"
                  @update:model-value="(v) => formData.workflow_id = v ? Number(v) : undefined"
                />
              </el-form-item>
              <el-form-item label="父节点" prop="parent_node_id" :required="false">
                <LazySelect
                  v-model="parentNodeIdStr"
                  :fetcher="workflowNodeFetcher"
                  placeholder="请选择父节点（空为顶层节点）"
                  @update:model-value="(v) => formData.parent_node_id = v ? Number(v) : undefined"
                />
              </el-form-item>
              <el-form-item label="节点顺序" prop="node_order" :required="false">
                <el-input-number v-model="formData.node_order" :min="0" placeholder="请输入节点顺序" style="width: 100%" />
              </el-form-item>
              <el-form-item label="节点类型" prop="node_type" :required="false">
                <el-select v-model="formData.node_type" placeholder="请选择节点类型" clearable style="width: 100%">
                  <el-option value="step" label="step（步骤）" />
                  <el-option value="condition" label="condition（条件）" />
                  <el-option value="loop" label="loop（循环）" />
                  <el-option value="parallel" label="parallel（并行）" />
                  <el-option value="router" label="router（路由）" />
                </el-select>
              </el-form-item>
              <el-form-item label="节点名称" prop="name" :required="false">
                <el-input v-model="formData.name" placeholder="请输入节点名称" />
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
                  :rows="3"
                  :maxlength="200"
                  show-word-limit
                  type="textarea"
                  placeholder="请输入描述"
                />
              </el-form-item>
            </el-tab-pane>

            <!-- Tab2: 执行器配置 -->
            <el-tab-pane label="执行器配置">
              <el-form-item label="执行器类型" prop="executor_type" :required="false">
                <el-select v-model="formData.executor_type" placeholder="请选择执行器类型" clearable style="width: 100%">
                  <el-option value="agent" label="agent（Agent）" />
                  <el-option value="team" label="team（Team）" />
                  <el-option value="custom" label="custom（自定义）" />
                </el-select>
              </el-form-item>
              <el-form-item label="关联Agent" prop="agent_id" :required="false">
                <LazySelect
                  v-model="agentIdStr"
                  :fetcher="agentFetcher"
                  placeholder="请选择Agent（executor_type=agent时）"
                  @update:model-value="(v) => formData.agent_id = v ? Number(v) : undefined"
                />
              </el-form-item>
              <el-form-item label="关联Team" prop="team_id" :required="false">
                <LazySelect
                  v-model="teamIdStr"
                  :fetcher="teamFetcher"
                  placeholder="请选择Team（executor_type=team时）"
                  @update:model-value="(v) => formData.team_id = v ? Number(v) : undefined"
                />
              </el-form-item>
              <el-form-item label="自定义执行器模块" prop="executor_module" :required="false">
                <el-input v-model="formData.executor_module" placeholder="自定义执行器模块路径（executor_type=custom时）" />
              </el-form-item>
              <el-form-item label="传入工作流历史" prop="add_workflow_history" :required="false">
                <el-select v-model="formData.add_workflow_history" placeholder="默认" clearable style="width: 100%">
                  <el-option label="开启" :value="true" />
                  <el-option label="关闭" :value="false" />
                </el-select>
              </el-form-item>
              <el-form-item label="历史运行次数" prop="num_history_runs" :required="false">
                <el-input-number v-model="formData.num_history_runs" :min="0" placeholder="请输入历史运行次数" style="width: 100%" />
              </el-form-item>
              <el-form-item label="严格校验输入" prop="strict_input_validation" :required="false">
                <el-select v-model="formData.strict_input_validation" placeholder="默认" clearable style="width: 100%">
                  <el-option label="开启" :value="true" />
                  <el-option label="关闭" :value="false" />
                </el-select>
              </el-form-item>
              <el-form-item label="最大重试次数" prop="max_retries" :required="false">
                <el-input-number v-model="formData.max_retries" :min="0" placeholder="请输入最大重试次数" style="width: 100%" />
              </el-form-item>
              <el-form-item label="失败时跳过" prop="skip_on_failure" :required="false">
                <el-select v-model="formData.skip_on_failure" placeholder="默认" clearable style="width: 100%">
                  <el-option label="开启" :value="true" />
                  <el-option label="关闭" :value="false" />
                </el-select>
              </el-form-item>
            </el-tab-pane>

            <!-- Tab3: 条件与循环 -->
            <el-tab-pane label="条件与循环">
              <el-form-item label="条件评估器类型" prop="evaluator_type" :required="false">
                <el-select v-model="formData.evaluator_type" placeholder="请选择" clearable style="width: 100%">
                  <el-option value="bool" label="bool" />
                  <el-option value="cel" label="cel（CEL表达式）" />
                  <el-option value="function" label="function（函数）" />
                </el-select>
              </el-form-item>
              <el-form-item label="条件评估器值" prop="evaluator_value" :required="false">
                <el-input
                  v-model="formData.evaluator_value"
                  :rows="3"
                  type="textarea"
                  placeholder="请输入条件评估器值"
                />
              </el-form-item>
              <el-form-item label="分支标记" prop="branch" :required="false">
                <el-select v-model="formData.branch" placeholder="请选择" clearable style="width: 100%">
                  <el-option value="if" label="if" />
                  <el-option value="else" label="else" />
                </el-select>
              </el-form-item>
              <el-form-item label="循环最大迭代次数" prop="max_iterations" :required="false">
                <el-input-number v-model="formData.max_iterations" :min="0" placeholder="请输入最大迭代次数" style="width: 100%" />
              </el-form-item>
              <el-form-item label="循环终止条件类型" prop="end_condition_type" :required="false">
                <el-input v-model="formData.end_condition_type" placeholder="请输入循环终止条件类型" />
              </el-form-item>
              <el-form-item label="循环终止条件值" prop="end_condition_value" :required="false">
                <el-input
                  v-model="formData.end_condition_value"
                  :rows="3"
                  type="textarea"
                  placeholder="请输入循环终止条件值"
                />
              </el-form-item>
              <el-form-item label="传递迭代输出" prop="forward_iteration_output" :required="false">
                <el-select v-model="formData.forward_iteration_output" placeholder="默认" clearable style="width: 100%">
                  <el-option label="开启" :value="true" />
                  <el-option label="关闭" :value="false" />
                </el-select>
              </el-form-item>
            </el-tab-pane>

            <!-- Tab4: 路由配置 -->
            <el-tab-pane label="路由配置">
              <el-form-item label="路由选择器类型" prop="selector_type" :required="false">
                <el-input v-model="formData.selector_type" placeholder="请输入路由选择器类型" />
              </el-form-item>
              <el-form-item label="路由选择器值" prop="selector_value" :required="false">
                <el-input
                  v-model="formData.selector_value"
                  :rows="3"
                  type="textarea"
                  placeholder="请输入路由选择器值"
                />
              </el-form-item>
              <el-form-item label="允许多路由选择" prop="allow_multiple_selections" :required="false">
                <el-select v-model="formData.allow_multiple_selections" placeholder="默认" clearable style="width: 100%">
                  <el-option label="开启" :value="true" />
                  <el-option label="关闭" :value="false" />
                </el-select>
              </el-form-item>
            </el-tab-pane>

            <!-- Tab5: 人机交互（HITL） -->
            <el-tab-pane label="人机交互（HITL）">
              <el-form-item label="需要用户确认" prop="requires_confirmation" :required="false">
                <el-select v-model="formData.requires_confirmation" placeholder="默认" clearable style="width: 100%">
                  <el-option label="开启" :value="true" />
                  <el-option label="关闭" :value="false" />
                </el-select>
              </el-form-item>
              <el-form-item label="确认提示消息" prop="confirmation_message" :required="false">
                <el-input
                  v-model="formData.confirmation_message"
                  :rows="3"
                  type="textarea"
                  placeholder="请输入确认提示消息"
                />
              </el-form-item>
              <el-form-item label="需要用户输入" prop="requires_user_input" :required="false">
                <el-select v-model="formData.requires_user_input" placeholder="默认" clearable style="width: 100%">
                  <el-option label="开启" :value="true" />
                  <el-option label="关闭" :value="false" />
                </el-select>
              </el-form-item>
              <el-form-item label="用户输入提示消息" prop="user_input_message" :required="false">
                <el-input
                  v-model="formData.user_input_message"
                  :rows="3"
                  type="textarea"
                  placeholder="请输入用户输入提示消息"
                />
              </el-form-item>
              <el-form-item label="用户输入Schema" prop="user_input_schema" :required="false">
                <DictEditor v-model="formData.user_input_schema" />
              </el-form-item>
              <el-form-item label="拒绝时处理策略" prop="on_reject" :required="false">
                <el-select v-model="formData.on_reject" placeholder="请选择" clearable style="width: 100%">
                  <el-option value="skip" label="skip（跳过）" />
                  <el-option value="abort" label="abort（中止）" />
                </el-select>
              </el-form-item>
              <el-form-item label="出错时处理策略" prop="on_error" :required="false">
                <el-select v-model="formData.on_error" placeholder="请选择" clearable style="width: 100%">
                  <el-option value="skip" label="skip（跳过）" />
                  <el-option value="abort" label="abort（中止）" />
                </el-select>
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
  name: "AgWorkflowNode",
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
import LazySelect from "@/views/module_agno_manage/components/LazySelect/index.vue";
import AgWorkflowNodeAPI, {
  AgWorkflowNodePageQuery,
  AgWorkflowNodeTable,
  AgWorkflowNodeForm,
} from "@/api/module_agno_manage/workflow_nodes";
import AgWorkflowAPI from "@/api/module_agno_manage/workflows";
import AgAgentAPI from "@/api/module_agno_manage/agents";
import AgTeamAPI from "@/api/module_agno_manage/teams";

// ---- LazySelect fetcher 函数 ----
const workflowFetcher = async (params: { page_no: number; page_size: number; name?: string }) => {
  const res = await AgWorkflowAPI.listAgWorkflow({ ...params });
  const items = (res.data?.data?.items || []).map((item: any) => ({
    value: String(item.id),
    label: item.name || String(item.id),
    raw: item,
  }));
  return { items, total: res.data?.data?.total || 0 };
};

const workflowNodeFetcher = async (params: { page_no: number; page_size: number; name?: string }) => {
  const res = await AgWorkflowNodeAPI.listAgWorkflowNode({ ...params });
  const items = (res.data?.data?.items || []).map((item: any) => ({
    value: String(item.id),
    label: item.name || String(item.id),
    raw: item,
  }));
  return { items, total: res.data?.data?.total || 0 };
};

const agentFetcher = async (params: { page_no: number; page_size: number; name?: string }) => {
  const res = await AgAgentAPI.listAgAgent({ ...params });
  const items = (res.data?.data?.items || []).map((item: any) => ({
    value: String(item.id),
    label: item.name || String(item.id),
    raw: item,
  }));
  return { items, total: res.data?.data?.total || 0 };
};

const teamFetcher = async (params: { page_no: number; page_size: number; name?: string }) => {
  const res = await AgTeamAPI.listAgTeam({ ...params });
  const items = (res.data?.data?.items || []).map((item: any) => ({
    value: String(item.id),
    label: item.name || String(item.id),
    raw: item,
  }));
  return { items, total: res.data?.data?.total || 0 };
};

// ---- 名称缓存（用于表格/详情显示）----
const workflowNameCache = ref<Record<string, string>>({});
const nodeNameCache = ref<Record<string, string>>({});
const agentNameCache = ref<Record<string, string>>({});
const teamNameCache = ref<Record<string, string>>({});

function getWorkflowName(id?: number | string | null): string {
  if (!id) return "-";
  const key = String(id);
  if (workflowNameCache.value[key]) return workflowNameCache.value[key];
  AgWorkflowAPI.detailAgWorkflow(Number(id))
    .then((res) => { workflowNameCache.value[key] = res.data?.data?.name || key; })
    .catch(() => { workflowNameCache.value[key] = key; });
  return key;
}

function getNodeName(id?: number | string | null): string {
  if (!id) return "-";
  const key = String(id);
  if (nodeNameCache.value[key]) return nodeNameCache.value[key];
  AgWorkflowNodeAPI.detailAgWorkflowNode(Number(id))
    .then((res) => { nodeNameCache.value[key] = res.data?.data?.name || key; })
    .catch(() => { nodeNameCache.value[key] = key; });
  return key;
}

function getAgentName(id?: number | string | null): string {
  if (!id) return "-";
  const key = String(id);
  if (agentNameCache.value[key]) return agentNameCache.value[key];
  AgAgentAPI.detailAgAgent(Number(id))
    .then((res) => { agentNameCache.value[key] = res.data?.data?.name || key; })
    .catch(() => { agentNameCache.value[key] = key; });
  return key;
}

function getTeamName(id?: number | string | null): string {
  if (!id) return "-";
  const key = String(id);
  if (teamNameCache.value[key]) return teamNameCache.value[key];
  AgTeamAPI.detailAgTeam(Number(id))
    .then((res) => { teamNameCache.value[key] = res.data?.data?.name || key; })
    .catch(() => { teamNameCache.value[key] = key; });
  return key;
}

// ---- 表单中的 LazySelect 绑定字符串（number 字段桥接）----
const workflowIdStr = ref<string>("");
const parentNodeIdStr = ref<string>("");
const agentIdStr = ref<string>("");
const teamIdStr = ref<string>("");

const visible = ref(false);
const queryFormRef = ref();
const dataFormRef = ref();
const total = ref(0);
const selectIds = ref<number[]>([]);
const selectionRows = ref<AgWorkflowNodeTable[]>([]);
const loading = ref(false);
const isExpand = ref(false);
const isExpandable = ref(true);

const pageTableData = ref<AgWorkflowNodeTable[]>([]);

const tableColumns = ref([
  { prop: "selection", label: "选择框", show: true },
  { prop: "index", label: "序号", show: true },
  { prop: "workflow_id", label: "所属工作流", show: true },
  { prop: "parent_node_id", label: "父节点", show: true },
  { prop: "node_order", label: "节点顺序", show: true },
  { prop: "node_type", label: "节点类型", show: true },
  { prop: "name", label: "节点名称", show: true },
  { prop: "executor_type", label: "执行器类型", show: true },
  { prop: "agent_id", label: "关联Agent", show: true },
  { prop: "team_id", label: "关联Team", show: false },
  { prop: "add_workflow_history", label: "传入工作流历史", show: false },
  { prop: "max_retries", label: "最大重试次数", show: false },
  { prop: "skip_on_failure", label: "失败时跳过", show: false },
  { prop: "requires_confirmation", label: "需要用户确认", show: false },
  { prop: "requires_user_input", label: "需要用户输入", show: false },
  { prop: "status", label: "状态", show: true },
  { prop: "description", label: "描述", show: true },
  { prop: "created_time", label: "创建时间", show: true },
  { prop: "updated_time", label: "更新时间", show: false },
  { prop: "created_id", label: "创建人", show: true },
  { prop: "updated_id", label: "更新人", show: false },
  { prop: "operation", label: "操作", show: true },
]);

const exportColumns = [
  { prop: "workflow_id", label: "所属工作流ID" },
  { prop: "parent_node_id", label: "父节点ID" },
  { prop: "node_order", label: "节点顺序" },
  { prop: "node_type", label: "节点类型" },
  { prop: "name", label: "节点名称" },
  { prop: "executor_type", label: "执行器类型" },
  { prop: "agent_id", label: "关联AgentID" },
  { prop: "team_id", label: "关联TeamID" },
  { prop: "executor_module", label: "自定义执行器模块" },
  { prop: "add_workflow_history", label: "传入工作流历史" },
  { prop: "num_history_runs", label: "历史运行次数" },
  { prop: "strict_input_validation", label: "严格校验输入" },
  { prop: "max_retries", label: "最大重试次数" },
  { prop: "skip_on_failure", label: "失败时跳过" },
  { prop: "evaluator_type", label: "条件评估器类型" },
  { prop: "evaluator_value", label: "条件评估器值" },
  { prop: "branch", label: "分支标记" },
  { prop: "max_iterations", label: "循环最大迭代次数" },
  { prop: "end_condition_type", label: "循环终止条件类型" },
  { prop: "end_condition_value", label: "循环终止条件值" },
  { prop: "forward_iteration_output", label: "传递迭代输出" },
  { prop: "selector_type", label: "路由选择器类型" },
  { prop: "selector_value", label: "路由选择器值" },
  { prop: "allow_multiple_selections", label: "允许多路由选择" },
  { prop: "requires_confirmation", label: "需要用户确认" },
  { prop: "confirmation_message", label: "确认提示消息" },
  { prop: "requires_user_input", label: "需要用户输入" },
  { prop: "user_input_message", label: "用户输入提示消息" },
  { prop: "on_reject", label: "拒绝时处理策略" },
  { prop: "on_error", label: "出错时处理策略" },
  { prop: "status", label: "状态" },
  { prop: "description", label: "描述" },
  { prop: "created_time", label: "创建时间" },
  { prop: "updated_time", label: "更新时间" },
  { prop: "created_id", label: "创建人ID" },
  { prop: "updated_id", label: "更新人ID" },
];

const curdContentConfig = {
  permPrefix: "module_agno_manage:workflow_nodes",
  cols: exportColumns as any,
  importTemplate: () => AgWorkflowNodeAPI.downloadTemplateAgWorkflowNode(),
  exportsAction: async (params: any) => {
    const query: any = { ...params };
    query.page_no = 1;
    query.page_size = 9999;
    const all: any[] = [];
    while (true) {
      const res = await AgWorkflowNodeAPI.listAgWorkflowNode(query);
      const items = res.data?.data?.items || [];
      const total = res.data?.data?.total || 0;
      all.push(...items);
      if (all.length >= total || items.length === 0) break;
      query.page_no += 1;
    }
    return all;
  },
} as unknown as IContentConfig;

const detailFormData = ref<AgWorkflowNodeTable>({});
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

const queryFormData = reactive<AgWorkflowNodePageQuery>({
  page_no: 1,
  page_size: 10,
  workflow_id: undefined,
  name: undefined,
  node_type: undefined,
  executor_type: undefined,
  status: undefined,
  created_time: undefined,
  updated_time: undefined,
  created_id: undefined,
  updated_id: undefined,
});

const initialFormData: AgWorkflowNodeForm = {
  id: undefined,
  workflow_id: undefined,
  parent_node_id: undefined,
  node_order: undefined,
  node_type: undefined,
  name: undefined,
  executor_type: undefined,
  agent_id: undefined,
  team_id: undefined,
  executor_module: undefined,
  add_workflow_history: undefined,
  num_history_runs: undefined,
  strict_input_validation: undefined,
  max_retries: undefined,
  skip_on_failure: undefined,
  evaluator_type: undefined,
  evaluator_value: undefined,
  branch: undefined,
  max_iterations: undefined,
  end_condition_type: undefined,
  end_condition_value: undefined,
  forward_iteration_output: undefined,
  selector_type: undefined,
  selector_value: undefined,
  allow_multiple_selections: undefined,
  requires_confirmation: undefined,
  confirmation_message: undefined,
  requires_user_input: undefined,
  user_input_message: undefined,
  user_input_schema: undefined,
  on_reject: undefined,
  on_error: undefined,
  status: "0",
  description: undefined,
};

const formData = reactive<AgWorkflowNodeForm>({ ...initialFormData });

const dictStore = useDictStore();
const dictTypes: any = [];

const dialogVisible = reactive({
  title: "",
  visible: false,
  type: "create" as "create" | "update" | "detail",
});

const rules = reactive({
  name: [{ required: false, message: "请输入节点名称", trigger: "blur" }],
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
    const response = await AgWorkflowNodeAPI.listAgWorkflowNode(queryFormData);
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
  workflowIdStr.value = "";
  parentNodeIdStr.value = "";
  agentIdStr.value = "";
  teamIdStr.value = "";
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
    const response = await AgWorkflowNodeAPI.detailAgWorkflowNode(id);
    const data = response.data.data;
    if (type === "detail") {
      dialogVisible.title = "详情";
      Object.assign(detailFormData.value, data);
    } else if (type === "update") {
      dialogVisible.title = "修改";
      Object.assign(formData, initialFormData, data);
      workflowIdStr.value = data.workflow_id ? String(data.workflow_id) : "";
      parentNodeIdStr.value = data.parent_node_id ? String(data.parent_node_id) : "";
      agentIdStr.value = data.agent_id ? String(data.agent_id) : "";
      teamIdStr.value = data.team_id ? String(data.team_id) : "";
    }
  } else {
    dialogVisible.title = "新增工作流节点";
    Object.assign(formData, initialFormData);
    formData.status = "0";
    workflowIdStr.value = "";
    parentNodeIdStr.value = "";
    agentIdStr.value = "";
    teamIdStr.value = "";
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
          await AgWorkflowNodeAPI.updateAgWorkflowNode(id, { id, ...submitData });
          handleCloseDialog();
          handleResetQuery();
        } catch (error: any) {
          console.error(error);
        } finally {
          loading.value = false;
        }
      } else {
        try {
          await AgWorkflowNodeAPI.createAgWorkflowNode(submitData);
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
        await AgWorkflowNodeAPI.deleteAgWorkflowNode(ids);
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
          await AgWorkflowNodeAPI.batchAgWorkflowNode({ ids: selectIds.value, status });
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
    const response = await AgWorkflowNodeAPI.importAgWorkflowNode(formData);
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
