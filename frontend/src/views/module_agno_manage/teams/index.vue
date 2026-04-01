<!-- Team管理 -->
<template>
  <div class="app-container">
    <!-- 内容区域 -->
    <el-card class="data-table">
      <template #header>
        <div class="card-header">
          <span>
            Team管理列表
            <el-tooltip content="Team管理列表">
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
            <el-form-item label="Team名称" prop="name">
              <el-input v-model="queryFormData.name" placeholder="请输入Team名称" clearable />
            </el-form-item>
            <el-form-item label="主模型ID" prop="model_id">
              <el-input v-model="queryFormData.model_id" placeholder="请输入主模型ID" clearable />
            </el-form-item>
            <el-form-item label="记忆管理器ID" prop="memory_manager_id">
              <el-input v-model="queryFormData.memory_manager_id" placeholder="请输入记忆管理器ID" clearable />
            </el-form-item>
            <el-form-item label="协作模式(route/coordinate/collaborate/tasks)" prop="mode">
              <el-input v-model="queryFormData.mode" placeholder="请输入协作模式(route/coordinate/collaborate/tasks)" clearable />
            </el-form-item>
            <el-form-item label="是否直接响应" prop="respond_directly">
              <el-input v-model="queryFormData.respond_directly" placeholder="请输入是否直接响应" clearable />
            </el-form-item>
            <el-form-item label="是否分发给所有成员" prop="delegate_to_all_members">
              <el-input v-model="queryFormData.delegate_to_all_members" placeholder="请输入是否分发给所有成员" clearable />
            </el-form-item>
            <el-form-item label="是否为成员决定输入内容" prop="determine_input_for_members">
              <el-input v-model="queryFormData.determine_input_for_members" placeholder="请输入是否为成员决定输入内容" clearable />
            </el-form-item>
            <el-form-item label="最大迭代次数" prop="max_iterations">
              <el-input v-model="queryFormData.max_iterations" placeholder="请输入最大迭代次数" clearable />
            </el-form-item>
            <el-form-item label="Team指令" prop="instructions">
              <el-input v-model="queryFormData.instructions" placeholder="请输入Team指令" clearable />
            </el-form-item>
            <el-form-item label="期望输出格式说明" prop="expected_output">
              <el-input v-model="queryFormData.expected_output" placeholder="请输入期望输出格式说明" clearable />
            </el-form-item>
            <el-form-item label="是否输出Markdown格式" prop="markdown">
              <el-input v-model="queryFormData.markdown" placeholder="请输入是否输出Markdown格式" clearable />
            </el-form-item>
            <el-form-item label="是否将Team历史传给成员" prop="add_team_history_to_members">
              <el-input v-model="queryFormData.add_team_history_to_members" placeholder="请输入是否将Team历史传给成员" clearable />
            </el-form-item>
            <el-form-item label="传给成员的历史运行次数" prop="num_team_history_runs">
              <el-input v-model="queryFormData.num_team_history_runs" placeholder="请输入传给成员的历史运行次数" clearable />
            </el-form-item>
            <el-form-item label="是否共享成员交互记录" prop="share_member_interactions">
              <el-input v-model="queryFormData.share_member_interactions" placeholder="请输入是否共享成员交互记录" clearable />
            </el-form-item>
            <el-form-item label="是否将成员工具加入上下文" prop="add_member_tools_to_context">
              <el-input v-model="queryFormData.add_member_tools_to_context" placeholder="请输入是否将成员工具加入上下文" clearable />
            </el-form-item>
            <el-form-item label="是否读取聊天历史" prop="read_chat_history">
              <el-input v-model="queryFormData.read_chat_history" placeholder="请输入是否读取聊天历史" clearable />
            </el-form-item>
            <el-form-item label="是否搜索历史会话" prop="search_past_sessions">
              <el-input v-model="queryFormData.search_past_sessions" placeholder="请输入是否搜索历史会话" clearable />
            </el-form-item>
            <el-form-item label="搜索历史会话数量" prop="num_past_sessions_to_search">
              <el-input v-model="queryFormData.num_past_sessions_to_search" placeholder="请输入搜索历史会话数量" clearable />
            </el-form-item>
            <el-form-item label="是否搜索知识库" prop="search_knowledge">
              <el-input v-model="queryFormData.search_knowledge" placeholder="请输入是否搜索知识库" clearable />
            </el-form-item>
            <el-form-item label="是否允许更新知识库" prop="update_knowledge">
              <el-input v-model="queryFormData.update_knowledge" placeholder="请输入是否允许更新知识库" clearable />
            </el-form-item>
            <el-form-item label="是否开启智能知识过滤" prop="enable_agentic_knowledge_filters">
              <el-input v-model="queryFormData.enable_agentic_knowledge_filters" placeholder="请输入是否开启智能知识过滤" clearable />
            </el-form-item>
            <el-form-item label="是否开启智能状态" prop="enable_agentic_state">
              <el-input v-model="queryFormData.enable_agentic_state" placeholder="请输入是否开启智能状态" clearable />
            </el-form-item>
            <el-form-item label="是否开启智能记忆" prop="enable_agentic_memory">
              <el-input v-model="queryFormData.enable_agentic_memory" placeholder="请输入是否开启智能记忆" clearable />
            </el-form-item>
            <el-form-item label="是否每次运行后更新记忆" prop="update_memory_on_run">
              <el-input v-model="queryFormData.update_memory_on_run" placeholder="请输入是否每次运行后更新记忆" clearable />
            </el-form-item>
            <el-form-item label="是否开启会话摘要" prop="enable_session_summaries">
              <el-input v-model="queryFormData.enable_session_summaries" placeholder="请输入是否开启会话摘要" clearable />
            </el-form-item>
            <el-form-item label="是否将会话摘要加入上下文" prop="add_session_summary_to_context">
              <el-input v-model="queryFormData.add_session_summary_to_context" placeholder="请输入是否将会话摘要加入上下文" clearable />
            </el-form-item>
            <el-form-item label="工具调用次数上限" prop="tool_call_limit">
              <el-input v-model="queryFormData.tool_call_limit" placeholder="请输入工具调用次数上限" clearable />
            </el-form-item>
            <el-form-item label="是否开启流式输出" prop="stream">
              <el-input v-model="queryFormData.stream" placeholder="请输入是否开启流式输出" clearable />
            </el-form-item>
            <el-form-item label="是否流式推送事件" prop="stream_events">
              <el-input v-model="queryFormData.stream_events" placeholder="请输入是否流式推送事件" clearable />
            </el-form-item>
            <el-form-item label="是否开启调试模式" prop="debug_mode">
              <el-input v-model="queryFormData.debug_mode" placeholder="请输入是否开启调试模式" clearable />
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
                v-hasPerm="['module_agno_manage:teams:query']"
                type="primary"
                icon="search"
                @click="handleQuery"
              >
                查询
              </el-button>
              <el-button
                v-hasPerm="['module_agno_manage:teams:query']"
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
                v-hasPerm="['module_agno_manage:teams:create']"
                type="success"
                icon="plus"
                @click="handleOpenDialog('create')"
              >
                新增
              </el-button>
            </el-col>
            <el-col :span="1.5">
              <el-button
                v-hasPerm="['module_agno_manage:teams:delete']"
                type="danger"
                icon="delete"
                :disabled="selectIds.length === 0"
                @click="handleDelete(selectIds)"
              >
                批量删除
              </el-button>
            </el-col>
            <el-col :span="1.5">
              <el-dropdown v-hasPerm="['module_agno_manage:teams:batch']" trigger="click">
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
                  v-hasPerm="['module_agno_manage:teams:import']"
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
                  v-hasPerm="['module_agno_manage:teams:export']"
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
                  v-hasPerm="['module_agno_manage:teams:query']"
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
          label="Team名称"
          prop="name"
          min-width="140"
          show-overflow-tooltip
        />
        <el-table-column
          v-if="tableColumns.find((col) => col.prop === 'model_id')?.show"
          label="主模型ID"
          prop="model_id"
          min-width="140"
          show-overflow-tooltip
        />
        <el-table-column
          v-if="tableColumns.find((col) => col.prop === 'memory_manager_id')?.show"
          label="记忆管理器ID"
          prop="memory_manager_id"
          min-width="140"
          show-overflow-tooltip
        />
        <el-table-column
          v-if="tableColumns.find((col) => col.prop === 'mode')?.show"
          label="协作模式(route/coordinate/collaborate/tasks)"
          prop="mode"
          min-width="140"
          show-overflow-tooltip
        />
        <el-table-column
          v-if="tableColumns.find((col) => col.prop === 'respond_directly')?.show"
          label="是否直接响应"
          prop="respond_directly"
          min-width="140"
          show-overflow-tooltip
        />
        <el-table-column
          v-if="tableColumns.find((col) => col.prop === 'delegate_to_all_members')?.show"
          label="是否分发给所有成员"
          prop="delegate_to_all_members"
          min-width="140"
          show-overflow-tooltip
        />
        <el-table-column
          v-if="tableColumns.find((col) => col.prop === 'determine_input_for_members')?.show"
          label="是否为成员决定输入内容"
          prop="determine_input_for_members"
          min-width="140"
          show-overflow-tooltip
        />
        <el-table-column
          v-if="tableColumns.find((col) => col.prop === 'max_iterations')?.show"
          label="最大迭代次数"
          prop="max_iterations"
          min-width="140"
          show-overflow-tooltip
        />
        <el-table-column
          v-if="tableColumns.find((col) => col.prop === 'instructions')?.show"
          label="Team指令"
          prop="instructions"
          min-width="140"
          show-overflow-tooltip
        />
        <el-table-column
          v-if="tableColumns.find((col) => col.prop === 'expected_output')?.show"
          label="期望输出格式说明"
          prop="expected_output"
          min-width="140"
          show-overflow-tooltip
        />
        <el-table-column
          v-if="tableColumns.find((col) => col.prop === 'markdown')?.show"
          label="是否输出Markdown格式"
          prop="markdown"
          min-width="140"
          show-overflow-tooltip
        />
        <el-table-column
          v-if="tableColumns.find((col) => col.prop === 'add_team_history_to_members')?.show"
          label="是否将Team历史传给成员"
          prop="add_team_history_to_members"
          min-width="140"
          show-overflow-tooltip
        />
        <el-table-column
          v-if="tableColumns.find((col) => col.prop === 'num_team_history_runs')?.show"
          label="传给成员的历史运行次数"
          prop="num_team_history_runs"
          min-width="140"
          show-overflow-tooltip
        />
        <el-table-column
          v-if="tableColumns.find((col) => col.prop === 'share_member_interactions')?.show"
          label="是否共享成员交互记录"
          prop="share_member_interactions"
          min-width="140"
          show-overflow-tooltip
        />
        <el-table-column
          v-if="tableColumns.find((col) => col.prop === 'add_member_tools_to_context')?.show"
          label="是否将成员工具加入上下文"
          prop="add_member_tools_to_context"
          min-width="140"
          show-overflow-tooltip
        />
        <el-table-column
          v-if="tableColumns.find((col) => col.prop === 'read_chat_history')?.show"
          label="是否读取聊天历史"
          prop="read_chat_history"
          min-width="140"
          show-overflow-tooltip
        />
        <el-table-column
          v-if="tableColumns.find((col) => col.prop === 'search_past_sessions')?.show"
          label="是否搜索历史会话"
          prop="search_past_sessions"
          min-width="140"
          show-overflow-tooltip
        />
        <el-table-column
          v-if="tableColumns.find((col) => col.prop === 'num_past_sessions_to_search')?.show"
          label="搜索历史会话数量"
          prop="num_past_sessions_to_search"
          min-width="140"
          show-overflow-tooltip
        />
        <el-table-column
          v-if="tableColumns.find((col) => col.prop === 'search_knowledge')?.show"
          label="是否搜索知识库"
          prop="search_knowledge"
          min-width="140"
          show-overflow-tooltip
        />
        <el-table-column
          v-if="tableColumns.find((col) => col.prop === 'update_knowledge')?.show"
          label="是否允许更新知识库"
          prop="update_knowledge"
          min-width="140"
          show-overflow-tooltip
        />
        <el-table-column
          v-if="tableColumns.find((col) => col.prop === 'enable_agentic_knowledge_filters')?.show"
          label="是否开启智能知识过滤"
          prop="enable_agentic_knowledge_filters"
          min-width="140"
          show-overflow-tooltip
        />
        <el-table-column
          v-if="tableColumns.find((col) => col.prop === 'enable_agentic_state')?.show"
          label="是否开启智能状态"
          prop="enable_agentic_state"
          min-width="140"
          show-overflow-tooltip
        />
        <el-table-column
          v-if="tableColumns.find((col) => col.prop === 'enable_agentic_memory')?.show"
          label="是否开启智能记忆"
          prop="enable_agentic_memory"
          min-width="140"
          show-overflow-tooltip
        />
        <el-table-column
          v-if="tableColumns.find((col) => col.prop === 'update_memory_on_run')?.show"
          label="是否每次运行后更新记忆"
          prop="update_memory_on_run"
          min-width="140"
          show-overflow-tooltip
        />
        <el-table-column
          v-if="tableColumns.find((col) => col.prop === 'enable_session_summaries')?.show"
          label="是否开启会话摘要"
          prop="enable_session_summaries"
          min-width="140"
          show-overflow-tooltip
        />
        <el-table-column
          v-if="tableColumns.find((col) => col.prop === 'add_session_summary_to_context')?.show"
          label="是否将会话摘要加入上下文"
          prop="add_session_summary_to_context"
          min-width="140"
          show-overflow-tooltip
        />
        <el-table-column
          v-if="tableColumns.find((col) => col.prop === 'tool_call_limit')?.show"
          label="工具调用次数上限"
          prop="tool_call_limit"
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
          v-if="tableColumns.find((col) => col.prop === 'debug_mode')?.show"
          label="是否开启调试模式"
          prop="debug_mode"
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
              v-hasPerm="['module_agno_manage:teams:detail']"
              type="info"
              size="small"
              link
              icon="document"
              @click="handleOpenDialog('detail', scope.row.id)"
            >
              详情
            </el-button>
            <el-button
              v-hasPerm="['module_agno_manage:teams:update']"
              type="primary"
              size="small"
              link
              icon="edit"
              @click="handleOpenDialog('update', scope.row.id)"
            >
              编辑
            </el-button>
            <el-button
              v-hasPerm="['module_agno_manage:teams:delete']"
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
          <el-descriptions-item label="Team名称" :span="2">
            {{ detailFormData.name }}
          </el-descriptions-item>
          <el-descriptions-item label="主模型ID" :span="2">
            {{ detailFormData.model_id }}
          </el-descriptions-item>
          <el-descriptions-item label="记忆管理器ID" :span="2">
            {{ detailFormData.memory_manager_id }}
          </el-descriptions-item>
          <el-descriptions-item label="协作模式(route/coordinate/collaborate/tasks)" :span="2">
            {{ detailFormData.mode }}
          </el-descriptions-item>
          <el-descriptions-item label="是否直接响应" :span="2">
            {{ detailFormData.respond_directly }}
          </el-descriptions-item>
          <el-descriptions-item label="是否分发给所有成员" :span="2">
            {{ detailFormData.delegate_to_all_members }}
          </el-descriptions-item>
          <el-descriptions-item label="是否为成员决定输入内容" :span="2">
            {{ detailFormData.determine_input_for_members }}
          </el-descriptions-item>
          <el-descriptions-item label="最大迭代次数" :span="2">
            {{ detailFormData.max_iterations }}
          </el-descriptions-item>
          <el-descriptions-item label="Team指令" :span="2">
            {{ detailFormData.instructions }}
          </el-descriptions-item>
          <el-descriptions-item label="期望输出格式说明" :span="2">
            {{ detailFormData.expected_output }}
          </el-descriptions-item>
          <el-descriptions-item label="是否输出Markdown格式" :span="2">
            {{ detailFormData.markdown }}
          </el-descriptions-item>
          <el-descriptions-item label="是否将Team历史传给成员" :span="2">
            {{ detailFormData.add_team_history_to_members }}
          </el-descriptions-item>
          <el-descriptions-item label="传给成员的历史运行次数" :span="2">
            {{ detailFormData.num_team_history_runs }}
          </el-descriptions-item>
          <el-descriptions-item label="是否共享成员交互记录" :span="2">
            {{ detailFormData.share_member_interactions }}
          </el-descriptions-item>
          <el-descriptions-item label="是否将成员工具加入上下文" :span="2">
            {{ detailFormData.add_member_tools_to_context }}
          </el-descriptions-item>
          <el-descriptions-item label="是否读取聊天历史" :span="2">
            {{ detailFormData.read_chat_history }}
          </el-descriptions-item>
          <el-descriptions-item label="是否搜索历史会话" :span="2">
            {{ detailFormData.search_past_sessions }}
          </el-descriptions-item>
          <el-descriptions-item label="搜索历史会话数量" :span="2">
            {{ detailFormData.num_past_sessions_to_search }}
          </el-descriptions-item>
          <el-descriptions-item label="是否搜索知识库" :span="2">
            {{ detailFormData.search_knowledge }}
          </el-descriptions-item>
          <el-descriptions-item label="是否允许更新知识库" :span="2">
            {{ detailFormData.update_knowledge }}
          </el-descriptions-item>
          <el-descriptions-item label="是否开启智能知识过滤" :span="2">
            {{ detailFormData.enable_agentic_knowledge_filters }}
          </el-descriptions-item>
          <el-descriptions-item label="是否开启智能状态" :span="2">
            {{ detailFormData.enable_agentic_state }}
          </el-descriptions-item>
          <el-descriptions-item label="是否开启智能记忆" :span="2">
            {{ detailFormData.enable_agentic_memory }}
          </el-descriptions-item>
          <el-descriptions-item label="是否每次运行后更新记忆" :span="2">
            {{ detailFormData.update_memory_on_run }}
          </el-descriptions-item>
          <el-descriptions-item label="是否开启会话摘要" :span="2">
            {{ detailFormData.enable_session_summaries }}
          </el-descriptions-item>
          <el-descriptions-item label="是否将会话摘要加入上下文" :span="2">
            {{ detailFormData.add_session_summary_to_context }}
          </el-descriptions-item>
          <el-descriptions-item label="工具调用次数上限" :span="2">
            {{ detailFormData.tool_call_limit }}
          </el-descriptions-item>
          <el-descriptions-item label="是否开启流式输出" :span="2">
            {{ detailFormData.stream }}
          </el-descriptions-item>
          <el-descriptions-item label="是否流式推送事件" :span="2">
            {{ detailFormData.stream_events }}
          </el-descriptions-item>
          <el-descriptions-item label="是否开启调试模式" :span="2">
            {{ detailFormData.debug_mode }}
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
          <el-form-item label="Team名称" prop="name" :required="false">
            <el-input v-model="formData.name" placeholder="请输入Team名称" />
          </el-form-item>
          <el-form-item label="主模型ID" prop="model_id" :required="false">
            <el-input v-model="formData.model_id" placeholder="请输入主模型ID" />
          </el-form-item>
          <el-form-item label="记忆管理器ID" prop="memory_manager_id" :required="false">
            <el-input v-model="formData.memory_manager_id" placeholder="请输入记忆管理器ID" />
          </el-form-item>
          <el-form-item label="协作模式(route/coordinate/collaborate/tasks)" prop="mode" :required="false">
            <el-input v-model="formData.mode" placeholder="请输入协作模式(route/coordinate/collaborate/tasks)" />
          </el-form-item>
          <el-form-item label="是否直接响应" prop="respond_directly" :required="false">
            <el-input v-model="formData.respond_directly" placeholder="请输入是否直接响应" />
          </el-form-item>
          <el-form-item label="是否分发给所有成员" prop="delegate_to_all_members" :required="false">
            <el-input v-model="formData.delegate_to_all_members" placeholder="请输入是否分发给所有成员" />
          </el-form-item>
          <el-form-item label="是否为成员决定输入内容" prop="determine_input_for_members" :required="false">
            <el-input v-model="formData.determine_input_for_members" placeholder="请输入是否为成员决定输入内容" />
          </el-form-item>
          <el-form-item label="最大迭代次数" prop="max_iterations" :required="false">
            <el-input v-model="formData.max_iterations" placeholder="请输入最大迭代次数" />
          </el-form-item>
          <el-form-item label="Team指令" prop="instructions" :required="false">
            <el-input v-model="formData.instructions" placeholder="请输入Team指令" />
          </el-form-item>
          <el-form-item label="期望输出格式说明" prop="expected_output" :required="false">
            <el-input v-model="formData.expected_output" placeholder="请输入期望输出格式说明" />
          </el-form-item>
          <el-form-item label="是否输出Markdown格式" prop="markdown" :required="false">
            <el-input v-model="formData.markdown" placeholder="请输入是否输出Markdown格式" />
          </el-form-item>
          <el-form-item label="是否将Team历史传给成员" prop="add_team_history_to_members" :required="false">
            <el-input v-model="formData.add_team_history_to_members" placeholder="请输入是否将Team历史传给成员" />
          </el-form-item>
          <el-form-item label="传给成员的历史运行次数" prop="num_team_history_runs" :required="false">
            <el-input v-model="formData.num_team_history_runs" placeholder="请输入传给成员的历史运行次数" />
          </el-form-item>
          <el-form-item label="是否共享成员交互记录" prop="share_member_interactions" :required="false">
            <el-input v-model="formData.share_member_interactions" placeholder="请输入是否共享成员交互记录" />
          </el-form-item>
          <el-form-item label="是否将成员工具加入上下文" prop="add_member_tools_to_context" :required="false">
            <el-input v-model="formData.add_member_tools_to_context" placeholder="请输入是否将成员工具加入上下文" />
          </el-form-item>
          <el-form-item label="是否读取聊天历史" prop="read_chat_history" :required="false">
            <el-input v-model="formData.read_chat_history" placeholder="请输入是否读取聊天历史" />
          </el-form-item>
          <el-form-item label="是否搜索历史会话" prop="search_past_sessions" :required="false">
            <el-input v-model="formData.search_past_sessions" placeholder="请输入是否搜索历史会话" />
          </el-form-item>
          <el-form-item label="搜索历史会话数量" prop="num_past_sessions_to_search" :required="false">
            <el-input v-model="formData.num_past_sessions_to_search" placeholder="请输入搜索历史会话数量" />
          </el-form-item>
          <el-form-item label="是否搜索知识库" prop="search_knowledge" :required="false">
            <el-input v-model="formData.search_knowledge" placeholder="请输入是否搜索知识库" />
          </el-form-item>
          <el-form-item label="是否允许更新知识库" prop="update_knowledge" :required="false">
            <el-input v-model="formData.update_knowledge" placeholder="请输入是否允许更新知识库" />
          </el-form-item>
          <el-form-item label="是否开启智能知识过滤" prop="enable_agentic_knowledge_filters" :required="false">
            <el-input v-model="formData.enable_agentic_knowledge_filters" placeholder="请输入是否开启智能知识过滤" />
          </el-form-item>
          <el-form-item label="是否开启智能状态" prop="enable_agentic_state" :required="false">
            <el-input v-model="formData.enable_agentic_state" placeholder="请输入是否开启智能状态" />
          </el-form-item>
          <el-form-item label="是否开启智能记忆" prop="enable_agentic_memory" :required="false">
            <el-input v-model="formData.enable_agentic_memory" placeholder="请输入是否开启智能记忆" />
          </el-form-item>
          <el-form-item label="是否每次运行后更新记忆" prop="update_memory_on_run" :required="false">
            <el-input v-model="formData.update_memory_on_run" placeholder="请输入是否每次运行后更新记忆" />
          </el-form-item>
          <el-form-item label="是否开启会话摘要" prop="enable_session_summaries" :required="false">
            <el-input v-model="formData.enable_session_summaries" placeholder="请输入是否开启会话摘要" />
          </el-form-item>
          <el-form-item label="是否将会话摘要加入上下文" prop="add_session_summary_to_context" :required="false">
            <el-input v-model="formData.add_session_summary_to_context" placeholder="请输入是否将会话摘要加入上下文" />
          </el-form-item>
          <el-form-item label="工具调用次数上限" prop="tool_call_limit" :required="false">
            <el-input v-model="formData.tool_call_limit" placeholder="请输入工具调用次数上限" />
          </el-form-item>
          <el-form-item label="是否开启流式输出" prop="stream" :required="false">
            <el-input v-model="formData.stream" placeholder="请输入是否开启流式输出" />
          </el-form-item>
          <el-form-item label="是否流式推送事件" prop="stream_events" :required="false">
            <el-input v-model="formData.stream_events" placeholder="请输入是否流式推送事件" />
          </el-form-item>
          <el-form-item label="是否开启调试模式" prop="debug_mode" :required="false">
            <el-input v-model="formData.debug_mode" placeholder="请输入是否开启调试模式" />
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
  name: "AgTeam",
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
import AgTeamAPI, {
  AgTeamPageQuery,
  AgTeamTable,
  AgTeamForm,
} from "@/api/module_agno_manage/teams";

