<!-- Agent管理 -->
<template>
  <div class="app-container">
    <!-- 内容区域 -->
    <el-card class="data-table">
      <template #header>
        <div class="card-header">
          <span>
            Agent管理列表
            <el-tooltip content="Agent管理列表">
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
            <el-form-item label="Agent名称" prop="name">
              <el-input v-model="queryFormData.name" placeholder="请输入Agent名称" clearable />
            </el-form-item>
            <el-form-item label="主模型" prop="model_id">
              <el-select
                v-model="queryFormData.model_id"
                placeholder="请选择主模型"
                style="width: 200px"
                clearable
                filterable
              >
                <el-option
                  v-for="model in modelList"
                  :key="model.id"
                  :label="model.name"
                  :value="String(model.id)"
                />
              </el-select>
            </el-form-item>
            <el-form-item label="推理模型ID" prop="reasoning_model_id">
              <el-input v-model="queryFormData.reasoning_model_id" placeholder="请输入推理模型ID" clearable />
            </el-form-item>
            <el-form-item label="输出模型ID" prop="output_model_id">
              <el-input v-model="queryFormData.output_model_id" placeholder="请输入输出模型ID" clearable />
            </el-form-item>
            <el-form-item label="解析模型ID" prop="parser_model_id">
              <el-input v-model="queryFormData.parser_model_id" placeholder="请输入解析模型ID" clearable />
            </el-form-item>
            <el-form-item label="记忆管理器ID" prop="memory_manager_id">
              <el-select v-model="queryFormData.memory_manager_id" placeholder="请选择记忆管理器" clearable filterable style="width: 200px">
                <el-option v-for="item in memoryManagerList" :key="item.id" :label="item.name" :value="String(item.id)" />
              </el-select>
            </el-form-item>
            <el-form-item label="学习机配置ID" prop="learning_config_id">
              <el-select v-model="queryFormData.learning_config_id" placeholder="请选择学习机配置" clearable filterable style="width: 200px">
                <el-option v-for="item in learningConfigList" :key="item.id" :label="item.name" :value="String(item.id)" />
              </el-select>
            </el-form-item>
            <el-form-item label="推理配置ID" prop="reasoning_config_id">
              <el-select v-model="queryFormData.reasoning_config_id" placeholder="请选择推理配置" clearable filterable style="width: 200px">
                <el-option v-for="item in reasoningConfigList" :key="item.id" :label="item.name" :value="String(item.id)" />
              </el-select>
            </el-form-item>
            <el-form-item label="压缩管理器配置ID" prop="compression_config_id">
              <el-select v-model="queryFormData.compression_config_id" placeholder="请选择压缩配置" clearable filterable style="width: 200px">
                <el-option v-for="item in compressionConfigList" :key="item.id" :label="item.name" :value="String(item.id)" />
              </el-select>
            </el-form-item>
            <el-form-item label="会话摘要配置ID" prop="session_summary_config_id">
              <el-select v-model="queryFormData.session_summary_config_id" placeholder="请选择会话摘要配置" clearable filterable style="width: 200px">
                <el-option v-for="item in sessSummaryConfigList" :key="item.id" :label="item.name" :value="String(item.id)" />
              </el-select>
            </el-form-item>
            <el-form-item label="文化管理器配置ID" prop="culture_config_id">
              <el-select v-model="queryFormData.culture_config_id" placeholder="请选择文化管理器配置" clearable filterable style="width: 200px">
                <el-option v-for="item in cultureConfigList" :key="item.id" :label="item.name" :value="String(item.id)" />
              </el-select>
            </el-form-item>
            <el-form-item label="Agent指令" prop="instructions">
              <el-input v-model="queryFormData.instructions" placeholder="请输入Agent指令" clearable />
            </el-form-item>
            <el-form-item label="期望输出格式说明" prop="expected_output">
              <el-input v-model="queryFormData.expected_output" placeholder="请输入期望输出格式说明" clearable />
            </el-form-item>
            <el-form-item label="附加上下文" prop="additional_context">
              <el-input v-model="queryFormData.additional_context" placeholder="请输入附加上下文" clearable />
            </el-form-item>
            <el-form-item label="是否开启推理" prop="reasoning">
              <el-select v-model="queryFormData.reasoning" placeholder="请选择" style="width: 120px" clearable>
                <el-option :value="'true'" label="是" />
                <el-option :value="'false'" label="否" />
              </el-select>
            </el-form-item>
            <el-form-item label="最少推理步数" prop="reasoning_min_steps">
              <el-input v-model="queryFormData.reasoning_min_steps" placeholder="请输入最少推理步数" clearable />
            </el-form-item>
            <el-form-item label="最多推理步数" prop="reasoning_max_steps">
              <el-input v-model="queryFormData.reasoning_max_steps" placeholder="请输入最多推理步数" clearable />
            </el-form-item>
            <el-form-item label="是否开启学习" prop="learning">
              <el-select v-model="queryFormData.learning" placeholder="请选择" style="width: 120px" clearable>
                <el-option :value="'true'" label="是" />
                <el-option :value="'false'" label="否" />
              </el-select>
            </el-form-item>
            <el-form-item label="是否搜索知识库" prop="search_knowledge">
              <el-select v-model="queryFormData.search_knowledge" placeholder="请选择" style="width: 120px" clearable>
                <el-option :value="'true'" label="是" />
                <el-option :value="'false'" label="否" />
              </el-select>
            </el-form-item>
            <el-form-item label="是否允许更新知识库" prop="update_knowledge">
              <el-select v-model="queryFormData.update_knowledge" placeholder="请选择" style="width: 120px" clearable>
                <el-option :value="'true'" label="是" />
                <el-option :value="'false'" label="否" />
              </el-select>
            </el-form-item>
            <el-form-item label="是否将知识库内容加入上下文" prop="add_knowledge_to_context">
              <el-select v-model="queryFormData.add_knowledge_to_context" placeholder="请选择" style="width: 120px" clearable>
                <el-option :value="'true'" label="是" />
                <el-option :value="'false'" label="否" />
              </el-select>
            </el-form-item>
            <el-form-item label="是否开启智能知识过滤" prop="enable_agentic_knowledge_filters">
              <el-select v-model="queryFormData.enable_agentic_knowledge_filters" placeholder="请选择" style="width: 120px" clearable>
                <el-option :value="'true'" label="是" />
                <el-option :value="'false'" label="否" />
              </el-select>
            </el-form-item>
            <el-form-item label="是否开启智能状态" prop="enable_agentic_state">
              <el-select v-model="queryFormData.enable_agentic_state" placeholder="请选择" style="width: 120px" clearable>
                <el-option :value="'true'" label="是" />
                <el-option :value="'false'" label="否" />
              </el-select>
            </el-form-item>
            <el-form-item label="是否开启智能记忆" prop="enable_agentic_memory">
              <el-select v-model="queryFormData.enable_agentic_memory" placeholder="请选择" style="width: 120px" clearable>
                <el-option :value="'true'" label="是" />
                <el-option :value="'false'" label="否" />
              </el-select>
            </el-form-item>
            <el-form-item label="是否每次运行后更新记忆" prop="update_memory_on_run">
              <el-select v-model="queryFormData.update_memory_on_run" placeholder="请选择" style="width: 120px" clearable>
                <el-option :value="'true'" label="是" />
                <el-option :value="'false'" label="否" />
              </el-select>
            </el-form-item>
            <el-form-item label="是否将记忆加入上下文" prop="add_memories_to_context">
              <el-select v-model="queryFormData.add_memories_to_context" placeholder="请选择" style="width: 120px" clearable>
                <el-option :value="'true'" label="是" />
                <el-option :value="'false'" label="否" />
              </el-select>
            </el-form-item>
            <el-form-item label="是否将历史记录加入上下文" prop="add_history_to_context">
              <el-select v-model="queryFormData.add_history_to_context" placeholder="请选择" style="width: 120px" clearable>
                <el-option :value="'true'" label="是" />
                <el-option :value="'false'" label="否" />
              </el-select>
            </el-form-item>
            <el-form-item label="加入上下文的历史运行次数" prop="num_history_runs">
              <el-input v-model="queryFormData.num_history_runs" placeholder="请输入加入上下文的历史运行次数" clearable />
            </el-form-item>
            <el-form-item label="加入上下文的历史消息数" prop="num_history_messages">
              <el-input v-model="queryFormData.num_history_messages" placeholder="请输入加入上下文的历史消息数" clearable />
            </el-form-item>
            <el-form-item label="是否搜索历史会话" prop="search_past_sessions">
              <el-select v-model="queryFormData.search_past_sessions" placeholder="请选择" style="width: 120px" clearable>
                <el-option :value="'true'" label="是" />
                <el-option :value="'false'" label="否" />
              </el-select>
            </el-form-item>
            <el-form-item label="搜索历史会话数量" prop="num_past_sessions_to_search">
              <el-input v-model="queryFormData.num_past_sessions_to_search" placeholder="请输入搜索历史会话数量" clearable />
            </el-form-item>
            <el-form-item label="是否开启会话摘要" prop="enable_session_summaries">
              <el-select v-model="queryFormData.enable_session_summaries" placeholder="请选择" style="width: 120px" clearable>
                <el-option :value="'true'" label="是" />
                <el-option :value="'false'" label="否" />
              </el-select>
            </el-form-item>
            <el-form-item label="是否将会话摘要加入上下文" prop="add_session_summary_to_context">
              <el-select v-model="queryFormData.add_session_summary_to_context" placeholder="请选择" style="width: 120px" clearable>
                <el-option :value="'true'" label="是" />
                <el-option :value="'false'" label="否" />
              </el-select>
            </el-form-item>
            <el-form-item label="工具调用次数上限" prop="tool_call_limit">
              <el-input v-model="queryFormData.tool_call_limit" placeholder="请输入工具调用次数上限" clearable />
            </el-form-item>
            <el-form-item label="工具选择策略(none/auto/specific)" prop="tool_choice">
              <el-input v-model="queryFormData.tool_choice" placeholder="请输入工具选择策略(none/auto/specific)" clearable />
            </el-form-item>
            <el-form-item label="是否使用JSON输出模式" prop="use_json_mode">
              <el-select v-model="queryFormData.use_json_mode" placeholder="请选择" style="width: 120px" clearable>
                <el-option :value="'true'" label="是" />
                <el-option :value="'false'" label="否" />
              </el-select>
            </el-form-item>
            <el-form-item label="是否使用结构化输出" prop="structured_outputs">
              <el-select v-model="queryFormData.structured_outputs" placeholder="请选择" style="width: 120px" clearable>
                <el-option :value="'true'" label="是" />
                <el-option :value="'false'" label="否" />
              </el-select>
            </el-form-item>
            <el-form-item label="是否解析响应" prop="parse_response">
              <el-select v-model="queryFormData.parse_response" placeholder="请选择" style="width: 120px" clearable>
                <el-option :value="'true'" label="是" />
                <el-option :value="'false'" label="否" />
              </el-select>
            </el-form-item>
            <el-form-item label="失败重试次数" prop="retries">
              <el-input v-model="queryFormData.retries" placeholder="请输入失败重试次数" clearable />
            </el-form-item>
            <el-form-item label="重试间隔秒数" prop="delay_between_retries">
              <el-input v-model="queryFormData.delay_between_retries" placeholder="请输入重试间隔秒数" clearable />
            </el-form-item>
            <el-form-item label="是否指数退避重试" prop="exponential_backoff">
              <el-select v-model="queryFormData.exponential_backoff" placeholder="请选择" style="width: 120px" clearable>
                <el-option :value="'true'" label="是" />
                <el-option :value="'false'" label="否" />
              </el-select>
            </el-form-item>
            <el-form-item label="是否将当前时间加入上下文" prop="add_datetime_to_context">
              <el-select v-model="queryFormData.add_datetime_to_context" placeholder="请选择" style="width: 120px" clearable>
                <el-option :value="'true'" label="是" />
                <el-option :value="'false'" label="否" />
              </el-select>
            </el-form-item>
            <el-form-item label="是否将Agent名称加入上下文" prop="add_name_to_context">
              <el-select v-model="queryFormData.add_name_to_context" placeholder="请选择" style="width: 120px" clearable>
                <el-option :value="'true'" label="是" />
                <el-option :value="'false'" label="否" />
              </el-select>
            </el-form-item>
            <el-form-item label="是否压缩工具结果" prop="compress_tool_results">
              <el-select v-model="queryFormData.compress_tool_results" placeholder="请选择" style="width: 120px" clearable>
                <el-option :value="'true'" label="是" />
                <el-option :value="'false'" label="否" />
              </el-select>
            </el-form-item>
            <el-form-item label="是否开启流式输出" prop="stream">
              <el-select v-model="queryFormData.stream" placeholder="请选择" style="width: 120px" clearable>
                <el-option :value="'true'" label="是" />
                <el-option :value="'false'" label="否" />
              </el-select>
            </el-form-item>
            <el-form-item label="是否流式推送事件" prop="stream_events">
              <el-select v-model="queryFormData.stream_events" placeholder="请选择" style="width: 120px" clearable>
                <el-option :value="'true'" label="是" />
                <el-option :value="'false'" label="否" />
              </el-select>
            </el-form-item>
            <el-form-item label="是否存储事件" prop="store_events">
              <el-select v-model="queryFormData.store_events" placeholder="请选择" style="width: 120px" clearable>
                <el-option :value="'true'" label="是" />
                <el-option :value="'false'" label="否" />
              </el-select>
            </el-form-item>
            <el-form-item label="是否输出Markdown格式" prop="markdown">
              <el-select v-model="queryFormData.markdown" placeholder="请选择" style="width: 120px" clearable>
                <el-option :value="'true'" label="是" />
                <el-option :value="'false'" label="否" />
              </el-select>
            </el-form-item>
            <el-form-item label="是否生成追问" prop="followups">
              <el-select v-model="queryFormData.followups" placeholder="请选择" style="width: 120px" clearable>
                <el-option :value="'true'" label="是" />
                <el-option :value="'false'" label="否" />
              </el-select>
            </el-form-item>
            <el-form-item label="追问数量" prop="num_followups">
              <el-input v-model="queryFormData.num_followups" placeholder="请输入追问数量" clearable />
            </el-form-item>
            <el-form-item label="是否开启调试模式" prop="debug_mode">
              <el-select v-model="queryFormData.debug_mode" placeholder="请选择" style="width: 120px" clearable>
                <el-option :value="'true'" label="是" />
                <el-option :value="'false'" label="否" />
              </el-select>
            </el-form-item>
            <el-form-item label="调试级别" prop="debug_level">
              <el-input v-model="queryFormData.debug_level" placeholder="请输入调试级别" clearable />
            </el-form-item>
            <el-form-item label="是否对外暴露A2A接口" prop="a2a_enabled">
              <el-select v-model="queryFormData.a2a_enabled" placeholder="请选择" style="width: 120px" clearable>
                <el-option :value="'true'" label="是" />
                <el-option :value="'false'" label="否" />
              </el-select>
            </el-form-item>
            <el-form-item label="是否为远程Agent" prop="is_remote">
              <el-select v-model="queryFormData.is_remote" placeholder="请选择" style="width: 120px" clearable>
                <el-option :value="'true'" label="是" />
                <el-option :value="'false'" label="否" />
              </el-select>
            </el-form-item>
            <el-form-item label="远程Agent地址" prop="remote_url">
              <el-input v-model="queryFormData.remote_url" placeholder="请输入远程Agent地址" clearable />
            </el-form-item>
            <el-form-item label="远程Agent标识符" prop="remote_agent_id">
              <el-input v-model="queryFormData.remote_agent_id" placeholder="请输入远程Agent标识符" clearable />
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
                v-hasPerm="['module_agno_manage:agents:query']"
                type="primary"
                icon="search"
                @click="handleQuery"
              >
                查询
              </el-button>
              <el-button
                v-hasPerm="['module_agno_manage:agents:query']"
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
                v-hasPerm="['module_agno_manage:agents:create']"
                type="success"
                icon="plus"
                @click="handleOpenDialog('create')"
              >
                新增
              </el-button>
            </el-col>
            <el-col :span="1.5">
              <el-button
                v-hasPerm="['module_agno_manage:agents:delete']"
                type="danger"
                icon="delete"
                :disabled="selectIds.length === 0"
                @click="handleDelete(selectIds)"
              >
                批量删除
              </el-button>
            </el-col>
            <el-col :span="1.5">
              <el-dropdown v-hasPerm="['module_agno_manage:agents:batch']" trigger="click">
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
                  v-hasPerm="['module_agno_manage:agents:import']"
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
                  v-hasPerm="['module_agno_manage:agents:export']"
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
                  v-hasPerm="['module_agno_manage:agents:query']"
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
          label="Agent名称"
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
          v-if="tableColumns.find((col) => col.prop === 'reasoning_model_id')?.show"
          label="推理模型ID"
          prop="reasoning_model_id"
          min-width="140"
          show-overflow-tooltip
        />
        <el-table-column
          v-if="tableColumns.find((col) => col.prop === 'output_model_id')?.show"
          label="输出模型ID"
          prop="output_model_id"
          min-width="140"
          show-overflow-tooltip
        />
        <el-table-column
          v-if="tableColumns.find((col) => col.prop === 'parser_model_id')?.show"
          label="解析模型ID"
          prop="parser_model_id"
          min-width="140"
          show-overflow-tooltip
        />
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
          v-if="tableColumns.find((col) => col.prop === 'learning_config_id')?.show"
          label="学习机配置"
          prop="learning_config_id"
          min-width="140"
          show-overflow-tooltip
        >
          <template #default="scope">{{ getLearningConfigName(scope.row.learning_config_id) }}</template>
        </el-table-column>
        <el-table-column
          v-if="tableColumns.find((col) => col.prop === 'reasoning_config_id')?.show"
          label="推理配置"
          prop="reasoning_config_id"
          min-width="140"
          show-overflow-tooltip
        >
          <template #default="scope">{{ getReasoningConfigName(scope.row.reasoning_config_id) }}</template>
        </el-table-column>
        <el-table-column
          v-if="tableColumns.find((col) => col.prop === 'compression_config_id')?.show"
          label="压缩管理器配置"
          prop="compression_config_id"
          min-width="140"
          show-overflow-tooltip
        >
          <template #default="scope">{{ getCompressionConfigName(scope.row.compression_config_id) }}</template>
        </el-table-column>
        <el-table-column
          v-if="tableColumns.find((col) => col.prop === 'session_summary_config_id')?.show"
          label="会话摘要配置"
          prop="session_summary_config_id"
          min-width="140"
          show-overflow-tooltip
        >
          <template #default="scope">{{ getSessSummaryConfigName(scope.row.session_summary_config_id) }}</template>
        </el-table-column>
        <el-table-column
          v-if="tableColumns.find((col) => col.prop === 'culture_config_id')?.show"
          label="文化管理器配置"
          prop="culture_config_id"
          min-width="140"
          show-overflow-tooltip
        >
          <template #default="scope">{{ getCultureConfigName(scope.row.culture_config_id) }}</template>
        </el-table-column>
        <el-table-column
          v-if="tableColumns.find((col) => col.prop === 'instructions')?.show"
          label="Agent指令"
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
          v-if="tableColumns.find((col) => col.prop === 'additional_context')?.show"
          label="附加上下文"
          prop="additional_context"
          min-width="140"
          show-overflow-tooltip
        />
        <el-table-column
          v-if="tableColumns.find((col) => col.prop === 'reasoning')?.show"
          label="是否开启推理"
          prop="reasoning"
          min-width="100"
        >
          <template #default="scope">
            <el-tag :type="scope.row.reasoning === true ? 'success' : scope.row.reasoning === false ? 'danger' : undefined">{{ scope.row.reasoning === true ? '是' : scope.row.reasoning === false ? '否' : '默认' }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column
          v-if="tableColumns.find((col) => col.prop === 'reasoning_min_steps')?.show"
          label="最少推理步数"
          prop="reasoning_min_steps"
          min-width="140"
          show-overflow-tooltip
        />
        <el-table-column
          v-if="tableColumns.find((col) => col.prop === 'reasoning_max_steps')?.show"
          label="最多推理步数"
          prop="reasoning_max_steps"
          min-width="140"
          show-overflow-tooltip
        />
        <el-table-column
          v-if="tableColumns.find((col) => col.prop === 'learning')?.show"
          label="是否开启学习"
          prop="learning"
          min-width="100"
        >
          <template #default="scope">
            <el-tag :type="scope.row.learning === true ? 'success' : scope.row.learning === false ? 'danger' : undefined">{{ scope.row.learning === true ? '是' : scope.row.learning === false ? '否' : '默认' }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column
          v-if="tableColumns.find((col) => col.prop === 'search_knowledge')?.show"
          label="是否搜索知识库"
          prop="search_knowledge"
          min-width="100"
        >
          <template #default="scope">
            <el-tag :type="scope.row.search_knowledge === true ? 'success' : scope.row.search_knowledge === false ? 'danger' : undefined">{{ scope.row.search_knowledge === true ? '是' : scope.row.search_knowledge === false ? '否' : '默认' }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column
          v-if="tableColumns.find((col) => col.prop === 'update_knowledge')?.show"
          label="是否允许更新知识库"
          prop="update_knowledge"
          min-width="100"
        >
          <template #default="scope">
            <el-tag :type="scope.row.update_knowledge === true ? 'success' : scope.row.update_knowledge === false ? 'danger' : undefined">{{ scope.row.update_knowledge === true ? '是' : scope.row.update_knowledge === false ? '否' : '默认' }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column
          v-if="tableColumns.find((col) => col.prop === 'add_knowledge_to_context')?.show"
          label="是否将知识库内容加入上下文"
          prop="add_knowledge_to_context"
          min-width="100"
        >
          <template #default="scope">
            <el-tag :type="scope.row.add_knowledge_to_context === true ? 'success' : scope.row.add_knowledge_to_context === false ? 'danger' : undefined">{{ scope.row.add_knowledge_to_context === true ? '是' : scope.row.add_knowledge_to_context === false ? '否' : '默认' }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column
          v-if="tableColumns.find((col) => col.prop === 'enable_agentic_knowledge_filters')?.show"
          label="是否开启智能知识过滤"
          prop="enable_agentic_knowledge_filters"
          min-width="100"
        >
          <template #default="scope">
            <el-tag :type="scope.row.enable_agentic_knowledge_filters === true ? 'success' : scope.row.enable_agentic_knowledge_filters === false ? 'danger' : undefined">{{ scope.row.enable_agentic_knowledge_filters === true ? '是' : scope.row.enable_agentic_knowledge_filters === false ? '否' : '默认' }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column
          v-if="tableColumns.find((col) => col.prop === 'enable_agentic_state')?.show"
          label="是否开启智能状态"
          prop="enable_agentic_state"
          min-width="100"
        >
          <template #default="scope">
            <el-tag :type="scope.row.enable_agentic_state === true ? 'success' : scope.row.enable_agentic_state === false ? 'danger' : undefined">{{ scope.row.enable_agentic_state === true ? '是' : scope.row.enable_agentic_state === false ? '否' : '默认' }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column
          v-if="tableColumns.find((col) => col.prop === 'enable_agentic_memory')?.show"
          label="是否开启智能记忆"
          prop="enable_agentic_memory"
          min-width="100"
        >
          <template #default="scope">
            <el-tag :type="scope.row.enable_agentic_memory === true ? 'success' : scope.row.enable_agentic_memory === false ? 'danger' : undefined">{{ scope.row.enable_agentic_memory === true ? '是' : scope.row.enable_agentic_memory === false ? '否' : '默认' }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column
          v-if="tableColumns.find((col) => col.prop === 'update_memory_on_run')?.show"
          label="是否每次运行后更新记忆"
          prop="update_memory_on_run"
          min-width="100"
        >
          <template #default="scope">
            <el-tag :type="scope.row.update_memory_on_run === true ? 'success' : scope.row.update_memory_on_run === false ? 'danger' : undefined">{{ scope.row.update_memory_on_run === true ? '是' : scope.row.update_memory_on_run === false ? '否' : '默认' }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column
          v-if="tableColumns.find((col) => col.prop === 'add_memories_to_context')?.show"
          label="是否将记忆加入上下文"
          prop="add_memories_to_context"
          min-width="100"
        >
          <template #default="scope">
            <el-tag :type="scope.row.add_memories_to_context === true ? 'success' : scope.row.add_memories_to_context === false ? 'danger' : undefined">{{ scope.row.add_memories_to_context === true ? '是' : scope.row.add_memories_to_context === false ? '否' : '默认' }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column
          v-if="tableColumns.find((col) => col.prop === 'add_history_to_context')?.show"
          label="是否将历史记录加入上下文"
          prop="add_history_to_context"
          min-width="100"
        >
          <template #default="scope">
            <el-tag :type="scope.row.add_history_to_context === true ? 'success' : scope.row.add_history_to_context === false ? 'danger' : undefined">{{ scope.row.add_history_to_context === true ? '是' : scope.row.add_history_to_context === false ? '否' : '默认' }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column
          v-if="tableColumns.find((col) => col.prop === 'num_history_runs')?.show"
          label="加入上下文的历史运行次数"
          prop="num_history_runs"
          min-width="140"
          show-overflow-tooltip
        />
        <el-table-column
          v-if="tableColumns.find((col) => col.prop === 'num_history_messages')?.show"
          label="加入上下文的历史消息数"
          prop="num_history_messages"
          min-width="140"
          show-overflow-tooltip
        />
        <el-table-column
          v-if="tableColumns.find((col) => col.prop === 'search_past_sessions')?.show"
          label="是否搜索历史会话"
          prop="search_past_sessions"
          min-width="100"
        >
          <template #default="scope">
            <el-tag :type="scope.row.search_past_sessions === true ? 'success' : scope.row.search_past_sessions === false ? 'danger' : undefined">{{ scope.row.search_past_sessions === true ? '是' : scope.row.search_past_sessions === false ? '否' : '默认' }}</el-tag>
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
          v-if="tableColumns.find((col) => col.prop === 'enable_session_summaries')?.show"
          label="是否开启会话摘要"
          prop="enable_session_summaries"
          min-width="100"
        >
          <template #default="scope">
            <el-tag :type="scope.row.enable_session_summaries === true ? 'success' : scope.row.enable_session_summaries === false ? 'danger' : undefined">{{ scope.row.enable_session_summaries === true ? '是' : scope.row.enable_session_summaries === false ? '否' : '默认' }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column
          v-if="tableColumns.find((col) => col.prop === 'add_session_summary_to_context')?.show"
          label="是否将会话摘要加入上下文"
          prop="add_session_summary_to_context"
          min-width="100"
        >
          <template #default="scope">
            <el-tag :type="scope.row.add_session_summary_to_context === true ? 'success' : scope.row.add_session_summary_to_context === false ? 'danger' : undefined">{{ scope.row.add_session_summary_to_context === true ? '是' : scope.row.add_session_summary_to_context === false ? '否' : '默认' }}</el-tag>
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
          v-if="tableColumns.find((col) => col.prop === 'tool_choice')?.show"
          label="工具选择策略(none/auto/specific)"
          prop="tool_choice"
          min-width="140"
          show-overflow-tooltip
        />
        <el-table-column
          v-if="tableColumns.find((col) => col.prop === 'output_schema')?.show"
          label="输出结构体JSON Schema"
          prop="output_schema"
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
          v-if="tableColumns.find((col) => col.prop === 'use_json_mode')?.show"
          label="是否使用JSON输出模式"
          prop="use_json_mode"
          min-width="100"
        >
          <template #default="scope">
            <el-tag :type="scope.row.use_json_mode === true ? 'success' : scope.row.use_json_mode === false ? 'danger' : undefined">{{ scope.row.use_json_mode === true ? '是' : scope.row.use_json_mode === false ? '否' : '默认' }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column
          v-if="tableColumns.find((col) => col.prop === 'structured_outputs')?.show"
          label="是否使用结构化输出"
          prop="structured_outputs"
          min-width="100"
        >
          <template #default="scope">
            <el-tag :type="scope.row.structured_outputs === true ? 'success' : scope.row.structured_outputs === false ? 'danger' : undefined">{{ scope.row.structured_outputs === true ? '是' : scope.row.structured_outputs === false ? '否' : '默认' }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column
          v-if="tableColumns.find((col) => col.prop === 'parse_response')?.show"
          label="是否解析响应"
          prop="parse_response"
          min-width="100"
        >
          <template #default="scope">
            <el-tag :type="scope.row.parse_response === true ? 'success' : scope.row.parse_response === false ? 'danger' : undefined">{{ scope.row.parse_response === true ? '是' : scope.row.parse_response === false ? '否' : '默认' }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column
          v-if="tableColumns.find((col) => col.prop === 'retries')?.show"
          label="失败重试次数"
          prop="retries"
          min-width="140"
          show-overflow-tooltip
        />
        <el-table-column
          v-if="tableColumns.find((col) => col.prop === 'delay_between_retries')?.show"
          label="重试间隔秒数"
          prop="delay_between_retries"
          min-width="140"
          show-overflow-tooltip
        />
        <el-table-column
          v-if="tableColumns.find((col) => col.prop === 'exponential_backoff')?.show"
          label="是否指数退避重试"
          prop="exponential_backoff"
          min-width="100"
        >
          <template #default="scope">
            <el-tag :type="scope.row.exponential_backoff === true ? 'success' : scope.row.exponential_backoff === false ? 'danger' : undefined">{{ scope.row.exponential_backoff === true ? '是' : scope.row.exponential_backoff === false ? '否' : '默认' }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column
          v-if="tableColumns.find((col) => col.prop === 'add_datetime_to_context')?.show"
          label="是否将当前时间加入上下文"
          prop="add_datetime_to_context"
          min-width="100"
        >
          <template #default="scope">
            <el-tag :type="scope.row.add_datetime_to_context === true ? 'success' : scope.row.add_datetime_to_context === false ? 'danger' : undefined">{{ scope.row.add_datetime_to_context === true ? '是' : scope.row.add_datetime_to_context === false ? '否' : '默认' }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column
          v-if="tableColumns.find((col) => col.prop === 'add_name_to_context')?.show"
          label="是否将Agent名称加入上下文"
          prop="add_name_to_context"
          min-width="100"
        >
          <template #default="scope">
            <el-tag :type="scope.row.add_name_to_context === true ? 'success' : scope.row.add_name_to_context === false ? 'danger' : undefined">{{ scope.row.add_name_to_context === true ? '是' : scope.row.add_name_to_context === false ? '否' : '默认' }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column
          v-if="tableColumns.find((col) => col.prop === 'compress_tool_results')?.show"
          label="是否压缩工具结果"
          prop="compress_tool_results"
          min-width="100"
        >
          <template #default="scope">
            <el-tag :type="scope.row.compress_tool_results === true ? 'success' : scope.row.compress_tool_results === false ? 'danger' : undefined">{{ scope.row.compress_tool_results === true ? '是' : scope.row.compress_tool_results === false ? '否' : '默认' }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column
          v-if="tableColumns.find((col) => col.prop === 'stream')?.show"
          label="是否开启流式输出"
          prop="stream"
          min-width="100"
        >
          <template #default="scope">
            <el-tag :type="scope.row.stream === true ? 'success' : scope.row.stream === false ? 'danger' : undefined">{{ scope.row.stream === true ? '是' : scope.row.stream === false ? '否' : '默认' }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column
          v-if="tableColumns.find((col) => col.prop === 'stream_events')?.show"
          label="是否流式推送事件"
          prop="stream_events"
          min-width="100"
        >
          <template #default="scope">
            <el-tag :type="scope.row.stream_events === true ? 'success' : scope.row.stream_events === false ? 'danger' : undefined">{{ scope.row.stream_events === true ? '是' : scope.row.stream_events === false ? '否' : '默认' }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column
          v-if="tableColumns.find((col) => col.prop === 'store_events')?.show"
          label="是否存储事件"
          prop="store_events"
          min-width="100"
        >
          <template #default="scope">
            <el-tag :type="scope.row.store_events === true ? 'success' : scope.row.store_events === false ? 'danger' : undefined">{{ scope.row.store_events === true ? '是' : scope.row.store_events === false ? '否' : '默认' }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column
          v-if="tableColumns.find((col) => col.prop === 'markdown')?.show"
          label="是否输出Markdown格式"
          prop="markdown"
          min-width="100"
        >
          <template #default="scope">
            <el-tag :type="scope.row.markdown === true ? 'success' : scope.row.markdown === false ? 'danger' : undefined">{{ scope.row.markdown === true ? '是' : scope.row.markdown === false ? '否' : '默认' }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column
          v-if="tableColumns.find((col) => col.prop === 'followups')?.show"
          label="是否生成追问"
          prop="followups"
          min-width="100"
        >
          <template #default="scope">
            <el-tag :type="scope.row.followups === true ? 'success' : scope.row.followups === false ? 'danger' : undefined">{{ scope.row.followups === true ? '是' : scope.row.followups === false ? '否' : '默认' }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column
          v-if="tableColumns.find((col) => col.prop === 'num_followups')?.show"
          label="追问数量"
          prop="num_followups"
          min-width="140"
          show-overflow-tooltip
        />
        <el-table-column
          v-if="tableColumns.find((col) => col.prop === 'debug_mode')?.show"
          label="是否开启调试模式"
          prop="debug_mode"
          min-width="100"
        >
          <template #default="scope">
            <el-tag :type="scope.row.debug_mode === true ? 'success' : scope.row.debug_mode === false ? 'danger' : undefined">{{ scope.row.debug_mode === true ? '是' : scope.row.debug_mode === false ? '否' : '默认' }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column
          v-if="tableColumns.find((col) => col.prop === 'debug_level')?.show"
          label="调试级别"
          prop="debug_level"
          min-width="140"
          show-overflow-tooltip
        />
        <el-table-column
          v-if="tableColumns.find((col) => col.prop === 'a2a_enabled')?.show"
          label="是否对外暴露A2A接口"
          prop="a2a_enabled"
          min-width="100"
        >
          <template #default="scope">
            <el-tag :type="scope.row.a2a_enabled === true ? 'success' : scope.row.a2a_enabled === false ? 'danger' : undefined">{{ scope.row.a2a_enabled === true ? '是' : scope.row.a2a_enabled === false ? '否' : '默认' }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column
          v-if="tableColumns.find((col) => col.prop === 'is_remote')?.show"
          label="是否为远程Agent"
          prop="is_remote"
          min-width="100"
        >
          <template #default="scope">
            <el-tag :type="scope.row.is_remote === true ? 'success' : scope.row.is_remote === false ? 'danger' : undefined">{{ scope.row.is_remote === true ? '是' : scope.row.is_remote === false ? '否' : '默认' }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column
          v-if="tableColumns.find((col) => col.prop === 'remote_url')?.show"
          label="远程Agent地址"
          prop="remote_url"
          min-width="140"
          show-overflow-tooltip
        />
        <el-table-column
          v-if="tableColumns.find((col) => col.prop === 'remote_agent_id')?.show"
          label="远程Agent标识符"
          prop="remote_agent_id"
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
              v-hasPerm="['module_agno_manage:agents:detail']"
              type="info"
              size="small"
              link
              icon="document"
              @click="handleOpenDialog('detail', scope.row.id)"
            >
              详情
            </el-button>
            <el-button
              v-hasPerm="['module_agno_manage:agents:update']"
              type="primary"
              size="small"
              link
              icon="edit"
              @click="handleOpenDialog('update', scope.row.id)"
            >
              编辑
            </el-button>
            <el-button
              v-hasPerm="['module_agno_manage:agents:delete']"
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
          <el-descriptions-item label="" :span="2">
            {{ detailFormData.id }}
          </el-descriptions-item>
          <el-descriptions-item label="" :span="2">
            {{ detailFormData.uuid }}
          </el-descriptions-item>
          <el-descriptions-item label="Agent名称" :span="2">
            {{ detailFormData.name }}
          </el-descriptions-item>
          <el-descriptions-item label="主模型ID" :span="2">
            {{ detailFormData.model_id }}
          </el-descriptions-item>
          <el-descriptions-item label="推理模型ID" :span="2">
            {{ detailFormData.reasoning_model_id }}
          </el-descriptions-item>
          <el-descriptions-item label="输出模型ID" :span="2">
            {{ detailFormData.output_model_id }}
          </el-descriptions-item>
          <el-descriptions-item label="解析模型ID" :span="2">
            {{ detailFormData.parser_model_id }}
          </el-descriptions-item>
          <el-descriptions-item label="记忆管理器ID" :span="2">
            {{ getMemoryManagerName(detailFormData.memory_manager_id) }}
          </el-descriptions-item>
          <el-descriptions-item label="学习机配置ID" :span="2">
            {{ getLearningConfigName(detailFormData.learning_config_id) }}
          </el-descriptions-item>
          <el-descriptions-item label="推理配置ID" :span="2">
            {{ getReasoningConfigName(detailFormData.reasoning_config_id) }}
          </el-descriptions-item>
          <el-descriptions-item label="压缩管理器配置ID" :span="2">
            {{ getCompressionConfigName(detailFormData.compression_config_id) }}
          </el-descriptions-item>
          <el-descriptions-item label="会话摘要配置ID" :span="2">
            {{ getSessSummaryConfigName(detailFormData.session_summary_config_id) }}
          </el-descriptions-item>
          <el-descriptions-item label="文化管理器配置ID" :span="2">
            {{ getCultureConfigName(detailFormData.culture_config_id) }}
          </el-descriptions-item>
          <el-descriptions-item label="Agent指令" :span="2">
            {{ detailFormData.instructions }}
          </el-descriptions-item>
          <el-descriptions-item label="期望输出格式说明" :span="2">
            {{ detailFormData.expected_output }}
          </el-descriptions-item>
          <el-descriptions-item label="附加上下文" :span="2">
            {{ detailFormData.additional_context }}
          </el-descriptions-item>
          <el-descriptions-item label="是否开启推理" :span="2">
            <el-tag :type="detailFormData.reasoning === true ? 'success' : detailFormData.reasoning === false ? 'danger' : undefined">{{ detailFormData.reasoning === true ? '是' : detailFormData.reasoning === false ? '否' : '默认' }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="最少推理步数" :span="2">
            {{ detailFormData.reasoning_min_steps }}
          </el-descriptions-item>
          <el-descriptions-item label="最多推理步数" :span="2">
            {{ detailFormData.reasoning_max_steps }}
          </el-descriptions-item>
          <el-descriptions-item label="是否开启学习" :span="2">
            <el-tag :type="detailFormData.learning === true ? 'success' : detailFormData.learning === false ? 'danger' : undefined">{{ detailFormData.learning === true ? '是' : detailFormData.learning === false ? '否' : '默认' }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="是否搜索知识库" :span="2">
            <el-tag :type="detailFormData.search_knowledge === true ? 'success' : detailFormData.search_knowledge === false ? 'danger' : undefined">{{ detailFormData.search_knowledge === true ? '是' : detailFormData.search_knowledge === false ? '否' : '默认' }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="是否允许更新知识库" :span="2">
            <el-tag :type="detailFormData.update_knowledge === true ? 'success' : detailFormData.update_knowledge === false ? 'danger' : undefined">{{ detailFormData.update_knowledge === true ? '是' : detailFormData.update_knowledge === false ? '否' : '默认' }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="是否将知识库内容加入上下文" :span="2">
            <el-tag :type="detailFormData.add_knowledge_to_context === true ? 'success' : detailFormData.add_knowledge_to_context === false ? 'danger' : undefined">{{ detailFormData.add_knowledge_to_context === true ? '是' : detailFormData.add_knowledge_to_context === false ? '否' : '默认' }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="是否开启智能知识过滤" :span="2">
            <el-tag :type="detailFormData.enable_agentic_knowledge_filters === true ? 'success' : detailFormData.enable_agentic_knowledge_filters === false ? 'danger' : undefined">{{ detailFormData.enable_agentic_knowledge_filters === true ? '是' : detailFormData.enable_agentic_knowledge_filters === false ? '否' : '默认' }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="是否开启智能状态" :span="2">
            <el-tag :type="detailFormData.enable_agentic_state === true ? 'success' : detailFormData.enable_agentic_state === false ? 'danger' : undefined">{{ detailFormData.enable_agentic_state === true ? '是' : detailFormData.enable_agentic_state === false ? '否' : '默认' }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="是否开启智能记忆" :span="2">
            <el-tag :type="detailFormData.enable_agentic_memory === true ? 'success' : detailFormData.enable_agentic_memory === false ? 'danger' : undefined">{{ detailFormData.enable_agentic_memory === true ? '是' : detailFormData.enable_agentic_memory === false ? '否' : '默认' }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="是否每次运行后更新记忆" :span="2">
            <el-tag :type="detailFormData.update_memory_on_run === true ? 'success' : detailFormData.update_memory_on_run === false ? 'danger' : undefined">{{ detailFormData.update_memory_on_run === true ? '是' : detailFormData.update_memory_on_run === false ? '否' : '默认' }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="是否将记忆加入上下文" :span="2">
            <el-tag :type="detailFormData.add_memories_to_context === true ? 'success' : detailFormData.add_memories_to_context === false ? 'danger' : undefined">{{ detailFormData.add_memories_to_context === true ? '是' : detailFormData.add_memories_to_context === false ? '否' : '默认' }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="是否将历史记录加入上下文" :span="2">
            <el-tag :type="detailFormData.add_history_to_context === true ? 'success' : detailFormData.add_history_to_context === false ? 'danger' : undefined">{{ detailFormData.add_history_to_context === true ? '是' : detailFormData.add_history_to_context === false ? '否' : '默认' }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="加入上下文的历史运行次数" :span="2">
            {{ detailFormData.num_history_runs }}
          </el-descriptions-item>
          <el-descriptions-item label="加入上下文的历史消息数" :span="2">
            {{ detailFormData.num_history_messages }}
          </el-descriptions-item>
          <el-descriptions-item label="是否搜索历史会话" :span="2">
            <el-tag :type="detailFormData.search_past_sessions === true ? 'success' : detailFormData.search_past_sessions === false ? 'danger' : undefined">{{ detailFormData.search_past_sessions === true ? '是' : detailFormData.search_past_sessions === false ? '否' : '默认' }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="搜索历史会话数量" :span="2">
            {{ detailFormData.num_past_sessions_to_search }}
          </el-descriptions-item>
          <el-descriptions-item label="是否开启会话摘要" :span="2">
            <el-tag :type="detailFormData.enable_session_summaries === true ? 'success' : detailFormData.enable_session_summaries === false ? 'danger' : undefined">{{ detailFormData.enable_session_summaries === true ? '是' : detailFormData.enable_session_summaries === false ? '否' : '默认' }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="是否将会话摘要加入上下文" :span="2">
            <el-tag :type="detailFormData.add_session_summary_to_context === true ? 'success' : detailFormData.add_session_summary_to_context === false ? 'danger' : undefined">{{ detailFormData.add_session_summary_to_context === true ? '是' : detailFormData.add_session_summary_to_context === false ? '否' : '默认' }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="工具调用次数上限" :span="2">
            {{ detailFormData.tool_call_limit }}
          </el-descriptions-item>
          <el-descriptions-item label="工具选择策略(none/auto/specific)" :span="2">
            {{ detailFormData.tool_choice }}
          </el-descriptions-item>
          <el-descriptions-item label="输出结构体JSON Schema" :span="4">
            <pre style="margin: 0; white-space: pre-wrap; font-size: 12px">{{ JSON.stringify(detailFormData.output_schema, null, 2) }}</pre>
          </el-descriptions-item>
          <el-descriptions-item label="输入结构体JSON Schema" :span="4">
            <pre style="margin: 0; white-space: pre-wrap; font-size: 12px">{{ JSON.stringify(detailFormData.input_schema, null, 2) }}</pre>
          </el-descriptions-item>
          <el-descriptions-item label="是否使用JSON输出模式" :span="2">
            <el-tag :type="detailFormData.use_json_mode === true ? 'success' : detailFormData.use_json_mode === false ? 'danger' : undefined">{{ detailFormData.use_json_mode === true ? '是' : detailFormData.use_json_mode === false ? '否' : '默认' }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="是否使用结构化输出" :span="2">
            <el-tag :type="detailFormData.structured_outputs === true ? 'success' : detailFormData.structured_outputs === false ? 'danger' : undefined">{{ detailFormData.structured_outputs === true ? '是' : detailFormData.structured_outputs === false ? '否' : '默认' }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="是否解析响应" :span="2">
            <el-tag :type="detailFormData.parse_response === true ? 'success' : detailFormData.parse_response === false ? 'danger' : undefined">{{ detailFormData.parse_response === true ? '是' : detailFormData.parse_response === false ? '否' : '默认' }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="失败重试次数" :span="2">
            {{ detailFormData.retries }}
          </el-descriptions-item>
          <el-descriptions-item label="重试间隔秒数" :span="2">
            {{ detailFormData.delay_between_retries }}
          </el-descriptions-item>
          <el-descriptions-item label="是否指数退避重试" :span="2">
            <el-tag :type="detailFormData.exponential_backoff === true ? 'success' : detailFormData.exponential_backoff === false ? 'danger' : undefined">{{ detailFormData.exponential_backoff === true ? '是' : detailFormData.exponential_backoff === false ? '否' : '默认' }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="是否将当前时间加入上下文" :span="2">
            <el-tag :type="detailFormData.add_datetime_to_context === true ? 'success' : detailFormData.add_datetime_to_context === false ? 'danger' : undefined">{{ detailFormData.add_datetime_to_context === true ? '是' : detailFormData.add_datetime_to_context === false ? '否' : '默认' }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="是否将Agent名称加入上下文" :span="2">
            <el-tag :type="detailFormData.add_name_to_context === true ? 'success' : detailFormData.add_name_to_context === false ? 'danger' : undefined">{{ detailFormData.add_name_to_context === true ? '是' : detailFormData.add_name_to_context === false ? '否' : '默认' }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="是否压缩工具结果" :span="2">
            <el-tag :type="detailFormData.compress_tool_results === true ? 'success' : detailFormData.compress_tool_results === false ? 'danger' : undefined">{{ detailFormData.compress_tool_results === true ? '是' : detailFormData.compress_tool_results === false ? '否' : '默认' }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="是否开启流式输出" :span="2">
            <el-tag :type="detailFormData.stream === true ? 'success' : detailFormData.stream === false ? 'danger' : undefined">{{ detailFormData.stream === true ? '是' : detailFormData.stream === false ? '否' : '默认' }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="是否流式推送事件" :span="2">
            <el-tag :type="detailFormData.stream_events === true ? 'success' : detailFormData.stream_events === false ? 'danger' : undefined">{{ detailFormData.stream_events === true ? '是' : detailFormData.stream_events === false ? '否' : '默认' }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="是否存储事件" :span="2">
            <el-tag :type="detailFormData.store_events === true ? 'success' : detailFormData.store_events === false ? 'danger' : undefined">{{ detailFormData.store_events === true ? '是' : detailFormData.store_events === false ? '否' : '默认' }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="是否输出Markdown格式" :span="2">
            <el-tag :type="detailFormData.markdown === true ? 'success' : detailFormData.markdown === false ? 'danger' : undefined">{{ detailFormData.markdown === true ? '是' : detailFormData.markdown === false ? '否' : '默认' }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="是否生成追问" :span="2">
            <el-tag :type="detailFormData.followups === true ? 'success' : detailFormData.followups === false ? 'danger' : undefined">{{ detailFormData.followups === true ? '是' : detailFormData.followups === false ? '否' : '默认' }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="追问数量" :span="2">
            {{ detailFormData.num_followups }}
          </el-descriptions-item>
          <el-descriptions-item label="是否开启调试模式" :span="2">
            <el-tag :type="detailFormData.debug_mode === true ? 'success' : detailFormData.debug_mode === false ? 'danger' : undefined">{{ detailFormData.debug_mode === true ? '是' : detailFormData.debug_mode === false ? '否' : '默认' }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="调试级别" :span="2">
            {{ detailFormData.debug_level }}
          </el-descriptions-item>
          <el-descriptions-item label="是否对外暴露A2A接口" :span="2">
            <el-tag :type="detailFormData.a2a_enabled === true ? 'success' : detailFormData.a2a_enabled === false ? 'danger' : undefined">{{ detailFormData.a2a_enabled === true ? '是' : detailFormData.a2a_enabled === false ? '否' : '默认' }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="是否为远程Agent" :span="2">
            <el-tag :type="detailFormData.is_remote === true ? 'success' : detailFormData.is_remote === false ? 'danger' : undefined">{{ detailFormData.is_remote === true ? '是' : detailFormData.is_remote === false ? '否' : '默认' }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="远程Agent地址" :span="2">
            {{ detailFormData.remote_url }}
          </el-descriptions-item>
          <el-descriptions-item label="远程Agent标识符" :span="2">
            {{ detailFormData.remote_agent_id }}
          </el-descriptions-item>
          <el-descriptions-item label="元数据" :span="4">
            <pre style="margin: 0; white-space: pre-wrap; font-size: 12px">{{ JSON.stringify(detailFormData.metadata, null, 2) }}</pre>
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
          label-width="160px"
          label-position="right"
        >
          <el-tabs type="border-card" class="agent-form-tabs">
            <!-- ══ Tab 1: 基本信息 ══ -->
            <el-tab-pane label="基本信息">
              <el-row :gutter="20">
                <el-col :span="12">
                  <el-form-item label="Agent名称" prop="name">
                    <el-input v-model="formData.name" placeholder="请输入Agent名称" />
                  </el-form-item>
                </el-col>
                <el-col :span="12">
                  <el-form-item label="主模型" prop="model_id">
                    <el-select v-model="formData.model_id" placeholder="请选择主模型" style="width:100%" clearable filterable>
                      <el-option v-for="model in modelList" :key="model.id" :label="model.name" :value="String(model.id)" />
                    </el-select>
                  </el-form-item>
                </el-col>
                <el-col :span="12">
                  <el-form-item label="状态" prop="status">
                    <el-radio-group v-model="formData.status">
                      <el-radio value="0">启用</el-radio>
                      <el-radio value="1">停用</el-radio>
                    </el-radio-group>
                  </el-form-item>
                </el-col>
                <el-col :span="24">
                  <el-form-item label="Agent指令" prop="instructions">
                    <el-input v-model="formData.instructions" placeholder="请输入Agent指令（system prompt）" type="textarea" :rows="4" />
                  </el-form-item>
                </el-col>
                <el-col :span="24">
                  <el-form-item label="期望输出格式" prop="expected_output">
                    <el-input v-model="formData.expected_output" placeholder="请输入期望输出格式说明" type="textarea" :rows="2" />
                  </el-form-item>
                </el-col>
                <el-col :span="24">
                  <el-form-item label="附加上下文" prop="additional_context">
                    <el-input v-model="formData.additional_context" placeholder="请输入附加上下文" type="textarea" :rows="2" />
                  </el-form-item>
                </el-col>
                <el-col :span="24">
                  <el-form-item label="描述" prop="description">
                    <el-input v-model="formData.description" :rows="3" :maxlength="100" show-word-limit type="textarea" placeholder="请输入描述" />
                  </el-form-item>
                </el-col>
              </el-row>
            </el-tab-pane>

            <!-- ══ Tab 2: 推理 & 学习 & 知识库 ══ -->
            <el-tab-pane label="推理 / 学习 / 知识库">
              <el-row :gutter="20">
                <!-- 推理 -->
                <el-col :span="12">
                  <el-form-item label="开启推理" prop="reasoning">
                    <el-select v-model="formData.reasoning" placeholder="默认" clearable style="width:100%">
                      <el-option label="开启" :value="true" />
                      <el-option label="关闭" :value="false" />
                    </el-select>
                  </el-form-item>
                </el-col>
                <el-col :span="12">
                  <el-form-item label="推理模型" prop="reasoning_model_id">
                    <el-select v-model="formData.reasoning_model_id" placeholder="请选择推理模型" style="width:100%" clearable filterable>
                      <el-option v-for="model in modelList" :key="model.id" :label="model.name" :value="String(model.id)" />
                    </el-select>
                  </el-form-item>
                </el-col>
                <el-col :span="12">
                  <el-form-item label="推理配置ID" prop="reasoning_config_id">
                    <el-select v-model="formData.reasoning_config_id" placeholder="请选择推理配置" clearable filterable style="width: 100%">
                      <el-option v-for="item in reasoningConfigList" :key="item.id" :label="item.name" :value="String(item.id)" />
                    </el-select>
                  </el-form-item>
                </el-col>
                <el-col :span="12">
                  <el-form-item label="最少推理步数" prop="reasoning_min_steps">
                    <el-input v-model="formData.reasoning_min_steps" placeholder="最少步数" />
                  </el-form-item>
                </el-col>
                <el-col :span="12">
                  <el-form-item label="最多推理步数" prop="reasoning_max_steps">
                    <el-input v-model="formData.reasoning_max_steps" placeholder="最多步数" />
                  </el-form-item>
                </el-col>
                <!-- 学习 -->
                <el-col :span="12">
                  <el-form-item label="开启学习" prop="learning">
                    <el-select v-model="formData.learning" placeholder="默认" clearable style="width:100%">
                      <el-option label="开启" :value="true" />
                      <el-option label="关闭" :value="false" />
                    </el-select>
                  </el-form-item>
                </el-col>
                <el-col :span="12">
                  <el-form-item label="学习机配置ID" prop="learning_config_id">
                    <el-select v-model="formData.learning_config_id" placeholder="请选择学习机配置" clearable filterable style="width: 100%">
                      <el-option v-for="item in learningConfigList" :key="item.id" :label="item.name" :value="String(item.id)" />
                    </el-select>
                  </el-form-item>
                </el-col>
                <!-- 知识库 -->
                <el-col :span="12">
                  <el-form-item label="搜索知识库" prop="search_knowledge">
                    <el-select v-model="formData.search_knowledge" placeholder="默认" clearable style="width:100%">
                      <el-option label="开启" :value="true" />
                      <el-option label="关闭" :value="false" />
                    </el-select>
                  </el-form-item>
                </el-col>
                <el-col :span="12">
                  <el-form-item label="允许更新知识库" prop="update_knowledge">
                    <el-select v-model="formData.update_knowledge" placeholder="默认" clearable style="width:100%">
                      <el-option label="开启" :value="true" />
                      <el-option label="关闭" :value="false" />
                    </el-select>
                  </el-form-item>
                </el-col>
                <el-col :span="12">
                  <el-form-item label="知识库加入上下文" prop="add_knowledge_to_context">
                    <el-select v-model="formData.add_knowledge_to_context" placeholder="默认" clearable style="width:100%">
                      <el-option label="开启" :value="true" />
                      <el-option label="关闭" :value="false" />
                    </el-select>
                  </el-form-item>
                </el-col>
                <el-col :span="12">
                  <el-form-item label="智能知识过滤" prop="enable_agentic_knowledge_filters">
                    <el-select v-model="formData.enable_agentic_knowledge_filters" placeholder="默认" clearable style="width:100%">
                      <el-option label="开启" :value="true" />
                      <el-option label="关闭" :value="false" />
                    </el-select>
                  </el-form-item>
                </el-col>
              </el-row>
            </el-tab-pane>

            <!-- ══ Tab 3: 记忆 & 历史 & 会话摘要 ══ -->
            <el-tab-pane label="记忆 / 历史 / 会话">
              <el-row :gutter="20">
                <!-- 记忆 -->
                <el-col :span="12">
                  <el-form-item label="开启智能记忆" prop="enable_agentic_memory">
                    <el-select v-model="formData.enable_agentic_memory" placeholder="默认" clearable style="width:100%">
                      <el-option label="开启" :value="true" />
                      <el-option label="关闭" :value="false" />
                    </el-select>
                  </el-form-item>
                </el-col>
                <el-col :span="12">
                  <el-form-item label="记忆管理器ID" prop="memory_manager_id">
                    <el-select v-model="formData.memory_manager_id" placeholder="请选择记忆管理器" clearable filterable style="width: 100%">
                      <el-option v-for="item in memoryManagerList" :key="item.id" :label="item.name" :value="String(item.id)" />
                    </el-select>
                  </el-form-item>
                </el-col>
                <el-col :span="12">
                  <el-form-item label="运行后更新记忆" prop="update_memory_on_run">
                    <el-select v-model="formData.update_memory_on_run" placeholder="默认" clearable style="width:100%">
                      <el-option label="开启" :value="true" />
                      <el-option label="关闭" :value="false" />
                    </el-select>
                  </el-form-item>
                </el-col>
                <el-col :span="12">
                  <el-form-item label="记忆加入上下文" prop="add_memories_to_context">
                    <el-select v-model="formData.add_memories_to_context" placeholder="默认" clearable style="width:100%">
                      <el-option label="开启" :value="true" />
                      <el-option label="关闭" :value="false" />
                    </el-select>
                  </el-form-item>
                </el-col>
                <!-- 状态 & 历史 -->
                <el-col :span="12">
                  <el-form-item label="开启智能状态" prop="enable_agentic_state">
                    <el-select v-model="formData.enable_agentic_state" placeholder="默认" clearable style="width:100%">
                      <el-option label="开启" :value="true" />
                      <el-option label="关闭" :value="false" />
                    </el-select>
                  </el-form-item>
                </el-col>
                <el-col :span="12">
                  <el-form-item label="历史记录加入上下文" prop="add_history_to_context">
                    <el-select v-model="formData.add_history_to_context" placeholder="默认" clearable style="width:100%">
                      <el-option label="开启" :value="true" />
                      <el-option label="关闭" :value="false" />
                    </el-select>
                  </el-form-item>
                </el-col>
                <el-col :span="12">
                  <el-form-item label="历史运行次数" prop="num_history_runs">
                    <el-input v-model="formData.num_history_runs" placeholder="加入上下文的历史运行次数" />
                  </el-form-item>
                </el-col>
                <el-col :span="12">
                  <el-form-item label="历史消息数" prop="num_history_messages">
                    <el-input v-model="formData.num_history_messages" placeholder="加入上下文的历史消息数" />
                  </el-form-item>
                </el-col>
                <el-col :span="12">
                  <el-form-item label="搜索历史会话" prop="search_past_sessions">
                    <el-select v-model="formData.search_past_sessions" placeholder="默认" clearable style="width:100%">
                      <el-option label="开启" :value="true" />
                      <el-option label="关闭" :value="false" />
                    </el-select>
                  </el-form-item>
                </el-col>
                <el-col :span="12">
                  <el-form-item label="搜索历史会话数量" prop="num_past_sessions_to_search">
                    <el-input v-model="formData.num_past_sessions_to_search" placeholder="请输入搜索历史会话数量" />
                  </el-form-item>
                </el-col>
                <!-- 会话摘要 -->
                <el-col :span="12">
                  <el-form-item label="开启会话摘要" prop="enable_session_summaries">
                    <el-select v-model="formData.enable_session_summaries" placeholder="默认" clearable style="width:100%">
                      <el-option label="开启" :value="true" />
                      <el-option label="关闭" :value="false" />
                    </el-select>
                  </el-form-item>
                </el-col>
                <el-col :span="12">
                  <el-form-item label="摘要加入上下文" prop="add_session_summary_to_context">
                    <el-select v-model="formData.add_session_summary_to_context" placeholder="默认" clearable style="width:100%">
                      <el-option label="开启" :value="true" />
                      <el-option label="关闭" :value="false" />
                    </el-select>
                  </el-form-item>
                </el-col>
                <el-col :span="12">
                  <el-form-item label="会话摘要配置ID" prop="session_summary_config_id">
                    <el-select v-model="formData.session_summary_config_id" placeholder="请选择会话摘要配置" clearable filterable style="width: 100%">
                      <el-option v-for="item in sessSummaryConfigList" :key="item.id" :label="item.name" :value="String(item.id)" />
                    </el-select>
                  </el-form-item>
                </el-col>
              </el-row>
            </el-tab-pane>

            <!-- ══ Tab 4: 输出格式 & 工具 & 压缩 ══ -->
            <el-tab-pane label="输出 / 工具">
              <el-row :gutter="20">
                <el-col :span="12">
                  <el-form-item label="输出模型" prop="output_model_id">
                    <el-select v-model="formData.output_model_id" placeholder="请选择输出模型" style="width:100%" clearable filterable>
                      <el-option v-for="model in modelList" :key="model.id" :label="model.name" :value="String(model.id)" />
                    </el-select>
                  </el-form-item>
                </el-col>
                <el-col :span="12">
                  <el-form-item label="JSON输出模式" prop="use_json_mode">
                    <el-select v-model="formData.use_json_mode" placeholder="默认" clearable style="width:100%">
                      <el-option label="开启" :value="true" />
                      <el-option label="关闭" :value="false" />
                    </el-select>
                  </el-form-item>
                </el-col>
                <el-col :span="12">
                  <el-form-item label="结构化输出" prop="structured_outputs">
                    <el-select v-model="formData.structured_outputs" placeholder="默认" clearable style="width:100%">
                      <el-option label="开启" :value="true" />
                      <el-option label="关闭" :value="false" />
                    </el-select>
                  </el-form-item>
                </el-col>
                <el-col :span="12">
                  <el-form-item label="解析响应" prop="parse_response">
                    <el-select v-model="formData.parse_response" placeholder="默认" clearable style="width:100%">
                      <el-option label="开启" :value="true" />
                      <el-option label="关闭" :value="false" />
                    </el-select>
                  </el-form-item>
                </el-col>
                <el-col :span="12">
                  <el-form-item label="解析模型" prop="parser_model_id">
                    <el-select v-model="formData.parser_model_id" placeholder="请选择解析模型" style="width:100%" clearable filterable>
                      <el-option v-for="model in modelList" :key="model.id" :label="model.name" :value="String(model.id)" />
                    </el-select>
                  </el-form-item>
                </el-col>
                <el-col :span="12">
                  <el-form-item label="工具调用次数上限" prop="tool_call_limit">
                    <el-input v-model="formData.tool_call_limit" placeholder="请输入工具调用次数上限" />
                  </el-form-item>
                </el-col>
                <el-col :span="12">
                  <el-form-item label="工具选择策略" prop="tool_choice">
                    <el-select v-model="formData.tool_choice" placeholder="请选择" clearable style="width:100%">
                      <el-option label="auto" value="auto" />
                      <el-option label="none" value="none" />
                      <el-option label="specific" value="specific" />
                    </el-select>
                  </el-form-item>
                </el-col>
                <el-col :span="12">
                  <el-form-item label="压缩工具结果" prop="compress_tool_results">
                    <el-select v-model="formData.compress_tool_results" placeholder="默认" clearable style="width:100%">
                      <el-option label="开启" :value="true" />
                      <el-option label="关闭" :value="false" />
                    </el-select>
                  </el-form-item>
                </el-col>
                <el-col :span="12">
                  <el-form-item label="压缩管理器配置ID" prop="compression_config_id">
                    <el-select v-model="formData.compression_config_id" placeholder="请选择压缩配置" clearable filterable style="width: 100%">
                      <el-option v-for="item in compressionConfigList" :key="item.id" :label="item.name" :value="String(item.id)" />
                    </el-select>
                  </el-form-item>
                </el-col>
                <el-col :span="12">
                  <el-form-item label="文化管理器配置ID" prop="culture_config_id">
                    <el-select v-model="formData.culture_config_id" placeholder="请选择文化管理器配置" clearable filterable style="width: 100%">
                      <el-option v-for="item in cultureConfigList" :key="item.id" :label="item.name" :value="String(item.id)" />
                    </el-select>
                  </el-form-item>
                </el-col>
                <el-col :span="24">
                  <el-form-item label="输出 JSON Schema" prop="output_schema">
                    <DictEditor v-model="formData.output_schema" />
                  </el-form-item>
                </el-col>
                <el-col :span="24">
                  <el-form-item label="输入 JSON Schema" prop="input_schema">
                    <DictEditor v-model="formData.input_schema" />
                  </el-form-item>
                </el-col>
              </el-row>
            </el-tab-pane>

            <!-- ══ Tab 5: 流式 / 重试 / 调试 / 远程 ══ -->
            <el-tab-pane label="流式 / 重试 / 调试">
              <el-row :gutter="20">
                <!-- 流式 -->
                <el-col :span="12">
                  <el-form-item label="流式输出" prop="stream">
                    <el-select v-model="formData.stream" placeholder="默认" clearable style="width:100%">
                      <el-option label="开启" :value="true" />
                      <el-option label="关闭" :value="false" />
                    </el-select>
                  </el-form-item>
                </el-col>
                <el-col :span="12">
                  <el-form-item label="流式推送事件" prop="stream_events">
                    <el-select v-model="formData.stream_events" placeholder="默认" clearable style="width:100%">
                      <el-option label="开启" :value="true" />
                      <el-option label="关闭" :value="false" />
                    </el-select>
                  </el-form-item>
                </el-col>
                <el-col :span="12">
                  <el-form-item label="存储事件" prop="store_events">
                    <el-select v-model="formData.store_events" placeholder="默认" clearable style="width:100%">
                      <el-option label="开启" :value="true" />
                      <el-option label="关闭" :value="false" />
                    </el-select>
                  </el-form-item>
                </el-col>
                <el-col :span="12">
                  <el-form-item label="Markdown输出" prop="markdown">
                    <el-select v-model="formData.markdown" placeholder="默认" clearable style="width:100%">
                      <el-option label="开启" :value="true" />
                      <el-option label="关闭" :value="false" />
                    </el-select>
                  </el-form-item>
                </el-col>
                <el-col :span="12">
                  <el-form-item label="生成追问" prop="followups">
                    <el-select v-model="formData.followups" placeholder="默认" clearable style="width:100%">
                      <el-option label="开启" :value="true" />
                      <el-option label="关闭" :value="false" />
                    </el-select>
                  </el-form-item>
                </el-col>
                <el-col :span="12">
                  <el-form-item label="追问数量" prop="num_followups">
                    <el-input v-model="formData.num_followups" placeholder="请输入追问数量" />
                  </el-form-item>
                </el-col>
                <!-- 上下文附加 -->
                <el-col :span="12">
                  <el-form-item label="时间加入上下文" prop="add_datetime_to_context">
                    <el-select v-model="formData.add_datetime_to_context" placeholder="默认" clearable style="width:100%">
                      <el-option label="开启" :value="true" />
                      <el-option label="关闭" :value="false" />
                    </el-select>
                  </el-form-item>
                </el-col>
                <el-col :span="12">
                  <el-form-item label="名称加入上下文" prop="add_name_to_context">
                    <el-select v-model="formData.add_name_to_context" placeholder="默认" clearable style="width:100%">
                      <el-option label="开启" :value="true" />
                      <el-option label="关闭" :value="false" />
                    </el-select>
                  </el-form-item>
                </el-col>
                <!-- 重试 -->
                <el-col :span="8">
                  <el-form-item label="失败重试次数" prop="retries">
                    <el-input v-model="formData.retries" placeholder="次数" />
                  </el-form-item>
                </el-col>
                <el-col :span="8">
                  <el-form-item label="重试间隔(秒)" prop="delay_between_retries">
                    <el-input v-model="formData.delay_between_retries" placeholder="秒数" />
                  </el-form-item>
                </el-col>
                <el-col :span="8">
                  <el-form-item label="指数退避重试" prop="exponential_backoff">
                    <el-select v-model="formData.exponential_backoff" placeholder="默认" clearable style="width:100%">
                      <el-option label="开启" :value="true" />
                      <el-option label="关闭" :value="false" />
                    </el-select>
                  </el-form-item>
                </el-col>
                <!-- 调试 -->
                <el-col :span="12">
                  <el-form-item label="调试模式" prop="debug_mode">
                    <el-select v-model="formData.debug_mode" placeholder="默认" clearable style="width:100%">
                      <el-option label="开启" :value="true" />
                      <el-option label="关闭" :value="false" />
                    </el-select>
                  </el-form-item>
                </el-col>
                <el-col :span="12">
                  <el-form-item label="调试级别" prop="debug_level">
                    <el-input v-model="formData.debug_level" placeholder="请输入调试级别" />
                  </el-form-item>
                </el-col>
                <!-- A2A & 远程 -->
                <el-col :span="12">
                  <el-form-item label="暴露A2A接口" prop="a2a_enabled">
                    <el-select v-model="formData.a2a_enabled" placeholder="默认" clearable style="width:100%">
                      <el-option label="开启" :value="true" />
                      <el-option label="关闭" :value="false" />
                    </el-select>
                  </el-form-item>
                </el-col>
                <el-col :span="12">
                  <el-form-item label="远程Agent" prop="is_remote">
                    <el-select v-model="formData.is_remote" placeholder="默认" clearable style="width:100%">
                      <el-option label="是" :value="true" />
                      <el-option label="否" :value="false" />
                    </el-select>
                  </el-form-item>
                </el-col>
                <el-col :span="12">
                  <el-form-item label="远程Agent地址" prop="remote_url">
                    <el-input v-model="formData.remote_url" placeholder="请输入远程Agent地址" />
                  </el-form-item>
                </el-col>
                <el-col :span="12">
                  <el-form-item label="远程Agent标识符" prop="remote_agent_id">
                    <el-input v-model="formData.remote_agent_id" placeholder="请输入远程Agent标识符" />
                  </el-form-item>
                </el-col>
                <el-col :span="24">
                  <el-form-item label="元数据" prop="metadata">
                    <DictEditor v-model="formData.metadata" />
                  </el-form-item>
                </el-col>
              </el-row>
            </el-tab-pane>

          </el-tabs>
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
  name: "AgAgent",
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
import AgAgentAPI, {
  AgAgentPageQuery,
  AgAgentTable,
  AgAgentForm,
} from "@/api/module_agno_manage/agents";
import AgModelAPI, { AgModelTable } from "@/api/module_agno_manage/models";
import AgMemoryManagerAPI, { AgMemoryManagerTable } from "@/api/module_agno_manage/memory_managers";
import AgReasoningConfigAPI, { AgReasoningConfigTable } from "@/api/module_agno_manage/reasoning_configs";
import AgLearningConfigAPI, { AgLearningConfigTable } from "@/api/module_agno_manage/learning_configs";
import AgSessSummaryConfigAPI, { AgSessSummaryConfigTable } from "@/api/module_agno_manage/sess_summary_configs";
import AgCultureConfigAPI, { AgCultureConfigTable } from "@/api/module_agno_manage/culture_configs";
import AgCompressionConfigAPI, { AgCompressionConfigTable } from "@/api/module_agno_manage/compression_configs";
import DictEditor from "@/views/module_agno_manage/components/DictEditor/index.vue";

// 模型列表（用于下拉选择）
const modelList = ref<AgModelTable[]>([]);
// 各配置列表（用于下拉选择）
const memoryManagerList = ref<AgMemoryManagerTable[]>([]);
const reasoningConfigList = ref<AgReasoningConfigTable[]>([]);
const learningConfigList = ref<AgLearningConfigTable[]>([]);
const sessSummaryConfigList = ref<AgSessSummaryConfigTable[]>([]);
const cultureConfigList = ref<AgCultureConfigTable[]>([]);
const compressionConfigList = ref<AgCompressionConfigTable[]>([]);

const visible = ref(false);
const queryFormRef = ref();
const dataFormRef = ref();
const total = ref(0);
const selectIds = ref<number[]>([]);
const selectionRows = ref<AgAgentTable[]>([]);
const loading = ref(false);
const isExpand = ref(false);
const isExpandable = ref(true);

// 分页表单
const pageTableData = ref<AgAgentTable[]>([]);

// 表格列配置
const tableColumns = ref([
  { prop: "selection", label: "选择框", show: true },
  { prop: "index", label: "序号", show: true },
  { prop: "name", label: "Agent名称", show: true },
  { prop: "model_id", label: "主模型ID", show: true },
  { prop: "reasoning_model_id", label: "推理模型ID", show: true },
  { prop: "output_model_id", label: "输出模型ID（response_model）", show: true },
  { prop: "parser_model_id", label: "解析模型ID", show: true },
  { prop: "memory_manager_id", label: "记忆管理器ID", show: true },
  { prop: "learning_config_id", label: "学习机配置ID", show: true },
  { prop: "reasoning_config_id", label: "推理配置ID", show: true },
  { prop: "compression_config_id", label: "压缩管理器配置ID", show: true },
  { prop: "session_summary_config_id", label: "会话摘要配置ID", show: true },
  { prop: "culture_config_id", label: "文化管理器配置ID", show: true },
  { prop: "instructions", label: "Agent指令（system prompt）", show: true },
  { prop: "expected_output", label: "期望输出格式说明", show: true },
  { prop: "additional_context", label: "附加上下文", show: true },
  { prop: "reasoning", label: "是否开启推理", show: true },
  { prop: "reasoning_min_steps", label: "最少推理步数", show: true },
  { prop: "reasoning_max_steps", label: "最多推理步数", show: true },
  { prop: "learning", label: "是否开启学习", show: true },
  { prop: "search_knowledge", label: "是否搜索知识库", show: true },
  { prop: "update_knowledge", label: "是否允许更新知识库", show: true },
  { prop: "add_knowledge_to_context", label: "是否将知识库内容加入上下文", show: true },
  { prop: "enable_agentic_knowledge_filters", label: "是否开启智能知识过滤", show: true },
  { prop: "enable_agentic_state", label: "是否开启智能状态", show: true },
  { prop: "enable_agentic_memory", label: "是否开启智能记忆", show: true },
  { prop: "update_memory_on_run", label: "是否每次运行后更新记忆", show: true },
  { prop: "add_memories_to_context", label: "是否将记忆加入上下文", show: true },
  { prop: "add_history_to_context", label: "是否将历史记录加入上下文", show: true },
  { prop: "num_history_runs", label: "加入上下文的历史运行次数", show: true },
  { prop: "num_history_messages", label: "加入上下文的历史消息数", show: true },
  { prop: "search_past_sessions", label: "是否搜索历史会话", show: true },
  { prop: "num_past_sessions_to_search", label: "搜索历史会话数量", show: true },
  { prop: "enable_session_summaries", label: "是否开启会话摘要", show: true },
  { prop: "add_session_summary_to_context", label: "是否将会话摘要加入上下文", show: true },
  { prop: "tool_call_limit", label: "工具调用次数上限", show: true },
  { prop: "tool_choice", label: "工具选择策略(none/auto/specific)", show: true },
  { prop: "output_schema", label: "输出结构体JSON Schema", show: true },
  { prop: "input_schema", label: "输入结构体JSON Schema", show: true },
  { prop: "use_json_mode", label: "是否使用JSON输出模式", show: true },
  { prop: "structured_outputs", label: "是否使用结构化输出", show: true },
  { prop: "parse_response", label: "是否解析响应", show: true },
  { prop: "retries", label: "失败重试次数", show: true },
  { prop: "delay_between_retries", label: "重试间隔秒数", show: true },
  { prop: "exponential_backoff", label: "是否指数退避重试", show: true },
  { prop: "add_datetime_to_context", label: "是否将当前时间加入上下文", show: true },
  { prop: "add_name_to_context", label: "是否将Agent名称加入上下文", show: true },
  { prop: "compress_tool_results", label: "是否压缩工具结果", show: true },
  { prop: "stream", label: "是否开启流式输出", show: true },
  { prop: "stream_events", label: "是否流式推送事件", show: true },
  { prop: "store_events", label: "是否存储事件", show: true },
  { prop: "markdown", label: "是否输出Markdown格式", show: true },
  { prop: "followups", label: "是否生成追问", show: true },
  { prop: "num_followups", label: "追问数量", show: true },
  { prop: "debug_mode", label: "是否开启调试模式", show: true },
  { prop: "debug_level", label: "调试级别", show: true },
  { prop: "a2a_enabled", label: "是否对外暴露A2A接口", show: true },
  { prop: "is_remote", label: "是否为远程Agent", show: true },
  { prop: "remote_url", label: "远程Agent地址", show: true },
  { prop: "remote_agent_id", label: "远程Agent标识符", show: true },
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
  { prop: "name", label: "Agent名称" },
  { prop: "model_id", label: "主模型ID" },
  { prop: "reasoning_model_id", label: "推理模型ID" },
  { prop: "output_model_id", label: "输出模型ID（response_model）" },
  { prop: "parser_model_id", label: "解析模型ID" },
  { prop: "memory_manager_id", label: "记忆管理器ID" },
  { prop: "learning_config_id", label: "学习机配置ID" },
  { prop: "reasoning_config_id", label: "推理配置ID" },
  { prop: "compression_config_id", label: "压缩管理器配置ID" },
  { prop: "session_summary_config_id", label: "会话摘要配置ID" },
  { prop: "culture_config_id", label: "文化管理器配置ID" },
  { prop: "instructions", label: "Agent指令（system prompt）" },
  { prop: "expected_output", label: "期望输出格式说明" },
  { prop: "additional_context", label: "附加上下文" },
  { prop: "reasoning", label: "是否开启推理" },
  { prop: "reasoning_min_steps", label: "最少推理步数" },
  { prop: "reasoning_max_steps", label: "最多推理步数" },
  { prop: "learning", label: "是否开启学习" },
  { prop: "search_knowledge", label: "是否搜索知识库" },
  { prop: "update_knowledge", label: "是否允许更新知识库" },
  { prop: "add_knowledge_to_context", label: "是否将知识库内容加入上下文" },
  { prop: "enable_agentic_knowledge_filters", label: "是否开启智能知识过滤" },
  { prop: "enable_agentic_state", label: "是否开启智能状态" },
  { prop: "enable_agentic_memory", label: "是否开启智能记忆" },
  { prop: "update_memory_on_run", label: "是否每次运行后更新记忆" },
  { prop: "add_memories_to_context", label: "是否将记忆加入上下文" },
  { prop: "add_history_to_context", label: "是否将历史记录加入上下文" },
  { prop: "num_history_runs", label: "加入上下文的历史运行次数" },
  { prop: "num_history_messages", label: "加入上下文的历史消息数" },
  { prop: "search_past_sessions", label: "是否搜索历史会话" },
  { prop: "num_past_sessions_to_search", label: "搜索历史会话数量" },
  { prop: "enable_session_summaries", label: "是否开启会话摘要" },
  { prop: "add_session_summary_to_context", label: "是否将会话摘要加入上下文" },
  { prop: "tool_call_limit", label: "工具调用次数上限" },
  { prop: "tool_choice", label: "工具选择策略(none/auto/specific)" },
  { prop: "output_schema", label: "输出结构体JSON Schema" },
  { prop: "input_schema", label: "输入结构体JSON Schema" },
  { prop: "use_json_mode", label: "是否使用JSON输出模式" },
  { prop: "structured_outputs", label: "是否使用结构化输出" },
  { prop: "parse_response", label: "是否解析响应" },
  { prop: "retries", label: "失败重试次数" },
  { prop: "delay_between_retries", label: "重试间隔秒数" },
  { prop: "exponential_backoff", label: "是否指数退避重试" },
  { prop: "add_datetime_to_context", label: "是否将当前时间加入上下文" },
  { prop: "add_name_to_context", label: "是否将Agent名称加入上下文" },
  { prop: "compress_tool_results", label: "是否压缩工具结果" },
  { prop: "stream", label: "是否开启流式输出" },
  { prop: "stream_events", label: "是否流式推送事件" },
  { prop: "store_events", label: "是否存储事件" },
  { prop: "markdown", label: "是否输出Markdown格式" },
  { prop: "followups", label: "是否生成追问" },
  { prop: "num_followups", label: "追问数量" },
  { prop: "debug_mode", label: "是否开启调试模式" },
  { prop: "debug_level", label: "调试级别" },
  { prop: "a2a_enabled", label: "是否对外暴露A2A接口" },
  { prop: "is_remote", label: "是否为远程Agent" },
  { prop: "remote_url", label: "远程Agent地址" },
  { prop: "remote_agent_id", label: "远程Agent标识符" },
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
  permPrefix: "module_agno_manage:agents",
  cols: exportColumns as any,
  importTemplate: () => AgAgentAPI.downloadTemplateAgAgent(),
  exportsAction: async (params: any) => {
    const query: any = { ...params };
    query.status = "0";
    query.page_no = 1;
    query.page_size = 9999;
    const all: any[] = [];
    while (true) {
      const res = await AgAgentAPI.listAgAgent(query);
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
const detailFormData = ref<AgAgentTable>({});
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
const queryFormData = reactive<AgAgentPageQuery>({
  page_no: 1,
  page_size: 10,
  name: undefined,
  model_id: undefined,
  reasoning_model_id: undefined,
  output_model_id: undefined,
  parser_model_id: undefined,
  memory_manager_id: undefined,
  learning_config_id: undefined,
  reasoning_config_id: undefined,
  compression_config_id: undefined,
  session_summary_config_id: undefined,
  culture_config_id: undefined,
  instructions: undefined,
  expected_output: undefined,
  additional_context: undefined,
  reasoning: undefined,
  reasoning_min_steps: undefined,
  reasoning_max_steps: undefined,
  learning: undefined,
  search_knowledge: undefined,
  update_knowledge: undefined,
  add_knowledge_to_context: undefined,
  enable_agentic_knowledge_filters: undefined,
  enable_agentic_state: undefined,
  enable_agentic_memory: undefined,
  update_memory_on_run: undefined,
  add_memories_to_context: undefined,
  add_history_to_context: undefined,
  num_history_runs: undefined,
  num_history_messages: undefined,
  search_past_sessions: undefined,
  num_past_sessions_to_search: undefined,
  enable_session_summaries: undefined,
  add_session_summary_to_context: undefined,
  tool_call_limit: undefined,
  tool_choice: undefined,
  use_json_mode: undefined,
  structured_outputs: undefined,
  parse_response: undefined,
  retries: undefined,
  delay_between_retries: undefined,
  exponential_backoff: undefined,
  add_datetime_to_context: undefined,
  add_name_to_context: undefined,
  compress_tool_results: undefined,
  stream: undefined,
  stream_events: undefined,
  store_events: undefined,
  markdown: undefined,
  followups: undefined,
  num_followups: undefined,
  debug_mode: undefined,
  debug_level: undefined,
  a2a_enabled: undefined,
  is_remote: undefined,
  remote_url: undefined,
  remote_agent_id: undefined,
  status: undefined,
  created_time: undefined,
  updated_time: undefined,
  created_id: undefined,
  updated_id: undefined,
});

// 编辑表单
const formData = reactive<AgAgentForm>({
  id: undefined,
  name: undefined,
  model_id: undefined,
  reasoning_model_id: undefined,
  output_model_id: undefined,
  parser_model_id: undefined,
  memory_manager_id: undefined,
  learning_config_id: undefined,
  reasoning_config_id: undefined,
  compression_config_id: undefined,
  session_summary_config_id: undefined,
  culture_config_id: undefined,
  instructions: undefined,
  expected_output: undefined,
  additional_context: undefined,
  reasoning: undefined,
  reasoning_min_steps: undefined,
  reasoning_max_steps: undefined,
  learning: undefined,
  search_knowledge: undefined,
  update_knowledge: undefined,
  add_knowledge_to_context: undefined,
  enable_agentic_knowledge_filters: undefined,
  enable_agentic_state: undefined,
  enable_agentic_memory: undefined,
  update_memory_on_run: undefined,
  add_memories_to_context: undefined,
  add_history_to_context: undefined,
  num_history_runs: undefined,
  num_history_messages: undefined,
  search_past_sessions: undefined,
  num_past_sessions_to_search: undefined,
  enable_session_summaries: undefined,
  add_session_summary_to_context: undefined,
  tool_call_limit: undefined,
  tool_choice: undefined,
  output_schema: undefined,
  input_schema: undefined,
  use_json_mode: undefined,
  structured_outputs: undefined,
  parse_response: undefined,
  retries: undefined,
  delay_between_retries: undefined,
  exponential_backoff: undefined,
  add_datetime_to_context: undefined,
  add_name_to_context: undefined,
  compress_tool_results: undefined,
  stream: undefined,
  stream_events: undefined,
  store_events: undefined,
  markdown: undefined,
  followups: undefined,
  num_followups: undefined,
  debug_mode: undefined,
  debug_level: undefined,
  a2a_enabled: undefined,
  is_remote: undefined,
  remote_url: undefined,
  remote_agent_id: undefined,
  metadata: undefined,
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
  name: [{ required: true, message: "请输入Agent名称", trigger: "blur" }],
  model_id: [{ required: true, message: "请选择主模型", trigger: "change" }],
//  id: [{ required: false, message: "请输入id", trigger: "blur" }],
//  uuid: [{ required: false, message: "请输入uuid", trigger: "blur" }],
//  name: [{ required: false, message: "请输入Agent名称", trigger: "blur" }],
//  model_id: [{ required: true, message: "请输入主模型ID", trigger: "blur" }],
//  reasoning_model_id: [{ required: true, message: "请输入推理模型ID", trigger: "blur" }],
//  output_model_id: [{ required: true, message: "请输入输出模型ID（response_model）", trigger: "blur" }],
//  parser_model_id: [{ required: true, message: "请输入解析模型ID", trigger: "blur" }],
//  memory_manager_id: [{ required: true, message: "请输入记忆管理器ID", trigger: "blur" }],
//  learning_config_id: [{ required: true, message: "请输入学习机配置ID", trigger: "blur" }],
//  reasoning_config_id: [{ required: true, message: "请输入推理配置ID", trigger: "blur" }],
//  compression_config_id: [{ required: true, message: "请输入压缩管理器配置ID", trigger: "blur" }],
//  session_summary_config_id: [{ required: true, message: "请输入会话摘要配置ID", trigger: "blur" }],
//  culture_config_id: [{ required: true, message: "请输入文化管理器配置ID", trigger: "blur" }],
//  instructions: [{ required: true, message: "请输入Agent指令（system prompt）", trigger: "blur" }],
//  expected_output: [{ required: true, message: "请输入期望输出格式说明", trigger: "blur" }],
//  additional_context: [{ required: true, message: "请输入附加上下文", trigger: "blur" }],
//  reasoning: [{ required: false, message: "请输入是否开启推理", trigger: "blur" }],
//  reasoning_min_steps: [{ required: false, message: "请输入最少推理步数", trigger: "blur" }],
//  reasoning_max_steps: [{ required: false, message: "请输入最多推理步数", trigger: "blur" }],
//  learning: [{ required: false, message: "请输入是否开启学习", trigger: "blur" }],
//  search_knowledge: [{ required: false, message: "请输入是否搜索知识库", trigger: "blur" }],
//  update_knowledge: [{ required: false, message: "请输入是否允许更新知识库", trigger: "blur" }],
//  add_knowledge_to_context: [{ required: false, message: "请输入是否将知识库内容加入上下文", trigger: "blur" }],
//  enable_agentic_knowledge_filters: [{ required: false, message: "请输入是否开启智能知识过滤", trigger: "blur" }],
//  enable_agentic_state: [{ required: false, message: "请输入是否开启智能状态", trigger: "blur" }],
//  enable_agentic_memory: [{ required: false, message: "请输入是否开启智能记忆", trigger: "blur" }],
//  update_memory_on_run: [{ required: false, message: "请输入是否每次运行后更新记忆", trigger: "blur" }],
//  add_memories_to_context: [{ required: false, message: "请输入是否将记忆加入上下文", trigger: "blur" }],
//  add_history_to_context: [{ required: false, message: "请输入是否将历史记录加入上下文", trigger: "blur" }],
//  num_history_runs: [{ required: true, message: "请输入加入上下文的历史运行次数", trigger: "blur" }],
//  num_history_messages: [{ required: true, message: "请输入加入上下文的历史消息数", trigger: "blur" }],
//  search_past_sessions: [{ required: false, message: "请输入是否搜索历史会话", trigger: "blur" }],
//  num_past_sessions_to_search: [{ required: true, message: "请输入搜索历史会话数量", trigger: "blur" }],
//  enable_session_summaries: [{ required: false, message: "请输入是否开启会话摘要", trigger: "blur" }],
//  add_session_summary_to_context: [{ required: false, message: "请输入是否将会话摘要加入上下文", trigger: "blur" }],
//  tool_call_limit: [{ required: true, message: "请输入工具调用次数上限", trigger: "blur" }],
//  tool_choice: [{ required: true, message: "请输入工具选择策略(none/auto/specific)", trigger: "blur" }],
//  output_schema: [{ required: true, message: "请输入输出结构体JSON Schema", trigger: "blur" }],
//  input_schema: [{ required: true, message: "请输入输入结构体JSON Schema", trigger: "blur" }],
//  use_json_mode: [{ required: false, message: "请输入是否使用JSON输出模式", trigger: "blur" }],
//  structured_outputs: [{ required: true, message: "请输入是否使用结构化输出", trigger: "blur" }],
//  parse_response: [{ required: false, message: "请输入是否解析响应", trigger: "blur" }],
//  retries: [{ required: false, message: "请输入失败重试次数", trigger: "blur" }],
//  delay_between_retries: [{ required: false, message: "请输入重试间隔秒数", trigger: "blur" }],
//  exponential_backoff: [{ required: false, message: "请输入是否指数退避重试", trigger: "blur" }],
//  add_datetime_to_context: [{ required: false, message: "请输入是否将当前时间加入上下文", trigger: "blur" }],
//  add_name_to_context: [{ required: false, message: "请输入是否将Agent名称加入上下文", trigger: "blur" }],
//  compress_tool_results: [{ required: false, message: "请输入是否压缩工具结果", trigger: "blur" }],
//  stream: [{ required: false, message: "请输入是否开启流式输出", trigger: "blur" }],
//  stream_events: [{ required: false, message: "请输入是否流式推送事件", trigger: "blur" }],
//  store_events: [{ required: false, message: "请输入是否存储事件", trigger: "blur" }],
//  markdown: [{ required: false, message: "请输入是否输出Markdown格式", trigger: "blur" }],
//  followups: [{ required: false, message: "请输入是否生成追问", trigger: "blur" }],
//  num_followups: [{ required: false, message: "请输入追问数量", trigger: "blur" }],
//  debug_mode: [{ required: false, message: "请输入是否开启调试模式", trigger: "blur" }],
//  debug_level: [{ required: false, message: "请输入调试级别", trigger: "blur" }],
//  a2a_enabled: [{ required: false, message: "请输入是否对外暴露A2A接口", trigger: "blur" }],
//  is_remote: [{ required: false, message: "请输入是否为远程Agent", trigger: "blur" }],
//  remote_url: [{ required: true, message: "请输入远程Agent地址", trigger: "blur" }],
//  remote_agent_id: [{ required: true, message: "请输入远程Agent标识符", trigger: "blur" }],
//  metadata: [{ required: false, message: "请输入元数据", trigger: "blur" }],
//  status: [{ required: false, message: "请输入status", trigger: "blur" }],
//  description: [{ required: false, message: "请输入description", trigger: "blur" }],
//  created_time: [{ required: false, message: "请输入created_time", trigger: "blur" }],
//  updated_time: [{ required: false, message: "请输入updated_time", trigger: "blur" }],
//  created_id: [{ required: true, message: "请输入created_id", trigger: "blur" }],
//  updated_id: [{ required: true, message: "请输入updated_id", trigger: "blur" }],
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
    const response = await AgAgentAPI.listAgAgent(queryFormData);
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
const initialFormData: AgAgentForm = {
  id: undefined,
  name: undefined,
  model_id: undefined,
  reasoning_model_id: undefined,
  output_model_id: undefined,
  parser_model_id: undefined,
  memory_manager_id: undefined,
  learning_config_id: undefined,
  reasoning_config_id: undefined,
  compression_config_id: undefined,
  session_summary_config_id: undefined,
  culture_config_id: undefined,
  instructions: undefined,
  expected_output: undefined,
  additional_context: undefined,
  reasoning: undefined,
  reasoning_min_steps: undefined,
  reasoning_max_steps: undefined,
  learning: undefined,
  search_knowledge: undefined,
  update_knowledge: undefined,
  add_knowledge_to_context: undefined,
  enable_agentic_knowledge_filters: undefined,
  enable_agentic_state: undefined,
  enable_agentic_memory: undefined,
  update_memory_on_run: undefined,
  add_memories_to_context: undefined,
  add_history_to_context: undefined,
  num_history_runs: undefined,
  num_history_messages: undefined,
  search_past_sessions: undefined,
  num_past_sessions_to_search: undefined,
  enable_session_summaries: undefined,
  add_session_summary_to_context: undefined,
  tool_call_limit: undefined,
  tool_choice: undefined,
  output_schema: undefined,
  input_schema: undefined,
  use_json_mode: undefined,
  structured_outputs: undefined,
  parse_response: undefined,
  retries: undefined,
  delay_between_retries: undefined,
  exponential_backoff: undefined,
  add_datetime_to_context: undefined,
  add_name_to_context: undefined,
  compress_tool_results: undefined,
  stream: undefined,
  stream_events: undefined,
  store_events: undefined,
  markdown: undefined,
  followups: undefined,
  num_followups: undefined,
  debug_mode: undefined,
  debug_level: undefined,
  a2a_enabled: undefined,
  is_remote: undefined,
  remote_url: undefined,
  remote_agent_id: undefined,
  metadata: undefined,
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
    const response = await AgAgentAPI.detailAgAgent(id);
    if (type === "detail") {
      dialogVisible.title = "详情";
      Object.assign(detailFormData.value, response.data.data);
    } else if (type === "update") {
      dialogVisible.title = "修改";
      Object.assign(formData, response.data.data);
    }
  } else {
    dialogVisible.title = "新增AgAgent";
    formData.id = undefined;
    formData.name = undefined;
    formData.model_id = undefined;
    formData.reasoning_model_id = undefined;
    formData.output_model_id = undefined;
    formData.parser_model_id = undefined;
    formData.memory_manager_id = undefined;
    formData.learning_config_id = undefined;
    formData.reasoning_config_id = undefined;
    formData.compression_config_id = undefined;
    formData.session_summary_config_id = undefined;
    formData.culture_config_id = undefined;
    formData.instructions = undefined;
    formData.expected_output = undefined;
    formData.additional_context = undefined;
    formData.reasoning = undefined;
    formData.reasoning_min_steps = undefined;
    formData.reasoning_max_steps = undefined;
    formData.learning = undefined;
    formData.search_knowledge = undefined;
    formData.update_knowledge = undefined;
    formData.add_knowledge_to_context = undefined;
    formData.enable_agentic_knowledge_filters = undefined;
    formData.enable_agentic_state = undefined;
    formData.enable_agentic_memory = undefined;
    formData.update_memory_on_run = undefined;
    formData.add_memories_to_context = undefined;
    formData.add_history_to_context = undefined;
    formData.num_history_runs = undefined;
    formData.num_history_messages = undefined;
    formData.search_past_sessions = undefined;
    formData.num_past_sessions_to_search = undefined;
    formData.enable_session_summaries = undefined;
    formData.add_session_summary_to_context = undefined;
    formData.tool_call_limit = undefined;
    formData.tool_choice = undefined;
    formData.output_schema = undefined;
    formData.input_schema = undefined;
    formData.use_json_mode = undefined;
    formData.structured_outputs = undefined;
    formData.parse_response = undefined;
    formData.retries = undefined;
    formData.delay_between_retries = undefined;
    formData.exponential_backoff = undefined;
    formData.add_datetime_to_context = undefined;
    formData.add_name_to_context = undefined;
    formData.compress_tool_results = undefined;
    formData.stream = undefined;
    formData.stream_events = undefined;
    formData.store_events = undefined;
    formData.markdown = undefined;
    formData.followups = undefined;
    formData.num_followups = undefined;
    formData.debug_mode = undefined;
    formData.debug_level = undefined;
    formData.a2a_enabled = undefined;
    formData.is_remote = undefined;
    formData.remote_url = undefined;
    formData.remote_agent_id = undefined;
    formData.metadata = undefined;
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
      // 根据弹窗传入的参数(deatil\create\update)判断走什么逻辑
      // 过滤 null/undefined 字段，不传递给接口（null 表示"使用默认值"）
      const submitData = Object.fromEntries(
        Object.entries({ ...formData }).filter(([, v]) => v !== null && v !== undefined)
      ) as AgAgentForm;
      const id = formData.id;
      if (id) {
        try {
          await AgAgentAPI.updateAgAgent(id, { id, ...submitData });
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
          await AgAgentAPI.createAgAgent(submitData);
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
        await AgAgentAPI.deleteAgAgent(ids);
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
          await AgAgentAPI.batchAgAgent({ ids: selectIds.value, status });
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
    const response = await AgAgentAPI.importAgAgent(formData);
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

// 配置名称查找辅助函数
function getMemoryManagerName(id?: string | number): string {
  if (!id) return "-";
  const found = memoryManagerList.value.find((item) => String(item.id) === String(id));
  return found ? (found.name || String(id)) : String(id);
}
function getReasoningConfigName(id?: string | number): string {
  if (!id) return "-";
  const found = reasoningConfigList.value.find((item) => String(item.id) === String(id));
  return found ? (found.name || String(id)) : String(id);
}
function getLearningConfigName(id?: string | number): string {
  if (!id) return "-";
  const found = learningConfigList.value.find((item) => String(item.id) === String(id));
  return found ? (found.name || String(id)) : String(id);
}
function getSessSummaryConfigName(id?: string | number): string {
  if (!id) return "-";
  const found = sessSummaryConfigList.value.find((item) => String(item.id) === String(id));
  return found ? (found.name || String(id)) : String(id);
}
function getCultureConfigName(id?: string | number): string {
  if (!id) return "-";
  const found = cultureConfigList.value.find((item) => String(item.id) === String(id));
  return found ? (found.name || String(id)) : String(id);
}
function getCompressionConfigName(id?: string | number): string {
  if (!id) return "-";
  const found = compressionConfigList.value.find((item) => String(item.id) === String(id));
  return found ? (found.name || String(id)) : String(id);
}

onMounted(async () => {
  // 预加载字典数据
  if (dictTypes.length > 0) {
    await dictStore.getDict(dictTypes);
  }
  // 加载模型列表（分页全量加载）
  const allModels: AgModelTable[] = [];
  let page = 1;
  while (true) {
    const res = await AgModelAPI.listAgModel({ page_no: page, page_size: 100 });
    const items = res.data?.data?.items || [];
    const total = res.data?.data?.total || 0;
    allModels.push(...items);
    if (allModels.length >= total || items.length === 0) break;
    page++;
  }
  modelList.value = allModels;
  // 并行加载各配置列表
  await Promise.all([
    AgMemoryManagerAPI.listAgMemoryManager({ page_no: 1, page_size: 100 }).then((res) => {
      memoryManagerList.value = res.data?.data?.items || [];
    }),
    AgReasoningConfigAPI.listAgReasoningConfig({ page_no: 1, page_size: 100 }).then((res) => {
      reasoningConfigList.value = res.data?.data?.items || [];
    }),
    AgLearningConfigAPI.listAgLearningConfig({ page_no: 1, page_size: 100 }).then((res) => {
      learningConfigList.value = res.data?.data?.items || [];
    }),
    AgSessSummaryConfigAPI.listAgSessSummaryConfig({ page_no: 1, page_size: 100 }).then((res) => {
      sessSummaryConfigList.value = res.data?.data?.items || [];
    }),
    AgCultureConfigAPI.listAgCultureConfig({ page_no: 1, page_size: 100 }).then((res) => {
      cultureConfigList.value = res.data?.data?.items || [];
    }),
    AgCompressionConfigAPI.listAgCompressionConfig({ page_no: 1, page_size: 100 }).then((res) => {
      compressionConfigList.value = res.data?.data?.items || [];
    }),
  ]);
  loadingData();
});
</script>

<style lang="scss" scoped>
.agent-form-tabs {
  :deep(.el-tabs__content) {
    max-height: 60vh;
    overflow-y: auto;
    padding: 16px 8px;
  }

  :deep(.el-tab-pane) {
    .el-form-item {
      margin-bottom: 16px;
    }
  }
}
</style>
