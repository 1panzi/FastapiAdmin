<!-- 工作流节点 -->
<template>
  <div class="app-container">
    <!-- 内容区域 -->
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
            <el-form-item label="所属工作流ID" prop="workflow_id">
              <el-input v-model="queryFormData.workflow_id" placeholder="请输入所属工作流ID" clearable />
            </el-form-item>
            <el-form-item label="父节点ID" prop="parent_node_id">
              <el-input v-model="queryFormData.parent_node_id" placeholder="请输入父节点ID" clearable />
            </el-form-item>
            <el-form-item label="节点顺序" prop="node_order">
              <el-input v-model="queryFormData.node_order" placeholder="请输入节点顺序" clearable />
            </el-form-item>
            <el-form-item label="节点类型(step/condition/loop/parallel/router)" prop="node_type">
              <el-input v-model="queryFormData.node_type" placeholder="请输入节点类型(step/condition/loop/parallel/router)" clearable />
            </el-form-item>
            <el-form-item label="节点名称" prop="name">
              <el-input v-model="queryFormData.name" placeholder="请输入节点名称" clearable />
            </el-form-item>
            <el-form-item label="执行器类型(agent/team/custom)" prop="executor_type">
              <el-input v-model="queryFormData.executor_type" placeholder="请输入执行器类型(agent/team/custom)" clearable />
            </el-form-item>
            <el-form-item label="联AgentID" prop="agent_id">
              <el-input v-model="queryFormData.agent_id" placeholder="请输入联AgentID" clearable />
            </el-form-item>
            <el-form-item label="关联TeamID" prop="team_id">
              <el-input v-model="queryFormData.team_id" placeholder="请输入关联TeamID" clearable />
            </el-form-item>
            <el-form-item label="自定义执行器模块路径" prop="executor_module">
              <el-input v-model="queryFormData.executor_module" placeholder="请输入自定义执行器模块路径" clearable />
            </el-form-item>
            <el-form-item label="是否传入工作流历史" prop="add_workflow_history">
              <el-input v-model="queryFormData.add_workflow_history" placeholder="请输入是否传入工作流历史" clearable />
            </el-form-item>
            <el-form-item label="传入历史运行次数" prop="num_history_runs">
              <el-input v-model="queryFormData.num_history_runs" placeholder="请输入传入历史运行次数" clearable />
            </el-form-item>
            <el-form-item label="是否严格校验输入" prop="strict_input_validation">
              <el-input v-model="queryFormData.strict_input_validation" placeholder="请输入是否严格校验输入" clearable />
            </el-form-item>
            <el-form-item label="最大重试次数" prop="max_retries">
              <el-input v-model="queryFormData.max_retries" placeholder="请输入最大重试次数" clearable />
            </el-form-item>
            <el-form-item label="失败时是否跳过" prop="skip_on_failure">
              <el-input v-model="queryFormData.skip_on_failure" placeholder="请输入失败时是否跳过" clearable />
            </el-form-item>
            <el-form-item label="条件评估器类型(bool/cel/function)" prop="evaluator_type">
              <el-input v-model="queryFormData.evaluator_type" placeholder="请输入条件评估器类型(bool/cel/function)" clearable />
            </el-form-item>
            <el-form-item label="条件评估器值" prop="evaluator_value">
              <el-input v-model="queryFormData.evaluator_value" placeholder="请输入条件评估器值" clearable />
            </el-form-item>
            <el-form-item label="分支标记(if/else)" prop="branch">
              <el-input v-model="queryFormData.branch" placeholder="请输入分支标记(if/else)" clearable />
            </el-form-item>
            <el-form-item label="循环最大迭代次数" prop="max_iterations">
              <el-input v-model="queryFormData.max_iterations" placeholder="请输入循环最大迭代次数" clearable />
            </el-form-item>
            <el-form-item label="循环终止条件类型" prop="end_condition_type">
              <el-input v-model="queryFormData.end_condition_type" placeholder="请输入循环终止条件类型" clearable />
            </el-form-item>
            <el-form-item label="循环终止条件值" prop="end_condition_value">
              <el-input v-model="queryFormData.end_condition_value" placeholder="请输入循环终止条件值" clearable />
            </el-form-item>
            <el-form-item label="是否传递迭代输出" prop="forward_iteration_output">
              <el-input v-model="queryFormData.forward_iteration_output" placeholder="请输入是否传递迭代输出" clearable />
            </el-form-item>
            <el-form-item label="路由选择器类型" prop="selector_type">
              <el-input v-model="queryFormData.selector_type" placeholder="请输入路由选择器类型" clearable />
            </el-form-item>
            <el-form-item label="路由选择器值" prop="selector_value">
              <el-input v-model="queryFormData.selector_value" placeholder="请输入路由选择器值" clearable />
            </el-form-item>
            <el-form-item label="是否允许多路由选择" prop="allow_multiple_selections">
              <el-input v-model="queryFormData.allow_multiple_selections" placeholder="请输入是否允许多路由选择" clearable />
            </el-form-item>
            <el-form-item label="是否需要用户确认" prop="requires_confirmation">
              <el-input v-model="queryFormData.requires_confirmation" placeholder="请输入是否需要用户确认" clearable />
            </el-form-item>
            <el-form-item label="确认提示消息" prop="confirmation_message">
              <el-input v-model="queryFormData.confirmation_message" placeholder="请输入确认提示消息" clearable />
            </el-form-item>
            <el-form-item label="是否需要用户输入" prop="requires_user_input">
              <el-input v-model="queryFormData.requires_user_input" placeholder="请输入是否需要用户输入" clearable />
            </el-form-item>
            <el-form-item label="用户输入提示消息" prop="user_input_message">
              <el-input v-model="queryFormData.user_input_message" placeholder="请输入用户输入提示消息" clearable />
            </el-form-item>
            <el-form-item label="用户输入结构体Schema" prop="user_input_schema">
              <el-input v-model="queryFormData.user_input_schema" placeholder="请输入用户输入结构体Schema" clearable />
            </el-form-item>
            <el-form-item label="用户拒绝时处理策略(skip/abort)" prop="on_reject">
              <el-input v-model="queryFormData.on_reject" placeholder="请输入用户拒绝时处理策略(skip/abort)" clearable />
            </el-form-item>
            <el-form-item label="节点出错时处理策略(skip/abort)" prop="on_error">
              <el-input v-model="queryFormData.on_error" placeholder="请输入节点出错时处理策略(skip/abort)" clearable />
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
          v-if="tableColumns.find((col) => col.prop === 'workflow_id')?.show"
          label="所属工作流ID"
          prop="workflow_id"
          min-width="140"
          show-overflow-tooltip
        />
        <el-table-column
          v-if="tableColumns.find((col) => col.prop === 'parent_node_id')?.show"
          label="父节点ID"
          prop="parent_node_id"
          min-width="140"
          show-overflow-tooltip
        />
        <el-table-column
          v-if="tableColumns.find((col) => col.prop === 'node_order')?.show"
          label="节点顺序"
          prop="node_order"
          min-width="140"
          show-overflow-tooltip
        />
        <el-table-column
          v-if="tableColumns.find((col) => col.prop === 'node_type')?.show"
          label="节点类型(step/condition/loop/parallel/router)"
          prop="node_type"
          min-width="140"
          show-overflow-tooltip
        />
        <el-table-column
          v-if="tableColumns.find((col) => col.prop === 'name')?.show"
          label="节点名称"
          prop="name"
          min-width="140"
          show-overflow-tooltip
        />
        <el-table-column
          v-if="tableColumns.find((col) => col.prop === 'executor_type')?.show"
          label="执行器类型(agent/team/custom)"
          prop="executor_type"
          min-width="140"
          show-overflow-tooltip
        />
        <el-table-column
          v-if="tableColumns.find((col) => col.prop === 'agent_id')?.show"
          label="联AgentID"
          prop="agent_id"
          min-width="140"
          show-overflow-tooltip
        />
        <el-table-column
          v-if="tableColumns.find((col) => col.prop === 'team_id')?.show"
          label="关联TeamID"
          prop="team_id"
          min-width="140"
          show-overflow-tooltip
        />
        <el-table-column
          v-if="tableColumns.find((col) => col.prop === 'executor_module')?.show"
          label="自定义执行器模块路径"
          prop="executor_module"
          min-width="140"
          show-overflow-tooltip
        />
        <el-table-column
          v-if="tableColumns.find((col) => col.prop === 'add_workflow_history')?.show"
          label="是否传入工作流历史"
          prop="add_workflow_history"
          min-width="140"
          show-overflow-tooltip
        />
        <el-table-column
          v-if="tableColumns.find((col) => col.prop === 'num_history_runs')?.show"
          label="传入历史运行次数"
          prop="num_history_runs"
          min-width="140"
          show-overflow-tooltip
        />
        <el-table-column
          v-if="tableColumns.find((col) => col.prop === 'strict_input_validation')?.show"
          label="是否严格校验输入"
          prop="strict_input_validation"
          min-width="140"
          show-overflow-tooltip
        />
        <el-table-column
          v-if="tableColumns.find((col) => col.prop === 'max_retries')?.show"
          label="最大重试次数"
          prop="max_retries"
          min-width="140"
          show-overflow-tooltip
        />
        <el-table-column
          v-if="tableColumns.find((col) => col.prop === 'skip_on_failure')?.show"
          label="失败时是否跳过"
          prop="skip_on_failure"
          min-width="140"
          show-overflow-tooltip
        />
        <el-table-column
          v-if="tableColumns.find((col) => col.prop === 'evaluator_type')?.show"
          label="条件评估器类型(bool/cel/function)"
          prop="evaluator_type"
          min-width="140"
          show-overflow-tooltip
        />
        <el-table-column
          v-if="tableColumns.find((col) => col.prop === 'evaluator_value')?.show"
          label="条件评估器值"
          prop="evaluator_value"
          min-width="140"
          show-overflow-tooltip
        />
        <el-table-column
          v-if="tableColumns.find((col) => col.prop === 'branch')?.show"
          label="分支标记(if/else)"
          prop="branch"
          min-width="140"
          show-overflow-tooltip
        />
        <el-table-column
          v-if="tableColumns.find((col) => col.prop === 'max_iterations')?.show"
          label="循环最大迭代次数"
          prop="max_iterations"
          min-width="140"
          show-overflow-tooltip
        />
        <el-table-column
          v-if="tableColumns.find((col) => col.prop === 'end_condition_type')?.show"
          label="循环终止条件类型"
          prop="end_condition_type"
          min-width="140"
          show-overflow-tooltip
        />
        <el-table-column
          v-if="tableColumns.find((col) => col.prop === 'end_condition_value')?.show"
          label="循环终止条件值"
          prop="end_condition_value"
          min-width="140"
          show-overflow-tooltip
        />
        <el-table-column
          v-if="tableColumns.find((col) => col.prop === 'forward_iteration_output')?.show"
          label="是否传递迭代输出"
          prop="forward_iteration_output"
          min-width="140"
          show-overflow-tooltip
        />
        <el-table-column
          v-if="tableColumns.find((col) => col.prop === 'selector_type')?.show"
          label="路由选择器类型"
          prop="selector_type"
          min-width="140"
          show-overflow-tooltip
        />
        <el-table-column
          v-if="tableColumns.find((col) => col.prop === 'selector_value')?.show"
          label="路由选择器值"
          prop="selector_value"
          min-width="140"
          show-overflow-tooltip
        />
        <el-table-column
          v-if="tableColumns.find((col) => col.prop === 'allow_multiple_selections')?.show"
          label="是否允许多路由选择"
          prop="allow_multiple_selections"
          min-width="140"
          show-overflow-tooltip
        />
        <el-table-column
          v-if="tableColumns.find((col) => col.prop === 'requires_confirmation')?.show"
          label="是否需要用户确认"
          prop="requires_confirmation"
          min-width="140"
          show-overflow-tooltip
        />
        <el-table-column
          v-if="tableColumns.find((col) => col.prop === 'confirmation_message')?.show"
          label="确认提示消息"
          prop="confirmation_message"
          min-width="140"
          show-overflow-tooltip
        />
        <el-table-column
          v-if="tableColumns.find((col) => col.prop === 'requires_user_input')?.show"
          label="是否需要用户输入"
          prop="requires_user_input"
          min-width="140"
          show-overflow-tooltip
        />
        <el-table-column
          v-if="tableColumns.find((col) => col.prop === 'user_input_message')?.show"
          label="用户输入提示消息"
          prop="user_input_message"
          min-width="140"
          show-overflow-tooltip
        />
        <el-table-column
          v-if="tableColumns.find((col) => col.prop === 'user_input_schema')?.show"
          label="用户输入结构体Schema"
          prop="user_input_schema"
          min-width="140"
          show-overflow-tooltip
        />
        <el-table-column
          v-if="tableColumns.find((col) => col.prop === 'on_reject')?.show"
          label="用户拒绝时处理策略(skip/abort)"
          prop="on_reject"
          min-width="140"
          show-overflow-tooltip
        />
        <el-table-column
          v-if="tableColumns.find((col) => col.prop === 'on_error')?.show"
          label="节点出错时处理策略(skip/abort)"
          prop="on_error"
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
          <el-descriptions-item label="所属工作流ID" :span="2">
            {{ detailFormData.workflow_id }}
          </el-descriptions-item>
          <el-descriptions-item label="父节点ID" :span="2">
            {{ detailFormData.parent_node_id }}
          </el-descriptions-item>
          <el-descriptions-item label="节点顺序" :span="2">
            {{ detailFormData.node_order }}
          </el-descriptions-item>
          <el-descriptions-item label="节点类型(step/condition/loop/parallel/router)" :span="2">
            {{ detailFormData.node_type }}
          </el-descriptions-item>
          <el-descriptions-item label="节点名称" :span="2">
            {{ detailFormData.name }}
          </el-descriptions-item>
          <el-descriptions-item label="执行器类型(agent/team/custom)" :span="2">
            {{ detailFormData.executor_type }}
          </el-descriptions-item>
          <el-descriptions-item label="联AgentID" :span="2">
            {{ detailFormData.agent_id }}
          </el-descriptions-item>
          <el-descriptions-item label="关联TeamID" :span="2">
            {{ detailFormData.team_id }}
          </el-descriptions-item>
          <el-descriptions-item label="自定义执行器模块路径" :span="2">
            {{ detailFormData.executor_module }}
          </el-descriptions-item>
          <el-descriptions-item label="是否传入工作流历史" :span="2">
            {{ detailFormData.add_workflow_history }}
          </el-descriptions-item>
          <el-descriptions-item label="传入历史运行次数" :span="2">
            {{ detailFormData.num_history_runs }}
          </el-descriptions-item>
          <el-descriptions-item label="是否严格校验输入" :span="2">
            {{ detailFormData.strict_input_validation }}
          </el-descriptions-item>
          <el-descriptions-item label="最大重试次数" :span="2">
            {{ detailFormData.max_retries }}
          </el-descriptions-item>
          <el-descriptions-item label="失败时是否跳过" :span="2">
            {{ detailFormData.skip_on_failure }}
          </el-descriptions-item>
          <el-descriptions-item label="条件评估器类型(bool/cel/function)" :span="2">
            {{ detailFormData.evaluator_type }}
          </el-descriptions-item>
          <el-descriptions-item label="条件评估器值" :span="2">
            {{ detailFormData.evaluator_value }}
          </el-descriptions-item>
          <el-descriptions-item label="分支标记(if/else)" :span="2">
            {{ detailFormData.branch }}
          </el-descriptions-item>
          <el-descriptions-item label="循环最大迭代次数" :span="2">
            {{ detailFormData.max_iterations }}
          </el-descriptions-item>
          <el-descriptions-item label="循环终止条件类型" :span="2">
            {{ detailFormData.end_condition_type }}
          </el-descriptions-item>
          <el-descriptions-item label="循环终止条件值" :span="2">
            {{ detailFormData.end_condition_value }}
          </el-descriptions-item>
          <el-descriptions-item label="是否传递迭代输出" :span="2">
            {{ detailFormData.forward_iteration_output }}
          </el-descriptions-item>
          <el-descriptions-item label="路由选择器类型" :span="2">
            {{ detailFormData.selector_type }}
          </el-descriptions-item>
          <el-descriptions-item label="路由选择器值" :span="2">
            {{ detailFormData.selector_value }}
          </el-descriptions-item>
          <el-descriptions-item label="是否允许多路由选择" :span="2">
            {{ detailFormData.allow_multiple_selections }}
          </el-descriptions-item>
          <el-descriptions-item label="是否需要用户确认" :span="2">
            {{ detailFormData.requires_confirmation }}
          </el-descriptions-item>
          <el-descriptions-item label="确认提示消息" :span="2">
            {{ detailFormData.confirmation_message }}
          </el-descriptions-item>
          <el-descriptions-item label="是否需要用户输入" :span="2">
            {{ detailFormData.requires_user_input }}
          </el-descriptions-item>
          <el-descriptions-item label="用户输入提示消息" :span="2">
            {{ detailFormData.user_input_message }}
          </el-descriptions-item>
          <el-descriptions-item label="用户输入结构体Schema" :span="2">
            {{ detailFormData.user_input_schema }}
          </el-descriptions-item>
          <el-descriptions-item label="用户拒绝时处理策略(skip/abort)" :span="2">
            {{ detailFormData.on_reject }}
          </el-descriptions-item>
          <el-descriptions-item label="节点出错时处理策略(skip/abort)" :span="2">
            {{ detailFormData.on_error }}
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
          <el-form-item label="所属工作流ID" prop="workflow_id" :required="false">
            <el-input v-model="formData.workflow_id" placeholder="请输入所属工作流ID" />
          </el-form-item>
          <el-form-item label="父节点ID" prop="parent_node_id" :required="false">
            <el-input v-model="formData.parent_node_id" placeholder="请输入父节点ID" />
          </el-form-item>
          <el-form-item label="节点顺序" prop="node_order" :required="false">
            <el-input v-model="formData.node_order" placeholder="请输入节点顺序" />
          </el-form-item>
          <el-form-item label="节点类型(step/condition/loop/parallel/router)" prop="node_type" :required="false">
            <el-input v-model="formData.node_type" placeholder="请输入节点类型(step/condition/loop/parallel/router)" />
          </el-form-item>
          <el-form-item label="节点名称" prop="name" :required="false">
            <el-input v-model="formData.name" placeholder="请输入节点名称" />
          </el-form-item>
          <el-form-item label="执行器类型(agent/team/custom)" prop="executor_type" :required="false">
            <el-input v-model="formData.executor_type" placeholder="请输入执行器类型(agent/team/custom)" />
          </el-form-item>
          <el-form-item label="联AgentID" prop="agent_id" :required="false">
            <el-input v-model="formData.agent_id" placeholder="请输入联AgentID" />
          </el-form-item>
          <el-form-item label="关联TeamID" prop="team_id" :required="false">
            <el-input v-model="formData.team_id" placeholder="请输入关联TeamID" />
          </el-form-item>
          <el-form-item label="自定义执行器模块路径" prop="executor_module" :required="false">
            <el-input v-model="formData.executor_module" placeholder="请输入自定义执行器模块路径" />
          </el-form-item>
          <el-form-item label="是否传入工作流历史" prop="add_workflow_history" :required="false">
            <el-input v-model="formData.add_workflow_history" placeholder="请输入是否传入工作流历史" />
          </el-form-item>
          <el-form-item label="传入历史运行次数" prop="num_history_runs" :required="false">
            <el-input v-model="formData.num_history_runs" placeholder="请输入传入历史运行次数" />
          </el-form-item>
          <el-form-item label="是否严格校验输入" prop="strict_input_validation" :required="false">
            <el-input v-model="formData.strict_input_validation" placeholder="请输入是否严格校验输入" />
          </el-form-item>
          <el-form-item label="最大重试次数" prop="max_retries" :required="false">
            <el-input v-model="formData.max_retries" placeholder="请输入最大重试次数" />
          </el-form-item>
          <el-form-item label="失败时是否跳过" prop="skip_on_failure" :required="false">
            <el-input v-model="formData.skip_on_failure" placeholder="请输入失败时是否跳过" />
          </el-form-item>
          <el-form-item label="条件评估器类型(bool/cel/function)" prop="evaluator_type" :required="false">
            <el-input v-model="formData.evaluator_type" placeholder="请输入条件评估器类型(bool/cel/function)" />
          </el-form-item>
          <el-form-item label="条件评估器值" prop="evaluator_value" :required="false">
            <el-input v-model="formData.evaluator_value" placeholder="请输入条件评估器值" />
          </el-form-item>
          <el-form-item label="分支标记(if/else)" prop="branch" :required="false">
            <el-input v-model="formData.branch" placeholder="请输入分支标记(if/else)" />
          </el-form-item>
          <el-form-item label="循环最大迭代次数" prop="max_iterations" :required="false">
            <el-input v-model="formData.max_iterations" placeholder="请输入循环最大迭代次数" />
          </el-form-item>
          <el-form-item label="循环终止条件类型" prop="end_condition_type" :required="false">
            <el-input v-model="formData.end_condition_type" placeholder="请输入循环终止条件类型" />
          </el-form-item>
          <el-form-item label="循环终止条件值" prop="end_condition_value" :required="false">
            <el-input v-model="formData.end_condition_value" placeholder="请输入循环终止条件值" />
          </el-form-item>
          <el-form-item label="是否传递迭代输出" prop="forward_iteration_output" :required="false">
            <el-input v-model="formData.forward_iteration_output" placeholder="请输入是否传递迭代输出" />
          </el-form-item>
          <el-form-item label="路由选择器类型" prop="selector_type" :required="false">
            <el-input v-model="formData.selector_type" placeholder="请输入路由选择器类型" />
          </el-form-item>
          <el-form-item label="路由选择器值" prop="selector_value" :required="false">
            <el-input v-model="formData.selector_value" placeholder="请输入路由选择器值" />
          </el-form-item>
          <el-form-item label="是否允许多路由选择" prop="allow_multiple_selections" :required="false">
            <el-input v-model="formData.allow_multiple_selections" placeholder="请输入是否允许多路由选择" />
          </el-form-item>
          <el-form-item label="是否需要用户确认" prop="requires_confirmation" :required="false">
            <el-input v-model="formData.requires_confirmation" placeholder="请输入是否需要用户确认" />
          </el-form-item>
          <el-form-item label="确认提示消息" prop="confirmation_message" :required="false">
            <el-input v-model="formData.confirmation_message" placeholder="请输入确认提示消息" />
          </el-form-item>
          <el-form-item label="是否需要用户输入" prop="requires_user_input" :required="false">
            <el-input v-model="formData.requires_user_input" placeholder="请输入是否需要用户输入" />
          </el-form-item>
          <el-form-item label="用户输入提示消息" prop="user_input_message" :required="false">
            <el-input v-model="formData.user_input_message" placeholder="请输入用户输入提示消息" />
          </el-form-item>
          <el-form-item label="用户输入结构体Schema" prop="user_input_schema" :required="false">
            <el-input v-model="formData.user_input_schema" placeholder="请输入用户输入结构体Schema" />
          </el-form-item>
          <el-form-item label="用户拒绝时处理策略(skip/abort)" prop="on_reject" :required="false">
            <el-input v-model="formData.on_reject" placeholder="请输入用户拒绝时处理策略(skip/abort)" />
          </el-form-item>
          <el-form-item label="节点出错时处理策略(skip/abort)" prop="on_error" :required="false">
            <el-input v-model="formData.on_error" placeholder="请输入节点出错时处理策略(skip/abort)" />
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
import AgWorkflowNodeAPI, {
  AgWorkflowNodePageQuery,
  AgWorkflowNodeTable,
  AgWorkflowNodeForm,
} from "@/api/module_agno_manage/workflow_nodes";

