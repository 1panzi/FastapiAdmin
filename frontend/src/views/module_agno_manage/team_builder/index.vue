<template>
  <div class="team-builder">
    <!-- 工具栏 -->
    <div class="team-builder__toolbar">
      <div class="toolbar-left">
        <span class="toolbar-title">Team 可视化构建器</span>
        <LazySelect
          v-model="rootTeamId"
          :fetcher="teamFetcher"
          placeholder="选择根 Team"
          style="width: 220px"
          @update:model-value="handleRootTeamChange"
        />
      </div>
      <div class="toolbar-right">
        <el-button icon="Plus" @click="handleCreateTeam">新建 Team</el-button>
        <el-button icon="User" @click="handleAddAgentMember">添加 Agent 成员</el-button>
        <el-button type="primary" icon="Check" :loading="saving" @click="handleSave">保存</el-button>
        <el-button icon="ArrowLeft" @click="handleBack">返回列表</el-button>
      </div>
    </div>

    <!-- 主内容区 -->
    <div class="team-builder__main">
      <!-- 画布区 -->
      <div class="team-builder__canvas" :style="{ width: panelVisible ? 'calc(100% - 400px)' : '100%' }">
        <div v-if="!rootTeamId" class="canvas-empty">
          <el-empty description="请在上方选择一个根 Team 开始可视化" />
        </div>
        <VueFlow
          v-else
          v-model:nodes="nodes"
          v-model:edges="edges"
          :node-types="nodeTypes"
          fit-view-on-init
          @node-click="handleNodeClick"
          @connect="handleConnect"
          @edges-change="handleEdgesChange"
        >
          <Background />
          <Controls />
          <MiniMap />
        </VueFlow>
      </div>

      <!-- 右侧配置面板 -->
      <div v-if="panelVisible" class="team-builder__panel">
        <div class="panel-header">
          <span>{{ selectedNode?.type === 'teamNode' ? '📋 Team 配置' : '🤖 Agent 成员' }}</span>
          <el-button icon="Close" circle size="small" @click="panelVisible = false" />
        </div>
        <div class="panel-body">
          <!-- TeamNode 面板 -->
          <template v-if="selectedNode?.type === 'teamNode'">
            <el-tabs v-model="panelActiveTab">
              <el-tab-pane label="Team 配置" name="config">
                <TeamFormFields
                  v-if="selectedTeamForm"
                  ref="panelFormRef"
                  :form-data="selectedTeamForm"
                />
              </el-tab-pane>
              <el-tab-pane label="成员列表" name="members">
                <div
                  v-for="m in selectedNodeMembers"
                  :key="String(m.id || m.member_id)"
                  class="member-item"
                >
                  <span class="member-icon">{{ m.member_type === 'agent' ? '🤖' : '🏢' }}</span>
                  <span class="member-name">{{ getMemberDisplayName(m) }}</span>
                  <div class="member-actions">
                    <el-input-number
                      v-model="m.member_order"
                      :min="1"
                      :precision="0"
                      size="small"
                      style="width: 80px"
                      @change="markMemberChanged(m)"
                    />
                    <el-button
                      type="danger"
                      size="small"
                      icon="Delete"
                      circle
                      @click="handleRemoveMember(m)"
                    />
                  </div>
                </div>
                <div v-if="selectedNodeMembers.length === 0" style="color:#909399;font-size:13px;padding:8px 0;">
                  暂无成员，可在画布中连线添加
                </div>
              </el-tab-pane>
            </el-tabs>
            <div style="margin-top: 12px; text-align: right;">
              <el-button type="primary" size="small" @click="handlePanelSaveTeamConfig">应用配置</el-button>
            </div>
          </template>

          <!-- AgentNode 面板 -->
          <template v-else-if="selectedNode?.type === 'agentNode'">
            <el-form label-width="90px" label-suffix=":">
              <el-form-item label="角色描述">
                <el-input v-model="selectedNode.data.member.role" type="textarea" :rows="2" />
              </el-form-item>
              <el-form-item label="排序">
                <el-input-number
                  v-model="selectedNode.data.member.member_order"
                  :min="1"
                  :precision="0"
                  style="width:100%"
                />
              </el-form-item>
              <el-form-item label="状态">
                <el-radio-group v-model="selectedNode.data.member.status">
                  <el-radio value="0">启用</el-radio>
                  <el-radio value="1">停用</el-radio>
                </el-radio-group>
              </el-form-item>
            </el-form>
            <div style="margin-top: 12px; text-align: right;">
              <el-button type="primary" size="small" @click="handlePanelSaveMemberConfig">应用配置</el-button>
            </div>
          </template>
        </div>
      </div>
    </div>

    <!-- 新建 Team 弹窗 -->
    <el-dialog v-model="createTeamDialog.visible" title="新建 Team" width="400px">
      <el-form :model="createTeamDialog.form" label-width="80px">
        <el-form-item label="名称" required>
          <el-input v-model="createTeamDialog.form.name" placeholder="请输入 Team 名称" />
        </el-form-item>
        <el-form-item label="协作模式">
          <el-select v-model="createTeamDialog.form.mode" style="width:100%">
            <el-option value="route" label="route（路由）" />
            <el-option value="coordinate" label="coordinate（协调）" />
            <el-option value="collaborate" label="collaborate（协作）" />
            <el-option value="tasks" label="tasks（任务）" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="createTeamDialog.visible = false">取消</el-button>
        <el-button type="primary" @click="handleConfirmCreateTeam">确定</el-button>
      </template>
    </el-dialog>

    <!-- 添加 Agent 成员弹窗 -->
    <el-dialog v-model="addAgentDialog.visible" title="选择 Agent 成员" width="400px">
      <el-form label-width="80px">
        <el-form-item label="Agent" required>
          <LazySelect
            v-model="addAgentDialog.selectedAgentId"
            :fetcher="agentFetcher"
            placeholder="请选择 Agent"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="addAgentDialog.visible = false">取消</el-button>
        <el-button type="primary" @click="handleConfirmAddAgent">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, markRaw } from "vue";
