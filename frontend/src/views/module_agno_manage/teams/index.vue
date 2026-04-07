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
            <el-form-item label="主模型" prop="model_id">
              <LazySelect
                v-model="queryFormData.model_id"
                :fetcher="modelFetcher"
                placeholder="请选择主模型"
                style="width: 200px"
              />
            </el-form-item>
            <el-form-item label="记忆管理器" prop="memory_manager_id">
              <LazySelect
                v-model="queryFormData.memory_manager_id"
                :fetcher="memoryManagerFetcher"
                placeholder="请选择记忆管理器"
                style="width: 200px"
              />
            </el-form-item>
            <el-form-item label="协作模式" prop="mode">
              <el-select v-model="queryFormData.mode" placeholder="请选择协作模式" clearable style="width: 160px">
                <el-option value="route" label="route" />
                <el-option value="coordinate" label="coordinate" />
                <el-option value="collaborate" label="collaborate" />
                <el-option value="tasks" label="tasks" />
              </el-select>
            </el-form-item>
            <el-form-item label="是否直接响应" prop="respond_directly">
              <el-select v-model="queryFormData.respond_directly" placeholder="请选择" style="width: 120px" clearable>
                <el-option :value="'true'" label="是" />
                <el-option :value="'false'" label="否" />
              </el-select>
            </el-form-item>
            <el-form-item label="是否分发给所有成员" prop="delegate_to_all_members">
              <el-select v-model="queryFormData.delegate_to_all_members" placeholder="请选择" style="width: 120px" clearable>
                <el-option :value="'true'" label="是" />
                <el-option :value="'false'" label="否" />
              </el-select>
            </el-form-item>
            <el-form-item label="搜索知识库" prop="search_knowledge">
              <el-select v-model="queryFormData.search_knowledge" placeholder="请选择" style="width: 120px" clearable>
                <el-option :value="'true'" label="是" />
                <el-option :value="'false'" label="否" />
              </el-select>
            </el-form-item>
            <el-form-item label="开启调试模式" prop="debug_mode">
              <el-select v-model="queryFormData.debug_mode" placeholder="请选择" style="width: 120px" clearable>
                <el-option :value="'true'" label="是" />
                <el-option :value="'false'" label="否" />
              </el-select>
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
          label="Team名称"
          prop="name"
          min-width="140"
          show-overflow-tooltip
        />
        <el-table-column
          v-if="tableColumns.find((col) => col.prop === 'model_id')?.show"
          label="主模型"
          prop="model_id"
          min-width="140"
          show-overflow-tooltip
        >
          <template #default="scope">{{ getModelName(scope.row.model_id) }}</template>
        </el-table-column>
        <el-table-column
          v-if="tableColumns.find((col) => col.prop === 'memory_manager_id')?.show"
          label="记忆管理器"
          prop="memory_manager_id"
          min-width="140"
          show-overflow-tooltip
        >
          <template #default="scope">{{ getMemoryManagerName(scope.row.memory_manager_id) }}</template>
        </el-table-column>
        <el-table-column
          v-if="tableColumns.find((col) => col.prop === 'mode')?.show"
          label="协作模式"
          prop="mode"
          min-width="120"
          show-overflow-tooltip
        />
        <el-table-column
          v-if="tableColumns.find((col) => col.prop === 'respond_directly')?.show"
          label="是否直接响应"
          prop="respond_directly"
          min-width="120"
        >
          <template #default="scope">
            <el-tag :type="scope.row.respond_directly === true ? 'success' : scope.row.respond_directly === false ? 'danger' : undefined">
              {{ scope.row.respond_directly === true ? '是' : scope.row.respond_directly === false ? '否' : '默认' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column
          v-if="tableColumns.find((col) => col.prop === 'delegate_to_all_members')?.show"
          label="分发给所有成员"
          prop="delegate_to_all_members"
          min-width="130"
        >
          <template #default="scope">
            <el-tag :type="scope.row.delegate_to_all_members === true ? 'success' : scope.row.delegate_to_all_members === false ? 'danger' : undefined">
              {{ scope.row.delegate_to_all_members === true ? '是' : scope.row.delegate_to_all_members === false ? '否' : '默认' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column
          v-if="tableColumns.find((col) => col.prop === 'determine_input_for_members')?.show"
          label="为成员决定输入"
          prop="determine_input_for_members"
          min-width="130"
        >
          <template #default="scope">
            <el-tag :type="scope.row.determine_input_for_members === true ? 'success' : scope.row.determine_input_for_members === false ? 'danger' : undefined">
              {{ scope.row.determine_input_for_members === true ? '是' : scope.row.determine_input_for_members === false ? '否' : '默认' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column
          v-if="tableColumns.find((col) => col.prop === 'max_iterations')?.show"
          label="最大迭代次数"
          prop="max_iterations"
          min-width="120"
          show-overflow-tooltip
        />
        <el-table-column
          v-if="tableColumns.find((col) => col.prop === 'instructions')?.show"
          label="Team指令"
          prop="instructions"
          min-width="160"
          show-overflow-tooltip
        />
        <el-table-column
          v-if="tableColumns.find((col) => col.prop === 'expected_output')?.show"
          label="期望输出格式"
          prop="expected_output"
          min-width="140"
          show-overflow-tooltip
        />
        <el-table-column
          v-if="tableColumns.find((col) => col.prop === 'markdown')?.show"
          label="输出Markdown"
          prop="markdown"
          min-width="120"
        >
          <template #default="scope">
            <el-tag :type="scope.row.markdown === true ? 'success' : scope.row.markdown === false ? 'danger' : undefined">
              {{ scope.row.markdown === true ? '是' : scope.row.markdown === false ? '否' : '默认' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column
          v-if="tableColumns.find((col) => col.prop === 'add_team_history_to_members')?.show"
          label="传Team历史给成员"
          prop="add_team_history_to_members"
          min-width="140"
        >
          <template #default="scope">
            <el-tag :type="scope.row.add_team_history_to_members === true ? 'success' : scope.row.add_team_history_to_members === false ? 'danger' : undefined">
              {{ scope.row.add_team_history_to_members === true ? '是' : scope.row.add_team_history_to_members === false ? '否' : '默认' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column
          v-if="tableColumns.find((col) => col.prop === 'num_team_history_runs')?.show"
          label="传给成员历史次数"
          prop="num_team_history_runs"
          min-width="140"
          show-overflow-tooltip
        />
        <el-table-column
          v-if="tableColumns.find((col) => col.prop === 'share_member_interactions')?.show"
          label="共享成员交互"
          prop="share_member_interactions"
          min-width="120"
        >
          <template #default="scope">
            <el-tag :type="scope.row.share_member_interactions === true ? 'success' : scope.row.share_member_interactions === false ? 'danger' : undefined">
              {{ scope.row.share_member_interactions === true ? '是' : scope.row.share_member_interactions === false ? '否' : '默认' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column
          v-if="tableColumns.find((col) => col.prop === 'add_member_tools_to_context')?.show"
          label="成员工具加入上下文"
          prop="add_member_tools_to_context"
          min-width="150"
        >
          <template #default="scope">
            <el-tag :type="scope.row.add_member_tools_to_context === true ? 'success' : scope.row.add_member_tools_to_context === false ? 'danger' : undefined">
              {{ scope.row.add_member_tools_to_context === true ? '是' : scope.row.add_member_tools_to_context === false ? '否' : '默认' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column
          v-if="tableColumns.find((col) => col.prop === 'read_chat_history')?.show"
          label="读取聊天历史"
          prop="read_chat_history"
          min-width="120"
        >
          <template #default="scope">
            <el-tag :type="scope.row.read_chat_history === true ? 'success' : scope.row.read_chat_history === false ? 'danger' : undefined">
              {{ scope.row.read_chat_history === true ? '是' : scope.row.read_chat_history === false ? '否' : '默认' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column
          v-if="tableColumns.find((col) => col.prop === 'search_past_sessions')?.show"
          label="搜索历史会话"
          prop="search_past_sessions"
          min-width="120"
        >
          <template #default="scope">
            <el-tag :type="scope.row.search_past_sessions === true ? 'success' : scope.row.search_past_sessions === false ? 'danger' : undefined">
              {{ scope.row.search_past_sessions === true ? '是' : scope.row.search_past_sessions === false ? '否' : '默认' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column
          v-if="tableColumns.find((col) => col.prop === 'num_past_sessions_to_search')?.show"
          label="搜索历史会话数量"
          prop="num_past_sessions_to_search"
          min-width="140"
          show-overflow-tooltip
        />
        <el-table-column
          v-if="tableColumns.find((col) => col.prop === 'search_knowledge')?.show"
          label="搜索知识库"
          prop="search_knowledge"
          min-width="110"
        >
          <template #default="scope">
            <el-tag :type="scope.row.search_knowledge === true ? 'success' : scope.row.search_knowledge === false ? 'danger' : undefined">
              {{ scope.row.search_knowledge === true ? '是' : scope.row.search_knowledge === false ? '否' : '默认' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column
          v-if="tableColumns.find((col) => col.prop === 'update_knowledge')?.show"
          label="允许更新知识库"
          prop="update_knowledge"
          min-width="130"
        >
          <template #default="scope">
            <el-tag :type="scope.row.update_knowledge === true ? 'success' : scope.row.update_knowledge === false ? 'danger' : undefined">
              {{ scope.row.update_knowledge === true ? '是' : scope.row.update_knowledge === false ? '否' : '默认' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column
          v-if="tableColumns.find((col) => col.prop === 'enable_agentic_knowledge_filters')?.show"
          label="智能知识过滤"
          prop="enable_agentic_knowledge_filters"
          min-width="120"
        >
          <template #default="scope">
            <el-tag :type="scope.row.enable_agentic_knowledge_filters === true ? 'success' : scope.row.enable_agentic_knowledge_filters === false ? 'danger' : undefined">
              {{ scope.row.enable_agentic_knowledge_filters === true ? '是' : scope.row.enable_agentic_knowledge_filters === false ? '否' : '默认' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column
          v-if="tableColumns.find((col) => col.prop === 'enable_agentic_state')?.show"
          label="智能状态"
          prop="enable_agentic_state"
          min-width="100"
        >
          <template #default="scope">
            <el-tag :type="scope.row.enable_agentic_state === true ? 'success' : scope.row.enable_agentic_state === false ? 'danger' : undefined">
              {{ scope.row.enable_agentic_state === true ? '是' : scope.row.enable_agentic_state === false ? '否' : '默认' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column
          v-if="tableColumns.find((col) => col.prop === 'enable_agentic_memory')?.show"
          label="智能记忆"
          prop="enable_agentic_memory"
          min-width="100"
        >
          <template #default="scope">
            <el-tag :type="scope.row.enable_agentic_memory === true ? 'success' : scope.row.enable_agentic_memory === false ? 'danger' : undefined">
              {{ scope.row.enable_agentic_memory === true ? '是' : scope.row.enable_agentic_memory === false ? '否' : '默认' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column
          v-if="tableColumns.find((col) => col.prop === 'update_memory_on_run')?.show"
          label="运行后更新记忆"
          prop="update_memory_on_run"
          min-width="130"
        >
          <template #default="scope">
            <el-tag :type="scope.row.update_memory_on_run === true ? 'success' : scope.row.update_memory_on_run === false ? 'danger' : undefined">
              {{ scope.row.update_memory_on_run === true ? '是' : scope.row.update_memory_on_run === false ? '否' : '默认' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column
          v-if="tableColumns.find((col) => col.prop === 'enable_session_summaries')?.show"
          label="开启会话摘要"
          prop="enable_session_summaries"
          min-width="120"
        >
          <template #default="scope">
            <el-tag :type="scope.row.enable_session_summaries === true ? 'success' : scope.row.enable_session_summaries === false ? 'danger' : undefined">
              {{ scope.row.enable_session_summaries === true ? '是' : scope.row.enable_session_summaries === false ? '否' : '默认' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column
          v-if="tableColumns.find((col) => col.prop === 'add_session_summary_to_context')?.show"
          label="摘要加入上下文"
          prop="add_session_summary_to_context"
          min-width="130"
        >
          <template #default="scope">
            <el-tag :type="scope.row.add_session_summary_to_context === true ? 'success' : scope.row.add_session_summary_to_context === false ? 'danger' : undefined">
              {{ scope.row.add_session_summary_to_context === true ? '是' : scope.row.add_session_summary_to_context === false ? '否' : '默认' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column
          v-if="tableColumns.find((col) => col.prop === 'tool_call_limit')?.show"
          label="工具调用次数上限"
          prop="tool_call_limit"
          min-width="140"
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
          label="status"
          prop="status"
          min-width="80"
          show-overflow-tooltip
        />
        <el-table-column
          v-if="tableColumns.find((col) => col.prop === 'status')?.show"
          label="状态"
          prop="status"
          min-width="100"
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
          label="created_id"
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
          label="updated_id"
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
              v-hasPerm="['module_agno_manage:teams:update']"
              type="warning"
              size="small"
              link
              icon="Share"
              @click="handleOpenVisualBuilder(scope.row.id)"
            >
              可视化
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
      width="860px"
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
          <el-descriptions-item label="Team名称" :span="2">
            {{ detailFormData.name }}
          </el-descriptions-item>
          <el-descriptions-item label="主模型" :span="2">
            {{ getModelName(detailFormData.model_id) }}
          </el-descriptions-item>
          <el-descriptions-item label="记忆管理器" :span="2">
            {{ getMemoryManagerName(detailFormData.memory_manager_id) }}
          </el-descriptions-item>
          <el-descriptions-item label="协作模式" :span="2">
            {{ detailFormData.mode }}
          </el-descriptions-item>
          <el-descriptions-item label="是否直接响应" :span="2">
            <el-tag :type="detailFormData.respond_directly === true ? 'success' : detailFormData.respond_directly === false ? 'danger' : undefined">
              {{ detailFormData.respond_directly === true ? '是' : detailFormData.respond_directly === false ? '否' : '默认' }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="分发给所有成员" :span="2">
            <el-tag :type="detailFormData.delegate_to_all_members === true ? 'success' : detailFormData.delegate_to_all_members === false ? 'danger' : undefined">
              {{ detailFormData.delegate_to_all_members === true ? '是' : detailFormData.delegate_to_all_members === false ? '否' : '默认' }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="为成员决定输入" :span="2">
            <el-tag :type="detailFormData.determine_input_for_members === true ? 'success' : detailFormData.determine_input_for_members === false ? 'danger' : undefined">
              {{ detailFormData.determine_input_for_members === true ? '是' : detailFormData.determine_input_for_members === false ? '否' : '默认' }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="最大迭代次数" :span="2">
            {{ detailFormData.max_iterations }}
          </el-descriptions-item>
          <el-descriptions-item label="Team指令" :span="4">
            <pre style="margin: 0; white-space: pre-wrap; font-size: 12px">{{ detailFormData.instructions }}</pre>
          </el-descriptions-item>
          <el-descriptions-item label="期望输出格式" :span="4">
            <pre style="margin: 0; white-space: pre-wrap; font-size: 12px">{{ detailFormData.expected_output }}</pre>
          </el-descriptions-item>
          <el-descriptions-item label="输出Markdown" :span="2">
            <el-tag :type="detailFormData.markdown === true ? 'success' : detailFormData.markdown === false ? 'danger' : undefined">
              {{ detailFormData.markdown === true ? '是' : detailFormData.markdown === false ? '否' : '默认' }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="传Team历史给成员" :span="2">
            <el-tag :type="detailFormData.add_team_history_to_members === true ? 'success' : detailFormData.add_team_history_to_members === false ? 'danger' : undefined">
              {{ detailFormData.add_team_history_to_members === true ? '是' : detailFormData.add_team_history_to_members === false ? '否' : '默认' }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="传给成员历史次数" :span="2">
            {{ detailFormData.num_team_history_runs }}
          </el-descriptions-item>
          <el-descriptions-item label="共享成员交互" :span="2">
            <el-tag :type="detailFormData.share_member_interactions === true ? 'success' : detailFormData.share_member_interactions === false ? 'danger' : undefined">
              {{ detailFormData.share_member_interactions === true ? '是' : detailFormData.share_member_interactions === false ? '否' : '默认' }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="成员工具加入上下文" :span="2">
            <el-tag :type="detailFormData.add_member_tools_to_context === true ? 'success' : detailFormData.add_member_tools_to_context === false ? 'danger' : undefined">
              {{ detailFormData.add_member_tools_to_context === true ? '是' : detailFormData.add_member_tools_to_context === false ? '否' : '默认' }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="读取聊天历史" :span="2">
            <el-tag :type="detailFormData.read_chat_history === true ? 'success' : detailFormData.read_chat_history === false ? 'danger' : undefined">
              {{ detailFormData.read_chat_history === true ? '是' : detailFormData.read_chat_history === false ? '否' : '默认' }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="搜索历史会话" :span="2">
            <el-tag :type="detailFormData.search_past_sessions === true ? 'success' : detailFormData.search_past_sessions === false ? 'danger' : undefined">
              {{ detailFormData.search_past_sessions === true ? '是' : detailFormData.search_past_sessions === false ? '否' : '默认' }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="搜索历史会话数量" :span="2">
            {{ detailFormData.num_past_sessions_to_search }}
          </el-descriptions-item>
          <el-descriptions-item label="搜索知识库" :span="2">
            <el-tag :type="detailFormData.search_knowledge === true ? 'success' : detailFormData.search_knowledge === false ? 'danger' : undefined">
              {{ detailFormData.search_knowledge === true ? '是' : detailFormData.search_knowledge === false ? '否' : '默认' }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="允许更新知识库" :span="2">
            <el-tag :type="detailFormData.update_knowledge === true ? 'success' : detailFormData.update_knowledge === false ? 'danger' : undefined">
              {{ detailFormData.update_knowledge === true ? '是' : detailFormData.update_knowledge === false ? '否' : '默认' }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="智能知识过滤" :span="2">
            <el-tag :type="detailFormData.enable_agentic_knowledge_filters === true ? 'success' : detailFormData.enable_agentic_knowledge_filters === false ? 'danger' : undefined">
              {{ detailFormData.enable_agentic_knowledge_filters === true ? '是' : detailFormData.enable_agentic_knowledge_filters === false ? '否' : '默认' }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="智能状态" :span="2">
            <el-tag :type="detailFormData.enable_agentic_state === true ? 'success' : detailFormData.enable_agentic_state === false ? 'danger' : undefined">
              {{ detailFormData.enable_agentic_state === true ? '是' : detailFormData.enable_agentic_state === false ? '否' : '默认' }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="智能记忆" :span="2">
            <el-tag :type="detailFormData.enable_agentic_memory === true ? 'success' : detailFormData.enable_agentic_memory === false ? 'danger' : undefined">
              {{ detailFormData.enable_agentic_memory === true ? '是' : detailFormData.enable_agentic_memory === false ? '否' : '默认' }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="运行后更新记忆" :span="2">
            <el-tag :type="detailFormData.update_memory_on_run === true ? 'success' : detailFormData.update_memory_on_run === false ? 'danger' : undefined">
              {{ detailFormData.update_memory_on_run === true ? '是' : detailFormData.update_memory_on_run === false ? '否' : '默认' }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="开启会话摘要" :span="2">
            <el-tag :type="detailFormData.enable_session_summaries === true ? 'success' : detailFormData.enable_session_summaries === false ? 'danger' : undefined">
              {{ detailFormData.enable_session_summaries === true ? '是' : detailFormData.enable_session_summaries === false ? '否' : '默认' }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="摘要加入上下文" :span="2">
            <el-tag :type="detailFormData.add_session_summary_to_context === true ? 'success' : detailFormData.add_session_summary_to_context === false ? 'danger' : undefined">
              {{ detailFormData.add_session_summary_to_context === true ? '是' : detailFormData.add_session_summary_to_context === false ? '否' : '默认' }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="工具调用次数上限" :span="2">
            {{ detailFormData.tool_call_limit }}
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
          <el-descriptions-item label="调试模式" :span="2">
            <el-tag :type="detailFormData.debug_mode === true ? 'success' : detailFormData.debug_mode === false ? 'danger' : undefined">
              {{ detailFormData.debug_mode === true ? '是' : detailFormData.debug_mode === false ? '否' : '默认' }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="元数据" :span="4">
            <pre style="margin: 0; white-space: pre-wrap; font-size: 12px">{{ JSON.stringify(detailFormData.metadata_config, null, 2) }}</pre>
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
        <TeamFormFields ref="dataFormRef" :form-data="formData" />
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
import { useRouter } from "vue-router";
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
import AgTeamAPI, {
  AgTeamPageQuery,
  AgTeamTable,
  AgTeamForm,
} from "@/api/module_agno_manage/teams";
import AgModelAPI from "@/api/module_agno_manage/models";
import AgMemoryManagerAPI from "@/api/module_agno_manage/memory_managers";
import LazySelect from "@/views/module_agno_manage/components/LazySelect/index.vue";
import TeamFormFields from "./components/TeamFormFields.vue";

const router = useRouter();

function handleOpenVisualBuilder(id: number) {
  router.push(`/agno/team-builder?root_id=${id}`);
}

// model 懒加载 fetcher
const modelFetcher = async (params: { page_no: number; page_size: number; name?: string }) => {
  const res = await AgModelAPI.listAgModel({ ...params });
  const items = (res.data?.data?.items || []).map((item: any) => ({
    value: String(item.id),
    label: item.name || String(item.id),
    raw: item,
  }));
  return { items, total: res.data?.data?.total || 0 };
};

// memory_manager 懒加载 fetcher
const memoryManagerFetcher = async (params: { page_no: number; page_size: number; name?: string }) => {
  const res = await AgMemoryManagerAPI.listAgMemoryManager({ ...params });
  const items = (res.data?.data?.items || []).map((item: any) => ({
    value: String(item.id),
    label: item.name || String(item.id),
    raw: item,
  }));
  return { items, total: res.data?.data?.total || 0 };
};

// model 名称查找（用于表格/详情，通过独立接口按需获取）
const modelNameCache = ref<Record<string, string>>({});
function getModelName(id?: string | number): string {
  if (!id) return "-";
  const key = String(id);
  if (modelNameCache.value[key]) return modelNameCache.value[key];
  // 异步填充 cache，触发响应式更新
  AgModelAPI.detailAgModel(Number(id))
    .then((res) => {
      const name = res.data?.data?.name || key;
      modelNameCache.value[key] = name;
    })
    .catch(() => {
      modelNameCache.value[key] = key;
    });
  return key; // 首次渲染暂显 id，异步回来后自动刷新
}

// memory_manager 名称查找（按需获取）
const memoryManagerNameCache = ref<Record<string, string>>({});
function getMemoryManagerName(id?: string | number): string {
  if (!id) return "-";
  const key = String(id);
  if (memoryManagerNameCache.value[key]) return memoryManagerNameCache.value[key];
  AgMemoryManagerAPI.detailAgMemoryManager(Number(id))
    .then((res) => {
      const name = res.data?.data?.name || key;
      memoryManagerNameCache.value[key] = name;
    })
    .catch(() => {
      memoryManagerNameCache.value[key] = key;
    });
  return key;
}

const visible = ref(false);
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
  { prop: "model_id", label: "主模型", show: true },
  { prop: "memory_manager_id", label: "记忆管理器", show: true },
  { prop: "mode", label: "协作模式", show: true },
  { prop: "respond_directly", label: "是否直接响应", show: true },
  { prop: "delegate_to_all_members", label: "分发给所有成员", show: true },
  { prop: "determine_input_for_members", label: "为成员决定输入", show: true },
  { prop: "max_iterations", label: "最大迭代次数", show: true },
  { prop: "instructions", label: "Team指令", show: true },
  { prop: "expected_output", label: "期望输出格式", show: true },
  { prop: "markdown", label: "输出Markdown", show: true },
  { prop: "add_team_history_to_members", label: "传Team历史给成员", show: true },
  { prop: "num_team_history_runs", label: "传给成员历史次数", show: true },
  { prop: "share_member_interactions", label: "共享成员交互", show: true },
  { prop: "add_member_tools_to_context", label: "成员工具加入上下文", show: true },
  { prop: "read_chat_history", label: "读取聊天历史", show: true },
  { prop: "search_past_sessions", label: "搜索历史会话", show: true },
  { prop: "num_past_sessions_to_search", label: "搜索历史会话数量", show: true },
  { prop: "search_knowledge", label: "搜索知识库", show: true },
  { prop: "update_knowledge", label: "允许更新知识库", show: true },
  { prop: "enable_agentic_knowledge_filters", label: "智能知识过滤", show: true },
  { prop: "enable_agentic_state", label: "智能状态", show: true },
  { prop: "enable_agentic_memory", label: "智能记忆", show: true },
  { prop: "update_memory_on_run", label: "运行后更新记忆", show: true },
  { prop: "enable_session_summaries", label: "开启会话摘要", show: true },
  { prop: "add_session_summary_to_context", label: "摘要加入上下文", show: true },
  { prop: "tool_call_limit", label: "工具调用次数上限", show: true },
  { prop: "stream", label: "流式输出", show: true },
  { prop: "stream_events", label: "流式推送事件", show: true },
  { prop: "debug_mode", label: "调试模式", show: true },
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
  { prop: "name", label: "Team名称" },
  { prop: "model_id", label: "主模型ID" },
  { prop: "memory_manager_id", label: "记忆管理器ID" },
  { prop: "mode", label: "协作模式" },
  { prop: "respond_directly", label: "是否直接响应" },
  { prop: "delegate_to_all_members", label: "分发给所有成员" },
  { prop: "determine_input_for_members", label: "为成员决定输入" },
  { prop: "max_iterations", label: "最大迭代次数" },
  { prop: "instructions", label: "Team指令" },
  { prop: "expected_output", label: "期望输出格式" },
  { prop: "markdown", label: "输出Markdown" },
  { prop: "add_team_history_to_members", label: "传Team历史给成员" },
  { prop: "num_team_history_runs", label: "传给成员历史次数" },
  { prop: "share_member_interactions", label: "共享成员交互" },
  { prop: "add_member_tools_to_context", label: "成员工具加入上下文" },
  { prop: "read_chat_history", label: "读取聊天历史" },
  { prop: "search_past_sessions", label: "搜索历史会话" },
  { prop: "num_past_sessions_to_search", label: "搜索历史会话数量" },
  { prop: "search_knowledge", label: "搜索知识库" },
  { prop: "update_knowledge", label: "允许更新知识库" },
  { prop: "enable_agentic_knowledge_filters", label: "智能知识过滤" },
  { prop: "enable_agentic_state", label: "智能状态" },
  { prop: "enable_agentic_memory", label: "智能记忆" },
  { prop: "update_memory_on_run", label: "运行后更新记忆" },
  { prop: "enable_session_summaries", label: "开启会话摘要" },
  { prop: "add_session_summary_to_context", label: "摘要加入上下文" },
  { prop: "tool_call_limit", label: "工具调用次数上限" },
  { prop: "stream", label: "流式输出" },
  { prop: "stream_events", label: "流式推送事件" },
  { prop: "debug_mode", label: "调试模式" },
  { prop: "status", label: "状态" },
  { prop: "description", label: "描述" },
  { prop: "created_time", label: "创建时间" },
  { prop: "updated_time", label: "更新时间" },
  { prop: "created_id", label: "创建人ID" },
  { prop: "updated_id", label: "更新人ID" },
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
  metadata_config: undefined,
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
  name: [{ required: false, message: "请输入Team名称", trigger: "blur" }],
  model_id: [{ required: false, message: "请选择主模型", trigger: "change" }],
  memory_manager_id: [{ required: false, message: "请选择记忆管理器", trigger: "change" }],
  mode: [{ required: false, message: "请选择协作模式", trigger: "change" }],
  respond_directly: [{ required: false, message: "请选择是否直接响应", trigger: "change" }],
  delegate_to_all_members: [{ required: false, message: "请选择是否分发给所有成员", trigger: "change" }],
  determine_input_for_members: [{ required: false, message: "请选择是否为成员决定输入", trigger: "change" }],
  max_iterations: [{ required: false, message: "请输入最大迭代次数", trigger: "blur" }],
  instructions: [{ required: false, message: "请输入Team指令", trigger: "blur" }],
  expected_output: [{ required: false, message: "请输入期望输出格式", trigger: "blur" }],
  markdown: [{ required: false, message: "请选择是否输出Markdown", trigger: "change" }],
  add_team_history_to_members: [{ required: false, message: "请选择", trigger: "change" }],
  num_team_history_runs: [{ required: false, message: "请输入传给成员历史次数", trigger: "blur" }],
  share_member_interactions: [{ required: false, message: "请选择", trigger: "change" }],
  add_member_tools_to_context: [{ required: false, message: "请选择", trigger: "change" }],
  read_chat_history: [{ required: false, message: "请选择", trigger: "change" }],
  search_past_sessions: [{ required: false, message: "请选择", trigger: "change" }],
  num_past_sessions_to_search: [{ required: false, message: "请输入搜索历史会话数量", trigger: "blur" }],
  search_knowledge: [{ required: false, message: "请选择", trigger: "change" }],
  update_knowledge: [{ required: false, message: "请选择", trigger: "change" }],
  enable_agentic_knowledge_filters: [{ required: false, message: "请选择", trigger: "change" }],
  enable_agentic_state: [{ required: false, message: "请选择", trigger: "change" }],
  enable_agentic_memory: [{ required: false, message: "请选择", trigger: "change" }],
  update_memory_on_run: [{ required: false, message: "请选择", trigger: "change" }],
  enable_session_summaries: [{ required: false, message: "请选择", trigger: "change" }],
  add_session_summary_to_context: [{ required: false, message: "请选择", trigger: "change" }],
  tool_call_limit: [{ required: false, message: "请输入工具调用次数上限", trigger: "blur" }],
  stream: [{ required: false, message: "请选择", trigger: "change" }],
  stream_events: [{ required: false, message: "请选择", trigger: "change" }],
  debug_mode: [{ required: false, message: "请选择", trigger: "change" }],
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
  metadata_config: undefined,
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
    formData.metadata_config = undefined;
    formData.status = "0";
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
      // 过滤 null/undefined 字段，不传递给接口
      const submitData = Object.fromEntries(
        Object.entries({ ...formData }).filter(([, v]) => v !== null && v !== undefined)
      ) as AgTeamForm;
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
