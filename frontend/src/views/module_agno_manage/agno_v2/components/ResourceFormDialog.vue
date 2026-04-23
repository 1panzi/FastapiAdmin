<!-- 资源创建/编辑弹窗 -->
<template>
  <el-dialog
    v-model="visible"
    :title="title"
    width="760px"
    :close-on-click-modal="false"
    @close="handleClose"
  >
    <el-form ref="formRef" :model="formData" :rules="rules" label-width="100px">
      <!-- 名称 -->
      <el-form-item label="名称" prop="name">
        <el-input v-model="formData.name" placeholder="请输入名称" clearable />
      </el-form-item>

      <!-- 类型（创建时可选，编辑时只读） -->
      <el-form-item label="类型" prop="type">
        <el-select
          v-if="!isEdit"
          v-model="formData.type"
          placeholder="请选择类型"
          clearable
          style="width: 100%"
          :loading="schemaLoading"
          @change="handleTypeChange"
        >
          <el-option
            v-for="t in schemaTypes"
            :key="t.type"
            :label="t.label"
            :value="t.type"
          />
        </el-select>
        <el-tag v-else>{{ formData.type }}</el-tag>
      </el-form-item>

      <!-- 描述 -->
      <el-form-item label="描述" prop="description">
        <el-input v-model="formData.description" type="textarea" :rows="2" placeholder="可选描述" />
      </el-form-item>

      <!-- 状态 -->
      <el-form-item label="状态" prop="status">
        <el-radio-group v-model="formData.status">
          <el-radio value="0">启用</el-radio>
          <el-radio value="1">停用</el-radio>
        </el-radio-group>
      </el-form-item>

      <!-- 动态 config 字段 -->
      <template v-if="schema && formData.type">
        <el-divider content-position="left">{{ schema.label ?? "配置参数" }}</el-divider>
        <DynamicFormRenderer ref="dynamicFormRef" :fields="schema.fields" :form-data="formData.config" prop-prefix="config" />
      </template>
    </el-form>

    <template #footer>
      <el-button @click="handleClose">取消</el-button>
      <el-button type="primary" :loading="submitting" @click="handleSubmit">确定</el-button>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, reactive, watch } from "vue";
import { ElMessage } from "element-plus";
import ResourceAPI from "@/api/module_agno_manage_v2/resources";
import type { SchemaResult, SchemaType, ResourceForm } from "@/api/module_agno_manage_v2/resources";
import DynamicFormRenderer from "./DynamicFormRenderer.vue";

interface Props {
  modelValue: boolean;
  category: string;
  /** 编辑时传入已有数据 */
  editData?: ResourceForm & { id?: number };
}

const props = defineProps<Props>();
const emit = defineEmits<{
  "update:modelValue": [v: boolean];
  success: [];
}>();

const visible = ref(props.modelValue);
const title = ref("新增资源");
const isEdit = ref(false);
const formRef = ref();
const dynamicFormRef = ref<any>(null);
const submitting = ref(false);
const schemaLoading = ref(false);
const schemaTypes = ref<SchemaType[]>([]);
const schema = ref<SchemaResult | null>(null);

const formData = reactive<ResourceForm>({
  name: "",
  category: props.category,
  type: "",
  config: {},
  status: "0",
  description: "",
});

const rules = {
  name: [{ required: true, message: "请输入名称", trigger: "blur" }],
  type: [{ required: true, message: "请选择类型", trigger: "change" }],
};

watch(() => props.modelValue, async (val) => {
  visible.value = val;
  if (val) {
    formData.category = props.category;
    if (props.editData?.id) {
      isEdit.value = true;
      title.value = "编辑资源";
      Object.assign(formData, props.editData);
      formData.config = { ...(props.editData.config ?? {}) };
      // 加载编辑时的 schema
      if (formData.type) {
        await loadSchema(formData.type);
      }
    } else {
      isEdit.value = false;
      title.value = "新增资源";
      resetForm();
    }
    await loadSchemaTypes();
  }
});

watch(visible, (val) => emit("update:modelValue", val));

async function loadSchemaTypes() {
  schemaLoading.value = true;
  try {
    const res = await ResourceAPI.getSchemaTypes(props.category);
    schemaTypes.value = res.data.data.types ?? [];
  } finally {
    schemaLoading.value = false;
  }
}

async function loadSchema(type: string) {
  const res = await ResourceAPI.getSchemaFields(props.category, type);
  schema.value = res.data.data;
}

async function handleTypeChange(type: string) {
  formData.config = {};
  schema.value = null;
  if (type) {
    await loadSchema(type);
    // 填充默认值
    if (schema.value) {
      for (const f of schema.value.fields) {
        if (f.default !== undefined && !(f.name in formData.config)) {
          formData.config[f.name] = f.default;
        }
      }
    }
  }
}

function resetForm() {
  Object.assign(formData, {
    name: "",
    category: props.category,
    type: "",
    config: {},
    status: "0",
    description: "",
  });
  schema.value = null;
  formRef.value?.clearValidate();
}

function handleClose() {
  visible.value = false;
  resetForm();
}

async function handleSubmit() {
  const valid = await formRef.value?.validate().catch(() => false);
  if (!valid) return;

  // 递归校验嵌套 ref_or_inline / ref_or_inline_array 必填项
  if (dynamicFormRef.value?.validate) {
    const { valid: nestedValid, errors } = await dynamicFormRef.value.validate();
    if (!nestedValid) {
      ElMessage.error(errors[0] ?? "嵌套配置校验失败，请检查必填项");
      return;
    }
  }

  submitting.value = true;
  try {
    const body: ResourceForm = {
      name: formData.name,
      category: formData.category,
      type: formData.type,
      config: { ...formData.config },
      status: formData.status,
      description: formData.description,
    };
    if (props.editData?.id) {
      await ResourceAPI.updateResource(props.editData.id, body);
      ElMessage.success("更新成功");
    } else {
      await ResourceAPI.createResource(body);
      ElMessage.success("创建成功");
    }
    visible.value = false;
    emit("success");
    resetForm();
  } finally {
    submitting.value = false;
  }
}
</script>