import { useRoute, useRouter } from "vue-router";
import { ElMessage } from "element-plus";
import { VueFlow, useVueFlow, type Node, type Edge, type NodeMouseEvent } from "@vue-flow/core";
import { Background } from "@vue-flow/background";
import { Controls } from "@vue-flow/controls";
import { MiniMap } from "@vue-flow/minimap";
import "@vue-flow/core/dist/style.css";
import "@vue-flow/core/dist/theme-default.css";
import "@vue-flow/controls/dist/style.css";
import "@vue-flow/minimap/dist/style.css";

import LazySelect from "@/views/module_agno_manage/components/LazySelect/index.vue";
import TeamFormFields from "../teams/components/TeamFormFields.vue";
import TeamNode from "./nodes/TeamNode.vue";
import AgentNode from "./nodes/AgentNode.vue";

import AgTeamAPI from "@/api/module_agno_manage/teams";
import AgTeamMemberAPI from "@/api/module_agno_manage/team_members";
import AgAgentAPI from "@/api/module_agno_manage/agents";
import type { AgTeamTable, AgTeamForm } from "@/api/module_agno_manage/teams";
import type { AgTeamMemberTable } from "@/api/module_agno_manage/team_members";

defineOptions({ name: "AgTeamBuilder", inheritAttrs: false });

const route = useRoute();
const router = useRouter();

// 自定义节点类型
const nodeTypes = {
  teamNode: markRaw(TeamNode),
  agentNode: markRaw(AgentNode),
} as any;

// Vue Flow
const { fitView, addNodes, addEdges } = useVueFlow();
const nodes = ref<Node[]>([]);
const edges = ref<Edge[]>([]);

// 根 Team
const rootTeamId = ref<string | undefined>(
  route.query.root_id ? String(route.query.root_id) : undefined
);

// 右侧面板
const panelVisible = ref(false);
const selectedNode = ref<{ id: string; type: string; data: any } | null>(null);
const panelActiveTab = ref("config");
const panelFormRef = ref();
const selectedTeamForm = ref<AgTeamForm | null>(null);
const selectedNodeMembers = ref<AgTeamMemberTable[]>([]);

// 保存状态
const saving = ref(false);

// 新建 Team 弹窗
const createTeamDialog = reactive({
  visible: false,
  form: { name: "", mode: "route" as string },
});

// 添加 Agent 弹窗
const addAgentDialog = reactive({
  visible: false,
  selectedAgentId: undefined as string | undefined,
});

