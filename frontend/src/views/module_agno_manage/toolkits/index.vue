<!-- 工具管理 -->
<template>
  <div class="app-container">
    <!-- 内容区域 -->
    <el-card class="data-table">
      <template #header>
        <div class="card-header">
          <span>
            工具管理列表
            <el-tooltip content="工具管理列表">
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
            <el-form-item label="工具包名称" prop="name">
              <el-input v-model="queryFormData.name" placeholder="请输入工具包名称" clearable />
            </el-form-item>
            <el-form-item label="类型" prop="type">
              <el-select v-model="queryFormData.type" placeholder="请选择类型" clearable>
                <el-option value="toolkit" label="toolkit" />
                <el-option value="function" label="function" />
                <el-option value="code" label="code" />
              </el-select>
            </el-form-item>
            <el-form-item label="工具来源" prop="tool_from">
              <el-select v-model="queryFormData.tool_from" placeholder="请选择工具来源" clearable>
                <el-option value="agno" label="agno" />
                <el-option value="custom" label="custom" />
                <el-option value="code" label="code" />
              </el-select>
            </el-form-item>
            <el-form-item label="分类" prop="category">
              <el-input v-model="queryFormData.category" placeholder="请输入分类" clearable />
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
                v-hasPerm="['module_agno_manage:toolkits:query']"
                type="primary"
                icon="search"
                @click="handleQuery"
              >
                查询
              </el-button>
              <el-button
                v-hasPerm="['module_agno_manage:toolkits:query']"
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
                v-hasPerm="['module_agno_manage:toolkits:create']"
                type="success"
                icon="plus"
                @click="handleOpenDialog('create')"
              >
                新增
              </el-button>
            </el-col>
            <el-col :span="1.5">
              <el-button
                v-hasPerm="['module_agno_manage:toolkits:delete']"
                type="danger"
                icon="delete"
                :disabled="selectIds.length === 0"
                @click="handleDelete(selectIds)"
              >
                批量删除
              </el-button>
            </el-col>
            <el-col :span="1.5">
              <el-dropdown v-hasPerm="['module_agno_manage:toolkits:batch']" trigger="click">
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
                  v-hasPerm="['module_agno_manage:toolkits:import']"
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
                  v-hasPerm="['module_agno_manage:toolkits:export']"
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
                  v-hasPerm="['module_agno_manage:toolkits:query']"
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
          label="工具包名称"
          prop="name"
          min-width="140"
          show-overflow-tooltip
        />
        <el-table-column
          v-if="tableColumns.find((col) => col.prop === 'type')?.show"
          label="类型"
          prop="type"
          min-width="100"
          show-overflow-tooltip
        />
        <el-table-column
          v-if="tableColumns.find((col) => col.prop === 'tool_from')?.show"
          label="工具来源"
          prop="tool_from"
          min-width="100"
          show-overflow-tooltip
        />
        <el-table-column
          v-if="tableColumns.find((col) => col.prop === 'category')?.show"
          label="分类"
          prop="category"
          min-width="100"
          show-overflow-tooltip
        />
        <el-table-column
          v-if="tableColumns.find((col) => col.prop === 'global_enabled')?.show"
          label="全局开关"
          prop="global_enabled"
          min-width="100"
          align="center"
        >
          <template #default="scope">
            <el-tag :type="scope.row.global_enabled ? 'success' : 'danger'">
              {{ scope.row.global_enabled ? "启用" : "禁用" }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column
          v-if="tableColumns.find((col) => col.prop === 'module_path')?.show"
          label="Python模块路径"
          prop="module_path"
          min-width="140"
          show-overflow-tooltip
        />
        <el-table-column
          v-if="tableColumns.find((col) => col.prop === 'class_name')?.show"
          label="类名"
          prop="class_name"
          min-width="100"
          show-overflow-tooltip
        />
        <el-table-column
          v-if="tableColumns.find((col) => col.prop === 'func_name')?.show"
          label="函数名"
          prop="func_name"
          min-width="100"
          show-overflow-tooltip
        />
        <el-table-column
          v-if="tableColumns.find((col) => col.prop === 'config')?.show"
          label="初始化参数"
          prop="config"
          min-width="140"
          show-overflow-tooltip
        >
          <template #default="scope">
            {{ scope.row.config ? JSON.stringify(scope.row.config) : '-' }}
          </template>
        </el-table-column>
        <el-table-column
          v-if="tableColumns.find((col) => col.prop === 'instructions')?.show"
          label="工具使用说明"
          prop="instructions"
          min-width="140"
          show-overflow-tooltip
        />
        <el-table-column
          v-if="tableColumns.find((col) => col.prop === 'requires_confirmation')?.show"
          label="需要确认"
          prop="requires_confirmation"
          min-width="100"
          align="center"
        >
          <template #default="scope">
            <el-tag :type="scope.row.requires_confirmation === true ? 'success' : scope.row.requires_confirmation === false ? 'danger' : ''">
              {{ scope.row.requires_confirmation === true ? '是' : scope.row.requires_confirmation === false ? '否' : '默认' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column
          v-if="tableColumns.find((col) => col.prop === 'approval_type')?.show"
          label="审批类型"
          prop="approval_type"
          min-width="100"
          show-overflow-tooltip
        />
        <el-table-column
          v-if="tableColumns.find((col) => col.prop === 'stop_after_call')?.show"
          label="调用后停止"
          prop="stop_after_call"
          min-width="100"
          align="center"
        >
          <template #default="scope">
            <el-tag :type="scope.row.stop_after_call === true ? 'success' : scope.row.stop_after_call === false ? 'danger' : ''">
              {{ scope.row.stop_after_call === true ? '是' : scope.row.stop_after_call === false ? '否' : '默认' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column
          v-if="tableColumns.find((col) => col.prop === 'show_result')?.show"
          label="展示结果"
          prop="show_result"
          min-width="100"
          align="center"
        >
          <template #default="scope">
            <el-tag :type="scope.row.show_result === true ? 'success' : scope.row.show_result === false ? 'danger' : ''">
              {{ scope.row.show_result === true ? '是' : scope.row.show_result === false ? '否' : '默认' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column
          v-if="tableColumns.find((col) => col.prop === 'cache_results')?.show"
          label="缓存结果"
          prop="cache_results"
          min-width="100"
          align="center"
        >
          <template #default="scope">
            <el-tag :type="scope.row.cache_results === true ? 'success' : scope.row.cache_results === false ? 'danger' : ''">
              {{ scope.row.cache_results === true ? '是' : scope.row.cache_results === false ? '否' : '默认' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column
          v-if="tableColumns.find((col) => col.prop === 'cache_ttl')?.show"
          label="缓存TTL(秒)"
          prop="cache_ttl"
          min-width="100"
          show-overflow-tooltip
        />
        <el-table-column
          v-if="tableColumns.find((col) => col.prop === 'status')?.show"
          label="状态"
          prop="status"
          min-width="80"
          align="center"
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
          label="创建人"
          prop="created_id"
          min-width="100"
          align="center"
        >
          <template #default="scope">
            <el-tag>{{ scope.row.created_by?.name }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column
          v-if="tableColumns.find((col) => col.prop === 'updated_id')?.show"
          label="更新人"
          prop="updated_id"
          min-width="100"
          align="center"
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
              v-hasPerm="['module_agno_manage:toolkits:detail']"
              type="info"
              size="small"
              link
              icon="document"
              @click="handleOpenDialog('detail', scope.row.id)"
            >
              详情
            </el-button>
            <el-button
              v-hasPerm="['module_agno_manage:toolkits:update']"
              type="primary"
              size="small"
              link
              icon="edit"
              @click="handleOpenDialog('update', scope.row.id)"
            >
              编辑
            </el-button>
            <el-button
              v-hasPerm="['module_agno_manage:toolkits:delete']"
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
          <el-descriptions-item label="工具包名称" :span="2">
            {{ detailFormData.name }}
          </el-descriptions-item>
          <el-descriptions-item label="类型" :span="2">
            {{ detailFormData.type }}
          </el-descriptions-item>
          <el-descriptions-item label="工具来源" :span="2">
            {{ detailFormData.tool_from }}
          </el-descriptions-item>
          <el-descriptions-item label="分类" :span="2">
            {{ detailFormData.category }}
          </el-descriptions-item>
          <el-descriptions-item label="全局开关" :span="2">
            <el-tag :type="detailFormData.global_enabled ? 'success' : 'danger'">
              {{ detailFormData.global_enabled ? "启用" : "禁用" }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item v-if="detailFormData.type !== 'code'" label="Python模块路径" :span="4">
            {{ detailFormData.module_path }}
          </el-descriptions-item>
          <el-descriptions-item v-if="detailFormData.type === 'toolkit'" label="类名" :span="2">
            {{ detailFormData.class_name }}
          </el-descriptions-item>
          <el-descriptions-item v-if="detailFormData.type === 'function'" label="函数名" :span="2">
            {{ detailFormData.func_name }}
          </el-descriptions-item>
          <el-descriptions-item v-if="detailFormData.type === 'code'" label="源代码" :span="4">
            <pre style="max-height: 300px; overflow: auto;">{{ detailFormData.source_code }}</pre>
          </el-descriptions-item>
          <el-descriptions-item label="初始化参数" :span="4">
            <pre>{{ JSON.stringify(detailFormData.config, null, 2) }}</pre>
          </el-descriptions-item>
          <el-descriptions-item label="工具使用说明" :span="4">
            {{ detailFormData.instructions }}
          </el-descriptions-item>
          <el-descriptions-item label="需要确认" :span="2">
            <el-tag :type="detailFormData.requires_confirmation === true ? 'success' : detailFormData.requires_confirmation === false ? 'danger' : ''">
              {{ detailFormData.requires_confirmation === true ? '是' : detailFormData.requires_confirmation === false ? '否' : '默认' }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="审批类型" :span="2">
            {{ detailFormData.approval_type || "无" }}
          </el-descriptions-item>
          <el-descriptions-item label="调用后停止" :span="2">
            <el-tag :type="detailFormData.stop_after_call === true ? 'success' : detailFormData.stop_after_call === false ? 'danger' : ''">
              {{ detailFormData.stop_after_call === true ? '是' : detailFormData.stop_after_call === false ? '否' : '默认' }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="展示结果" :span="2">
            <el-tag :type="detailFormData.show_result === true ? 'success' : detailFormData.show_result === false ? 'danger' : ''">
              {{ detailFormData.show_result === true ? '是' : detailFormData.show_result === false ? '否' : '默认' }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="缓存结果" :span="2">
            <el-tag :type="detailFormData.cache_results === true ? 'success' : detailFormData.cache_results === false ? 'danger' : ''">
              {{ detailFormData.cache_results === true ? '是' : detailFormData.cache_results === false ? '否' : '默认' }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item v-if="detailFormData.cache_results" label="缓存TTL(秒)" :span="2">
            {{ detailFormData.cache_ttl }}
          </el-descriptions-item>
          <el-descriptions-item v-if="detailFormData.param_schema" label="参数描述" :span="4">
            <pre>{{ JSON.stringify(detailFormData.param_schema, null, 2) }}</pre>
          </el-descriptions-item>
          <el-descriptions-item label="状态" :span="2">
            <el-tag :type="detailFormData.status == '0' ? 'success' : 'danger'">
              {{ detailFormData.status == "0" ? "启用" : "停用" }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="描述" :span="4">
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
          <el-form-item label="工具包名称" prop="name">
            <el-input v-model="formData.name" placeholder="请输入工具包名称" />
          </el-form-item>
          <el-form-item label="类型" prop="type">
            <el-select v-model="formData.type" placeholder="请选择类型" clearable>
              <el-option value="toolkit" label="toolkit - 整个工具类" />
              <el-option value="function" label="function - 单个函数" />
              <el-option value="code" label="code - 自定义代码" />
            </el-select>
          </el-form-item>
          <el-form-item label="工具来源" prop="tool_from">
            <el-select v-model="formData.tool_from" placeholder="请选择工具来源" clearable>
              <el-option value="agno" label="agno - Agno内置" />
              <el-option value="custom" label="custom - 自定义包" />
              <el-option value="code" label="code - 代码实现" />
            </el-select>
          </el-form-item>
          <el-form-item label="分类" prop="category">
            <el-input v-model="formData.category" placeholder="请输入工具分类" />
          </el-form-item>
          <el-form-item label="全局开关" prop="global_enabled">
            <el-switch v-model="formData.global_enabled" />
            <span class="ml-2 text-sm text-gray-500">关闭后所有用户不可见不可用</span>
          </el-form-item>
          <el-form-item v-if="formData.type !== 'code'" label="Python模块路径" prop="module_path">
            <el-input v-model="formData.module_path" placeholder="如: agno.tools.duckduckgo" />
          </el-form-item>
          <el-form-item v-if="formData.type === 'toolkit'" label="类名" prop="class_name">
            <el-input v-model="formData.class_name" placeholder="如: DuckDuckGo" />
          </el-form-item>
          <el-form-item v-if="formData.type === 'function'" label="函数名" prop="func_name">
            <el-input v-model="formData.func_name" placeholder="如: search_web" />
          </el-form-item>
          <el-form-item v-if="formData.type === 'code'" label="源代码" prop="source_code">
            <el-input
              v-model="formData.source_code"
              type="textarea"
              :rows="10"
              placeholder="请输入Python代码，可使用CONFIG变量访问配置"
            />
          </el-form-item>
          <el-form-item label="初始化参数" prop="config">
            <DictEditor v-model="formData.config" />
          </el-form-item>
          <el-form-item label="工具使用说明" prop="instructions">
            <el-input
              v-model="formData.instructions"
              type="textarea"
              :rows="3"
              placeholder="请输入工具使用说明"
            />
          </el-form-item>
          <el-form-item label="需要确认" prop="requires_confirmation">
            <el-select v-model="formData.requires_confirmation" placeholder="请选择" clearable>
              <el-option :value="true" label="是" />
              <el-option :value="false" label="否" />
              <el-option :value="null" label="默认" />
            </el-select>
          </el-form-item>
          <el-form-item label="审批类型" prop="approval_type">
            <el-select v-model="formData.approval_type" placeholder="请选择审批类型" clearable>
              <el-option value="required" label="required - 必须审批" />
              <el-option value="audit" label="audit - 审计模式" />
            </el-select>
          </el-form-item>
          <el-form-item label="调用后停止" prop="stop_after_call">
            <el-select v-model="formData.stop_after_call" placeholder="请选择" clearable>
              <el-option :value="true" label="是" />
              <el-option :value="false" label="否" />
              <el-option :value="null" label="默认" />
            </el-select>
          </el-form-item>
          <el-form-item label="展示结果" prop="show_result">
            <el-select v-model="formData.show_result" placeholder="请选择" clearable>
              <el-option :value="true" label="是" />
              <el-option :value="false" label="否" />
              <el-option :value="null" label="默认" />
            </el-select>
          </el-form-item>
          <el-form-item label="缓存结果" prop="cache_results">
            <el-select v-model="formData.cache_results" placeholder="请选择" clearable>
              <el-option :value="true" label="是" />
              <el-option :value="false" label="否" />
              <el-option :value="null" label="默认" />
            </el-select>
          </el-form-item>
          <el-form-item v-if="formData.cache_results" label="缓存TTL(秒)" prop="cache_ttl">
            <el-input-number v-model="formData.cache_ttl" :min="0" placeholder="缓存时间" />
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
  name: "AgToolkit",
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
import UserTableSelect from "@/views/module_system/user/components/UserTableSelect.vue";
import AgToolkitAPI, {
  AgToolkitPageQuery,
  AgToolkitTable,
  AgToolkitForm,
} from "@/api/module_agno_manage/toolkits";

const visible = ref(false);
const queryFormRef = ref();
const dataFormRef = ref();
const total = ref(0);
const selectIds = ref<number[]>([]);
const selectionRows = ref<AgToolkitTable[]>([]);
const loading = ref(false);
const isExpand = ref(false);
const isExpandable = ref(true);

// 分页表单
const pageTableData = ref<AgToolkitTable[]>([]);

// 表格列配置
const tableColumns = ref([
  { prop: "selection", label: "选择框", show: true },
  { prop: "index", label: "序号", show: true },
  { prop: "name", label: "工具包名称", show: true },
  { prop: "type", label: "类型", show: true },
  { prop: "tool_from", label: "工具来源", show: true },
  { prop: "category", label: "分类", show: true },
  { prop: "global_enabled", label: "全局开关", show: true },
  { prop: "module_path", label: "Python模块路径", show: false },
  { prop: "class_name", label: "类名", show: false },
  { prop: "func_name", label: "函数名", show: false },
  { prop: "config", label: "初始化参数", show: false },
  { prop: "instructions", label: "工具使用说明", show: true },
  { prop: "requires_confirmation", label: "需要确认", show: false },
  { prop: "approval_type", label: "审批类型", show: false },
  { prop: "stop_after_call", label: "调用后停止", show: false },
  { prop: "show_result", label: "展示结果", show: false },
  { prop: "cache_results", label: "缓存结果", show: false },
  { prop: "cache_ttl", label: "缓存TTL秒数", show: false },
  { prop: "status", label: "状态", show: true },
  { prop: "description", label: "描述", show: true },
  { prop: "created_time", label: "创建时间", show: false },
  { prop: "updated_time", label: "更新时间", show: false },
  { prop: "created_id", label: "创建人", show: false },
  { prop: "updated_id", label: "更新人", show: false },
  { prop: "operation", label: "操作", show: true },
]);

// 导出列（不含选择/序号/操作）
const exportColumns = [
  { prop: "name", label: "工具包名称" },
  { prop: "type", label: "类型" },
  { prop: "tool_from", label: "工具来源" },
  { prop: "category", label: "分类" },
  { prop: "global_enabled", label: "全局开关" },
  { prop: "module_path", label: "Python模块路径" },
  { prop: "class_name", label: "类名" },
  { prop: "func_name", label: "函数名" },
  { prop: "config", label: "初始化参数" },
  { prop: "instructions", label: "工具使用说明" },
  { prop: "requires_confirmation", label: "需要确认" },
  { prop: "approval_type", label: "审批类型" },
  { prop: "stop_after_call", label: "调用后停止" },
  { prop: "show_result", label: "展示结果" },
  { prop: "cache_results", label: "缓存结果" },
  { prop: "cache_ttl", label: "缓存TTL秒数" },
  { prop: "status", label: "状态" },
  { prop: "description", label: "描述" },
  { prop: "created_time", label: "创建时间" },
  { prop: "updated_time", label: "更新时间" },
  { prop: "created_id", label: "创建人ID" },
  { prop: "updated_id", label: "更新人ID" },
];

// 导入/导出配置
const curdContentConfig = {
  permPrefix: "module_agno_manage:toolkits",
  cols: exportColumns as any,
  importTemplate: () => AgToolkitAPI.downloadTemplateAgToolkit(),
  exportsAction: async (params: any) => {
    const query: any = { ...params };
    query.status = "0";
    query.page_no = 1;
    query.page_size = 9999;
    const all: any[] = [];
    while (true) {
      const res = await AgToolkitAPI.listAgToolkit(query);
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
const detailFormData = ref<AgToolkitTable>({});
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
const queryFormData = reactive<AgToolkitPageQuery>({
  page_no: 1,
  page_size: 10,
  name: undefined,
  type: undefined,
  tool_from: undefined,
  category: undefined,
  status: undefined,
  created_time: undefined,
  updated_time: undefined,
  created_id: undefined,
  updated_id: undefined,
});

// 编辑表单
const formData = reactive<AgToolkitForm>({
  id: undefined,
  name: undefined,
  type: undefined,
  tool_from: undefined,
  category: undefined,
  global_enabled: true,
  module_path: undefined,
  class_name: undefined,
  func_name: undefined,
  config: undefined,
  instructions: undefined,
  requires_confirmation: null,
  approval_type: undefined,
  stop_after_call: null,
  show_result: null,
  cache_results: null,
  cache_ttl: undefined,
  source_code: undefined,
  param_schema: undefined,
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
  name: [{ required: false, message: "请输入工具包名称", trigger: "blur" }],
  type: [{ required: false, message: "请输入类型(toolkit:整个类 function:单个函数)", trigger: "blur" }],
  module_path: [{ required: false, message: "请输入Python模块路径", trigger: "blur" }],
  class_name: [{ required: true, message: "请输入类名（type=toolkit时使用）", trigger: "blur" }],
  func_name: [{ required: true, message: "请输入函数名（type=function时使用）", trigger: "blur" }],
  config: [{ required: false, message: "请输入初始化参数", trigger: "blur" }],
  instructions: [{ required: true, message: "请输入工具使用说明", trigger: "blur" }],
  requires_confirmation: [{ required: false, message: "请输入是否需要确认", trigger: "blur" }],
  approval_type: [{ required: true, message: "请输入审批类型(NULL/required/audit)", trigger: "blur" }],
  stop_after_call: [{ required: false, message: "请输入调用后是否停止", trigger: "blur" }],
  show_result: [{ required: false, message: "请输入是否展示结果", trigger: "blur" }],
  cache_results: [{ required: false, message: "请输入是否缓存结果", trigger: "blur" }],
  cache_ttl: [{ required: false, message: "请输入缓存TTL秒数", trigger: "blur" }],
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
    const response = await AgToolkitAPI.listAgToolkit(queryFormData);
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
const initialFormData: AgToolkitForm = {
  id: undefined,
  name: undefined,
  type: undefined,
  tool_from: undefined,
  category: undefined,
  global_enabled: true,
  module_path: undefined,
  class_name: undefined,
  func_name: undefined,
  config: undefined,
  instructions: undefined,
  requires_confirmation: null,
  approval_type: undefined,
  stop_after_call: null,
  show_result: null,
  cache_results: null,
  cache_ttl: undefined,
  source_code: undefined,
  param_schema: undefined,
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
    const response = await AgToolkitAPI.detailAgToolkit(id);
    if (type === "detail") {
      dialogVisible.title = "详情";
      Object.assign(detailFormData.value, response.data.data);
    } else if (type === "update") {
      dialogVisible.title = "修改";
      Object.assign(formData, response.data.data);
    }
  } else {
    dialogVisible.title = "新增AgToolkit";
    formData.id = undefined;
    formData.name = undefined;
    formData.type = undefined;
    formData.tool_from = undefined;
    formData.category = undefined;
    formData.global_enabled = true;
    formData.module_path = undefined;
    formData.class_name = undefined;
    formData.func_name = undefined;
    formData.config = undefined;
    formData.instructions = undefined;
    formData.requires_confirmation = null;
    formData.approval_type = undefined;
    formData.stop_after_call = null;
    formData.show_result = null;
    formData.cache_results = null;
    formData.cache_ttl = undefined;
    formData.source_code = undefined;
    formData.param_schema = undefined;
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
      ) as AgToolkitForm;
      const id = formData.id;
      if (id) {
        try {
          await AgToolkitAPI.updateAgToolkit(id, { id, ...submitData });
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
          await AgToolkitAPI.createAgToolkit(submitData);
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
        await AgToolkitAPI.deleteAgToolkit(ids);
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
          await AgToolkitAPI.batchAgToolkit({ ids: selectIds.value, status });
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
    const response = await AgToolkitAPI.importAgToolkit(formData);
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
