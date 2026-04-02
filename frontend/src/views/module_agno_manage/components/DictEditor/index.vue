<!-- 字典编辑器：用于编辑 Record<string, any> 类型的配置参数 -->
<template>
  <div class="dict-editor">
    <!-- 键值对列表 -->
    <div v-if="configItems.length === 0" class="dict-editor__empty">
      <el-text type="info" size="small">暂无参数，点击"添加参数"开始配置</el-text>
    </div>

    <div v-for="(item, index) in configItems" :key="index" class="dict-editor__row">
      <!-- 类型选择 -->
      <el-select v-model="item.valueType" class="dict-editor__type" @change="onTypeChange(item)">
        <el-option value="str" label="str" />
        <el-option value="num" label="num" />
        <el-option value="bool" label="bool" />
        <el-option value="list" label="list" />
        <el-option value="object" label="obj" />
      </el-select>

      <!-- 参数名 -->
      <el-input
        v-model="item.key"
        placeholder="参数名"
        :class="['dict-editor__key', { 'is-duplicate': duplicateKeys.has(item.key) }]"
        @input="emitChange"
      />

      <span class="dict-editor__sep">:</span>

      <!-- 值输入：bool -->
      <el-select
        v-if="item.valueType === 'bool'"
        v-model="item.value"
        class="dict-editor__value"
        @change="emitChange"
      >
        <el-option value="true" label="true" />
        <el-option value="false" label="false" />
      </el-select>

      <!-- 值输入：list / object（textarea） -->
      <el-input
        v-else-if="item.valueType === 'list' || item.valueType === 'object'"
        v-model="item.value"
        type="textarea"
        :rows="2"
        :placeholder="item.valueType === 'list' ? '[1, 2, 3]' : objectPlaceholder"
        class="dict-editor__value"
        @input="emitChange"
      />

      <!-- 值输入：str / num -->
      <el-input
        v-else
        v-model="item.value"
        :type="item.valueType === 'num' ? 'number' : 'text'"
        :placeholder="item.valueType === 'num' ? '0' : '参数值'"
        class="dict-editor__value"
        @input="emitChange"
      />

      <!-- 删除 -->
      <el-button
        type="danger"
        size="small"
        :icon="Delete"
        circle
        @click="removeItem(index)"
      />
    </div>

    <!-- 底部操作栏 -->
    <div class="dict-editor__footer">
      <el-button size="small" :icon="Plus" @click="addItem">添加参数</el-button>
      <!-- 预留：从模板加载（后端接口就绪后启用，父组件传入 loadTemplate 函数） -->
      <!-- <el-button size="small" :icon="Download" :disabled="!loadTemplate" @click="handleLoadTemplate">从模板加载</el-button> -->
      <el-button size="small" @click="openJsonDialog">{ } JSON</el-button>
    </div>

    <!-- JSON 预览/编辑弹窗 -->
    <el-dialog
      v-model="jsonDialogVisible"
      title="JSON 预览 / 编辑"
      width="520px"
      append-to-body
      @open="onJsonDialogOpen"
    >
      <el-input
        v-model="jsonText"
        type="textarea"
        :rows="16"
        class="dict-editor__json-input"
        placeholder="{}"
      />
      <el-alert
        v-if="jsonError"
        :title="jsonError"
        type="error"
        :closable="false"
        class="dict-editor__json-error"
      />
      <template #footer>
        <el-button @click="jsonDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="applyJson">应用</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, nextTick, computed } from "vue";
import { Delete, Plus } from "@element-plus/icons-vue";

// ---- 类型定义 ----

type ConfigValueType = "str" | "num" | "bool" | "list" | "object";

interface ConfigItem {
  key: string;
  valueType: ConfigValueType;
  value: string;
}

// ---- Props / Emits ----

const props = defineProps<{
  modelValue?: Record<string, any>;
  // 预留：从模板加载的异步函数，就绪后由父组件传入
  // loadTemplate?: () => Promise<Record<string, any>>;
}>();

const emit = defineEmits<{
  "update:modelValue": [value: Record<string, any>];
}>();

// ---- 内部状态 ----

const objectPlaceholder = '{"key": "value"}';
const configItems = ref<ConfigItem[]>([]);
let isInternalChange = false;

/** 出现超过一次的 key 集合 */
const duplicateKeys = computed(() => {
  const count: Record<string, number> = {};
  for (const item of configItems.value) {
    if (item.key.trim()) count[item.key] = (count[item.key] ?? 0) + 1;
  }
  return new Set(Object.keys(count).filter((k) => count[k] > 1));
});
const jsonDialogVisible = ref(false);
const jsonText = ref("{}");
const jsonError = ref("");