// 变更队列
interface PendingChange {
  type: "createTeam" | "updateTeam" | "addMember" | "removeMember";
  payload: any;
  tmpId?: string;
}
const pendingChanges = ref<PendingChange[]>([]);

let tmpCounter = 0;
function genTmpId(): string {
  return `tmp_${Date.now()}_${tmpCounter++}`;
}

// ─── Fetchers ───────────────────────────────────────────────────────────────

const teamFetcher = async (params: { page_no: number; page_size: number; name?: string }) => {
  const res = await AgTeamAPI.listAgTeam({ ...params });
  return {
    items: (res.data?.data?.items || []).map((item: any) => ({
      value: String(item.id),
      label: item.name || String(item.id),
    })),
    total: res.data?.data?.total || 0,
  };
};

const agentFetcher = async (params: { page_no: number; page_size: number; name?: string }) => {
  const res = await AgAgentAPI.listAgAgent({ ...params });
  return {
    items: (res.data?.data?.items || []).map((item: any) => ({
      value: String(item.id),
      label: item.name || String(item.id),
    })),
    total: res.data?.data?.total || 0,
  };
};

// ─── 数据加载 ────────────────────────────────────────────────────────────────

async function fetchAllMembers(
  teamIds: string[],
  visited: Set<string>,
  rootTeam: AgTeamTable
): Promise<{ membersMap: Map<string, AgTeamMemberTable[]>; teamDataMap: Map<string, AgTeamTable> }> {
  const membersMap = new Map<string, AgTeamMemberTable[]>();
  const teamDataMap = new Map<string, AgTeamTable>();
  teamDataMap.set(String(rootTeam.id), rootTeam);

  const queue = [...teamIds];

  while (queue.length > 0) {
    const id = queue.shift()!;
    if (visited.has(id)) continue;
    visited.add(id);

    try {
      const res = await AgTeamMemberAPI.listAgTeamMember({
        team_id: id,
        page_no: 1,
        page_size: 20,
      });
      const members: AgTeamMemberTable[] = res.data?.data?.items || [];
      membersMap.set(id, members);

      for (const m of members) {
        if (m.member_type === "team" && m.member_id) {
          const childId = String(m.member_id);
          if (!visited.has(childId)) {
            queue.push(childId);
            AgTeamAPI.detailAgTeam(Number(childId))
              .then((r) => { if (r.data?.data) teamDataMap.set(childId, r.data.data); })
              .catch(() => {});
          }
        }
      }
    } catch {
      membersMap.set(id, []);
    }
  }
  return { membersMap, teamDataMap };
}

function buildGraph(
  rootTeam: AgTeamTable,
  membersMap: Map<string, AgTeamMemberTable[]>,
  teamDataMap: Map<string, AgTeamTable>
): { nodes: Node[]; edges: Edge[] } {
  const resultNodes: Node[] = [];
  const resultEdges: Edge[] = [];
  const createdNodeIds = new Set<string>();

  const X_GAP = 280;
  const Y_GAP = 160;

  function addTeamNode(team: AgTeamTable, depth: number, col: number) {
    const nodeId = `team-${team.id}`;
    if (createdNodeIds.has(nodeId)) return;
    createdNodeIds.add(nodeId);

    const members = membersMap.get(String(team.id)) || [];
    resultNodes.push({
      id: nodeId,
      type: "teamNode",
      position: { x: col * X_GAP, y: depth * Y_GAP },
      data: { team, members },
    });

    let childCol = col;
    for (const member of members) {
      const memberId = String(member.member_id);
      if (member.member_type === "agent") {
        const agentNodeId = `agent-${memberId}-in-${team.id}`;
        if (!createdNodeIds.has(agentNodeId)) {
          createdNodeIds.add(agentNodeId);
          resultNodes.push({
            id: agentNodeId,
            type: "agentNode",
            position: { x: childCol * X_GAP, y: (depth + 1) * Y_GAP },
            data: { member, agentId: memberId },
          });
          childCol++;
        }
        resultEdges.push({ id: `e-${nodeId}-${agentNodeId}`, source: nodeId, target: agentNodeId });
      } else if (member.member_type === "team") {
        const subTeamData = teamDataMap.get(memberId) || { id: Number(memberId), name: `Team#${memberId}` } as AgTeamTable;
        addTeamNode(subTeamData, depth + 1, childCol);
        childCol++;
        resultEdges.push({
          id: `e-${nodeId}-team-${memberId}`,
          source: nodeId,
          target: `team-${memberId}`,
          style: { stroke: "#409eff" },
        });
      }
    }
  }

  addTeamNode(rootTeam, 0, 0);
  return { nodes: resultNodes, edges: resultEdges };
}

