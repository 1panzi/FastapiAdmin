<!-- 知识库文档 -->
<template>
  <div class="app-container">
    <!-- 内容区域 -->
    <el-card class="data-table">
      <template #header>
        <div class="card-header">
          <span>
            知识库文档列表
            <el-tooltip content="知识库文档列表">
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
            <el-form-item label="所属知识库" prop="kb_id">
              <el-select v-model="queryFormData.kb_id" placeholder="请选择知识库" clearable filterable style="width: 200px">
                <el-option
                  v-for="item in kbList"
                  :key="item.id"
                  :label="item.name"
                  :value="item.id"
                />
              </el-select>
            </el-form-item>
            <el-form-item label="文档名称" prop="name">
              <el-input v-model="queryFormData.name" placeholder="请输入文档名称" clearable />
            </el-form-item>
            <el-form-item label="存储类型" prop="storage_type">
              <el-select v-model="queryFormData.storage_type" placeholder="请选择存储类型" clearable style="width: 140px">
                <el-option value="local" label="本地(local)" />
                <el-option value="s3" label="S3" />
                <el-option value="gcs" label="GCS" />
                <el-option value="url" label="URL" />
              </el-select>
            </el-form-item>
            <el-form-item label="向量化状态" prop="doc_status">
              <el-select v-model="queryFormData.doc_status" placeholder="请选择状态" clearable style="width: 140px">
                <el-option value="pending" label="待处理" />
                <el-option value="processing" label="处理中" />
                <el-option value="indexed" label="已完成" />
                <el-option value="failed" label="失败" />
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
                v-hasPerm="['module_agno_manage:documents:query']"
                type="primary"
                icon="search"
                @click="handleQuery"
              >
                查询
              </el-button>
              <el-button
                v-hasPerm="['module_agno_manage:documents:query']"
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
                v-hasPerm="['module_agno_manage:documents:create']"
                type="success"
                icon="plus"
                @click="handleOpenDialog('create')"
              >
                新增
              </el-button>
            </el-col>
            <el-col :span="1.5">
              <el-button
                v-hasPerm="['module_agno_manage:documents:create']"
                type="primary"
                icon="upload"
                @click="uploadDocDialog.visible = true"
              >
                上传文件
              </el-button>
            </el-col>
            <el-col :span="1.5">
              <el-button
                v-hasPerm="['module_agno_manage:documents:create']"
                type="success"
                icon="link"
                @click="insertDocDialog.visible = true"
              >
                插入URL/文本
              </el-button>
            </el-col>
            <el-col :span="1.5">
              <el-button
                v-hasPerm="['module_agno_manage:documents:delete']"
                type="danger"
                icon="delete"
                :disabled="selectIds.length === 0"
                @click="handleDelete(selectIds)"
              >
                批量删除
              </el-button>
            </el-col>
            <el-col :span="1.5">
              <el-dropdown v-hasPerm="['module_agno_manage:documents:batch']" trigger="click">
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
                  v-hasPerm="['module_agno_manage:documents:import']"
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
                  v-hasPerm="['module_agno_manage:documents:export']"
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
                  v-hasPerm="['module_agno_manage:documents:query']"
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
          v-if="tableColumns.find((col) => col.prop === 'kb_id')?.show"
          label="所属知识库"
          prop="kb_id"
          min-width="140"
          show-overflow-tooltip
        >
          <template #default="scope">
            <span>{{ getKbName(scope.row.kb_id) }}</span>
          </template>
        </el-table-column>
        <el-table-column
          v-if="tableColumns.find((col) => col.prop === 'name')?.show"
          label="文档名称"
          prop="name"
          min-width="160"
          show-overflow-tooltip
        />
        <el-table-column
          v-if="tableColumns.find((col) => col.prop === 'storage_type')?.show"
          label="存储类型"
          prop="storage_type"
          min-width="90"
          align="center"
        >
          <template #default="scope">
            <el-tag v-if="scope.row.storage_type" size="small" type="info">{{ scope.row.storage_type }}</el-tag>
            <span v-else>-</span>
          </template>
        </el-table-column>
        <el-table-column
          v-if="tableColumns.find((col) => col.prop === 'storage_path')?.show"
          label="存储路径"
          prop="storage_path"
          min-width="160"
          show-overflow-tooltip
        />
        <el-table-column
          v-if="tableColumns.find((col) => col.prop === 'doc_status')?.show"
          label="向量化状态"
          prop="doc_status"
          min-width="110"
          align="center"
        >
          <template #default="scope">
            <el-tag :type="docStatusTagType(scope.row.doc_status)" size="small">
              {{ docStatusLabel(scope.row.doc_status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column
          v-if="tableColumns.find((col) => col.prop === 'error_msg')?.show"
          label="错误信息"
          prop="error_msg"
          min-width="160"
          show-overflow-tooltip
        >
          <template #default="scope">
            <span v-if="scope.row.error_msg" style="color:var(--el-color-danger); font-size:12px;">
              {{ scope.row.error_msg }}
            </span>
            <span v-else style="color:var(--el-text-color-placeholder);">-</span>
          </template>
        </el-table-column>
        <el-table-column
          v-if="tableColumns.find((col) => col.prop === 'reader_id')?.show"
          label="Reader"
          prop="reader_id"
          min-width="120"
          show-overflow-tooltip
        >
          <template #default="scope">
            <span v-if="scope.row.reader_id">{{ getReaderName(scope.row.reader_id) }}</span>
            <span v-else style="color:var(--el-text-color-placeholder);">自动</span>
          </template>
        </el-table-column>
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
          show-overflow-tooltip
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
          min-width="210"
        >
          <template #default="scope">
            <el-button
              v-hasPerm="['module_agno_manage:documents:detail']"
              type="info"
              size="small"
              link
              icon="document"
              @click="handleOpenDialog('detail', scope.row.id)"
            >
              详情
            </el-button>
            <el-button
              v-hasPerm="['module_agno_manage:documents:update']"
              type="primary"
              size="small"
              link
              icon="edit"
              @click="handleOpenDialog('update', scope.row.id)"
            >
              编辑
            </el-button>
            <el-button
              v-hasPerm="['module_agno_manage:documents:update']"
              type="warning"
              size="small"
              link
              icon="refresh"
              @click="handleReprocessDocument(scope.row.id)"
            >
              重新向量化
            </el-button>
            <el-button
              v-hasPerm="['module_agno_manage:documents:delete']"
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
          <el-descriptions-item label="所属知识库" :span="2">
            {{ getKbName(detailFormData.kb_id) }}
          </el-descriptions-item>
          <el-descriptions-item label="文档名称" :span="2">
            {{ detailFormData.name }}
          </el-descriptions-item>
          <el-descriptions-item label="存储类型" :span="2">
            {{ detailFormData.storage_type }}
          </el-descriptions-item>
          <el-descriptions-item label="存储路径" :span="2">
            {{ detailFormData.storage_path }}
          </el-descriptions-item>
          <el-descriptions-item label="向量化状态" :span="2">
            <el-tag :type="docStatusTagType(detailFormData.doc_status)" size="small">
              {{ docStatusLabel(detailFormData.doc_status) }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="Reader" :span="2">
            <span v-if="detailFormData.reader_id">{{ getReaderName(detailFormData.reader_id) }}</span>
            <span v-else style="color:var(--el-text-color-placeholder);">自动</span>
          </el-descriptions-item>
          <el-descriptions-item label="错误信息" :span="4">
            <span v-if="detailFormData.error_msg" style="color:var(--el-color-danger);">{{ detailFormData.error_msg }}</span>
            <span v-else>-</span>
          </el-descriptions-item>
          <el-descriptions-item label="文档元数据" :span="4">
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
        <el-form
          ref="dataFormRef"
          :model="formData"
          :rules="rules"
          label-suffix=":"
          label-width="auto"
          label-position="right"
        >
          <el-form-item label="所属知识库" prop="kb_id" :required="false">
            <el-select v-model="formData.kb_id" placeholder="请选择知识库" clearable filterable style="width: 100%">
              <el-option
                v-for="item in kbList"
                :key="item.id"
                :label="item.name"
                :value="item.id"
              />
            </el-select>
          </el-form-item>
          <el-form-item label="文档名称" prop="name" :required="true">
            <el-input v-model="formData.name" placeholder="请输入文档名称" />
          </el-form-item>
          <el-form-item label="存储类型" prop="storage_type" :required="false">
            <el-select v-model="formData.storage_type" placeholder="请选择存储类型" clearable style="width: 100%">
              <el-option value="local" label="本地(local)" />
              <el-option value="s3" label="S3" />
              <el-option value="gcs" label="GCS" />
              <el-option value="url" label="URL" />
            </el-select>
          </el-form-item>
          <el-form-item label="存储路径" prop="storage_path" :required="false">
            <el-input v-model="formData.storage_path" placeholder="请输入存储路径或URL" />
          </el-form-item>
          <el-form-item label="向量化状态" prop="doc_status" :required="false">
            <el-select v-model="formData.doc_status" placeholder="请选择状态" clearable style="width: 100%">
              <el-option value="pending" label="待处理(pending)" />
              <el-option value="processing" label="处理中(processing)" />
              <el-option value="indexed" label="已完成(indexed)" />
              <el-option value="failed" label="失败(failed)" />
            </el-select>
          </el-form-item>
          <el-form-item label="错误信息" prop="error_msg" :required="false">
            <el-input v-model="formData.error_msg" placeholder="请输入处理失败错误信息" />
          </el-form-item>
          <el-form-item label="Reader配置" prop="reader_id" :required="false">
            <el-select v-model="formData.reader_id" placeholder="不填则 Agno 自动路由" clearable filterable style="width: 100%">
              <el-option
                v-for="item in readerList"
                :key="item.id"
                :label="`${item.name} (${item.reader_type})`"
                :value="item.id"
              />
            </el-select>
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

    <!-- ── 上传文件弹窗 ──────────────────────────────────────────────── -->
    <el-dialog
      v-model="uploadDocDialog.visible"
      title="上传文件并向量化"
      width="500px"
      :close-on-click-modal="false"
    >
      <el-form label-width="100px">
        <el-form-item label="所属知识库" required>
          <el-select v-model="uploadDocForm.kb_id" placeholder="请选择知识库" filterable clearable style="width: 100%">
            <el-option
              v-for="item in kbList"
              :key="item.id"
              :label="item.name"
              :value="item.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="文件" required>
          <el-upload
            ref="uploadDocRef"
            :auto-upload="false"
            :limit="1"
            :on-change="handleUploadDocFileChange"
            :on-remove="() => (uploadDocForm.file = null)"
            drag
            style="width: 100%;"
          >
            <el-icon style="font-size: 40px; color: var(--el-color-primary);"><UploadFilled /></el-icon>
            <div style="margin-top: 8px;">拖拽文件到此处，或 <em>点击选择</em></div>
          </el-upload>
        </el-form-item>
        <el-form-item label="文档名称">
          <el-input v-model="uploadDocForm.name" placeholder="留空则使用文件名" clearable />
        </el-form-item>
        <el-form-item label="Reader配置">
          <el-select v-model="uploadDocForm.reader_id" placeholder="不填则 Agno 自动路由" clearable filterable style="width: 100%">
            <el-option
              v-for="item in readerList"
              :key="item.id"
              :label="`${item.name} (${item.reader_type})`"
              :value="item.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="uploadDocForm.description" type="textarea" :rows="2" placeholder="可选" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="uploadDocDialog.visible = false">取消</el-button>
        <el-button type="primary" :loading="uploadDocDialog.loading" @click="handleUploadDocument">
          上传并向量化
        </el-button>
      </template>
    </el-dialog>

    <!-- ── 插入 URL / 文本弹窗 ──────────────────────────────────────── -->
    <el-dialog
      v-model="insertDocDialog.visible"
      title="插入 URL 或文本并向量化"
      width="540px"
      :close-on-click-modal="false"
    >
      <el-form label-width="100px">
        <el-form-item label="所属知识库" required>
          <el-select v-model="insertDocForm.kb_id" placeholder="请选择知识库" filterable clearable style="width: 100%">
            <el-option
              v-for="item in kbList"
              :key="item.id"
              :label="item.name"
              :value="item.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="类型">
          <el-radio-group v-model="insertDocForm.type">
            <el-radio value="url">URL</el-radio>
            <el-radio value="text">纯文本</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item v-if="insertDocForm.type === 'url'" label="URL" required>
          <el-input v-model="insertDocForm.url" placeholder="https://..." clearable />
        </el-form-item>
        <el-form-item v-else label="文本内容" required>
          <el-input
            v-model="insertDocForm.text_content"
            type="textarea"
            :rows="6"
            placeholder="输入要向量化的文本内容..."
          />
        </el-form-item>
        <el-form-item label="文档名称">
          <el-input v-model="insertDocForm.name" placeholder="可选，留空自动生成" clearable />
        </el-form-item>
        <el-form-item label="Reader配置">
          <el-select v-model="insertDocForm.reader_id" placeholder="不填则 Agno 自动路由" clearable filterable style="width: 100%">
            <el-option
              v-for="item in readerList"
              :key="item.id"
              :label="`${item.name} (${item.reader_type})`"
              :value="item.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="insertDocForm.description" type="textarea" :rows="2" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="insertDocDialog.visible = false">取消</el-button>
        <el-button type="primary" :loading="insertDocDialog.loading" @click="handleInsertDocument">
          确认插入
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
defineOptions({
  name: "AgDocument",
  inheritAttrs: false,
});

import { ref, reactive, onMounted } from "vue";
import { ElMessage, ElMessageBox } from "element-plus";
import { QuestionFilled, ArrowUp, ArrowDown, Check, CircleClose, UploadFilled } from "@element-plus/icons-vue";
import { formatToDateTime } from "@/utils/dateUtil";
import { useDictStore } from "@/store";
import { ResultEnum } from "@/enums/api/result.enum";
import DatePicker from "@/components/DatePicker/index.vue";
import type { IContentConfig } from "@/components/CURD/types";
import ImportModal from "@/components/CURD/ImportModal.vue";
import ExportModal from "@/components/CURD/ExportModal.vue";
import AgDocumentAPI, {
  AgDocumentPageQuery,
  AgDocumentTable,
  AgDocumentForm,
  DocInsertBody,
} from "@/api/module_agno_manage/documents";
import AgKnowledgeBaseAPI from "@/api/module_agno_manage/knowledge_bases";
import AgReaderAPI from "@/api/module_agno_manage/readers";

const visible = ref(false);
const queryFormRef = ref();
const dataFormRef = ref();
const total = ref(0);
const selectIds = ref<number[]>([]);
const selectionRows = ref<AgDocumentTable[]>([]);
const loading = ref(false);
const isExpand = ref(false);
const isExpandable = ref(true);
const uploadDocRef = ref();

// 知识库列表（关联外键下拉）
const kbList = ref<{ id: number; name: string }[]>([]);

async function loadKbList() {
  const res = await AgKnowledgeBaseAPI.listAgKnowledgeBase({ page_no: 1, page_size: 20 });
  kbList.value = (res.data?.data?.items || []).map((item: any) => ({
    id: item.id,
    name: item.name || `KB#${item.id}`,
  }));
}

function getKbName(kbId?: number): string {
  if (!kbId) return "-";
  const found = kbList.value.find((e) => e.id === kbId);
  return found ? found.name : String(kbId);
}

// Reader 列表
const readerList = ref<{ id: number; name: string; reader_type: string }[]>([]);

async function loadReaderList() {
  const res = await AgReaderAPI.listAgReader({ page_no: 1, page_size: 20 });
  readerList.value = (res.data?.data?.items || []).map((item: any) => ({
    id: item.id,
    name: item.name || `Reader#${item.id}`,
    reader_type: item.reader_type || '',
  }));
}

function getReaderName(readerId?: number): string {
  if (!readerId) return "-";
  const found = readerList.value.find((e) => e.id === readerId);
  return found ? `${found.name} (${found.reader_type})` : String(readerId);
}

function docStatusTagType(status?: string): 'success' | 'warning' | 'danger' | 'info' {
  if (status === 'indexed') return 'success';
  if (status === 'pending') return 'warning';
  if (status === 'failed') return 'danger';
  return 'info';
}

function docStatusLabel(status?: string): string {
  const map: Record<string, string> = {
    pending: '待处理',
    processing: '处理中',
    indexed: '已完成',
    failed: '失败',
  };
  return map[status ?? ''] ?? (status || '-');
}

// 分页表单
const pageTableData = ref<AgDocumentTable[]>([]);

// 表格列配置
const tableColumns = ref([
  { prop: "selection", label: "选择框", show: true },
  { prop: "index", label: "序号", show: true },
  { prop: "kb_id", label: "所属知识库", show: true },
  { prop: "name", label: "文档名称", show: true },
  { prop: "storage_type", label: "存储类型", show: true },
  { prop: "storage_path", label: "存储路径", show: false },
  { prop: "doc_status", label: "向量化状态", show: true },
  { prop: "error_msg", label: "错误信息", show: true },
  { prop: "reader_id", label: "Reader", show: true },
  { prop: "status", label: "状态", show: true },
  { prop: "description", label: "描述", show: false },
  { prop: "created_time", label: "创建时间", show: true },
  { prop: "updated_time", label: "更新时间", show: false },
  { prop: "created_id", label: "创建人", show: false },
  { prop: "updated_id", label: "更新人", show: false },
  { prop: "operation", label: "操作", show: true },
]);

// 导出列（不含选择/序号/操作）
const exportColumns = [
  { prop: "kb_id", label: "所属知识库ID" },
  { prop: "name", label: "文档名称" },
  { prop: "storage_type", label: "存储类型" },
  { prop: "storage_path", label: "存储路径" },
  { prop: "doc_status", label: "向量化状态" },
  { prop: "error_msg", label: "错误信息" },
  { prop: "reader_id", label: "Reader ID" },
  { prop: "status", label: "状态" },
  { prop: "description", label: "描述" },
  { prop: "created_time", label: "创建时间" },
  { prop: "updated_time", label: "更新时间" },
  { prop: "created_id", label: "创建人ID" },
  { prop: "updated_id", label: "更新人ID" },
];

// 导入/导出配置
const curdContentConfig = {
  permPrefix: "module_agno_manage:documents",
  cols: exportColumns as any,
  importTemplate: () => AgDocumentAPI.downloadTemplateAgDocument(),
  exportsAction: async (params: any) => {
    const query: any = { ...params };
    query.status = "0";
    query.page_no = 1;
    query.page_size = 9999;
    const all: any[] = [];
    while (true) {
      const res = await AgDocumentAPI.listAgDocument(query);
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
const detailFormData = ref<AgDocumentTable>({});
// 日期范围临时变量
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

// 分页查询参数
const queryFormData = reactive<AgDocumentPageQuery>({
  page_no: 1,
  page_size: 10,
  kb_id: undefined,
  name: undefined,
  storage_type: undefined,
  storage_path: undefined,
  doc_status: undefined,
  error_msg: undefined,
  status: undefined,
  created_time: undefined,
  updated_time: undefined,
  created_id: undefined,
  updated_id: undefined,
});

// 编辑表单
const formData = reactive<AgDocumentForm>({
  id: undefined,
  kb_id: undefined,
  name: undefined,
  storage_type: undefined,
  storage_path: undefined,
  doc_status: undefined,
  error_msg: undefined,
  metadata_config: undefined,
  reader_id: undefined,
  status: "0",
  description: undefined,
});

// 字典仓库与需要加载的字典类型
const dictStore = useDictStore();
const dictTypes: any = [];

// 弹窗状态
const dialogVisible = reactive({
  title: "",
  visible: false,
  type: "create" as "create" | "update" | "detail",
});

// 表单验证规则
const rules = reactive({
  name: [{ required: true, message: "请输入文档名称", trigger: "blur" }],
  status: [{ required: false, message: "请选择状态", trigger: "change" }],
});

// 导入弹窗显示状态
const importDialogVisible = ref(false);
const uploadLoading = ref(false);

// 导出弹窗显示状态
const exportsDialogVisible = ref(false);

// 上传文件弹窗
const uploadDocDialog = reactive({ visible: false, loading: false });
const uploadDocForm = reactive({
  kb_id: undefined as number | undefined,
  file: null as File | null,
  name: '',
  description: '',
  reader_id: undefined as number | undefined,
});

// 插入 URL/文本弹窗
const insertDocDialog = reactive({ visible: false, loading: false });
const insertDocForm = reactive({
  kb_id: undefined as number | undefined,
  type: 'url' as 'url' | 'text',
  url: '',
  text_content: '',
  name: '',
  description: '',
  reader_id: undefined as number | undefined,
});

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
    const response = await AgDocumentAPI.listAgDocument(queryFormData);
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

const initialFormData: AgDocumentForm = {
  id: undefined,
  kb_id: undefined,
  name: undefined,
  storage_type: undefined,
  storage_path: undefined,
  doc_status: undefined,
  error_msg: undefined,
  metadata_config: undefined,
  reader_id: undefined,
  status: "0",
  description: undefined,
};

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
    const response = await AgDocumentAPI.detailAgDocument(id);
    if (type === "detail") {
      dialogVisible.title = "详情";
      Object.assign(detailFormData.value, response.data.data);
    } else if (type === "update") {
      dialogVisible.title = "修改";
      Object.assign(formData, response.data.data);
    }
  } else {
    dialogVisible.title = "新增文档";
    Object.assign(formData, initialFormData);
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
          await AgDocumentAPI.updateAgDocument(id, { id, ...submitData });
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
          await AgDocumentAPI.createAgDocument(submitData);
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

async function handleDelete(ids: number[]) {
  ElMessageBox.confirm("确认删除该项数据?", "警告", {
    confirmButtonText: "确定",
    cancelButtonText: "取消",
    type: "warning",
  })
    .then(async () => {
      try {
        loading.value = true;
        await AgDocumentAPI.deleteAgDocument(ids);
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
          await AgDocumentAPI.batchAgDocument({ ids: selectIds.value, status });
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

const handleUpload = async (fd: FormData) => {
  try {
    uploadLoading.value = true;
    const response = await AgDocumentAPI.importAgDocument(fd);
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

function handleUploadDocFileChange(uploadFile: any) {
  uploadDocForm.file = uploadFile.raw as File;
}

async function handleUploadDocument() {
  if (!uploadDocForm.kb_id) {
    ElMessage.warning('请选择知识库');
    return;
  }
  if (!uploadDocForm.file) {
    ElMessage.warning('请选择要上传的文件');
    return;
  }
  uploadDocDialog.loading = true;
  try {
    const fd = new FormData();
    fd.append('kb_id', String(uploadDocForm.kb_id));
    fd.append('file', uploadDocForm.file);
    if (uploadDocForm.name) fd.append('name', uploadDocForm.name);
    if (uploadDocForm.description) fd.append('description', uploadDocForm.description);
    if (uploadDocForm.reader_id != null) fd.append('reader_id', String(uploadDocForm.reader_id));
    await AgDocumentAPI.uploadDocument(fd);
    ElMessage.success('上传成功，正在向量化');
    uploadDocDialog.visible = false;
    uploadDocForm.file = null;
    uploadDocForm.name = '';
    uploadDocForm.description = '';
    uploadDocForm.reader_id = undefined;
    if (uploadDocRef.value) uploadDocRef.value.clearFiles();
    handleQuery();
  } catch (e) {
    console.error(e);
  } finally {
    uploadDocDialog.loading = false;
  }
}

async function handleInsertDocument() {
  if (!insertDocForm.kb_id) {
    ElMessage.warning('请选择知识库');
    return;
  }
  if (insertDocForm.type === 'url' && !insertDocForm.url.trim()) {
    ElMessage.warning('请输入 URL');
    return;
  }
  if (insertDocForm.type === 'text' && !insertDocForm.text_content.trim()) {
    ElMessage.warning('请输入文本内容');
    return;
  }
  insertDocDialog.loading = true;
  try {
    const body: DocInsertBody = {
      kb_id: insertDocForm.kb_id,
      name: insertDocForm.name || undefined,
      description: insertDocForm.description || undefined,
      reader_id: insertDocForm.reader_id,
    };
    if (insertDocForm.type === 'url') {
      body.url = insertDocForm.url.trim();
    } else {
      body.text_content = insertDocForm.text_content.trim();
    }
    await AgDocumentAPI.insertDocument(body);
    ElMessage.success('插入成功，正在向量化');
    insertDocDialog.visible = false;
    insertDocForm.url = '';
    insertDocForm.text_content = '';
    insertDocForm.name = '';
    insertDocForm.description = '';
    insertDocForm.reader_id = undefined;
    handleQuery();
  } catch (e) {
    console.error(e);
  } finally {
    insertDocDialog.loading = false;
  }
}

async function handleReprocessDocument(id: number) {
  try {
    await AgDocumentAPI.reprocessDocument(id);
    ElMessage.success('重新向量化已提交');
    handleQuery();
  } catch (e) {
    console.error(e);
  }
}

onMounted(async () => {
  if (dictTypes.length > 0) {
    await dictStore.getDict(dictTypes);
  }
  await Promise.all([loadKbList(), loadReaderList()]);
  loadingData();
});
</script>

<style lang="scss" scoped></style>
