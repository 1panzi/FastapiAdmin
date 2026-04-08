<!-- ref_or_inline 字段：引用已有资源 | 内联定义 | 引用+覆盖 -->
<template>
  <div class="ref-or-inline-field">
    <!-- 模式切换 -->
    <el-radio-group v-model="mode" class="mode-switcher" @change="handleModeChange">
      <el-radio-button value="ref">
        <el-icon><Link /></el-icon> 引用资源
      </el-radio-button>
      <el-radio-button value="inline">
        <el-icon><EditPen /></el-icon> 内联定义
      </el-radio-button>
      <el-radio-button v-if="overridableFields.length > 0" value="override">
        <el-icon><MagicStick /></el-icon> 引用+覆盖
      </el-radio-button>
    </el-radio-group>

    <!-- 引用模式：只选 uuid -->
    <template v-if="mode === 'ref'">
      <div class="ref-select-wrap">
        <LazySelect
          :model-value="refUuid"
          :fetcher="fetchResources"
          placeholder="请选择资源"
          @update:model-value="handleRefChange"
        />
      </div>
    </template>

    <!-- 内联模式：选 type 后显示动态 schema -->
    <template v-else-if="mode === 'inline'">
      <div class="inline-type-select">
        <el-select
          v-model="inlineType"
          placeholder="请选择类型"
          clearable
          style="width: 100%"
          @change="handleInlineTypeChange"
        >
          <el-option
            v-for="t in schemaTypes"
            :key="t.type"
            :label="t.label"
            :value="t.type"
          />
        </el-select>
      </div>

      <!-- 树形分支：inline 子字段 -->
      <div v-if="inlineType && inlineSchema" class="tree-branch" :style="branchStyle">
        <div class="tree-branch-header">
          <el-icon class="tree-branch-icon"><Document /></el-icon>
          <span class="tree-branch-title">{{ inlineSchema.label ?? inlineType }}</span>
          <el-tag size="small" type="info" class="ml-2">内联</el-tag>
        </div>
        <div class="tree-branch-body">
          <DynamicFormRendererInner
            ref="inlineRendererRef"
            :fields="inlineSchema.fields"
            :form-data="inlineConfig"
            :standalone="true"
            :depth="depth + 1"
          />
        </div>
      </div>
    </template>

    <!-- 引用+覆盖模式 -->
    <template v-else-if="mode === 'override'">
      <div class="ref-select-wrap">
        <LazySelect
          :model-value="refUuid"
          :fetcher="fetchResources"
          placeholder="请选择基础资源"
          @update:model-value="(v) => { refUuid = v; emitValue(); }"
        />
      </div>

      <!-- 树形分支：override 子字段 -->
      <div v-if="overrideSchema" class="tree-branch" :style="branchStyle">
        <div class="tree-branch-header">
          <el-icon class="tree-branch-icon"><Edit /></el-icon>
          <span class="tree-branch-title">覆盖配置</span>
          <el-tag size="small" type="warning" class="ml-2">留空则沿用原值</el-tag>
        </div>
        <div class="tree-branch-body">
          <DynamicFormRendererInner
            ref="overrideRendererRef"
            :fields="overrideSchema.fields.filter(f => overridableFields.includes(f.name))"
            :form-data="overrideConfig"
            :standalone="true"
            :depth="depth + 1"
          />
        </div>
      </div>
    </template>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted } from "vue";
import { Link, EditPen, MagicStick, Document, Edit } from "@element-plus/icons-vue";
import ResourceAPI from "@/api/module_agno_manage_v2/resources";
import type { SchemaResult } from "@/api/module_agno_manage_v2/resources";
import LazySelect from "../../components/LazySelect/index.vue";
import DynamicFormRendererInner from "./DynamicFormRenderer.vue";

interface Props {
  modelValue?: any;         // { ref: uuid } | { ref, override: {} } | { category, type, ...config }
  sourceCategory: string;  // 资源来源 category
  overridableFields: string[];
  /** 当前嵌套深度，由父级 DynamicFormRenderer 传入，默认 0 */
  depth?: number;
}

