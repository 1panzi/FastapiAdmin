<template>
  <div class="agent-node">
    <Handle type="target" :position="Position.Left" />
    <div class="agent-node__header">
      <span class="agent-node__icon">🤖</span>
      <span class="agent-node__name">{{ displayName }}</span>
    </div>
    <div v-if="data.member?.role" class="agent-node__body">
      <span class="agent-node__role">{{ data.member.role }}</span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from "vue";
import { Handle, Position } from "@vue-flow/core";
import AgAgentAPI from "@/api/module_agno_manage/agents";

const props = defineProps<{
  data: {
    agentId: string;
    agentName?: string;
    member: any;
  };
}>();

const displayName = ref(props.data.agentName || props.data.agentId);

onMounted(async () => {
  if (props.data.agentName && !props.data.agentName.startsWith("agent-")) return;
  try {
    const res = await AgAgentAPI.detailAgAgent(Number(props.data.agentId));
    const name = res.data?.data?.name;
    if (name) displayName.value = name;
  } catch {
    // 保持 ID 占位
  }
});
</script>

<style lang="scss" scoped>
.agent-node {
  background: #fff;
  border: 2px solid #67c23a;
  border-radius: 8px;
  min-width: 160px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  cursor: pointer;

  &__header {
    display: flex;
    align-items: center;
    gap: 6px;
    padding: 8px 12px;
    background: #f0f9eb;
    border-radius: 6px 6px 0 0;
  }

  &__name {
    font-size: 13px;
    font-weight: 500;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }

  &__body {
    padding: 6px 12px;
  }

  &__role {
    font-size: 11px;
    color: #909399;
  }
}
</style>
