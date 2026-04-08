<!-- 通用资源列表组件，接收 category prop -->
<template>
  <div class="app-container">
    <el-card class="data-table">
      <template #header>
        <div class="card-header">
          <span>{{ categoryLabel }}管理</span>
        </div>

        <!-- 搜索栏 -->
        <div v-show="searchVisible" class="search-container">
          <el-form
            ref="queryFormRef"
            :model="query"
            label-suffix=":"
            :inline="true"
            @submit.prevent="handleQuery"
          >
            <el-form-item label="名称" prop="name">
              <el-input v-model="query.name" placeholder="请输入名称" clearable />
            </el-form-item>
            <el-form-item label="类型" prop="type">
              <el-select v-model="query.type" placeholder="请选择类型" clearable style="width: 160px">
                <el-option
                  v-for="t in schemaTypes"
                  :key="t.type"
                  :label="t.label"
                  :value="t.type"
                />
              </el-select>
            </el-form-item>
            <el-form-item prop="status" label="状态">
              <el-select v-model="query.status" placeholder="请选择状态" clearable style="width: 120px">
                <el-option value="0" label="启用" />
                <el-option value="1" label="停用" />
              </el-select>
            </el-form-item>
            <el-form-item>
              <el-button type="primary" icon="search" @click="handleQuery">查询</el-button>
              <el-button icon="refresh" @click="handleResetQuery">重置</el-button>
            </el-form-item>
          </el-form>
        </div>
      </template>

      <!-- 工具栏 -->
      <div class="data-table__toolbar">
        <div class="data-table__toolbar--left">
          <el-row :gutter="10">
            <el-col :span="1.5">
              <el-button
                v-hasPerm="[`module_agno_manage_v2:${category}:create`]"
                type="success"
                icon="plus"
                @click="handleOpenCreate"
              >
                新增
              </el-button>
            </el-col>
            <el-col :span="1.5">
              <el-button
                v-hasPerm="[`module_agno_manage_v2:${category}:delete`]"
                type="danger"
                icon="delete"
                :disabled="selectIds.length === 0"
                @click="handleDelete(selectIds)"
              >
                批量删除
              </el-button>
            </el-col>
            <el-col :span="1.5">
              <el-dropdown
                v-hasPerm="[`module_agno_manage_v2:${category}:batch`]"
                trigger="click"
              >
                <el-button type="default" :disabled="selectIds.length === 0" icon="ArrowDown">
                  更多
                </el-button>
                <template #dropdown>
                  <el-dropdown-menu>
                    <el-dropdown-item @click="handleBatchStatus('0')">批量启用</el-dropdown-item>
                    <el-dropdown-item @click="handleBatchStatus('1')">批量停用</el-dropdown-item>
                  </el-dropdown-menu>
                </template>
              </el-dropdown>
            </el-col>
          </el-row>
        </div>
        <div class="data-table__toolbar--right">
          <el-row :gutter="10">
            <el-col :span="1.5">
              <el-tooltip content="搜索显示/隐藏">
                <el-button type="info" icon="search" circle @click="searchVisible = !searchVisible" />
              </el-tooltip>
            </el-col>
            <el-col :span="1.5">
              <el-tooltip content="刷新">
                <el-button type="primary" icon="refresh" circle @click="loadData" />
              </el-tooltip>
            </el-col>
          </el-row>
        </div>
      </div>

      <!-- 表格 -->
      <el-table
        ref="tableRef"
        v-loading="loading"
        :data="tableData"
        highlight-current-row
        class="data-table__content"
        border
        stripe
        @selection-change="(rows: any[]) => (selectIds = rows.map((r) => r.id))"
      >
        <template #empty>
          <el-empty :image-size="80" description="暂无数据" />
        </template>
        <el-table-column type="selection" min-width="55" align="center" />
        <el-table-column fixed label="序号" min-width="60">
          <template #default="scope">
            {{ (query.page_no - 1) * query.page_size + scope.$index + 1 }}
          </template>
        </el-table-column>
        <el-table-column label="名称" prop="name" min-width="160" show-overflow-tooltip />
        <el-table-column label="类型" prop="type" min-width="140" show-overflow-tooltip>
          <template #default="scope">
            {{ schemaTypes.find((t) => t.type === scope.row.type)?.label ?? scope.row.type }}
          </template>
        </el-table-column>
        <el-table-column label="UUID" prop="uuid" min-width="280" show-overflow-tooltip />
        <el-table-column label="状态" prop="status" min-width="80" align="center">
          <template #default="scope">
            <el-tag :type="scope.row.status === '0' ? 'success' : 'danger'">
              {{ scope.row.status === "0" ? "启用" : "停用" }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="创建时间" prop="created_time" min-width="170" show-overflow-tooltip />
        <el-table-column label="操作" fixed="right" min-width="180" align="center">
          <template #default="scope">
            <el-button
              v-hasPerm="[`module_agno_manage_v2:${category}:query`]"
              link
              type="primary"
              icon="view"
              @click="handleOpenDetail(scope.row)"
            >
              详情
            </el-button>
            <el-button
              v-hasPerm="[`module_agno_manage_v2:${category}:update`]"
              link
              type="primary"
              icon="edit"
              @click="handleOpenEdit(scope.row)"
            >
              编辑
            </el-button>
            <el-button
              v-hasPerm="[`module_agno_manage_v2:${category}:delete`]"
              link
              type="danger"
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
        <Pagination
          v-model:page="query.page_no"
          v-model:limit="query.page_size"
          :total="total"
          @pagination="loadData"
        />
      </template>
    </el-card>

    <!-- 创建/编辑弹窗 -->
    <ResourceFormDialog
      v-model="formDialogVisible"
      :category="category"
      :edit-data="editData"
      @success="loadData"
    />

    <!-- 详情弹窗 -->
    <el-dialog v-model="detailDialogVisible" title="资源详情" width="700px">
      <ResourceDetail v-if="detailRow" :row="detailRow" />
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from "vue";
import { ElMessage, ElMessageBox } from "element-plus";
import ResourceAPI from "@/api/module_agno_manage_v2/resources";
import type { ResourceTable, ResourcePageQuery } from "@/api/module_agno_manage_v2/resources";
import Pagination from "@/components/Pagination/index.vue";
import ResourceFormDialog from "./ResourceFormDialog.vue";
import ResourceDetail from "./ResourceDetail.vue";

interface Props {
  category: string;
  categoryLabel?: string;
}

const props = withDefaults(defineProps<Props>(), {
  categoryLabel: "资源",
});

const searchVisible = ref(false);
const loading = ref(false);
const tableData = ref<ResourceTable[]>([]);
const total = ref(0);
const selectIds = ref<number[]>([]);
const schemaTypes = ref<Array<{ type: string; label: string }>>([]);

const query = reactive<ResourcePageQuery>({
  page_no: 1,
  page_size: 10,
  category: props.category,
  name: undefined,
  type: undefined,
  status: undefined,
});

// 弹窗状态
const formDialogVisible = ref(false);
const editData = ref<any>(undefined);
const detailDialogVisible = ref(false);
const detailRow = ref<ResourceTable | undefined>(undefined);

async function loadData() {
  loading.value = true;
  try {
    query.category = props.category;
    const res = await ResourceAPI.listResources(query);
    tableData.value = res.data.data.items ?? [];
    total.value = res.data.data.total ?? 0;
  } catch (e) {
    console.error("[ResourceList] loadData error:", e);
  } finally {
    loading.value = false;
  }
}

async function loadSchemaTypes() {
  try {
    const res = await ResourceAPI.getSchemaTypes(props.category);
    schemaTypes.value = res.data.data.types ?? [];
  } catch {/* ignore */}
}

function handleQuery() {
  query.page_no = 1;
  loadData();
}

function handleResetQuery() {
  query.name = undefined;
  query.type = undefined;
  query.status = undefined;
  query.page_no = 1;
  loadData();
}

function handleOpenCreate() {
  editData.value = undefined;
  formDialogVisible.value = true;
}

async function handleOpenEdit(row: ResourceTable) {
  const res = await ResourceAPI.detailResource(row.id!);
  editData.value = res.data.data;
  formDialogVisible.value = true;
}

function handleOpenDetail(row: ResourceTable) {
  detailRow.value = row;
  detailDialogVisible.value = true;
}

async function handleDelete(ids: number[]) {
  await ElMessageBox.confirm("确认删除该项数据?", "警告", {
    confirmButtonText: "确定",
    cancelButtonText: "取消",
    type: "warning",
  });
  loading.value = true;
  try {
    await ResourceAPI.deleteResources(ids);
    ElMessage.success("删除成功");
    loadData();
  } finally {
    loading.value = false;
  }
}

async function handleBatchStatus(status: string) {
  if (!selectIds.value.length) return;
  await ElMessageBox.confirm(`确认${status === "0" ? "启用" : "停用"}所选数据?`, "警告", {
    confirmButtonText: "确定",
    cancelButtonText: "取消",
    type: "warning",
  });
  loading.value = true;
  try {
    await ResourceAPI.batchSetAvailable({ ids: selectIds.value, status });
    ElMessage.success("操作成功");
    loadData();
  } finally {
    loading.value = false;
  }
}

onMounted(async () => {
  await loadSchemaTypes();
  loadData();
});
</script>

<style lang="scss" scoped></style>
