<template>
  <el-select
    v-model="proxyValue"
    :placeholder="placeholder"
    :clearable="clearable"
    :filterable="true"
    :filter-method="handleFilter"
    :loading="loading"
    style="width: 100%"
    v-bind="$attrs"
    @visible-change="handleVisibleChange"
    @clear="handleClear"
  >
    <el-option
      v-for="item in options"
      :key="item.value"
      :label="item.label"
      :value="item.value"
    >
      <slot name="option" :item="item">{{ item.label }}</slot>
    </el-option>
    <!-- 滚动哨兵：滚动到底部时触发加载 -->
    <div
      v-infinite-scroll="loadMore"
      :infinite-scroll-disabled="scrollDisabled"
      :infinite-scroll-distance="20"
      style="height: 1px"
    />
    <div v-if="loading" style="text-align: center; padding: 8px 0; color: #909399; font-size: 12px">
      加载中...
    </div>
    <div v-else-if="noMore" style="text-align: center; padding: 8px 0; color: #c0c4cc; font-size: 12px">
      已全部加载
    </div>
  </el-select>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted } from "vue";

interface OptionItem {
  value: string;
  label: string;
  raw?: any;
}

interface Props {
  modelValue?: string;
  placeholder?: string;
  clearable?: boolean;
  pageSize?: number;
  /** 拉取数据的函数，返回 { items, total } */
  fetcher: (params: { page_no: number; page_size: number; name?: string }) => Promise<{
    items: OptionItem[];
    total: number;
  }>;
  /** 初始值对应的标签（用于回显，避免首次打开才能显示） */
  initialLabel?: string;
}

const props = withDefaults(defineProps<Props>(), {
  placeholder: "请选择",
  clearable: true,
  pageSize: 20,
});

const emit = defineEmits<{
  "update:modelValue": [value: string | undefined];
  change: [value: string | undefined, raw?: any];
}>();

const proxyValue = computed({
  get: () => props.modelValue,
  set: (val) => emit("update:modelValue", val),
});

const options = ref<OptionItem[]>([]);
const loading = ref(false);
const currentPage = ref(1);
const total = ref(0);
const keyword = ref("");
// 用于去抖的定时器
let filterTimer: ReturnType<typeof setTimeout> | null = null;

const noMore = computed(() => options.value.length >= total.value && total.value > 0);
const scrollDisabled = computed(() => loading.value || noMore.value);

async function fetchPage(reset = false) {
  if (loading.value) return;
  loading.value = true;
  try {
    const page = reset ? 1 : currentPage.value;
    const result = await props.fetcher({
      page_no: page,
      page_size: props.pageSize,
      name: keyword.value || undefined,
    });
    if (reset) {
      options.value = result.items;
      currentPage.value = 2;
    } else {
      options.value.push(...result.items);
      currentPage.value = page + 1;
    }
    total.value = result.total;
  } finally {
    loading.value = false;
  }
}

async function loadMore() {
  if (scrollDisabled.value) return;
  await fetchPage(false);
}

function handleFilter(val: string) {
  keyword.value = val;
  if (filterTimer) clearTimeout(filterTimer);
  filterTimer = setTimeout(() => {
    fetchPage(true);
  }, 300);
}

function handleVisibleChange(visible: boolean) {
  if (visible && options.value.length === 0) {
    fetchPage(true);
  }
}

function handleClear() {
  keyword.value = "";
  fetchPage(true);
  emit("update:modelValue", undefined);
  emit("change", undefined);
}

// 如果有初始值但 options 为空（编辑场景），先加载第一页；若 options 中没有匹配项，
// 用 initialLabel 构造一个临时选项保证回显
watch(
  () => props.modelValue,
  (val) => {
    if (!val) return;
    if (options.value.length === 0) {
      fetchPage(true);
    }
  },
  { immediate: true }
);

onMounted(() => {
  // 有初始值时立即加载，保证回显
  if (props.modelValue && options.value.length === 0) {
    fetchPage(true);
  }
});
</script>
