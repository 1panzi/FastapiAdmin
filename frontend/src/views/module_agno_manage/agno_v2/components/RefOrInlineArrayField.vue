<!-- ref_or_inline_array：多个 ref_or_inline 项的列表 -->
<template>
  <div class="ref-array-field">
    <div
      v-for="(_, idx) in items"
      :key="idx"
      class="ref-array-item"
    >
      <RefOrInlineField
        :ref="(el: any) => setItemRef(idx, el)"
        :model-value="items[idx]"
        :source-category="sourceCategory"
        :overridable-fields="overridableFields"
        :depth="depth ?? 0"
        @update:model-value="(v) => updateItem(idx, v)"
      />
      <el-button
        type="danger"
        icon="Delete"
        circle
        size="small"
        class="remove-btn"
        @click="removeItem(idx)"
      />
    </div>
    <el-button icon="Plus" @click="addItem">添加</el-button>
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from "vue";
import RefOrInlineField from "./RefOrInlineField.vue";

interface Props {
  modelValue?: any[];
  sourceCategory: string;
  overridableFields: string[];
  /** 当前嵌套深度，透传给子 RefOrInlineField */
  depth?: number;
}

const props = defineProps<Props>();
const emit = defineEmits<{ "update:modelValue": [v: any[]] }>();

const items = ref<any[]>([...(props.modelValue ?? [])]);

watch(() => props.modelValue, (val) => {
  if (JSON.stringify(val) !== JSON.stringify(items.value)) {
    items.value = [...(val ?? [])];
  }
});

function updateItem(idx: number, val: any) {
  items.value[idx] = val;
  emit("update:modelValue", [...items.value]);
}

function addItem() {
  items.value.push(undefined);
  emit("update:modelValue", [...items.value]);
}

function removeItem(idx: number) {
  items.value.splice(idx, 1);
  // 同步清理 ref
  delete itemRefs[idx];
  emit("update:modelValue", [...items.value]);
}

// ── 子项 ref 收集 ────────────────────────────────────────────────
const itemRefs: Record<number, any> = {};

function setItemRef(idx: number, el: any) {
  if (el) itemRefs[idx] = el;
  else delete itemRefs[idx];
}

/** 递归校验所有子项 */
async function validate(
  parentLabel = ""
): Promise<{ valid: boolean; errors: string[] }> {
  const errors: string[] = [];
  for (let i = 0; i < items.value.length; i++) {
    const itemRef = itemRefs[i];
    if (itemRef?.validate) {
      const label = parentLabel ? `${parentLabel}[第${i + 1}项]` : `第${i + 1}项`;
      const result = await itemRef.validate(label);
      if (!result.valid) errors.push(...result.errors);
    }
  }
  return { valid: errors.length === 0, errors };
}

defineExpose({ validate });
</script>

<style scoped>
.ref-array-field {
  width: 100%;
}
.ref-array-item {
  display: flex;
  align-items: flex-start;
  gap: 8px;
  margin-bottom: 8px;
}
.ref-array-item > :first-child {
  flex: 1;
}
.remove-btn {
  flex-shrink: 0;
  margin-top: 4px;
}
</style>
