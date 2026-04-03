<!-- reader管理 -->
<template>
  <div class="app-container">
    <!-- 内容区域 -->
    <el-card class="data-table">
      <template #header>
        <div class="card-header">
          <span>
            reader管理列表
            <el-tooltip content="reader管理列表">
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
            <el-form-item label="Reader名称" prop="name">
              <el-input v-model="queryFormData.name" placeholder="请输入Reader名称" clearable />
            </el-form-item>
            <el-form-item label="Reader类型(pdf/csv/excel/docx/pptx/json/markdown/text/website/firecrawl/tavily/youtube/arxiv/wikipedia/web_search/field_labeled_csv)" prop="reader_type">
              <el-input v-model="queryFormData.reader_type" placeholder="请输入Reader类型(pdf/csv/excel/docx/pptx/json/markdown/text/website/firecrawl/tavily/youtube/arxiv/wikipedia/web_search/field_labeled_csv)" clearable />
            </el-form-item>
            <el-form-item label="是否对内容分块" prop="chunk">
              <el-input v-model="queryFormData.chunk" placeholder="请输入是否对内容分块" clearable />
            </el-form-item>
            <el-form-item label="分块大小" prop="chunk_size">
              <el-input v-model="queryFormData.chunk_size" placeholder="请输入分块大小" clearable />
            </el-form-item>
            <el-form-item label="文本编码" prop="encoding">
              <el-input v-model="queryFormData.encoding" placeholder="请输入文本编码" clearable />
            </el-form-item>
            <el-form-item label="Chunking策略(FixedSizeChunker/RecursiveChunker/DocumentChunker/MarkdownChunker/RowChunker/SemanticChunker/AgenticChunker/CodeChunker)" prop="chunking_strategy">
              <el-input v-model="queryFormData.chunking_strategy" placeholder="请输入Chunking策略(FixedSizeChunker/RecursiveChunker/DocumentChunker/MarkdownChunker/RowChunker/SemanticChunker/AgenticChunker/CodeChunker)" clearable />
            </el-form-item>
            <el-form-item label="Chunk重叠字符数" prop="chunk_overlap">
              <el-input v-model="queryFormData.chunk_overlap" placeholder="请输入Chunk重叠字符数" clearable />
            </el-form-item>
            <el-form-item label="Reader专属参数" prop="reader_config">
              <el-input v-model="queryFormData.reader_config" placeholder="请输入Reader专属参数" clearable />
            </el-form-item>
            <el-form-item label="关联Embedder ID" prop="embedder_id">
              <el-input v-model="queryFormData.embedder_id" placeholder="请输入关联Embedder ID" clearable />
            </el-form-item>
            <el-form-item label="关联Model ID" prop="model_id">
              <el-input v-model="queryFormData.model_id" placeholder="请输入关联Model ID" clearable />
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
                v-hasPerm="['module_agno_manage:readers:query']"
                type="primary"
                icon="search"
                @click="handleQuery"
              >
                查询
              </el-button>
              <el-button
                v-hasPerm="['module_agno_manage:readers:query']"
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
                v-hasPerm="['module_agno_manage:readers:create']"
                type="success"
                icon="plus"
                @click="handleOpenDialog('create')"
              >
                新增
              </el-button>
            </el-col>
            <el-col :span="1.5">
              <el-button
                v-hasPerm="['module_agno_manage:readers:delete']"
                type="danger"
                icon="delete"
                :disabled="selectIds.length === 0"
                @click="handleDelete(selectIds)"
              >
                批量删除
              </el-button>
            </el-col>
            <el-col :span="1.5">
              <el-dropdown v-hasPerm="['module_agno_manage:readers:batch']" trigger="click">
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
                  v-hasPerm="['module_agno_manage:readers:import']"
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
                  v-hasPerm="['module_agno_manage:readers:export']"
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
                  v-hasPerm="['module_agno_manage:readers:query']"
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
          label="Reader名称"
          prop="name"
          min-width="140"
          show-overflow-tooltip
        />
        <el-table-column
          v-if="tableColumns.find((col) => col.prop === 'reader_type')?.show"
          label="Reader类型(pdf/csv/excel/docx/pptx/json/markdown/text/website/firecrawl/tavily/youtube/arxiv/wikipedia/web_search/field_labeled_csv)"
          prop="reader_type"
          min-width="140"
          show-overflow-tooltip
        />
        <el-table-column
          v-if="tableColumns.find((col) => col.prop === 'chunk')?.show"
          label="是否对内容分块"
          prop="chunk"
          min-width="140"
          show-overflow-tooltip
        />
        <el-table-column
          v-if="tableColumns.find((col) => col.prop === 'chunk_size')?.show"
          label="分块大小"
          prop="chunk_size"
          min-width="140"
          show-overflow-tooltip
        />
        <el-table-column
          v-if="tableColumns.find((col) => col.prop === 'encoding')?.show"
          label="文本编码"
          prop="encoding"
          min-width="140"
          show-overflow-tooltip
        />
        <el-table-column
          v-if="tableColumns.find((col) => col.prop === 'chunking_strategy')?.show"
          label="Chunking策略(FixedSizeChunker/RecursiveChunker/DocumentChunker/MarkdownChunker/RowChunker/SemanticChunker/AgenticChunker/CodeChunker)"
          prop="chunking_strategy"
          min-width="140"
          show-overflow-tooltip
        />
        <el-table-column
          v-if="tableColumns.find((col) => col.prop === 'chunk_overlap')?.show"
          label="Chunk重叠字符数"
          prop="chunk_overlap"
          min-width="140"
          show-overflow-tooltip
        />
        <el-table-column
          v-if="tableColumns.find((col) => col.prop === 'reader_config')?.show"
          label="Reader专属参数"
          prop="reader_config"
          min-width="140"
          show-overflow-tooltip
        />
        <el-table-column
          v-if="tableColumns.find((col) => col.prop === 'embedder_id')?.show"
          label="关联Embedder ID"
          prop="embedder_id"
          min-width="140"
          show-overflow-tooltip
        />
        <el-table-column
          v-if="tableColumns.find((col) => col.prop === 'model_id')?.show"
          label="关联Model ID"
          prop="model_id"
          min-width="140"
          show-overflow-tooltip
        />
        <el-table-column
          v-if="tableColumns.find((col) => col.prop === 'status')?.show"
          label="是否启用(0:启用 1:禁用)"
          prop="status"
          min-width="140"
          show-overflow-tooltip
        />
        <el-table-column
          v-if="tableColumns.find((col) => col.prop === 'status')?.show"
          label="是否启用(0:启用 1:禁用)"
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
          label="备注/描述"
          prop="description"
          min-width="140"
          show-overflow-tooltip
        />
        <el-table-column
          v-if="tableColumns.find((col) => col.prop === 'created_time')?.show"
          label="创建时间"
          prop="created_time"
          min-width="140"
          show-overflow-tooltip
        />
        <el-table-column
          v-if="tableColumns.find((col) => col.prop === 'updated_time')?.show"
          label="更新时间"
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
              v-hasPerm="['module_agno_manage:readers:detail']"
              type="info"
              size="small"
              link
              icon="document"
              @click="handleOpenDialog('detail', scope.row.id)"
            >
              详情
            </el-button>
            <el-button
              v-hasPerm="['module_agno_manage:readers:update']"
              type="primary"
              size="small"
              link
              icon="edit"
              @click="handleOpenDialog('update', scope.row.id)"
            >
              编辑
            </el-button>
            <el-button
              v-hasPerm="['module_agno_manage:readers:delete']"
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
          <el-descriptions-item label="Reader名称" :span="2">
            {{ detailFormData.name }}
          </el-descriptions-item>
          <el-descriptions-item label="Reader类型(pdf/csv/excel/docx/pptx/json/markdown/text/website/firecrawl/tavily/youtube/arxiv/wikipedia/web_search/field_labeled_csv)" :span="2">
            {{ detailFormData.reader_type }}
          </el-descriptions-item>
          <el-descriptions-item label="是否对内容分块" :span="2">
            {{ detailFormData.chunk }}
          </el-descriptions-item>
          <el-descriptions-item label="分块大小" :span="2">
            {{ detailFormData.chunk_size }}
          </el-descriptions-item>
          <el-descriptions-item label="文本编码" :span="2">
            {{ detailFormData.encoding }}
          </el-descriptions-item>
          <el-descriptions-item label="Chunking策略(FixedSizeChunker/RecursiveChunker/DocumentChunker/MarkdownChunker/RowChunker/SemanticChunker/AgenticChunker/CodeChunker)" :span="2">
            {{ detailFormData.chunking_strategy }}
          </el-descriptions-item>
          <el-descriptions-item label="Chunk重叠字符数" :span="2">
            {{ detailFormData.chunk_overlap }}
          </el-descriptions-item>
          <el-descriptions-item label="Reader专属参数" :span="2">
            {{ detailFormData.reader_config }}
          </el-descriptions-item>
          <el-descriptions-item label="关联Embedder ID" :span="2">
            {{ detailFormData.embedder_id }}
          </el-descriptions-item>
          <el-descriptions-item label="关联Model ID" :span="2">
            {{ detailFormData.model_id }}
          </el-descriptions-item>
          <el-descriptions-item label="状态" :span="2">
            <el-tag :type="detailFormData.status == '0' ? 'success' : 'danger'">
              {{ detailFormData.status == "0" ? "启用" : "停用" }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="备注/描述" :span="2">
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
          <el-form-item label="Reader名称" prop="name" :required="false">
            <el-input v-model="formData.name" placeholder="请输入Reader名称" />
          </el-form-item>
          <el-form-item label="Reader类型(pdf/csv/excel/docx/pptx/json/markdown/text/website/firecrawl/tavily/youtube/arxiv/wikipedia/web_search/field_labeled_csv)" prop="reader_type" :required="false">
            <el-input v-model="formData.reader_type" placeholder="请输入Reader类型(pdf/csv/excel/docx/pptx/json/markdown/text/website/firecrawl/tavily/youtube/arxiv/wikipedia/web_search/field_labeled_csv)" />
          </el-form-item>
          <el-form-item label="是否对内容分块" prop="chunk" :required="false">
            <el-input v-model="formData.chunk" placeholder="请输入是否对内容分块" />
          </el-form-item>
          <el-form-item label="分块大小" prop="chunk_size" :required="false">
            <el-input v-model="formData.chunk_size" placeholder="请输入分块大小" />
          </el-form-item>
          <el-form-item label="文本编码" prop="encoding" :required="false">
            <el-input v-model="formData.encoding" placeholder="请输入文本编码" />
          </el-form-item>
          <el-form-item label="Chunking策略(FixedSizeChunker/RecursiveChunker/DocumentChunker/MarkdownChunker/RowChunker/SemanticChunker/AgenticChunker/CodeChunker)" prop="chunking_strategy" :required="false">
            <el-input v-model="formData.chunking_strategy" placeholder="请输入Chunking策略(FixedSizeChunker/RecursiveChunker/DocumentChunker/MarkdownChunker/RowChunker/SemanticChunker/AgenticChunker/CodeChunker)" />
          </el-form-item>
          <el-form-item label="Chunk重叠字符数" prop="chunk_overlap" :required="false">
            <el-input v-model="formData.chunk_overlap" placeholder="请输入Chunk重叠字符数" />
          </el-form-item>
          <el-form-item label="Reader专属参数" prop="reader_config" :required="false">
            <el-input v-model="formData.reader_config" placeholder="请输入Reader专属参数" />
          </el-form-item>
          <el-form-item label="关联Embedder ID" prop="embedder_id" :required="false">
            <el-input v-model="formData.embedder_id" placeholder="请输入关联Embedder ID" />
          </el-form-item>
          <el-form-item label="关联Model ID" prop="model_id" :required="false">
            <el-input v-model="formData.model_id" placeholder="请输入关联Model ID" />
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
  name: "AgReader",
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
import AgReaderAPI, {
  AgReaderPageQuery,
  AgReaderTable,
  AgReaderForm,
} from "@/api/module_agno_manage/readers";

const visible = ref(true);
const queryFormRef = ref();
const dataFormRef = ref();
const total = ref(0);
const selectIds = ref<number[]>([]);
const selectionRows = ref<AgReaderTable[]>([]);
const loading = ref(false);
const isExpand = ref(false);
const isExpandable = ref(true);

// 分页表单
const pageTableData = ref<AgReaderTable[]>([]);

// 表格列配置
const tableColumns = ref([
  { prop: "selection", label: "选择框", show: true },
  { prop: "index", label: "序号", show: true },
  { prop: "name", label: "Reader名称", show: true },
  { prop: "reader_type", label: "Reader类型(pdf/csv/excel/docx/pptx/json/markdown/text/website/firecrawl/tavily/youtube/arxiv/wikipedia/web_search/field_labeled_csv)", show: true },
  { prop: "chunk", label: "是否对内容分块", show: true },
  { prop: "chunk_size", label: "分块大小（字符数）", show: true },
  { prop: "encoding", label: "文本编码（utf-8/gbk等，文本类Reader使用）", show: true },
  { prop: "chunking_strategy", label: "Chunking策略(FixedSizeChunker/RecursiveChunker/DocumentChunker/MarkdownChunker/RowChunker/SemanticChunker/AgenticChunker/CodeChunker)", show: true },
  { prop: "chunk_overlap", label: "Chunk重叠字符数（FixedSize/Recursive/Document/Markdown策略支持）", show: true },
  { prop: "reader_config", label: "Reader专属参数（按reader_type不同，见表注释）", show: true },
  { prop: "embedder_id", label: "关联Embedder ID（SemanticChunker使用）", show: true },
  { prop: "model_id", label: "关联Model ID（AgenticChunker使用）", show: true },
  { prop: "status", label: "是否启用(0:启用 1:禁用)", show: true },
  { prop: "description", label: "备注/描述", show: true },
  { prop: "created_time", label: "创建时间", show: true },
  { prop: "updated_time", label: "更新时间", show: true },
  { prop: "created_id", label: "created_id", show: true },
  { prop: "updated_id", label: "updated_id", show: true },
  { prop: "operation", label: "操作", show: true },
]);

// 导出列（不含选择/序号/操作）
const exportColumns = [
  { prop: "name", label: "Reader名称" },
  { prop: "reader_type", label: "Reader类型(pdf/csv/excel/docx/pptx/json/markdown/text/website/firecrawl/tavily/youtube/arxiv/wikipedia/web_search/field_labeled_csv)" },
  { prop: "chunk", label: "是否对内容分块" },
  { prop: "chunk_size", label: "分块大小（字符数）" },
  { prop: "encoding", label: "文本编码（utf-8/gbk等，文本类Reader使用）" },
  { prop: "chunking_strategy", label: "Chunking策略(FixedSizeChunker/RecursiveChunker/DocumentChunker/MarkdownChunker/RowChunker/SemanticChunker/AgenticChunker/CodeChunker)" },
  { prop: "chunk_overlap", label: "Chunk重叠字符数（FixedSize/Recursive/Document/Markdown策略支持）" },
  { prop: "reader_config", label: "Reader专属参数（按reader_type不同，见表注释）" },
  { prop: "embedder_id", label: "关联Embedder ID（SemanticChunker使用）" },
  { prop: "model_id", label: "关联Model ID（AgenticChunker使用）" },
  { prop: "status", label: "是否启用(0:启用 1:禁用)" },
  { prop: "description", label: "备注/描述" },
  { prop: "created_time", label: "创建时间" },
  { prop: "updated_time", label: "更新时间" },
  { prop: "created_id", label: "created_id" },
  { prop: "updated_id", label: "updated_id" },
];

// 导入/导出配置
const curdContentConfig = {
  permPrefix: "module_agno_manage:readers",
  cols: exportColumns as any,
  importTemplate: () => AgReaderAPI.downloadTemplateAgReader(),
  exportsAction: async (params: any) => {
    const query: any = { ...params };
    query.status = "0";
    query.page_no = 1;
    query.page_size = 9999;
    const all: any[] = [];
    while (true) {
      const res = await AgReaderAPI.listAgReader(query);
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
const detailFormData = ref<AgReaderTable>({});
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
const queryFormData = reactive<AgReaderPageQuery>({
  page_no: 1,
  page_size: 10,
  name: undefined,
  reader_type: undefined,
  chunk: undefined,
  chunk_size: undefined,
  encoding: undefined,
  chunking_strategy: undefined,
  chunk_overlap: undefined,
  reader_config: undefined,
  embedder_id: undefined,
  model_id: undefined,
  status: undefined,
  created_time: undefined,
  updated_time: undefined,
  created_id: undefined,
  updated_id: undefined,
});

// 编辑表单
const formData = reactive<AgReaderForm>({
  id: undefined,
  name: undefined,
  reader_type: undefined,
  chunk: undefined,
  chunk_size: undefined,
  encoding: undefined,
  chunking_strategy: undefined,
  chunk_overlap: undefined,
  reader_config: undefined,
  embedder_id: undefined,
  model_id: undefined,
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
  name: [{ required: false, message: "请输入Reader名称", trigger: "blur" }],
  reader_type: [{ required: false, message: "请输入Reader类型(pdf/csv/excel/docx/pptx/json/markdown/text/website/firecrawl/tavily/youtube/arxiv/wikipedia/web_search/field_labeled_csv)", trigger: "blur" }],
  chunk: [{ required: false, message: "请输入是否对内容分块", trigger: "blur" }],
  chunk_size: [{ required: false, message: "请输入分块大小（字符数）", trigger: "blur" }],
  encoding: [{ required: true, message: "请输入文本编码（utf-8/gbk等，文本类Reader使用）", trigger: "blur" }],
  chunking_strategy: [{ required: true, message: "请输入Chunking策略(FixedSizeChunker/RecursiveChunker/DocumentChunker/MarkdownChunker/RowChunker/SemanticChunker/AgenticChunker/CodeChunker)", trigger: "blur" }],
  chunk_overlap: [{ required: false, message: "请输入Chunk重叠字符数（FixedSize/Recursive/Document/Markdown策略支持）", trigger: "blur" }],
  reader_config: [{ required: false, message: "请输入Reader专属参数（按reader_type不同，见表注释）", trigger: "blur" }],
  embedder_id: [{ required: true, message: "请输入关联Embedder ID（SemanticChunker使用）", trigger: "blur" }],
  model_id: [{ required: true, message: "请输入关联Model ID（AgenticChunker使用）", trigger: "blur" }],
  status: [{ required: false, message: "请输入是否启用(0:启用 1:禁用)", trigger: "blur" }],
  description: [{ required: true, message: "请输入备注/描述", trigger: "blur" }],
  created_time: [{ required: false, message: "请输入创建时间", trigger: "blur" }],
  updated_time: [{ required: false, message: "请输入更新时间", trigger: "blur" }],
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
    const response = await AgReaderAPI.listAgReader(queryFormData);
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
const initialFormData: AgReaderForm = {
  id: undefined,
  name: undefined,
  reader_type: undefined,
  chunk: undefined,
  chunk_size: undefined,
  encoding: undefined,
  chunking_strategy: undefined,
  chunk_overlap: undefined,
  reader_config: undefined,
  embedder_id: undefined,
  model_id: undefined,
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
    const response = await AgReaderAPI.detailAgReader(id);
    if (type === "detail") {
      dialogVisible.title = "详情";
      Object.assign(detailFormData.value, response.data.data);
    } else if (type === "update") {
      dialogVisible.title = "修改";
      Object.assign(formData, response.data.data);
    }
  } else {
    dialogVisible.title = "新增AgReader";
    formData.id = undefined;
    formData.name = undefined;
    formData.reader_type = undefined;
    formData.chunk = undefined;
    formData.chunk_size = undefined;
    formData.encoding = undefined;
    formData.chunking_strategy = undefined;
    formData.chunk_overlap = undefined;
    formData.reader_config = undefined;
    formData.embedder_id = undefined;
    formData.model_id = undefined;
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
          await AgReaderAPI.updateAgReader(id, { id, ...submitData });
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
          await AgReaderAPI.createAgReader(submitData);
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
        await AgReaderAPI.deleteAgReader(ids);
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
          await AgReaderAPI.batchAgReader({ ids: selectIds.value, status });
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
    const response = await AgReaderAPI.importAgReader(formData);
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
