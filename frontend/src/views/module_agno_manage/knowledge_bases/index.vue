<!-- 知识库 -->
<template>
  <div class="app-container">
    <!-- 内容区域 -->
    <el-card class="data-table">
      <template #header>
        <div class="card-header">
          <span>
            知识库列表
            <el-tooltip content="知识库列表">
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
            <el-form-item label="知识库名称" prop="name">
              <el-input v-model="queryFormData.name" placeholder="请输入知识库名称" clearable />
            </el-form-item>
            <el-form-item label="关联向量数据库" prop="vectordb_id">
              <el-select v-model="queryFormData.vectordb_id" placeholder="请选择向量数据库" clearable filterable style="width: 200px">
                <el-option
                  v-for="item in vectordbList"
                  :key="item.id"
                  :label="item.name"
                  :value="String(item.id)"
                />
              </el-select>
            </el-form-item>
            <!-- <el-form-item label="文档读取器类型" prop="reader_type">
              <el-select v-model="queryFormData.reader_type" placeholder="请选择类型" clearable style="width: 160px">
                <el-option value="pdf" label="PDF" />
                <el-option value="web" label="Web" />
                <el-option value="docx" label="Word(docx)" />
                <el-option value="csv" label="CSV" />
                <el-option value="json" label="JSON" />
                <el-option value="text" label="文本(text)" />
              </el-select>
            </el-form-item> -->
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
                v-hasPerm="['module_agno_manage:knowledge_bases:query']"
                type="primary"
                icon="search"
                @click="handleQuery"
              >
                查询
              </el-button>
              <el-button
                v-hasPerm="['module_agno_manage:knowledge_bases:query']"
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
                v-hasPerm="['module_agno_manage:knowledge_bases:create']"
                type="success"
                icon="plus"
                @click="handleOpenDialog('create')"
              >
                新增
              </el-button>
            </el-col>
            <el-col :span="1.5">
              <el-button
                v-hasPerm="['module_agno_manage:knowledge_bases:delete']"
                type="danger"
                icon="delete"
                :disabled="selectIds.length === 0"
                @click="handleDelete(selectIds)"
              >
                批量删除
              </el-button>
            </el-col>
            <el-col :span="1.5">
              <el-dropdown v-hasPerm="['module_agno_manage:knowledge_bases:batch']" trigger="click">
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
                  v-hasPerm="['module_agno_manage:knowledge_bases:import']"
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
                  v-hasPerm="['module_agno_manage:knowledge_bases:export']"
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
                  v-hasPerm="['module_agno_manage:knowledge_bases:query']"
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
          label="知识库名称"
          prop="name"
          min-width="140"
          show-overflow-tooltip
        />
        <el-table-column
          v-if="tableColumns.find((col) => col.prop === 'vectordb_id')?.show"
          label="关联向量数据库"
          prop="vectordb_id"
          min-width="160"
          show-overflow-tooltip
        >
          <template #default="scope">
            <span>{{ getVectordbName(scope.row.vectordb_id) }}</span>
          </template>
        </el-table-column>
        <el-table-column
          v-if="tableColumns.find((col) => col.prop === 'max_results')?.show"
          label="最大检索结果数"
          prop="max_results"
          min-width="120"
          show-overflow-tooltip
        />
        <!-- <el-table-column
          v-if="tableColumns.find((col) => col.prop === 'reader_type')?.show"
          label="文档读取器类型"
          prop="reader_type"
          min-width="130"
          align="center"
        >
          <template #default="scope">
            <el-tag v-if="scope.row.reader_type" type="info">{{ scope.row.reader_type }}</el-tag>
            <span v-else>-</span>
          </template>
        </el-table-column> -->
        <!-- <el-table-column
          v-if="tableColumns.find((col) => col.prop === 'reader_config')?.show"
          label="读取器配置参数"
          prop="reader_config"
          min-width="140"
          show-overflow-tooltip
        >
          <template #default="scope">
            <span v-if="scope.row.reader_config">{{ JSON.stringify(scope.row.reader_config) }}</span>
            <span v-else>-</span>
          </template>
        </el-table-column> -->
        <el-table-column
          v-if="tableColumns.find((col) => col.prop === 'default_filters')?.show"
          label="默认搜索过滤条件"
          prop="default_filters"
          min-width="140"
          show-overflow-tooltip
        />
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
          min-width="100"
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
          show-overflow-tooltip
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
              v-hasPerm="['module_agno_manage:knowledge_bases:detail']"
              type="info"
              size="small"
              link
              icon="document"
              @click="handleOpenDialog('detail', scope.row.id)"
            >
              详情
            </el-button>
            <el-button
              v-hasPerm="['module_agno_manage:knowledge_bases:update']"
              type="primary"
              size="small"
              link
              icon="edit"
              @click="handleOpenDialog('update', scope.row.id)"
            >
              编辑
            </el-button>
            <el-button
              v-hasPerm="['module_agno_manage:knowledge_bases:delete']"
              type="danger"
              size="small"
              link
              icon="delete"
              @click="handleDelete([scope.row.id])"
            >
              删除
            </el-button>
            <el-button
              v-hasPerm="['module_agno_manage:knowledge_bases:query']"
              type="warning"
              size="small"
              link
              icon="folder"
              @click="handleOpenDocDrawer(scope.row)"
            >
              文档
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
          <el-descriptions-item label="知识库名称" :span="2">
            {{ detailFormData.name }}
          </el-descriptions-item>
          <el-descriptions-item label="关联向量数据库" :span="2">
            {{ getVectordbName(detailFormData.vectordb_id) }}
          </el-descriptions-item>
          <el-descriptions-item label="最大检索结果数" :span="2">
            {{ detailFormData.max_results }}
          </el-descriptions-item>
          <el-descriptions-item label="文档读取器类型" :span="2">
            <el-tag v-if="detailFormData.reader_type" type="info">{{ detailFormData.reader_type }}</el-tag>
            <span v-else>-</span>
          </el-descriptions-item>
          <el-descriptions-item label="读取器配置参数" :span="4">
            <pre style="margin: 0; white-space: pre-wrap; font-size: 12px">{{ JSON.stringify(detailFormData.reader_config, null, 2) }}</pre>
          </el-descriptions-item>
          <el-descriptions-item label="默认搜索过滤条件" :span="2">
            {{ detailFormData.default_filters }}
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
        <el-form
          ref="dataFormRef"
          :model="formData"
          :rules="rules"
          label-suffix=":"
          label-width="auto"
          label-position="right"
        >
          <el-form-item label="知识库名称" prop="name" :required="false">
            <el-input v-model="formData.name" placeholder="请输入知识库名称" />
          </el-form-item>
          <el-form-item label="关联向量数据库" prop="vectordb_id" :required="false">
            <el-select v-model="formData.vectordb_id" placeholder="请选择向量数据库" clearable filterable style="width: 100%">
              <el-option
                v-for="item in vectordbList"
                :key="item.id"
                :label="item.name"
                :value="String(item.id)"
              >
                <el-tooltip
                  :content="`ID: ${item.id}`"
                  placement="right"
                  :show-after="300"
                  :teleported="true"
                  :enterable="false"
                >
                  <span style="display: block; width: 100%;">{{ item.name }}</span>
                </el-tooltip>
              </el-option>
            </el-select>
          </el-form-item>
          <el-form-item label="最大检索结果数" prop="max_results" :required="false">
            <el-input v-model="formData.max_results" placeholder="请输入最大检索结果数" />
          </el-form-item>
          <!-- <el-form-item label="文档读取器类型" prop="reader_type" :required="false">
            <el-select v-model="formData.reader_type" placeholder="请选择文档读取器类型" clearable style="width: 100%">
              <el-option value="pdf" label="PDF" />
              <el-option value="web" label="Web" />
              <el-option value="docx" label="Word(docx)" />
              <el-option value="csv" label="CSV" />
              <el-option value="json" label="JSON" />
              <el-option value="text" label="文本(text)" />
            </el-select>
          </el-form-item>
          <el-form-item label="读取器配置参数" prop="reader_config" :required="false">
            <DictEditor v-model="formData.reader_config" />
          </el-form-item> -->
          <el-form-item label="默认搜索过滤条件" prop="default_filters" :required="false">
            <el-input v-model="formData.default_filters" placeholder="请输入默认搜索过滤条件" />
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

    <!-- ── 文档管理抽屉 ─────────────────────────────────────────────── -->
    <el-drawer
      v-model="docDrawer.visible"
      :title="`文档管理 — ${docDrawer.kbName}`"
      direction="rtl"
      size="75%"
      :destroy-on-close="true"
    >
      <!-- 工具栏 -->
      <div style="display:flex; gap:8px; margin-bottom:16px; flex-wrap:wrap; align-items:center;">
        <el-button type="primary" icon="upload" @click="uploadDialog.visible = true">上传文件</el-button>
        <el-button type="success" icon="link" @click="insertDialog.visible = true">插入URL/文本</el-button>
        <el-button icon="refresh" :loading="docLoading" @click="loadKBDocs">刷新</el-button>
        <el-input
          v-model="searchQuery"
          placeholder="输入内容检索知识库..."
          style="flex:1; min-width:200px;"
          clearable
          @keyup.enter="handleKBSearch"
        >
          <template #append>
            <el-button icon="search" :loading="searchLoading" @click="handleKBSearch">检索</el-button>
          </template>
        </el-input>
      </div>

      <!-- 检索结果 -->
      <el-card v-if="searchResults.length > 0" shadow="never" style="margin-bottom:16px;">
        <template #header>
          <span style="font-weight:600;">检索结果（{{ searchResults.length }} 条）</span>
          <el-button style="float:right;" text @click="searchResults = []">清除</el-button>
        </template>
        <div
          v-for="(r, i) in searchResults"
          :key="i"
          style="padding:8px 0; border-bottom:1px solid var(--el-border-color-lighter);"
        >
          <div style="font-weight:500; margin-bottom:4px;">
            {{ r.name || `结果 ${i + 1}` }}
            <el-tag
              v-if="r.reranking_score != null"
              size="small"
              type="info"
              style="margin-left:8px;"
            >
              score: {{ typeof r.reranking_score === 'number' ? r.reranking_score.toFixed(4) : r.reranking_score }}
            </el-tag>
          </div>
          <div style="color:var(--el-text-color-secondary); font-size:13px; white-space:pre-wrap; word-break:break-all;">
            {{ r.content }}
          </div>
        </div>
      </el-card>

      <!-- 文档列表 -->
      <el-table v-loading="docLoading" :data="docList" border stripe>
        <template #empty>
          <el-empty :image-size="60" description="暂无文档，请上传文件或插入URL/文本" />
        </template>
        <el-table-column label="文档名称" prop="name" min-width="180" show-overflow-tooltip />
        <el-table-column label="类型" prop="storage_type" min-width="80" align="center">
          <template #default="scope">
            <el-tag size="small" type="info">{{ scope.row.storage_type || '-' }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="向量化状态" prop="doc_status" min-width="110" align="center">
          <template #default="scope">
            <el-tag :type="docStatusTagType(scope.row.doc_status)" size="small">
              {{ docStatusLabel(scope.row.doc_status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="错误信息" prop="error_msg" min-width="160" show-overflow-tooltip>
          <template #default="scope">
            <span v-if="scope.row.error_msg" style="color:var(--el-color-danger); font-size:12px;">
              {{ scope.row.error_msg }}
            </span>
            <span v-else style="color:var(--el-text-color-placeholder);">-</span>
          </template>
        </el-table-column>
        <el-table-column label="创建时间" prop="created_time" min-width="150" show-overflow-tooltip />
        <el-table-column label="操作" fixed="right" align="center" min-width="150">
          <template #default="scope">
            <el-button
              size="small"
              link
              type="warning"
              icon="refresh"
              @click="handleReprocessDoc(scope.row)"
            >
              重新向量化
            </el-button>
            <el-button
              size="small"
              link
              type="danger"
              icon="delete"
              @click="handleDeleteKBDoc(scope.row)"
            >
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <div style="display:flex; justify-content:flex-end; margin-top:12px;">
        <el-pagination
          v-model:current-page="docQuery.page_no"
          v-model:page-size="docQuery.page_size"
          :total="docTotal"
          :page-sizes="[10, 20, 50]"
          layout="total, sizes, prev, pager, next"
          @change="loadKBDocs"
        />
      </div>
    </el-drawer>

    <!-- ── 上传文件弹窗 ──────────────────────────────────────────────── -->
    <el-dialog
      v-model="uploadDialog.visible"
      title="上传文件到知识库"
      width="480px"
      :close-on-click-modal="false"
    >
      <el-form label-width="80px">
        <el-form-item label="文件" required>
          <el-upload
            ref="uploadRef"
            :auto-upload="false"
            :limit="1"
            :on-change="handleFileChange"
            :on-remove="() => (uploadForm.file = null)"
            drag
            style="width:100%;"
          >
            <el-icon style="font-size:40px; color:var(--el-color-primary);"><UploadFilled /></el-icon>
            <div style="margin-top:8px;">拖拽文件到此处，或 <em>点击选择</em></div>
          </el-upload>
        </el-form-item>
        <el-form-item label="文档名称">
          <el-input v-model="uploadForm.name" placeholder="留空则使用文件名" clearable />
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="uploadForm.description" type="textarea" :rows="2" placeholder="可选" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="uploadDialog.visible = false">取消</el-button>
        <el-button type="primary" :loading="uploadDialog.loading" @click="handleUploadDoc">
          上传并向量化
        </el-button>
      </template>
    </el-dialog>

    <!-- ── 插入 URL / 文本弹窗 ──────────────────────────────────────── -->
    <el-dialog
      v-model="insertDialog.visible"
      title="插入 URL 或文本"
      width="520px"
      :close-on-click-modal="false"
    >
      <el-form label-width="90px">
        <el-form-item label="类型">
          <el-radio-group v-model="insertForm.type">
            <el-radio value="url">URL</el-radio>
            <el-radio value="text">纯文本</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item v-if="insertForm.type === 'url'" label="URL" required>
          <el-input v-model="insertForm.url" placeholder="https://..." clearable />
        </el-form-item>
        <el-form-item v-else label="文本内容" required>
          <el-input
            v-model="insertForm.text_content"
            type="textarea"
            :rows="6"
            placeholder="输入要向量化的文本内容..."
          />
        </el-form-item>
        <el-form-item label="文档名称">
          <el-input v-model="insertForm.name" placeholder="可选，留空自动生成" clearable />
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="insertForm.description" type="textarea" :rows="2" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="insertDialog.visible = false">取消</el-button>
        <el-button type="primary" :loading="insertDialog.loading" @click="handleInsertDoc">
          确认插入
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
defineOptions({
  name: "AgKnowledgeBase",
  inheritAttrs: false,
});

import { ref, reactive, onMounted } from "vue";
import { ElMessage, ElMessageBox } from "element-plus";
import { QuestionFilled, ArrowUp, ArrowDown, Check, CircleClose, UploadFilled } from "@element-plus/icons-vue";
import { formatToDateTime } from "@/utils/dateUtil";
import { ResultEnum } from "@/enums/api/result.enum";
import DatePicker from "@/components/DatePicker/index.vue";
import type { IContentConfig } from "@/components/CURD/types";
import ImportModal from "@/components/CURD/ImportModal.vue";
import ExportModal from "@/components/CURD/ExportModal.vue";
import DictEditor from "@/views/module_agno_manage/components/DictEditor/index.vue";
import AgKnowledgeBaseAPI, {
  AgKnowledgeBasePageQuery,
  AgKnowledgeBaseTable,
  AgKnowledgeBaseForm,
  AgKBDocumentItem,
  KBSearchResult,
} from "@/api/module_agno_manage/knowledge_bases";
import AgVectordbAPI from "@/api/module_agno_manage/vectordbs";

const visible = ref(false);
const queryFormRef = ref();
const dataFormRef = ref();
const total = ref(0);
const selectIds = ref<number[]>([]);
const selectionRows = ref<AgKnowledgeBaseTable[]>([]);
const loading = ref(false);
const isExpand = ref(false);
const isExpandable = ref(true);

// 向量数据库列表（关联外键下拉）
const vectordbList = ref<any[]>([]);

async function loadVectordbList() {
  const res = await AgVectordbAPI.listAgVectordb({ page_no: 1, page_size: 100 });
  vectordbList.value = (res.data?.data?.items || []).map((item: any) => ({
    id: item.id,
    name: item.name || `Vectordb#${item.id}`,
  }));
}

function getVectordbName(vectordbId?: string): string {
  if (!vectordbId) return "-";
  const found = vectordbList.value.find((e) => String(e.id) === String(vectordbId));
  return found ? found.name : String(vectordbId);
}

// 分页表单
const pageTableData = ref<AgKnowledgeBaseTable[]>([]);

// 表格列配置
const tableColumns = ref([
  { prop: "selection", label: "选择框", show: true },
  { prop: "index", label: "序号", show: true },
  { prop: "name", label: "知识库名称", show: true },
  { prop: "vectordb_id", label: "关联向量数据库", show: true },
  { prop: "max_results", label: "最大检索结果数", show: true },
  { prop: "reader_type", label: "文档读取器类型", show: true },
  { prop: "reader_config", label: "读取器配置参数", show: true },
  { prop: "default_filters", label: "默认搜索过滤条件", show: true },
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
  { prop: "name", label: "知识库名称" },
  { prop: "vectordb_id", label: "关联向量数据库" },
  { prop: "max_results", label: "最大检索结果数" },
  { prop: "reader_type", label: "文档读取器类型" },
  { prop: "reader_config", label: "读取器配置参数" },
  { prop: "default_filters", label: "默认搜索过滤条件" },
  { prop: "status", label: "状态" },
  { prop: "description", label: "描述" },
  { prop: "created_time", label: "创建时间" },
  { prop: "updated_time", label: "更新时间" },
  { prop: "created_id", label: "创建人ID" },
  { prop: "updated_id", label: "更新人ID" },
];

// 导入/导出配置
const curdContentConfig = {
  permPrefix: "module_agno_manage:knowledge_bases",
  cols: exportColumns as any,
  importTemplate: () => AgKnowledgeBaseAPI.downloadTemplateAgKnowledgeBase(),
  exportsAction: async (params: any) => {
    const query: any = { ...params };
    query.status = "0";
    query.page_no = 1;
    query.page_size = 9999;
    const all: any[] = [];
    while (true) {
      const res = await AgKnowledgeBaseAPI.listAgKnowledgeBase(query);
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
const detailFormData = ref<AgKnowledgeBaseTable>({});
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
const queryFormData = reactive<AgKnowledgeBasePageQuery>({
  page_no: 1,
  page_size: 10,
  name: undefined,
  vectordb_id: undefined,
  reader_type: undefined,
  status: undefined,
  created_time: undefined,
  updated_time: undefined,
  created_id: undefined,
  updated_id: undefined,
});

// 编辑表单
const formData = reactive<AgKnowledgeBaseForm>({
  id: undefined,
  name: undefined,
  vectordb_id: undefined,
  max_results: undefined,
  reader_type: undefined,
  reader_config: undefined,
  default_filters: undefined,
  status: "0",
  description: undefined,
});

// 弹窗状态
const dialogVisible = reactive({
  title: "",
  visible: false,
  type: "create" as "create" | "update" | "detail",
});

// 表单验证规则
const rules = reactive({
  name: [{ required: false, message: "请输入知识库名称", trigger: "blur" }],
  vectordb_id: [{ required: false, message: "请选择关联向量数据库", trigger: "change" }],
  max_results: [{ required: false, message: "请输入最大检索结果数", trigger: "blur" }],
  reader_type: [{ required: false, message: "请选择文档读取器类型", trigger: "change" }],
  reader_config: [{ required: false, message: "请输入读取器配置参数", trigger: "blur" }],
  default_filters: [{ required: false, message: "请输入默认搜索过滤条件", trigger: "blur" }],
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
    const response = await AgKnowledgeBaseAPI.listAgKnowledgeBase(queryFormData);
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
const initialFormData: AgKnowledgeBaseForm = {
  id: undefined,
  name: undefined,
  vectordb_id: undefined,
  max_results: undefined,
  reader_type: undefined,
  reader_config: undefined,
  default_filters: undefined,
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
    const response = await AgKnowledgeBaseAPI.detailAgKnowledgeBase(id);
    if (type === "detail") {
      dialogVisible.title = "详情";
      Object.assign(detailFormData.value, response.data.data);
    } else if (type === "update") {
      dialogVisible.title = "修改";
      Object.assign(formData, response.data.data);
    }
  } else {
    dialogVisible.title = "新增AgKnowledgeBase";
    formData.id = undefined;
    formData.name = undefined;
    formData.vectordb_id = undefined;
    formData.max_results = undefined;
    formData.reader_type = undefined;
    formData.reader_config = undefined;
    formData.default_filters = undefined;
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
      const submitData = { ...formData };
      const id = formData.id;
      if (id) {
        try {
          await AgKnowledgeBaseAPI.updateAgKnowledgeBase(id, { id, ...submitData });
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
          await AgKnowledgeBaseAPI.createAgKnowledgeBase(submitData);
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
        await AgKnowledgeBaseAPI.deleteAgKnowledgeBase(ids);
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
          await AgKnowledgeBaseAPI.batchAgKnowledgeBase({ ids: selectIds.value, status });
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
    const response = await AgKnowledgeBaseAPI.importAgKnowledgeBase(formData);
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
  await loadVectordbList();
  loadingData();
});

// ── 文档管理抽屉 ──────────────────────────────────────────────────────
const docDrawer = reactive({ visible: false, kbId: 0, kbName: '' });
const docList = ref<AgKBDocumentItem[]>([]);
const docTotal = ref(0);
const docLoading = ref(false);
const docQuery = reactive({ page_no: 1, page_size: 10 });
const searchQuery = ref('');
const searchResults = ref<KBSearchResult[]>([]);
const searchLoading = ref(false);
const uploadRef = ref();
const uploadDialog = reactive({ visible: false, loading: false });
const uploadForm = reactive({ file: null as File | null, name: '', description: '' });
const insertDialog = reactive({ visible: false, loading: false });
const insertForm = reactive({ type: 'url' as 'url' | 'text', url: '', text_content: '', name: '', description: '' });

function docStatusTagType(status?: string): 'success' | 'warning' | 'danger' | 'info' {
  if (status === 'completed') return 'success';
  if (status === 'pending') return 'warning';
  if (status === 'failed') return 'danger';
  return 'info';
}

function docStatusLabel(status?: string): string {
  const map: Record<string, string> = {
    pending: '待处理',
    processing: '处理中',
    completed: '已完成',
    failed: '失败',
  };
  return map[status ?? ''] ?? (status || '-');
}

function handleOpenDocDrawer(row: AgKnowledgeBaseTable) {
  docDrawer.kbId = row.id as number;
  docDrawer.kbName = row.name || String(row.id);
  docDrawer.visible = true;
  docQuery.page_no = 1;
  docList.value = [];
  docTotal.value = 0;
  searchResults.value = [];
  searchQuery.value = '';
  loadKBDocs();
}

async function loadKBDocs() {
  docLoading.value = true;
  try {
    const res = await AgKnowledgeBaseAPI.listKBDocs(docDrawer.kbId, {
      page_no: docQuery.page_no,
      page_size: docQuery.page_size,
    });
    docList.value = res.data?.data?.items || [];
    docTotal.value = res.data?.data?.total || 0;
  } catch (e) {
    console.error(e);
  } finally {
    docLoading.value = false;
  }
}

async function handleKBSearch() {
  if (!searchQuery.value.trim()) return;
  searchLoading.value = true;
  try {
    const res = await AgKnowledgeBaseAPI.searchKB(docDrawer.kbId, { query: searchQuery.value.trim(), limit: 10 });
    searchResults.value = res.data?.data || [];
  } catch (e) {
    console.error(e);
  } finally {
    searchLoading.value = false;
  }
}

async function handleReprocessDoc(row: AgKBDocumentItem) {
  try {
    await AgKnowledgeBaseAPI.reprocessKBDoc(docDrawer.kbId, row.id as number);
    ElMessage.success('重新向量化已提交');
    loadKBDocs();
  } catch (e) {
    console.error(e);
  }
}

async function handleDeleteKBDoc(row: AgKBDocumentItem) {
  ElMessageBox.confirm('确认删除该文档及其向量数据?', '警告', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning',
  }).then(async () => {
    try {
      await AgKnowledgeBaseAPI.deleteKBDoc(docDrawer.kbId, row.id as number);
      ElMessage.success('删除成功');
      loadKBDocs();
    } catch (e) {
      console.error(e);
    }
  }).catch(() => {});
}

function handleFileChange(uploadFile: any) {
  uploadForm.file = uploadFile.raw as File;
}

async function handleUploadDoc() {
  if (!uploadForm.file) {
    ElMessage.warning('请选择要上传的文件');
    return;
  }
  uploadDialog.loading = true;
  try {
    const fd = new FormData();
    fd.append('file', uploadForm.file);
    if (uploadForm.name) fd.append('name', uploadForm.name);
    if (uploadForm.description) fd.append('description', uploadForm.description);
    await AgKnowledgeBaseAPI.uploadKBDoc(docDrawer.kbId, fd);
    ElMessage.success('上传成功，正在向量化');
    uploadDialog.visible = false;
    uploadForm.file = null;
    uploadForm.name = '';
    uploadForm.description = '';
    if (uploadRef.value) uploadRef.value.clearFiles();
    loadKBDocs();
  } catch (e) {
    console.error(e);
  } finally {
    uploadDialog.loading = false;
  }
}

async function handleInsertDoc() {
  if (insertForm.type === 'url' && !insertForm.url.trim()) {
    ElMessage.warning('请输入 URL');
    return;
  }
  if (insertForm.type === 'text' && !insertForm.text_content.trim()) {
    ElMessage.warning('请输入文本内容');
    return;
  }
  insertDialog.loading = true;
  try {
    const body: any = {
      name: insertForm.name || undefined,
      description: insertForm.description || undefined,
    };
    if (insertForm.type === 'url') {
      body.url = insertForm.url.trim();
    } else {
      body.text_content = insertForm.text_content.trim();
    }
    await AgKnowledgeBaseAPI.insertKBDoc(docDrawer.kbId, body);
    ElMessage.success('插入成功，正在向量化');
    insertDialog.visible = false;
    insertForm.url = '';
    insertForm.text_content = '';
    insertForm.name = '';
    insertForm.description = '';
    loadKBDocs();
  } catch (e) {
    console.error(e);
  } finally {
    insertDialog.loading = false;
  }
}
</script>

<style lang="scss" scoped></style>