const props = defineProps<Props>();
const emit = defineEmits<{ "update:modelValue": [v: any] }>();

// 不同深度对应的左边框颜色
const BRANCH_COLORS = [
  "var(--el-color-primary)",
  "var(--el-color-success)",
  "var(--el-color-warning)",
  "var(--el-color-danger)",
  "#909399",
];

const branchStyle = computed(() => {
  const d = props.depth ?? 0;
  const color = BRANCH_COLORS[d % BRANCH_COLORS.length];
  return { "--branch-color": color };
});

type Mode = "ref" | "inline" | "override";
const mode = ref<Mode>("ref");
const refUuid = ref<string | undefined>(undefined);
const inlineType = ref<string | undefined>(undefined);
const inlineConfig = ref<Record<string, any>>({});
const overrideConfig = ref<Record<string, any>>({});
const schemaTypes = ref<Array<{ type: string; label: string }>>([]);
const inlineSchema = ref<SchemaResult | null>(null);
const overrideSchema = ref<SchemaResult | null>(null);

/** 子 DynamicFormRenderer 实例 ref，用于递归 validate */
const inlineRendererRef = ref<any>(null);
const overrideRendererRef = ref<any>(null);

/** 上一次 emit 出去的序列化值，用于防止父→子→父的循环 */
let lastEmitted = "";

// 解析 modelValue → mode + 子字段
function parseValue(val: any) {
  if (!val) { mode.value = "ref"; return; }
  if (val.ref && val.override) {
    mode.value = "override";
    refUuid.value = val.ref;
    overrideConfig.value = val.override ?? {};
  } else if (val.ref) {
    mode.value = "ref";
    refUuid.value = val.ref;
  } else {
    mode.value = "inline";
    const { category, type, ...rest } = val;
    inlineType.value = type;
    inlineConfig.value = rest;
    // 编辑回显时：若 inlineSchema 尚未加载（或类型变了）则自动加载
    if (type && props.sourceCategory && inlineSchema.value?.type !== type) {
      ResourceAPI.getSchemaFields(props.sourceCategory, type)
        .then((res) => { inlineSchema.value = res.data.data; })
        .catch(() => {});
    }
  }
}

// 发出新值
function emitValue() {
  let val: any;
  if (mode.value === "ref") {
    val = refUuid.value ? { ref: refUuid.value } : undefined;
  } else if (mode.value === "inline") {
    if (!inlineType.value) { val = undefined; }
    else { val = { category: props.sourceCategory, type: inlineType.value, ...inlineConfig.value }; }
  } else {
    val = refUuid.value
      ? { ref: refUuid.value, override: { ...overrideConfig.value } }
      : undefined;
  }
  lastEmitted = JSON.stringify(val);
  emit("update:modelValue", val);
}

function handleModeChange() {
  refUuid.value = undefined;
  inlineType.value = undefined;
  inlineConfig.value = {};
  overrideConfig.value = {};
  emitValue();
}

function handleRefChange(uuid: string | undefined) {
  refUuid.value = uuid;
  emitValue();
}

async function handleInlineTypeChange(type: string) {
  inlineType.value = type;
  inlineConfig.value = {};
  if (type && props.sourceCategory) {
    const res = await ResourceAPI.getSchemaFields(props.sourceCategory, type);
    inlineSchema.value = res.data.data;
  }
  emitValue();
}

async function fetchResources(params: { page_no: number; page_size: number; name?: string }) {
  const res = await ResourceAPI.listResources({ ...params, category: props.sourceCategory });
  const items = res.data.data.items ?? [];
  return {
    items: items.map((r: any) => ({ value: r.uuid, label: r.name })),
    total: res.data.data.total ?? 0,
  };
}