// ---- 序列化 / 反序列化 ----

/** 将外部对象解析为内部 ConfigItem 列表 */
function parseFromObject(obj: Record<string, any> | undefined | null) {
  if (!obj || typeof obj !== "object" || Array.isArray(obj)) {
    configItems.value = [];
    return;
  }
  configItems.value = Object.entries(obj).map(([key, value]) => {
    let valueType: ConfigValueType = "str";
    let strValue = "";

    if (typeof value === "number") {
      valueType = "num";
      strValue = String(value);
    } else if (typeof value === "boolean") {
      valueType = "bool";
      strValue = String(value);
    } else if (Array.isArray(value)) {
      valueType = "list";
      strValue = JSON.stringify(value, null, 2);
    } else if (typeof value === "object" && value !== null) {
      valueType = "object";
      strValue = JSON.stringify(value, null, 2);
    } else {
      valueType = "str";
      strValue = String(value ?? "");
    }

    return { key, valueType, value: strValue };
  });
}

/** 将内部 ConfigItem 列表序列化为对象 */
function serializeToObject(): Record<string, any> {
  const result: Record<string, any> = {};
  for (const item of configItems.value) {
    if (!item.key.trim()) continue;
    switch (item.valueType) {
      case "num":
        result[item.key] = Number(item.value);
        break;
      case "bool":
        result[item.key] = item.value === "true";
        break;
      case "list":
      case "object":
        try {
          result[item.key] = JSON.parse(item.value);
        } catch {
          result[item.key] = item.value;
        }
        break;
      default:
        result[item.key] = item.value;
    }
  }
  return result;
}

// ---- 键值对操作 ----

function addItem() {
  configItems.value.push({ key: "", valueType: "str", value: "" });
}

function removeItem(index: number) {
  configItems.value.splice(index, 1);
  emitChange();
}

/** 切换类型时重置 value，避免类型不匹配 */
function onTypeChange(item: ConfigItem) {
  if (item.valueType === "bool") {
    item.value = "true";
  } else if (item.valueType === "list") {
    item.value = "[]";
  } else if (item.valueType === "object") {
    item.value = "{}";
  } else {
    item.value = "";
  }
  emitChange();
}

function emitChange() {
  isInternalChange = true;
  emit("update:modelValue", serializeToObject());
  nextTick(() => { isInternalChange = false; });
}

// ---- JSON 弹窗 ----

function openJsonDialog() {
  jsonDialogVisible.value = true;
}

function onJsonDialogOpen() {
  jsonText.value = JSON.stringify(serializeToObject(), null, 2) || "{}";
  jsonError.value = "";
}

function applyJson() {
  try {
    const parsed = JSON.parse(jsonText.value || "{}");
    if (typeof parsed !== "object" || Array.isArray(parsed)) {
      jsonError.value = "顶层必须是一个 JSON 对象 { }";
      return;
    }
    parseFromObject(parsed);
    emit("update:modelValue", parsed);
    jsonError.value = "";
    jsonDialogVisible.value = false;
  } catch (e: any) {
    jsonError.value = `JSON 解析错误：${e.message}`;
  }
}

// ---- 监听外部 modelValue 变化 ----

watch(
  () => props.modelValue,
  (val) => {
    if (isInternalChange) return;
    parseFromObject(val);
  },
  { immediate: true }
);
</script>

<style lang="scss" scoped>
.dict-editor {
  width: 100%;

  &__empty {
    padding: 4px 0 8px;
  }

  &__row {
    display: flex;
    align-items: flex-start;
    gap: 6px;
    margin-bottom: 8px;
  }

  &__type {
    width: 72px;
    flex-shrink: 0;
  }

  &__key {
    width: 130px;
    flex-shrink: 0;

    &.is-duplicate :deep(.el-input__wrapper) {
      box-shadow: 0 0 0 1px var(--el-color-danger) inset;
    }
  }

  &__sep {
    line-height: 32px;
    color: #909399;
    flex-shrink: 0;
  }

  &__value {
    flex: 1;
    min-width: 0;
  }

  &__footer {
    display: flex;
    gap: 8px;
    margin-top: 4px;
  }

  &__json-input {
    :deep(textarea) {
      font-family: "Courier New", Courier, monospace;
      font-size: 13px;
    }
  }

  &__json-error {
    margin-top: 8px;
  }
}
</style>