const visible = ref(false);
const queryFormRef = ref();
const dataFormRef = ref();
const total = ref(0);
const selectIds = ref<number[]>([]);
const selectionRows = ref<AgWorkflowNodeTable[]>([]);
const loading = ref(false);
const isExpand = ref(false);
const isExpandable = ref(true);

// 分页表单
const pageTableData = ref<AgWorkflowNodeTable[]>([]);

// 表格列配置
const tableColumns = ref([
  { prop: "selection", label: "选择框", show: true },
  { prop: "index", label: "序号", show: true },
  { prop: "workflow_id", label: "所属工作流ID", show: true },
  { prop: "parent_node_id", label: "父节点ID（NULL为顶层节点）", show: true },
  { prop: "node_order", label: "节点顺序", show: true },
  { prop: "node_type", label: "节点类型(step/condition/loop/parallel/router)", show: true },
  { prop: "name", label: "节点名称", show: true },
  { prop: "executor_type", label: "执行器类型(agent/team/custom)", show: true },
  { prop: "agent_id", label: "联AgentID（executor_type=agent时）", show: true },
  { prop: "team_id", label: "关联TeamID（executor_type=team时）", show: true },
  { prop: "executor_module", label: "自定义执行器模块路径（executor_type=custom时）", show: true },
  { prop: "add_workflow_history", label: "是否传入工作流历史", show: true },
  { prop: "num_history_runs", label: "传入历史运行次数", show: true },
  { prop: "strict_input_validation", label: "是否严格校验输入", show: true },
  { prop: "max_retries", label: "最大重试次数", show: true },
  { prop: "skip_on_failure", label: "失败时是否跳过", show: true },
  { prop: "evaluator_type", label: "条件评估器类型(bool/cel/function)", show: true },
  { prop: "evaluator_value", label: "条件评估器值", show: true },
  { prop: "branch", label: "分支标记(if/else)", show: true },
  { prop: "max_iterations", label: "循环最大迭代次数", show: true },
  { prop: "end_condition_type", label: "循环终止条件类型", show: true },
  { prop: "end_condition_value", label: "循环终止条件值", show: true },
  { prop: "forward_iteration_output", label: "是否传递迭代输出", show: true },
  { prop: "selector_type", label: "路由选择器类型", show: true },
  { prop: "selector_value", label: "路由选择器值", show: true },
  { prop: "allow_multiple_selections", label: "是否允许多路由选择", show: true },
  { prop: "requires_confirmation", label: "是否需要用户确认（HITL）", show: true },
  { prop: "confirmation_message", label: "确认提示消息", show: true },
  { prop: "requires_user_input", label: "是否需要用户输入（HITL）", show: true },
  { prop: "user_input_message", label: "用户输入提示消息", show: true },
  { prop: "user_input_schema", label: "用户输入结构体Schema", show: true },
  { prop: "on_reject", label: "用户拒绝时处理策略(skip/abort)", show: true },
  { prop: "on_error", label: "节点出错时处理策略(skip/abort)", show: true },
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
  { prop: "workflow_id", label: "所属工作流ID" },
  { prop: "parent_node_id", label: "父节点ID（NULL为顶层节点）" },
  { prop: "node_order", label: "节点顺序" },
  { prop: "node_type", label: "节点类型(step/condition/loop/parallel/router)" },
  { prop: "name", label: "节点名称" },
  { prop: "executor_type", label: "执行器类型(agent/team/custom)" },
  { prop: "agent_id", label: "联AgentID（executor_type=agent时）" },
  { prop: "team_id", label: "关联TeamID（executor_type=team时）" },
  { prop: "executor_module", label: "自定义执行器模块路径（executor_type=custom时）" },
  { prop: "add_workflow_history", label: "是否传入工作流历史" },
  { prop: "num_history_runs", label: "传入历史运行次数" },
  { prop: "strict_input_validation", label: "是否严格校验输入" },
  { prop: "max_retries", label: "最大重试次数" },
  { prop: "skip_on_failure", label: "失败时是否跳过" },
  { prop: "evaluator_type", label: "条件评估器类型(bool/cel/function)" },
  { prop: "evaluator_value", label: "条件评估器值" },
  { prop: "branch", label: "分支标记(if/else)" },
  { prop: "max_iterations", label: "循环最大迭代次数" },
  { prop: "end_condition_type", label: "循环终止条件类型" },
  { prop: "end_condition_value", label: "循环终止条件值" },
  { prop: "forward_iteration_output", label: "是否传递迭代输出" },
  { prop: "selector_type", label: "路由选择器类型" },
  { prop: "selector_value", label: "路由选择器值" },
  { prop: "allow_multiple_selections", label: "是否允许多路由选择" },
  { prop: "requires_confirmation", label: "是否需要用户确认（HITL）" },
  { prop: "confirmation_message", label: "确认提示消息" },
  { prop: "requires_user_input", label: "是否需要用户输入（HITL）" },
  { prop: "user_input_message", label: "用户输入提示消息" },
  { prop: "user_input_schema", label: "用户输入结构体Schema" },
  { prop: "on_reject", label: "用户拒绝时处理策略(skip/abort)" },
  { prop: "on_error", label: "节点出错时处理策略(skip/abort)" },
  { prop: "status", label: "status" },
  { prop: "description", label: "description" },
  { prop: "created_time", label: "created_time" },
  { prop: "updated_time", label: "updated_time" },
  { prop: "created_id", label: "created_id" },
  { prop: "updated_id", label: "updated_id" },
];

// 导入/导出配置
const curdContentConfig = {
  permPrefix: "module_agno_manage:workflow_nodes",
  cols: exportColumns as any,
  importTemplate: () => AgWorkflowNodeAPI.downloadTemplateAgWorkflowNode(),
  exportsAction: async (params: any) => {
    const query: any = { ...params };
    query.status = "0";
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

// 详情表单
const detailFormData = ref<AgWorkflowNodeTable>({});
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
const queryFormData = reactive<AgWorkflowNodePageQuery>({
  page_no: 1,
  page_size: 10,
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
  status: undefined,
  created_time: undefined,
  updated_time: undefined,
  created_id: undefined,
  updated_id: undefined,
});

// 编辑表单
const formData = reactive<AgWorkflowNodeForm>({
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
  workflow_id: [{ required: false, message: "请输入所属工作流ID", trigger: "blur" }],
  parent_node_id: [{ required: true, message: "请输入父节点ID（NULL为顶层节点）", trigger: "blur" }],
  node_order: [{ required: false, message: "请输入节点顺序", trigger: "blur" }],
  node_type: [{ required: false, message: "请输入节点类型(step/condition/loop/parallel/router)", trigger: "blur" }],
  name: [{ required: true, message: "请输入节点名称", trigger: "blur" }],
  executor_type: [{ required: true, message: "请输入执行器类型(agent/team/custom)", trigger: "blur" }],
  agent_id: [{ required: true, message: "请输入联AgentID（executor_type=agent时）", trigger: "blur" }],
  team_id: [{ required: true, message: "请输入关联TeamID（executor_type=team时）", trigger: "blur" }],
  executor_module: [{ required: true, message: "请输入自定义执行器模块路径（executor_type=custom时）", trigger: "blur" }],
  add_workflow_history: [{ required: true, message: "请输入是否传入工作流历史", trigger: "blur" }],
  num_history_runs: [{ required: true, message: "请输入传入历史运行次数", trigger: "blur" }],
  strict_input_validation: [{ required: false, message: "请输入是否严格校验输入", trigger: "blur" }],
  max_retries: [{ required: false, message: "请输入最大重试次数", trigger: "blur" }],
  skip_on_failure: [{ required: false, message: "请输入失败时是否跳过", trigger: "blur" }],
  evaluator_type: [{ required: true, message: "请输入条件评估器类型(bool/cel/function)", trigger: "blur" }],
  evaluator_value: [{ required: true, message: "请输入条件评估器值", trigger: "blur" }],
  branch: [{ required: true, message: "请输入分支标记(if/else)", trigger: "blur" }],
  max_iterations: [{ required: true, message: "请输入循环最大迭代次数", trigger: "blur" }],
  end_condition_type: [{ required: true, message: "请输入循环终止条件类型", trigger: "blur" }],
  end_condition_value: [{ required: true, message: "请输入循环终止条件值", trigger: "blur" }],
  forward_iteration_output: [{ required: false, message: "请输入是否传递迭代输出", trigger: "blur" }],
  selector_type: [{ required: true, message: "请输入路由选择器类型", trigger: "blur" }],
  selector_value: [{ required: true, message: "请输入路由选择器值", trigger: "blur" }],
  allow_multiple_selections: [{ required: false, message: "请输入是否允许多路由选择", trigger: "blur" }],
  requires_confirmation: [{ required: false, message: "请输入是否需要用户确认（HITL）", trigger: "blur" }],
  confirmation_message: [{ required: true, message: "请输入确认提示消息", trigger: "blur" }],
  requires_user_input: [{ required: false, message: "请输入是否需要用户输入（HITL）", trigger: "blur" }],
  user_input_message: [{ required: true, message: "请输入用户输入提示消息", trigger: "blur" }],
  user_input_schema: [{ required: true, message: "请输入用户输入结构体Schema", trigger: "blur" }],
  on_reject: [{ required: false, message: "请输入用户拒绝时处理策略(skip/abort)", trigger: "blur" }],
  on_error: [{ required: false, message: "请输入节点出错时处理策略(skip/abort)", trigger: "blur" }],
  status: [{ required: false, message: "请输入status", trigger: "blur" }],
  description: [{ required: false, message: "请输入description", trigger: "blur" }],
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
    const response = await AgWorkflowNodeAPI.listAgWorkflowNode(queryFormData);
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
    const response = await AgWorkflowNodeAPI.detailAgWorkflowNode(id);
    if (type === "detail") {
      dialogVisible.title = "详情";
      Object.assign(detailFormData.value, response.data.data);
    } else if (type === "update") {
      dialogVisible.title = "修改";
      Object.assign(formData, response.data.data);
    }
  } else {
    dialogVisible.title = "新增AgWorkflowNode";
    formData.id = undefined;
    formData.workflow_id = undefined;
    formData.parent_node_id = undefined;
    formData.node_order = undefined;
    formData.node_type = undefined;
    formData.name = undefined;
    formData.executor_type = undefined;
    formData.agent_id = undefined;
    formData.team_id = undefined;
    formData.executor_module = undefined;
    formData.add_workflow_history = undefined;
    formData.num_history_runs = undefined;
    formData.strict_input_validation = undefined;
    formData.max_retries = undefined;
    formData.skip_on_failure = undefined;
    formData.evaluator_type = undefined;
    formData.evaluator_value = undefined;
    formData.branch = undefined;
    formData.max_iterations = undefined;
    formData.end_condition_type = undefined;
    formData.end_condition_value = undefined;
    formData.forward_iteration_output = undefined;
    formData.selector_type = undefined;
    formData.selector_value = undefined;
    formData.allow_multiple_selections = undefined;
    formData.requires_confirmation = undefined;
    formData.confirmation_message = undefined;
    formData.requires_user_input = undefined;
    formData.user_input_message = undefined;
    formData.user_input_schema = undefined;
    formData.on_reject = undefined;
    formData.on_error = undefined;
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
          await AgWorkflowNodeAPI.updateAgWorkflowNode(id, { id, ...submitData });
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
          await AgWorkflowNodeAPI.createAgWorkflowNode(submitData);
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

// 处理上传
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
  // 预加载字典数据
  if (dictTypes.length > 0) {
    await dictStore.getDict(dictTypes);
  }
  loadingData();
});
</script>

<style lang="scss" scoped></style>
