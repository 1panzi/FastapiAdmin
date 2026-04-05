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
    <!-- 触底哨兵：被 IntersectionObserver 观察，进入视口时加载下一页 -->
    <div ref="sentinelRef" style="height: 1px" />
    <div v-if="loading" style="text-align: center; padding: 8px 0; color: #909399; font-size: 12px">
      加载中...
    </div>
    <div v-else-if="appending" style="height: 28px" />
    <div v-else-if="noMore && total > 0" style="text-align: center; padding: 8px 0; color: #c0c4cc; font-size: 12px">
      已全部加载
    </div>
  </el-select>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted, onUnmounted, nextTick } from "vue";

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
  /** 挂载时立即预拉取第一页，使首次打开下拉无加载闪烁 */
  preload?: boolean;
}

const props = withDefaults(defineProps<Props>(), {
  placeholder: "请选择",
  clearable: true,
  pageSize: 20,
  preload: false,
});

const emit = defineEmits<{
  "update:modelValue": [value: string | undefined];
  change: [value: string | undefined, raw?: any];
}>();

const proxyValue = computed({
  get: () => props.modelValue,
  set: (val) => emit("update:modelValue", val),
});

const sentinelRef = ref<HTMLElement | null>(null);
const options = ref<OptionItem[]>([]);
const loading = ref(false);    // 首次/搜索加载（会显示 input 转圈）
const appending = ref(false);  // 翻页追加（静默，不影响 input）
const currentPage = ref(1);
const total = ref(0);
const keyword = ref("");
let filterTimer: ReturnType<typeof setTimeout> | null = null;
let observer: IntersectionObserver | null = null;

const noMore = computed(() => options.value.length >= total.value && total.value > 0);

async function fetchPage(reset = false) {
  if (loading.value || appending.value) return;
  if (reset) {
    loading.value = true;
  } else {
    appending.value = true;
  }
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
    appending.value = false;
  }
}

async function loadMore() {
  if (loading.value || appending.value || noMore.value) return;
  await fetchPage(false);
}

function setupObserver() {
  if (observer) {
    observer.disconnect();
    observer = null;
  }
  if (!sentinelRef.value) return;
  // IntersectionObserver 挂载后会立即触发一次初始检测，用 initialized 标志跳过它
  let initialized = false;
  observer = new IntersectionObserver(
    (entries) => {
      if (!initialized) {
        initialized = true;
        return;
      }
      if (entries[0].isIntersecting && !loading.value && !noMore.value) {
        loadMore();
      }
    },
    { threshold: 0.1 }
  );
  observer.observe(sentinelRef.value);
}

function handleFilter(val: string) {
  // el-select 每次打开时会以当前输入值调用 filter-method，keyword 未变时无需重新请求
  if (val === keyword.value) return;
  keyword.value = val;
  if (filterTimer) clearTimeout(filterTimer);
  filterTimer = setTimeout(() => {
    fetchPage(true);
  }, 300);
}

function handleVisibleChange(visible: boolean) {
  if (visible) {
    if (options.value.length === 0) {
      fetchPage(true);
    }
    nextTick(() => setupObserver());
  } else {
    observer?.disconnect();
    observer = null;
  }
}

function handleClear() {
  keyword.value = "";
  fetchPage(true);
  emit("update:modelValue", undefined);
  emit("change", undefined);
}

// 编辑场景：有初始值但 options 为空时，先加载第一页保证回显
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
  if (props.preload || props.modelValue) {
    if (options.value.length === 0) {
      fetchPage(true);
    }
  }
});

onUnmounted(() => {
  observer?.disconnect();
});
</script>
