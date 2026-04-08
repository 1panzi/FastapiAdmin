<!-- 动态表单渲染器：根据后端 FieldSchema[] 渲染表单字段 -->
<template>
  <el-row :gutter="16">
    <template v-for="field in visibleFields" :key="field.name">
      <el-col :span="field.span ?? 24">
        <!-- standalone 模式（嵌套在 RefOrInlineField 中）：不接入外层 el-form 校验 -->
        <template v-if="standalone">
          <div class="standalone-form-item">
            <label class="standalone-label">
              <span v-if="field.required" class="required-star">*</span>
              {{ field.label ?? field.name }}
              <el-tooltip v-if="field.tooltip" :content="field.tooltip" placement="top">
                <el-icon class="ml-1 cursor-pointer"><QuestionFilled /></el-icon>
              </el-tooltip>
            </label>
            <div class="standalone-control">
              <!-- str / password -->
              <el-input
                v-if="field.type === 'str' || field.type === 'password'"
                v-model="formData[field.name]"
                :type="field.type === 'password' ? 'password' : 'text'"
                :placeholder="field.placeholder ?? `请输入 ${field.label ?? field.name}`"
                :minlength="field.min_length"
                :maxlength="field.max_length"
                :show-password="field.type === 'password'"
                clearable
              />
              <!-- int / float -->
              <el-input-number
                v-else-if="field.type === 'int' || field.type === 'float'"
                v-model="formData[field.name]"
                :min="field.min"
                :max="field.max"
                :step="field.step ?? (field.type === 'float' ? 0.1 : 1)"
                :precision="field.type === 'float' ? 4 : 0"
                controls-position="right"
                style="width: 100%"
              />
              <!-- bool -->
              <el-switch v-else-if="field.type === 'bool'" v-model="formData[field.name]" />
              <!-- select -->
              <el-select
                v-else-if="field.type === 'select'"
                v-model="formData[field.name]"
                clearable
                style="width: 100%"
                @change="(val: any) => handleSelectChange(field, val)"
              >
                <el-option
                  v-for="opt in field.options ?? []"
                  :key="opt.value"
                  :label="opt.label"
                  :value="opt.value"
                />
              </el-select>
              <!-- ref_or_inline -->
              <RefOrInlineField
                v-else-if="field.type === 'ref_or_inline'"
                :ref="(el: any) => setNestedRef(field.name, el)"
                v-model="formData[field.name]"
                :source-category="field.source ?? ''"
                :overridable-fields="field.overridable_fields ?? []"
                :depth="(depth ?? 0) + 1"
              />
              <!-- ref_or_inline_array -->
              <RefOrInlineArrayField
                v-else-if="field.type === 'ref_or_inline_array'"
                :ref="(el: any) => setNestedRef(field.name, el)"
                v-model="formData[field.name]"
                :source-category="field.source ?? ''"
                :overridable-fields="field.overridable_fields ?? []"
                :depth="(depth ?? 0) + 1"
              />
              <!-- fallback: str -->
              <el-input
                v-else
                v-model="formData[field.name]"
                :placeholder="field.placeholder ?? `请输入 ${field.label ?? field.name}`"
                clearable
              />
            </div>
          </div>
        </template>

        <!-- 正常模式：接入外层 el-form 校验 -->
        <el-form-item
          v-else
          :label="field.label ?? field.name"
          :prop="propPrefix ? `${propPrefix}.${field.name}` : field.name"
          :required="field.required"
        >
          <!-- str / password -->
          <el-input
            v-if="field.type === 'str' || field.type === 'password'"
            v-model="formData[field.name]"
            :type="field.type === 'password' ? 'password' : 'text'"
            :placeholder="field.placeholder ?? `请输入 ${field.label ?? field.name}`"
            :minlength="field.min_length"
            :maxlength="field.max_length"
            :show-password="field.type === 'password'"
            clearable
          />

          <!-- int / float -->
          <el-input-number
            v-else-if="field.type === 'int' || field.type === 'float'"
            v-model="formData[field.name]"
            :min="field.min"
            :max="field.max"
            :step="field.step ?? (field.type === 'float' ? 0.1 : 1)"
            :precision="field.type === 'float' ? 4 : 0"
            controls-position="right"
            style="width: 100%"
          />

          <!-- bool -->
          <el-switch
            v-else-if="field.type === 'bool'"
            v-model="formData[field.name]"
          />

          <!-- select -->
          <el-select
            v-else-if="field.type === 'select'"
            v-model="formData[field.name]"
            clearable
            style="width: 100%"
            @change="(val: any) => handleSelectChange(field, val)"
          >
            <el-option
              v-for="opt in field.options ?? []"
              :key="opt.value"
              :label="opt.label"
              :value="opt.value"
            />
          </el-select>

          <!-- ref_or_inline -->
          <RefOrInlineField
            v-else-if="field.type === 'ref_or_inline'"
            :ref="(el: any) => setNestedRef(field.name, el)"
            v-model="formData[field.name]"
            :source-category="field.source ?? ''"
            :overridable-fields="field.overridable_fields ?? []"
            :depth="depth ?? 0"
          />

          <!-- ref_or_inline_array -->
          <RefOrInlineArrayField
            v-else-if="field.type === 'ref_or_inline_array'"
            :ref="(el: any) => setNestedRef(field.name, el)"
            v-model="formData[field.name]"
            :source-category="field.source ?? ''"
            :overridable-fields="field.overridable_fields ?? []"
            :depth="depth ?? 0"
          />

          <!-- fallback: str -->
          <el-input
            v-else
            v-model="formData[field.name]"
            :placeholder="field.placeholder ?? `请输入 ${field.label ?? field.name}`"
            clearable
          />

          <template v-if="field.tooltip" #label>
            {{ field.label ?? field.name }}
            <el-tooltip :content="field.tooltip" placement="top">
              <el-icon class="ml-1 cursor-pointer"><QuestionFilled /></el-icon>
            </el-tooltip>
          </template>
        </el-form-item>
      </el-col>
    </template>
  </el-row>