async function loadGraph(teamId: string) {
  const res = await AgTeamAPI.detailAgTeam(Number(teamId));
  const rootTeam = res.data?.data;
  if (!rootTeam) {
    ElMessage.error("Team 不存在");
    return;
  }

  const visited = new Set<string>();
  const { membersMap, teamDataMap } = await fetchAllMembers([teamId], visited, rootTeam);
  const { nodes: newNodes, edges: newEdges } = buildGraph(rootTeam, membersMap, teamDataMap);
  nodes.value = newNodes;
  edges.value = newEdges;
  pendingChanges.value = [];

  setTimeout(() => fitView({ padding: 0.2 }), 100);
}

// ─── 工具栏操作 ──────────────────────────────────────────────────────────────

function handleRootTeamChange(id: string | undefined) {
  if (!id) return;
  router.replace({ query: { root_id: id } });
  loadGraph(id);
}

function handleBack() {
  router.push("/agno/teams");
}

function handleCreateTeam() {
  createTeamDialog.form = { name: "", mode: "route" };
  createTeamDialog.visible = true;
}

function handleConfirmCreateTeam() {
  if (!createTeamDialog.form.name) {
    ElMessage.warning("请输入 Team 名称");
    return;
  }
  const tmpId = genTmpId();
  addNodes([{
    id: tmpId,
    type: "teamNode",
    position: { x: 300, y: 300 },
    data: {
      team: { id: null, name: createTeamDialog.form.name, mode: createTeamDialog.form.mode },
      members: [],
    },
  }]);
  pendingChanges.value.push({
    type: "createTeam",
    tmpId,
    payload: { name: createTeamDialog.form.name, mode: createTeamDialog.form.mode, status: "0" },
  });
  createTeamDialog.visible = false;
  ElMessage.success("Team 节点已添加到画布，保存后生效");
}

function handleAddAgentMember() {
  if (!selectedNode.value || selectedNode.value.type !== "teamNode") {
    ElMessage.warning("请先在画布中点击一个 Team 节点，再添加 Agent 成员");
    return;
  }
  addAgentDialog.selectedAgentId = undefined;
  addAgentDialog.visible = true;
}

function handleConfirmAddAgent() {
  if (!addAgentDialog.selectedAgentId) {
    ElMessage.warning("请选择 Agent");
    return;
  }
  const teamNode = selectedNode.value;
  if (!teamNode || teamNode.type !== "teamNode") return;

  const agentId = addAgentDialog.selectedAgentId;
  const agentNodeId = `agent-${agentId}-in-${teamNode.data.team?.id || teamNode.id}-${Date.now()}`;
  const teamPos = nodes.value.find((n) => n.id === teamNode.id)?.position || { x: 0, y: 0 };

  addNodes([{
    id: agentNodeId,
    type: "agentNode",
    position: { x: teamPos.x, y: teamPos.y + 180 },
    data: { agentId, member: { member_type: "agent", member_id: agentId, member_order: 99, status: "0" } },
  }]);
  addEdges([{ id: `e-${teamNode.id}-${agentNodeId}`, source: teamNode.id, target: agentNodeId }]);

  const teamId = teamNode.data.team?.id ? String(teamNode.data.team.id) : teamNode.id;
  pendingChanges.value.push({
    type: "addMember",
    payload: { team_id: teamId, member_type: "agent", member_id: agentId, member_order: 99, status: "0" },
  });

  addAgentDialog.visible = false;
  ElMessage.success("Agent 成员已添加，保存后生效");
}

// ─── 右侧面板 ────────────────────────────────────────────────────────────────

function handleNodeClick(event: NodeMouseEvent) {
  const node = event.node;
  selectedNode.value = { id: node.id, type: node.type!, data: node.data };
  panelVisible.value = true;
  panelActiveTab.value = "config";

  if (node.type === "teamNode") {
    selectedTeamForm.value = { ...node.data.team } as AgTeamForm;
    selectedNodeMembers.value = [...(node.data.members || [])];
  }
}

