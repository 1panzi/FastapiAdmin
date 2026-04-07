<template>
  <div class="team-node" :class="`mode-${data.team?.mode || 'default'}`">
    <Handle type="target" :position="Position.Left" />
    <div class="team-node__header">
      <span class="team-node__icon">🏢</span>
      <span class="team-node__name">{{ data.team?.name || 'Team' }}</span>
      <el-tag size="small" :type="modeTagType" class="team-node__mode">
        {{ data.team?.mode || '-' }}
      </el-tag>
    </div>
    <div class="team-node__body">
      <div class="team-node__meta">成员: {{ data.members?.length || 0 }} 个</div>
    </div>
    <Handle type="source" :position="Position.Bottom" />
  </div>
</template>

<script setup lang="ts">
import { computed } from "vue";
import { Handle, Position } from "@vue-flow/core";

const props = defineProps<{
  data: {
    team: any;
    members: any[];
  };
}>();

const modeTagType = computed(() => {
  const map: Record<string, string> = {
    route: "",
    coordinate: "warning",
    collaborate: "success",
    tasks: "info",
  };
  return (map[props.data.team?.mode] ?? "") as any;
});
</script>

<style lang="scss" scoped>
.team-node {
  background: #fff;
  border: 2px solid #409eff;
  border-radius: 8px;
  min-width: 200px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  cursor: pointer;

  &__header {
    display: flex;
    align-items: center;
    gap: 6px;
    padding: 8px 12px;
    background: #ecf5ff;
    border-radius: 6px 6px 0 0;
  }

  &__name {
    font-weight: 600;
    font-size: 13px;
    flex: 1;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }

  &__body {
    padding: 8px 12px;
  }

  &__meta {
    font-size: 12px;
    color: #909399;
  }

  &.mode-coordinate {
    border-color: #e6a23c;
    .team-node__header { background: #fdf6ec; }
  }

  &.mode-collaborate {
    border-color: #67c23a;
    .team-node__header { background: #f0f9eb; }
  }

  &.mode-tasks {
    border-color: #909399;
    .team-node__header { background: #f4f4f5; }
  }
}
</style>