</template>

<script setup lang="ts">
import { computed } from "vue";
import { QuestionFilled } from "@element-plus/icons-vue";
import RefOrInlineField from "./RefOrInlineField.vue";
import RefOrInlineArrayField from "./RefOrInlineArrayField.vue";
import type { FieldSchema } from "@/api/module_agno_manage_v2/resources";

interface Props {
  fields: FieldSchema[];
  formData: Record<string, any>;
  /** el-form-item :prop 前缀，如 "config" → prop="config.fieldName" */
  propPrefix?: string;
  /**
   * standalone 模式：嵌套在 RefOrInlineField 内部时使用。
   * 不向外层 el-form 注册校验（避免 prop 路径错误导致外层提交失败）。
   */
  standalone?: boolean;
  /** 当前嵌套深度，用于向 RefOrInlineField 传递颜色层级，默认 0 */
  depth?: number;
}

const props = defineProps<Props>();

/** 过滤隐藏字段 + depends_on 条件显示 */
const visibleFields = computed(() => {
  const sorted = [...props.fields].sort((a, b) => (a.order ?? 0) - (b.order ?? 0));
  return sorted.filter((field) => {
    if (field.hidden) return false;
    if (field.depends_on) {
      for (const [key, expected] of Object.entries(field.depends_on)) {
        if (props.formData[key] !== expected) return false;
      }
    }
    return true;
  });
});

/** select affects：切换选项时隐藏不相关字段（通过 depends_on 机制自动处理），此处做默认值清除 */
function handleSelectChange(field: FieldSchema, val: any) {
  if (!field.affects) return;
  // 保留当前 affects[val] 中的字段，清除其他受控字段的值
  const keepFields = new Set<string>(field.affects[val] ?? []);
  for (const affectedFields of Object.values(field.affects)) {
    for (const f of affectedFields) {
      if (!keepFields.has(f) && f in props.formData) {
        // 用 Vue.set 等价写法——直接修改 reactive 对象内部属性是允许的
        // 但不能整体替换 props.formData（那才是 prop mutation）
        (props.formData as Record<string, any>)[f] = undefined;
      }
    }
  }
}

// ── 嵌套子组件 ref 收集 ──────────────────────────────────────────
/** field.name → RefOrInlineField / RefOrInlineArrayField 实例 */
const nestedRefs: Record<string, any> = {};

function setNestedRef(name: string, el: any) {
  if (el) nestedRefs[name] = el;
  else delete nestedRefs[name];
}

function isValueEmpty(field: FieldSchema, value: any): boolean {
  if (value === null || value === undefined) return true;
  if (
    field.type === "str" ||
    field.type === "password" ||
    field.type === "select"
  )
    return value === "";
  if (field.type === "ref_or_inline_array")
    return Array.isArray(value) && value.length === 0;
  return false;
}

/** 递归校验所有可见必填字段及嵌套子组件 */
async function validate(
  pathLabel = ""
): Promise<{ valid: boolean; errors: string[] }> {
  const errors: string[] = [];
  for (const field of visibleFields.value) {
    const value = props.formData[field.name];
    const label = pathLabel
      ? `${pathLabel} > ${field.label ?? field.name}`
      : (field.label ?? field.name);

    if (field.required && isValueEmpty(field, value)) {
      errors.push(`"${label}" 为必填项`);
      continue; // 必填未填，无需继续深入
    }

    if (
      field.type === "ref_or_inline" ||
      field.type === "ref_or_inline_array"
    ) {
      const nestedRef = nestedRefs[field.name];
      if (nestedRef?.validate) {
        const result = await nestedRef.validate(label);
        if (!result.valid) errors.push(...result.errors);
      }
    }
  }
  return { valid: errors.length === 0, errors };
}

defineExpose({ validate });
</script>

<style scoped>
.standalone-form-item {
  margin-bottom: 18px;
}
.standalone-label {
  display: block;
  font-size: 14px;
  color: var(--el-text-color-regular);
  margin-bottom: 6px;
  line-height: 1.4;
}
.required-star {
  color: var(--el-color-danger);
  margin-right: 4px;
}
.standalone-control {
  width: 100%;
}
</style>