function getMemberDisplayName(member: AgTeamMemberTable): string {
  const id = String(member.member_id);
  if (member.member_type === "agent") {
    const agentNode = nodes.value.find((n) => n.type === "agentNode" && n.data.agentId === id);
    return agentNode?.data.agentName || `Agent#${id}`;
  }
  const teamNode = nodes.value.find((n) => n.id === `team-${id}`);
  return teamNode?.data.team?.name || `Team#${id}`;
}

function markMemberChanged(member: AgTeamMemberTable) {
  // 加入更新成员配置的变更
  pendingChanges.value.push({
    type: "updateTeam",
    payload: { id: selectedNode.value?.data.team?.id, member },
  });
}

function handleRemoveMember(member: AgTeamMemberTable) {
  selectedNodeMembers.value = selectedNodeMembers.value.filter(
    (m) => m.id !== member.id
  );
  pendingChanges.value.push({
    type: "removeMember",
    payload: {
      team_id: String(selectedNode.value?.data.team?.id),
      member_id: String(member.member_id),
      member_type: member.member_type,
    },
  });
  ElMessage.success("已标记删除，保存后生效");
}

function handlePanelSaveTeamConfig() {
  if (!selectedTeamForm.value || !selectedNode.value) return;
  const teamId = selectedNode.value.data.team?.id;
  if (teamId) {
    pendingChanges.value.push({
      type: "updateTeam",
      payload: { ...selectedTeamForm.value, id: teamId },
    });
  }
  // 更新节点 data（画布即时反馈）
  const node = nodes.value.find((n) => n.id === selectedNode.value?.id);
  if (node) {
    node.data = { ...node.data, team: { ...selectedTeamForm.value } };
  }
  ElMessage.success("配置已暂存，点击工具栏「保存」提交");
}

function handlePanelSaveMemberConfig() {
  ElMessage.success("成员配置已暂存，点击工具栏「保存」提交");
}

// ─── 连线与断线 ──────────────────────────────────────────────────────────────

function wouldCreateCycle(sourceId: string, targetId: string): boolean {
  // BFS 可达性检测：从 targetId 出发，若能到达 sourceId，则形成循环
  const visited = new Set<string>();
  const queue = [targetId];
  while (queue.length > 0) {
    const curr = queue.shift()!;
    if (curr === sourceId) return true;
    if (visited.has(curr)) continue;
    visited.add(curr);
    edges.value.filter((e) => e.source === curr).forEach((e) => queue.push(e.target));
  }
  return false;
}

function handleConnect(params: { source: string; target: string }) {
  const { source, target } = params;
  const sourceNode = nodes.value.find((n) => n.id === source);
  const targetNode = nodes.value.find((n) => n.id === target);

  if (!sourceNode || sourceNode.type !== "teamNode") {
    ElMessage.warning("只能从 Team 节点连出");
    return;
  }
  if (targetNode?.type === "teamNode" && wouldCreateCycle(source, target)) {
    ElMessage.error("不能创建循环引用：该连线会形成嵌套环");
    return;
  }

  const edgeId = `e-${source}-${target}-${Date.now()}`;
  addEdges([{ id: edgeId, source, target }]);

  const teamId = source.startsWith("tmp_") ? source : source.replace("team-", "");
  const memberId = targetNode?.type === "teamNode"
    ? target.replace("team-", "")
    : target.split("-in-")[0].replace("agent-", "");
  const memberType = targetNode?.type === "teamNode" ? "team" : "agent";

  pendingChanges.value.push({
    type: "addMember",
    payload: { team_id: teamId, member_type: memberType, member_id: memberId, member_order: 99, status: "0" },
  });
}

function handleEdgesChange(changes: any[]) {
  const removes = changes.filter((c) => c.type === "remove");
  for (const change of removes) {
    const edge = edges.value.find((e) => e.id === change.id);
    if (!edge) continue;
    const teamId = edge.source.startsWith("tmp_") ? edge.source : edge.source.replace("team-", "");
    const isTeamTarget = edge.target.startsWith("team-");
    const memberId = isTeamTarget
      ? edge.target.replace("team-", "")
      : edge.target.split("-in-")[0].replace("agent-", "");
    const memberType = isTeamTarget ? "team" : "agent";
    pendingChanges.value.push({
      type: "removeMember",
      payload: { team_id: teamId, member_id: memberId, member_type: memberType },
    });
  }
}