// 加载 category 下的 type 列表
async function loadSchemaTypes() {
  if (!props.sourceCategory) return;
  const res = await ResourceAPI.getSchemaTypes(props.sourceCategory);
  schemaTypes.value = res.data.data.types ?? [];
  // schemaTypes 加载完成后，补触发一次 override schema 加载
  // （编辑回显时 refUuid 已有值但 schemaTypes 当时为空，watch 未执行）
  if (mode.value === "override" && refUuid.value && !overrideSchema.value) {
    loadOverrideSchema(refUuid.value);
  }
}

// 加载 override schema（抽成独立函数，方便复用）
async function loadOverrideSchema(uuid: string) {
  if (!props.sourceCategory) return;
  try {
    const listRes = await ResourceAPI.listResources({ page_no: 1, page_size: 100, category: props.sourceCategory });
    const found = listRes.data.data.items?.find((r: any) => r.uuid === uuid);
    if (found?.type) {
      const schemaRes = await ResourceAPI.getSchemaFields(props.sourceCategory, found.type);
      overrideSchema.value = schemaRes.data.data;
    }
  } catch {/* ignore */}
}

// 加载 override schema
watch(refUuid, async (uuid) => {
  if (mode.value === "override" && uuid && props.sourceCategory && schemaTypes.value.length > 0) {
    loadOverrideSchema(uuid);
  }
});

watch(() => props.modelValue, (val) => {
  const serialized = JSON.stringify(val);
  if (serialized === lastEmitted) return;
  parseValue(val);
}, { immediate: true });
watch(inlineConfig, emitValue, { deep: true });
watch(overrideConfig, emitValue, { deep: true });

onMounted(loadSchemaTypes);

/** 递归校验：由父级 DynamicFormRenderer 调用 */
async function validate(
  parentLabel = ""
): Promise<{ valid: boolean; errors: string[] }> {
  const errors: string[] = [];

  if (mode.value === "ref") {
    // ref 模式：不做额外校验（ref 本身的 required 由父级判断）
    return { valid: true, errors: [] };
  }

  if (mode.value === "inline") {
    if (!inlineType.value) {
      errors.push(`"${parentLabel}" 内联定义：请先选择类型`);
      return { valid: false, errors };
    }
    if (inlineRendererRef.value?.validate) {
      const result = await inlineRendererRef.value.validate(parentLabel);
      if (!result.valid) errors.push(...result.errors);
    }
  }

  if (mode.value === "override") {
    if (overrideRendererRef.value?.validate) {
      const result = await overrideRendererRef.value.validate(parentLabel);
      if (!result.valid) errors.push(...result.errors);
    }
  }

  return { valid: errors.length === 0, errors };
}

defineExpose({ validate });
</script>

<style scoped>
.ref-or-inline-field {
  width: 100%;
}

/* 模式切换按钮组 */
.mode-switcher {
  margin-bottom: 10px;
}
.mode-switcher :deep(.el-radio-button__inner) {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 13px;
}

/* 引用模式选择框 */
.ref-select-wrap {
  margin-top: 4px;
}

/* 内联类型选择 */
.inline-type-select {
  margin-bottom: 0;
}

/* ───── 树形分支卡片 ───── */
.tree-branch {
  margin-top: 10px;
  border-left: 3px solid var(--branch-color, var(--el-color-primary));
  border-radius: 0 6px 6px 0;
  background: var(--el-fill-color-extra-light);
  overflow: hidden;
  transition: border-color 0.2s;
}

.tree-branch-header {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 7px 12px;
  background: var(--el-fill-color-light);
  border-bottom: 1px solid var(--el-border-color-extra-light);
  font-size: 13px;
  color: var(--el-text-color-secondary);
}

.tree-branch-icon {
  color: var(--branch-color, var(--el-color-primary));
  font-size: 14px;
  flex-shrink: 0;
}

.tree-branch-title {
  font-weight: 500;
  color: var(--el-text-color-primary);
}

.tree-branch-body {
  padding: 12px 14px 4px;
}
</style>
