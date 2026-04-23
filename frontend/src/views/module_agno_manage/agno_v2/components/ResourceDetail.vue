<!-- 资源详情面板 -->
<template>
  <el-descriptions :column="2" border>
    <el-descriptions-item label="ID">{{ row.id }}</el-descriptions-item>
    <el-descriptions-item label="UUID">{{ row.uuid }}</el-descriptions-item>
    <el-descriptions-item label="名称">{{ row.name }}</el-descriptions-item>
    <el-descriptions-item label="类别">{{ row.category }}</el-descriptions-item>
    <el-descriptions-item label="类型">{{ row.type }}</el-descriptions-item>
    <el-descriptions-item label="状态">
      <el-tag :type="row.status === '0' ? 'success' : 'danger'">
        {{ row.status === "0" ? "启用" : "停用" }}
      </el-tag>
    </el-descriptions-item>
    <el-descriptions-item label="描述" :span="2">{{ row.description ?? "—" }}</el-descriptions-item>
    <el-descriptions-item label="配置" :span="2">
      <el-scrollbar max-height="300px">
        <pre class="config-pre">{{ JSON.stringify(row.config, null, 2) }}</pre>
      </el-scrollbar>
    </el-descriptions-item>
    <el-descriptions-item label="创建人">
      {{ row.created_by?.username ?? row.created_by?.id ?? "—" }}
    </el-descriptions-item>
    <el-descriptions-item label="更新人">
      {{ row.updated_by?.username ?? row.updated_by?.id ?? "—" }}
    </el-descriptions-item>
    <el-descriptions-item label="创建时间">{{ row.created_time }}</el-descriptions-item>
    <el-descriptions-item label="更新时间">{{ row.updated_time }}</el-descriptions-item>
  </el-descriptions>
</template>

<script setup lang="ts">
import type { ResourceTable } from "@/api/module_agno_manage_v2/resources";

interface Props {
  row: ResourceTable;
}
defineProps<Props>();
</script>

<style scoped>
.config-pre {
  font-size: 12px;
  line-height: 1.5;
  margin: 0;
  white-space: pre-wrap;
  word-break: break-all;
}
</style>