// ─── 保存 ────────────────────────────────────────────────────────────────────

async function handleSave() {
  if (pendingChanges.value.length === 0) {
    ElMessage.info("没有待保存的变更");
    return;
  }

  saving.value = true;
  try {
    const tmpToRealId = new Map<string, string>();

    // Step 1: 创建新 Team
    for (const change of pendingChanges.value.filter((c) => c.type === "createTeam")) {
      const res = await AgTeamAPI.createAgTeam(change.payload);
      const realId = String(res.data?.data?.id || res.data?.data);
      if (change.tmpId) tmpToRealId.set(change.tmpId, realId);
    }

    // Step 2: 更新 Team 配置
    const updateChanges = pendingChanges.value.filter(
      (c) => c.type === "updateTeam" && c.payload?.id
    );
    await Promise.all(
      updateChanges.map((c) => AgTeamAPI.updateAgTeam(Number(c.payload.id), c.payload))
    );

    // Step 3: 删除成员关系
    for (const change of pendingChanges.value.filter((c) => c.type === "removeMember")) {
      const res = await AgTeamMemberAPI.listAgTeamMember({
        team_id: change.payload.team_id,
        member_id: change.payload.member_id,
        member_type: change.payload.member_type,
        page_no: 1,
        page_size: 10,
      });
      const records: any[] = res.data?.data?.items || [];
      if (records.length > 0) {
        await AgTeamMemberAPI.deleteAgTeamMember(records.map((r) => r.id));
      }
    }

    // Step 4: 新建成员关系（替换临时 ID）
    for (const change of pendingChanges.value.filter((c) => c.type === "addMember")) {
      const payload = { ...change.payload };
      if (tmpToRealId.has(payload.team_id)) payload.team_id = tmpToRealId.get(payload.team_id)!;
      if (tmpToRealId.has(payload.member_id)) payload.member_id = tmpToRealId.get(payload.member_id)!;
      await AgTeamMemberAPI.createAgTeamMember(payload);
    }

    pendingChanges.value = [];
    ElMessage.success("保存成功");
    if (rootTeamId.value) await loadGraph(rootTeamId.value);
  } catch (e: any) {
    ElMessage.error(`保存失败: ${e?.message || "未知错误"}`);
  } finally {
    saving.value = false;
  }
}

// ─── 生命周期 ─────────────────────────────────────────────────────────────────

onMounted(() => {
  if (rootTeamId.value) loadGraph(rootTeamId.value);
});
</script>

<style lang="scss" scoped>
.team-builder {
  display: flex;
  flex-direction: column;
  height: calc(100vh - 84px);
  background: #fff;

  &__toolbar {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 8px 16px;
    border-bottom: 1px solid #e4e7ed;
    background: #fff;
    flex-shrink: 0;

    .toolbar-left {
      display: flex;
      align-items: center;
      gap: 12px;
    }

    .toolbar-title {
      font-size: 15px;
      font-weight: 600;
      color: #303133;
    }

    .toolbar-right {
      display: flex;
      gap: 8px;
    }
  }

  &__main {
    display: flex;
    flex: 1;
    overflow: hidden;
  }

  &__canvas {
    flex: 1;
    position: relative;
    transition: width 0.2s;
    overflow: hidden;

    .canvas-empty {
      display: flex;
      align-items: center;
      justify-content: center;
      height: 100%;
    }
  }

  &__panel {
    width: 400px;
    flex-shrink: 0;
    border-left: 1px solid #e4e7ed;
    display: flex;
    flex-direction: column;
    overflow: hidden;

    .panel-header {
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 12px 16px;
      border-bottom: 1px solid #e4e7ed;
      font-weight: 600;
    }

    .panel-body {
      flex: 1;
      overflow-y: auto;
      padding: 16px;
    }
  }
}

.member-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 6px 0;
  border-bottom: 1px solid #f0f0f0;

  &:last-child {
    border-bottom: none;
  }

  .member-icon {
    font-size: 16px;
  }

  .member-name {
    flex: 1;
    font-size: 13px;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }

  .member-actions {
    display: flex;
    align-items: center;
    gap: 4px;
  }
}
</style>