const visible = ref(true);
const queryFormRef = ref();
const dataFormRef = ref();
const total = ref(0);
const selectIds = ref<number[]>([]);
const selectionRows = ref<AgTeamTable[]>([]);
const loading = ref(false);
const isExpand = ref(false);
const isExpandable = ref(true);

// 分页表单
const pageTableData = ref<AgTeamTable[]>([]);

// 表格列配置
const tableColumns = ref([
  { prop: "selection", label: "选择框", show: true },
  { prop: "index", label: "序号", show: true },
  { prop: "name", label: "Team名称", show: true },
  { prop: "model_id", label: "主模型ID", show: true },
  { prop: "memory_manager_id", label: "记忆管理器ID", show: true },
  { prop: "mode", label: "协作模式(route/coordinate/collaborate/tasks)", show: true },
  { prop: "respond_directly", label: "是否直接响应（不经过协调）", show: true },
  { prop: "delegate_to_all_members", label: "是否分发给所有成员", show: true },
  { prop: "determine_input_for_members", label: "是否为成员决定输入内容", show: true },
  { prop: "max_iterations", label: "最大迭代次数", show: true },
  { prop: "instructions", label: "Team指令", show: true },
  { prop: "expected_output", label: "期望输出格式说明", show: true },
  { prop: "markdown", label: "是否输出Markdown格式", show: true },
  { prop: "add_team_history_to_members", label: "是否将Team历史传给成员", show: true },
  { prop: "num_team_history_runs", label: "传给成员的历史运行次数", show: true },
  { prop: "share_member_interactions", label: "是否共享成员交互记录", show: true },
  { prop: "add_member_tools_to_context", label: "是否将成员工具加入上下文", show: true },
  { prop: "read_chat_history", label: "是否读取聊天历史", show: true },
  { prop: "search_past_sessions", label: "是否搜索历史会话", show: true },
  { prop: "num_past_sessions_to_search", label: "搜索历史会话数量", show: true },
  { prop: "search_knowledge", label: "是否搜索知识库", show: true },
  { prop: "update_knowledge", label: "是否允许更新知识库", show: true },
  { prop: "enable_agentic_knowledge_filters", label: "是否开启智能知识过滤", show: true },
  { prop: "enable_agentic_state", label: "是否开启智能状态", show: true },
  { prop: "enable_agentic_memory", label: "是否开启智能记忆", show: true },
  { prop: "update_memory_on_run", label: "是否每次运行后更新记忆", show: true },
  { prop: "enable_session_summaries", label: "是否开启会话摘要", show: true },
  { prop: "add_session_summary_to_context", label: "是否将会话摘要加入上下文", show: true },
  { prop: "tool_call_limit", label: "工具调用次数上限", show: true },
  { prop: "stream", label: "是否开启流式输出", show: true },
  { prop: "stream_events", label: "是否流式推送事件", show: true },
  { prop: "debug_mode", label: "是否开启调试模式", show: true },
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
  { prop: "name", label: "Team名称" },
  { prop: "model_id", label: "主模型ID" },
  { prop: "memory_manager_id", label: "记忆管理器ID" },
  { prop: "mode", label: "协作模式(route/coordinate/collaborate/tasks)" },
  { prop: "respond_directly", label: "是否直接响应（不经过协调）" },
  { prop: "delegate_to_all_members", label: "是否分发给所有成员" },
  { prop: "determine_input_for_members", label: "是否为成员决定输入内容" },
  { prop: "max_iterations", label: "最大迭代次数" },
  { prop: "instructions", label: "Team指令" },
  { prop: "expected_output", label: "期望输出格式说明" },
  { prop: "markdown", label: "是否输出Markdown格式" },
  { prop: "add_team_history_to_members", label: "是否将Team历史传给成员" },
  { prop: "num_team_history_runs", label: "传给成员的历史运行次数" },
  { prop: "share_member_interactions", label: "是否共享成员交互记录" },
  { prop: "add_member_tools_to_context", label: "是否将成员工具加入上下文" },
  { prop: "read_chat_history", label: "是否读取聊天历史" },
  { prop: "search_past_sessions", label: "是否搜索历史会话" },
  { prop: "num_past_sessions_to_search", label: "搜索历史会话数量" },
  { prop: "search_knowledge", label: "是否搜索知识库" },
  { prop: "update_knowledge", label: "是否允许更新知识库" },
  { prop: "enable_agentic_knowledge_filters", label: "是否开启智能知识过滤" },
  { prop: "enable_agentic_state", label: "是否开启智能状态" },
  { prop: "enable_agentic_memory", label: "是否开启智能记忆" },
  { prop: "update_memory_on_run", label: "是否每次运行后更新记忆" },
  { prop: "enable_session_summaries", label: "是否开启会话摘要" },
  { prop: "add_session_summary_to_context", label: "是否将会话摘要加入上下文" },
  { prop: "tool_call_limit", label: "工具调用次数上限" },
  { prop: "stream", label: "是否开启流式输出" },
  { prop: "stream_events", label: "是否流式推送事件" },
  { prop: "debug_mode", label: "是否开启调试模式" },
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
  permPrefix: "module_agno_manage:teams",
  cols: exportColumns as any,
  importTemplate: () => AgTeamAPI.downloadTemplateAgTeam(),
  exportsAction: async (params: any) => {
    const query: any = { ...params };
    query.status = "0";
    query.page_no = 1;
    query.page_size = 9999;
    const all: any[] = [];
    while (true) {
      const res = await AgTeamAPI.listAgTeam(query);
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
const detailFormData = ref<AgTeamTable>({});
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
const queryFormData = reactive<AgTeamPageQuery>({
  page_no: 1,
  page_size: 10,
  name: undefined,
  model_id: undefined,
  memory_manager_id: undefined,
  mode: undefined,
  respond_directly: undefined,
  delegate_to_all_members: undefined,
  determine_input_for_members: undefined,
  max_iterations: undefined,
  instructions: undefined,
  expected_output: undefined,
  markdown: undefined,
  add_team_history_to_members: undefined,
  num_team_history_runs: undefined,
  share_member_interactions: undefined,
  add_member_tools_to_context: undefined,
  read_chat_history: undefined,
  search_past_sessions: undefined,
  num_past_sessions_to_search: undefined,
  search_knowledge: undefined,
  update_knowledge: undefined,
  enable_agentic_knowledge_filters: undefined,
  enable_agentic_state: undefined,
  enable_agentic_memory: undefined,
  update_memory_on_run: undefined,
  enable_session_summaries: undefined,
  add_session_summary_to_context: undefined,
  tool_call_limit: undefined,
  stream: undefined,
  stream_events: undefined,
  debug_mode: undefined,
  metadata: undefined,
  status: undefined,
  created_time: undefined,
  updated_time: undefined,
  created_id: undefined,
  updated_id: undefined,
});

// 编辑表单
const formData = reactive<AgTeamForm>({
  id: undefined,
  name: undefined,
  model_id: undefined,
  memory_manager_id: undefined,
  mode: undefined,
  respond_directly: undefined,
  delegate_to_all_members: undefined,
  determine_input_for_members: undefined,
  max_iterations: undefined,
  instructions: undefined,
  expected_output: undefined,
  markdown: undefined,
  add_team_history_to_members: undefined,
  num_team_history_runs: undefined,
  share_member_interactions: undefined,
  add_member_tools_to_context: undefined,
  read_chat_history: undefined,
  search_past_sessions: undefined,
  num_past_sessions_to_search: undefined,
  search_knowledge: undefined,
  update_knowledge: undefined,
  enable_agentic_knowledge_filters: undefined,
  enable_agentic_state: undefined,
  enable_agentic_memory: undefined,
  update_memory_on_run: undefined,
  enable_session_summaries: undefined,
  add_session_summary_to_context: undefined,
  tool_call_limit: undefined,
  stream: undefined,
  stream_events: undefined,
  debug_mode: undefined,
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
  name: [{ required: false, message: "请输入Team名称", trigger: "blur" }],
  model_id: [{ required: true, message: "请输入主模型ID", trigger: "blur" }],
  memory_manager_id: [{ required: true, message: "请输入记忆管理器ID", trigger: "blur" }],
  mode: [{ required: false, message: "请输入协作模式(route/coordinate/collaborate/tasks)", trigger: "blur" }],
  respond_directly: [{ required: false, message: "请输入是否直接响应（不经过协调）", trigger: "blur" }],
  delegate_to_all_members: [{ required: false, message: "请输入是否分发给所有成员", trigger: "blur" }],
  determine_input_for_members: [{ required: false, message: "请输入是否为成员决定输入内容", trigger: "blur" }],
  max_iterations: [{ required: false, message: "请输入最大迭代次数", trigger: "blur" }],
  instructions: [{ required: true, message: "请输入Team指令", trigger: "blur" }],
  expected_output: [{ required: true, message: "请输入期望输出格式说明", trigger: "blur" }],
  markdown: [{ required: false, message: "请输入是否输出Markdown格式", trigger: "blur" }],
  add_team_history_to_members: [{ required: false, message: "请输入是否将Team历史传给成员", trigger: "blur" }],
  num_team_history_runs: [{ required: false, message: "请输入传给成员的历史运行次数", trigger: "blur" }],
  share_member_interactions: [{ required: false, message: "请输入是否共享成员交互记录", trigger: "blur" }],
  add_member_tools_to_context: [{ required: false, message: "请输入是否将成员工具加入上下文", trigger: "blur" }],
  read_chat_history: [{ required: false, message: "请输入是否读取聊天历史", trigger: "blur" }],
  search_past_sessions: [{ required: false, message: "请输入是否搜索历史会话", trigger: "blur" }],
  num_past_sessions_to_search: [{ required: true, message: "请输入搜索历史会话数量", trigger: "blur" }],
  search_knowledge: [{ required: false, message: "请输入是否搜索知识库", trigger: "blur" }],
  update_knowledge: [{ required: false, message: "请输入是否允许更新知识库", trigger: "blur" }],
  enable_agentic_knowledge_filters: [{ required: false, message: "请输入是否开启智能知识过滤", trigger: "blur" }],
  enable_agentic_state: [{ required: false, message: "请输入是否开启智能状态", trigger: "blur" }],
  enable_agentic_memory: [{ required: false, message: "请输入是否开启智能记忆", trigger: "blur" }],
  update_memory_on_run: [{ required: false, message: "请输入是否每次运行后更新记忆", trigger: "blur" }],
  enable_session_summaries: [{ required: false, message: "请输入是否开启会话摘要", trigger: "blur" }],
  add_session_summary_to_context: [{ required: false, message: "请输入是否将会话摘要加入上下文", trigger: "blur" }],
  tool_call_limit: [{ required: true, message: "请输入工具调用次数上限", trigger: "blur" }],
  stream: [{ required: false, message: "请输入是否开启流式输出", trigger: "blur" }],
  stream_events: [{ required: false, message: "请输入是否流式推送事件", trigger: "blur" }],
  debug_mode: [{ required: false, message: "请输入是否开启调试模式", trigger: "blur" }],
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
    const response = await AgTeamAPI.listAgTeam(queryFormData);
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
const initialFormData: AgTeamForm = {
  id: undefined,
  name: undefined,
  model_id: undefined,
  memory_manager_id: undefined,
  mode: undefined,
  respond_directly: undefined,
  delegate_to_all_members: undefined,
  determine_input_for_members: undefined,
  max_iterations: undefined,
  instructions: undefined,
  expected_output: undefined,
  markdown: undefined,
  add_team_history_to_members: undefined,
  num_team_history_runs: undefined,
  share_member_interactions: undefined,
  add_member_tools_to_context: undefined,
  read_chat_history: undefined,
  search_past_sessions: undefined,
  num_past_sessions_to_search: undefined,
  search_knowledge: undefined,
  update_knowledge: undefined,
  enable_agentic_knowledge_filters: undefined,
  enable_agentic_state: undefined,
  enable_agentic_memory: undefined,
  update_memory_on_run: undefined,
  enable_session_summaries: undefined,
  add_session_summary_to_context: undefined,
  tool_call_limit: undefined,
  stream: undefined,
  stream_events: undefined,
  debug_mode: undefined,
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
    const response = await AgTeamAPI.detailAgTeam(id);
    if (type === "detail") {
      dialogVisible.title = "详情";
      Object.assign(detailFormData.value, response.data.data);
    } else if (type === "update") {
      dialogVisible.title = "修改";
      Object.assign(formData, response.data.data);
    }
  } else {
    dialogVisible.title = "新增AgTeam";
    formData.id = undefined;
    formData.name = undefined;
    formData.model_id = undefined;
    formData.memory_manager_id = undefined;
    formData.mode = undefined;
    formData.respond_directly = undefined;
    formData.delegate_to_all_members = undefined;
    formData.determine_input_for_members = undefined;
    formData.max_iterations = undefined;
    formData.instructions = undefined;
    formData.expected_output = undefined;
    formData.markdown = undefined;
    formData.add_team_history_to_members = undefined;
    formData.num_team_history_runs = undefined;
    formData.share_member_interactions = undefined;
    formData.add_member_tools_to_context = undefined;
    formData.read_chat_history = undefined;
    formData.search_past_sessions = undefined;
    formData.num_past_sessions_to_search = undefined;
    formData.search_knowledge = undefined;
    formData.update_knowledge = undefined;
    formData.enable_agentic_knowledge_filters = undefined;
    formData.enable_agentic_state = undefined;
    formData.enable_agentic_memory = undefined;
    formData.update_memory_on_run = undefined;
    formData.enable_session_summaries = undefined;
    formData.add_session_summary_to_context = undefined;
    formData.tool_call_limit = undefined;
    formData.stream = undefined;
    formData.stream_events = undefined;
    formData.debug_mode = undefined;
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
          await AgTeamAPI.updateAgTeam(id, { id, ...submitData });
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
          await AgTeamAPI.createAgTeam(submitData);
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
        await AgTeamAPI.deleteAgTeam(ids);
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
          await AgTeamAPI.batchAgTeam({ ids: selectIds.value, status });
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
    const response = await AgTeamAPI.importAgTeam(formData);
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
