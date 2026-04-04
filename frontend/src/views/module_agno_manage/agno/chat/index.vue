<template>
  <div class="chat-layout">
    <!-- 左侧：类型 + 组件选择 + 会话列表 -->
    <div class="chat-sidebar">
      <div class="sidebar-header">
        <!-- 类型切换 -->
        <el-segmented
          v-model="sessionType"
          :options="typeOptions"
          size="small"
          class="type-segmented"
          @change="onTypeChange"
        />
        <!-- 组件选择 -->
        <el-select
          v-model="selectedComponentId"
          :placeholder="`选择 ${typeLabel}`"
          filterable
          class="component-select"
          @change="(v: any) => onComponentChange(v)"
        >
          <el-option
            v-for="item in componentList"
            :key="item.id!"
            :label="item.name"
            :value="item.id!"
          />
        </el-select>
        <el-button
          type="primary"
          :icon="Plus"
          :disabled="!selectedComponentId"
          @click="createSession"
        >
          新建会话
        </el-button>
      </div>

      <div class="session-list" v-loading="loadingSessions">
        <div
          v-for="session in sessions"
          :key="session.id"
          class="session-item"
          :class="{ active: currentSessionId === session.id }"
          @click="switchSession(session.id)"
        >
          <el-icon class="session-icon"><ChatDotRound /></el-icon>
          <div class="session-info">
            <template v-if="editingSessionId === session.id">
              <el-input
                v-model="editingName"
                size="small"
                autofocus
                @blur="confirmRename(session.id)"
                @keydown.enter.prevent="confirmRename(session.id)"
                @keydown.esc.prevent="cancelRename"
                @click.stop
              />
            </template>
            <template v-else>
              <div class="session-name" @dblclick.stop="startRename(session)">{{ session.name }}</div>
              <div class="session-meta">{{ session.componentName }}</div>
            </template>
          </div>
          <div class="session-actions">
            <el-tooltip content="重命名" placement="top">
              <el-button class="action-btn" :icon="Edit" size="small" text @click.stop="startRename(session)" />
            </el-tooltip>
            <el-tooltip content="删除" placement="top">
              <el-button class="action-btn" :icon="Delete" size="small" text type="danger" @click.stop="deleteSession(session.id)" />
            </el-tooltip>
          </div>
        </div>
        <el-empty v-if="!loadingSessions && sessions.length === 0" description="暂无会话" :image-size="60" />
      </div>
    </div>

    <!-- 右侧：聊天区域 -->
    <div class="chat-main">
      <template v-if="currentSession">
        <div class="chat-toolbar">
          <span class="chat-title">
            <el-tag size="small" :type="typeTagType" style="margin-right:6px">{{ typeLabel }}</el-tag>
            {{ currentSession.componentName }} · {{ currentSession.name }}
          </span>
          <div class="toolbar-options">
            <el-tooltip content="流式输出">
              <div class="option-item">
                <span class="option-label">流式</span>
                <el-switch v-model="options.stream" size="small" />
              </div>
            </el-tooltip>
            <el-divider direction="vertical" />
            <el-tooltip content="清空消息（仅本地）">
              <el-button :icon="Delete" size="small" text @click="clearMessages" />
            </el-tooltip>
            <el-tooltip content="重新加载历史">
              <el-button :icon="Refresh" size="small" text :loading="loadingMessages" @click="reloadMessages" />
            </el-tooltip>
          </div>
        </div>

        <div ref="messageListRef" class="message-list" v-loading="loadingMessages">
          <div
            v-for="msg in currentSession.messages"
            :key="msg.id"
            class="message-row"
            :class="msg.role"
          >
            <el-avatar
              :size="32"
              :icon="msg.role === 'user' ? UserFilled : Service"
              :class="['msg-avatar', msg.role]"
            />
            <div class="message-bubble">
              <!-- 进度面板（仅 assistant 且有进度项时显示） -->
              <div v-if="msg.role === 'assistant' && msg.progress?.length" class="run-progress">
                <div class="run-progress-header" @click="toggleProgress(msg.id)">
                  <el-icon class="progress-icon" :class="{ spinning: msg.streaming }"><Loading v-if="msg.streaming" /><CircleCheck v-else /></el-icon>
                  <span class="progress-title">{{ msg.streaming ? '运行中...' : `完成 · ${msg.progress.length} 步` }}</span>
                  <el-icon class="progress-chevron" :class="{ expanded: expandedProgress.has(msg.id) }"><ArrowRight /></el-icon>
                </div>
                <transition name="progress-collapse">
                  <div v-if="expandedProgress.has(msg.id)" class="run-progress-body">
                    <div v-for="(item, idx) in msg.progress" :key="idx" class="progress-item" :class="item.status">
                      <el-icon class="item-icon">
                        <Loading v-if="item.status === 'running'" class="spinning" />
                        <CircleCheck v-else-if="item.status === 'done'" />
                        <CircleClose v-else />
                      </el-icon>
                      <div class="item-body">
                        <span class="item-label">{{ item.label }}</span>
                        <span v-if="item.tokens" class="item-meta">{{ item.tokens }} tokens</span>
                        <span v-if="item.duration" class="item-meta">{{ item.duration.toFixed(2) }}s</span>
                        <div v-if="item.detail" class="item-detail">{{ item.detail }}</div>
                      </div>
                    </div>
                  </div>
                </transition>
              </div>
              <div class="bubble-content" :class="{ 'bubble-markdown': msg.role === 'assistant' }">
                <template v-if="msg.role === 'user'">{{ msg.content }}</template>
                <template v-else>
                  <MarkdownRender
                    :content="msg.content"
                    :final="!msg.streaming"
                    :typewriter="false"
                  />
                </template>
              </div>
              <div v-if="msg.files?.length" class="bubble-files">
                <el-tag v-for="f in msg.files" :key="f.name" size="small" type="info">
                  <el-icon style="margin-right:3px"><Paperclip /></el-icon>{{ f.name }}
                </el-tag>
              </div>
              <div v-if="msg.metrics && msg.role === 'assistant'" class="bubble-metrics">
                <span v-if="msg.metrics.total_tokens">{{ msg.metrics.total_tokens }} tokens</span>
                <span v-if="msg.metrics.duration">· {{ msg.metrics.duration?.toFixed(2) }}s</span>
              </div>
            </div>
          </div>
          <div ref="bottomRef" />
        </div>

        <div class="chat-input-area">
          <div v-if="pendingFiles.length" class="pending-files">
            <el-tag v-for="(f, i) in pendingFiles" :key="i" closable size="small" @close="removeFile(i)">
              {{ f.name }}
            </el-tag>
          </div>
          <div class="input-row">
            <el-input
              v-model="inputText"
              type="textarea"
              :autosize="{ minRows: 2, maxRows: 6 }"
              placeholder="输入消息，Ctrl+Enter 发送"
              resize="none"
              @keydown.ctrl.enter.prevent="sendMessage"
            />
            <div class="input-actions">
              <el-upload ref="uploadRef" :auto-upload="false" :show-file-list="false" multiple :on-change="onFileChange">
                <el-button :icon="Paperclip" circle title="上传附件" />
              </el-upload>
              <el-button type="primary" :icon="Promotion" :loading="sending" @click="sendMessage">发送</el-button>
            </div>
          </div>
        </div>
      </template>

      <div v-else class="chat-empty">
        <el-empty :description="selectedComponentId ? '新建一个会话开始聊天' : `请先选择 ${typeLabel}`">
          <el-button v-if="selectedComponentId" type="primary" @click="createSession">新建会话</el-button>
        </el-empty>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, nextTick, onMounted, onUnmounted, watch } from "vue";
import { Plus, Delete, Paperclip, Promotion, UserFilled, Service, ChatDotRound, Edit, Refresh, Loading, CircleCheck, CircleClose, ArrowRight } from "@element-plus/icons-vue";
import { ElMessage, ElMessageBox } from "element-plus";
import { MarkdownRender } from "markstream-vue";
import AgAgentAPI from "@/api/module_agno_manage/agents";
import AgTeamAPI from "@/api/module_agno_manage/teams";
import AgWorkflowAPI from "@/api/module_agno_manage/workflows";
import AgnoAgentChatAPI from "@/api/module_agno_manage/agno/chat";
import AgnoTeamChatAPI from "@/api/module_agno_manage/agno/team";
import AgnoWorkflowChatAPI from "@/api/module_agno_manage/agno/workflow";
import AgnoSessionAPI from "@/api/module_agno_manage/agno/session";
import type { ChatSession, ChatMessage, SessionType, AgentStreamEvent, RunProgressItem } from "@/api/module_agno_manage/agno/chat";
import { useUserStoreHook } from "@/store/modules/user.store";

const uuidv4 = () =>
  "xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx".replace(/[xy]/g, (c) => {
    const r = (Math.random() * 16) | 0;
    return (c === "x" ? r : (r & 0x3) | 0x8).toString(16);
  });

const userStore = useUserStoreHook();
const userId = computed(() => userStore.basicInfo.id ?? 1);

// ─── 类型切换 ───────────────────────────────────
const sessionType = ref<SessionType>("agent");
const typeOptions = [
  { label: "Agent", value: "agent" },
  { label: "Team", value: "team" },
  { label: "Workflow", value: "workflow" },
];
const typeLabel = computed(() => {
  const map = { agent: "Agent", team: "Team", workflow: "Workflow" };
  return map[sessionType.value];
});
const typeTagType = computed(() => {
  const map: Record<SessionType, "primary" | "success" | "warning" | "info" | "danger" | undefined> = {
    agent: undefined,
    team: "success",
    workflow: "warning",
  };
  return map[sessionType.value];
});

// ─── 组件列表（agent/team/workflow） ─────────────
const componentList = ref<{ id?: number; name?: string }[]>([]);
const selectedComponentId = ref<number | null>(null);

async function loadComponentList() {
  componentList.value = [];
  selectedComponentId.value = null;
  sessions.value = [];
  currentSessionId.value = null;
  try {
    if (sessionType.value === "agent") {
      const res = await AgAgentAPI.listAgAgent({ page_no: 1, page_size: 100 });
      componentList.value = res.data.data?.items ?? [];
    } else if (sessionType.value === "team") {
      const res = await AgTeamAPI.listAgTeam({ page_no: 1, page_size: 100 });
      componentList.value = res.data.data?.items ?? [];
    } else {
      const res = await AgWorkflowAPI.listAgWorkflow({ page_no: 1, page_size: 100 });
      componentList.value = res.data.data?.items ?? [];
    }
  } catch {
    ElMessage.error(`加载 ${typeLabel.value} 列表失败`);
  }
}

// ─── 会话 ────────────────────────────────────────
const sessions = ref<ChatSession[]>([]);
const currentSessionId = ref<string | null>(null);
const currentSession = computed(() =>
  sessions.value.find((s) => s.id === currentSessionId.value) ?? null
);

// 加载状态
const loadingSessions = ref(false);
const loadingMessages = ref(false);
const sending = ref(false);

// 输入
const inputText = ref("");
const pendingFiles = ref<File[]>([]);
const messageListRef = ref<HTMLElement | null>(null);
const bottomRef = ref<HTMLElement | null>(null);
const uploadRef = ref();
const options = ref({ stream: true });

// 重命名状态
const editingSessionId = ref<string | null>(null);
const editingName = ref("");

// 进度面板展开状态
const expandedProgress = ref<Set<string>>(new Set());
function toggleProgress(msgId: string) {
  if (expandedProgress.value.has(msgId)) expandedProgress.value.delete(msgId);
  else expandedProgress.value.add(msgId);
}

// 流式控制
let streamController: AbortController | null = null;

onMounted(() => loadComponentList());
onUnmounted(() => streamController?.abort());

watch(sessionType, () => loadComponentList());
watch(selectedComponentId, (id) => {
  if (id) loadSessions(id);
  else { sessions.value = []; currentSessionId.value = null; }
});
watch(currentSessionId, async (id) => {
  if (!id) return;
  const session = sessions.value.find((s) => s.id === id);
  if (session && !session.loaded) await loadSessionMessages(id);
  else await scrollToBottom();
});

// ─── 事件处理 ────────────────────────────────────
function onTypeChange() {
  // watch(sessionType) 已处理
}

function onComponentChange(id: number | undefined) {
  selectedComponentId.value = id ?? null;
  sessions.value = [];
  currentSessionId.value = null;
}

// ─── 会话操作 ────────────────────────────────────
async function loadSessions(componentId: number) {
  loadingSessions.value = true;
  try {
    const res = await AgnoSessionAPI.listSessions({
      type: sessionType.value,
      component_id: componentId,
      user_id: String(userId.value),
      limit: 50,
      sort_by: "updated_at",
      sort_order: "desc",
    });
    // Agno 直接返回 { data: [...], meta: {...} }
    const list: any[] = (res.data as any)?.data ?? [];
    const componentName = componentList.value.find((c) => c.id === componentId)?.name ?? String(componentId);
    sessions.value = (Array.isArray(list) ? list : []).map((s: any) => ({
      id: s.session_id,
      name: s.session_name || s.session_id.slice(0, 8),
      componentId,
      componentName,
      createdAt: s.created_at ? new Date(s.created_at).getTime() : Date.now(),
      messages: [],
      loaded: false,
    }));
    if (sessions.value.length > 0 && !currentSessionId.value) {
      currentSessionId.value = sessions.value[0].id;
    }
  } catch {
    ElMessage.error("加载会话列表失败");
    sessions.value = [];
  } finally {
    loadingSessions.value = false;
  }
}

async function loadSessionMessages(sessionId: string) {
  const session = sessions.value.find((s) => s.id === sessionId);
  if (!session) return;
  loadingMessages.value = true;
  try {
    const res = await AgnoSessionAPI.getSessionRuns(sessionId, {
      type: sessionType.value,
      user_id: String(userId.value),
    });
    // Agno 直接返回 run 数组
    const runs: any[] = Array.isArray(res.data) ? (res.data as any) : [];
    const messages: ChatMessage[] = [];
    for (const run of runs) {
      if (run.run_input) {
        messages.push({ id: `${run.run_id}-user`, role: "user", content: run.run_input, createdAt: (run.created_at ?? 0) * 1000 });
      }
      if (run.content) {
        messages.push({ id: `${run.run_id}-assistant`, role: "assistant", content: run.content, createdAt: (run.created_at ?? 0) * 1000, metrics: run.metrics });
      }
    }
    session.messages = messages;
    session.loaded = true;
  } catch {
    session.loaded = true;
  } finally {
    loadingMessages.value = false;
    await scrollToBottom();
  }
}

async function reloadMessages() {
  if (!currentSession.value) return;
  currentSession.value.loaded = false;
  currentSession.value.messages = [];
  await loadSessionMessages(currentSession.value.id);
}

function createSession() {
  if (!selectedComponentId.value) return;
  const component = componentList.value.find((c) => c.id === selectedComponentId.value);
  const newId = uuidv4();
  const name = `新会话 ${sessions.value.length + 1}`;
  const newSession: ChatSession = {
    id: newId,
    name,
    componentId: selectedComponentId.value,
    componentName: component?.name ?? String(selectedComponentId.value),
    createdAt: Date.now(),
    messages: [],
    loaded: true,
  };
  sessions.value.unshift(newSession);
  currentSessionId.value = newId;
}

function switchSession(id: string) {
  currentSessionId.value = id;
}

async function deleteSession(id: string) {
  try {
    await ElMessageBox.confirm("确定删除该会话吗？此操作不可撤销。", "删除会话", {
      type: "warning", confirmButtonText: "删除", cancelButtonText: "取消",
    });
  } catch { return; }
  sessions.value = sessions.value.filter((s) => s.id !== id);
  if (currentSessionId.value === id) currentSessionId.value = sessions.value[0]?.id ?? null;
  try { await AgnoSessionAPI.deleteSession(id, { user_id: String(userId.value) }); } catch { /* 非关键 */ }
}

function startRename(session: ChatSession) {
  editingSessionId.value = session.id;
  editingName.value = session.name;
}
function cancelRename() {
  editingSessionId.value = null;
  editingName.value = "";
}
async function confirmRename(id: string) {
  const name = editingName.value.trim();
  editingSessionId.value = null;
  editingName.value = "";
  if (!name) return;
  const session = sessions.value.find((s) => s.id === id);
  if (!session || session.name === name) return;
  const oldName = session.name;
  session.name = name;
  try {
    await AgnoSessionAPI.renameSession(id, name, { type: sessionType.value, user_id: String(userId.value) });
  } catch {
    session.name = oldName;
    ElMessage.error("重命名失败");
  }
}

function clearMessages() {
  if (!currentSession.value) return;
  currentSession.value.messages = [];
  currentSession.value.loaded = false;
}

// ─── 发送消息 ────────────────────────────────────
function onFileChange(file: any) {
  const raw = file.raw as File;
  if (!pendingFiles.value.some((f) => f.name === raw.name && f.size === raw.size)) {
    pendingFiles.value.push(raw);
  }
}
function removeFile(index: number) { pendingFiles.value.splice(index, 1); }

async function sendMessage() {
  const text = inputText.value.trim();
  if (!text || !currentSession.value || sending.value) return;
  streamController?.abort();
  streamController = null;
  const session = currentSession.value;
  const files = [...pendingFiles.value];
  session.messages.push({ id: uuidv4(), role: "user", content: text, createdAt: Date.now(), files: files.map((f) => ({ name: f.name, size: f.size })) });
  inputText.value = "";
  pendingFiles.value = [];
  uploadRef.value?.clearFiles?.();
  await scrollToBottom();
  sending.value = true;
  if (options.value.stream) await sendStream(session, text, files);
  else await sendNormal(session, text, files);
  sending.value = false;
}

async function sendNormal(session: ChatSession, text: string, files: File[]) {
  const body = { message: text, session_id: session.id, user_id: Number(userId.value), files };
  try {
    let data: any;
    if (sessionType.value === "agent") {
      data = (await AgnoAgentChatAPI.runAgent(session.componentId, body)).data;
    } else if (sessionType.value === "team") {
      data = (await AgnoTeamChatAPI.runTeam(session.componentId, body)).data;
    } else {
      data = (await AgnoWorkflowChatAPI.runWorkflow(session.componentId, body)).data;
    }
    session.messages.push({ id: uuidv4(), role: "assistant", content: data?.content ?? "", createdAt: Date.now(), metrics: data?.metrics });
  } catch { ElMessage.error("发送失败"); }
  await scrollToBottom();
}

async function sendStream(session: ChatSession, text: string, files: File[]) {
  session.messages.push({ id: uuidv4(), role: "assistant", content: "", createdAt: Date.now(), streaming: true, progress: [] });
  await scrollToBottom();
  const reactiveMsg = session.messages[session.messages.length - 1];
  const body = { message: text, session_id: session.id, user_id: Number(userId.value), files };

  const onChunk = async (_event: string, data: AgentStreamEvent) => {
    const progress = reactiveMsg.progress!;

    if (_event === "RunStarted") {
      progress.push({ event: _event, label: `运行开始`, status: "running", detail: data.model ? `${data.model_provider} · ${data.model}` : undefined });
    } else if (_event === "ModelRequestStarted") {
      progress.push({ event: _event, label: "模型请求中", status: "running", detail: data.model ? `${data.model_provider} · ${data.model}` : undefined });
    } else if (_event === "ModelRequestCompleted") {
      const last = [...progress].reverse().find(p => p.event === "ModelRequestStarted");
      if (last) { last.status = "done"; last.label = "模型请求完成"; last.tokens = data.total_tokens; }
      else progress.push({ event: _event, label: "模型请求完成", status: "done", tokens: data.total_tokens });
    } else if (_event === "ToolCallStarted") {
      const toolName = data.tool?.tool_name ?? "工具";
      const args = data.tool?.tool_args ? JSON.stringify(data.tool.tool_args) : undefined;
      progress.push({ event: _event, label: `调用工具: ${toolName}`, status: "running", detail: args });
    } else if (_event === "ToolCallCompleted") {
      const toolName = data.tool?.tool_name ?? "工具";
      const last = [...progress].reverse().find(p => p.event === "ToolCallStarted" && p.label.includes(toolName));
      const dur = data.tool?.metrics?.duration;
      if (last) { last.status = "done"; last.label = `工具完成: ${toolName}`; last.duration = dur; }
      else progress.push({ event: _event, label: `工具完成: ${toolName}`, status: "done", duration: dur });
    } else if (_event === "ToolCallError") {
      const toolName = data.tool?.tool_name ?? "工具";
      const last = [...progress].reverse().find(p => p.label.includes(toolName));
      if (last) { last.status = "error"; last.label = `工具错误: ${toolName}`; last.detail = data.error ?? data.tool?.result ?? undefined; }
      else progress.push({ event: _event, label: `工具错误: ${toolName}`, status: "error", detail: data.error ?? undefined });
    } else if (_event === "RunContent" && data.content) {
      reactiveMsg.content += data.content;
      await scrollToBottom();
    } else if (_event === "RunCompleted") {
      reactiveMsg.metrics = data.metrics;
      // 将所有还在 running 的进度项标记为 done
      progress.forEach(p => { if (p.status === "running") p.status = "done"; });
    }
  };
  const onDone = async () => { reactiveMsg.streaming = false; await scrollToBottom(); };
  const onError = (err: Error) => { reactiveMsg.streaming = false; reactiveMsg.content = reactiveMsg.content || `[错误: ${err.message}]`; };

  return new Promise<void>((resolve) => {
    const wrappedDone = () => { onDone(); resolve(); };
    const wrappedError = (err: Error) => { onError(err); resolve(); };
    if (sessionType.value === "agent") {
      streamController = AgnoAgentChatAPI.runAgentStream(session.componentId, body, onChunk, wrappedDone, wrappedError);
    } else if (sessionType.value === "team") {
      streamController = AgnoTeamChatAPI.runTeamStream(session.componentId, body, onChunk, wrappedDone, wrappedError);
    } else {
      streamController = AgnoWorkflowChatAPI.runWorkflowStream(session.componentId, body, onChunk, wrappedDone, wrappedError);
    }
  });
}

async function scrollToBottom() {
  await nextTick();
  bottomRef.value?.scrollIntoView({ behavior: "smooth" });
}
</script>

<style scoped>
.chat-layout {
  display: flex;
  height: calc(100vh - 120px);
  min-height: 500px;
  background: var(--el-bg-color);
  border-radius: 8px;
  overflow: hidden;
  border: 1px solid var(--el-border-color-light);
}

/* ── 左侧 ── */
.chat-sidebar {
  width: 260px;
  flex-shrink: 0;
  display: flex;
  flex-direction: column;
  border-right: 1px solid var(--el-border-color-light);
  background: var(--el-fill-color-extra-light);
}

.sidebar-header {
  padding: 12px;
  display: flex;
  flex-direction: column;
  gap: 8px;
  border-bottom: 1px solid var(--el-border-color-light);
}

.type-segmented {
  width: 100%;
}

.component-select {
  width: 100%;
}

.session-list {
  flex: 1;
  overflow-y: auto;
  padding: 8px;
  min-height: 0;
}

.session-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 10px;
  border-radius: 6px;
  cursor: pointer;
  transition: background 0.15s;
}

.session-item:hover { background: var(--el-fill-color); }
.session-item.active { background: var(--el-color-primary-light-9); color: var(--el-color-primary); }

.session-icon { flex-shrink: 0; color: var(--el-text-color-secondary); }

.session-info { flex: 1; min-width: 0; }

.session-name {
  font-size: 13px;
  font-weight: 500;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  cursor: text;
}

.session-meta {
  font-size: 11px;
  color: var(--el-text-color-placeholder);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.session-actions {
  display: flex;
  gap: 2px;
  opacity: 0;
  transition: opacity 0.15s;
  flex-shrink: 0;
}
.session-item:hover .session-actions,
.session-item.active .session-actions { opacity: 1; }

.action-btn { padding: 2px !important; }

/* ── 右侧 ── */
.chat-main {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-width: 0;
}

.chat-toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 10px 16px;
  border-bottom: 1px solid var(--el-border-color-light);
  background: var(--el-bg-color);
}

.chat-title {
  font-size: 14px;
  font-weight: 600;
  color: var(--el-text-color-primary);
  display: flex;
  align-items: center;
}

.toolbar-options {
  display: flex;
  align-items: center;
  gap: 12px;
}

.option-item { display: flex; align-items: center; gap: 6px; }
.option-label { font-size: 12px; color: var(--el-text-color-secondary); }

/* ── 消息列表 ── */
.message-list {
  flex: 1;
  overflow-y: auto;
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.message-row { display: flex; gap: 10px; align-items: flex-start; }
.message-row.user { flex-direction: row-reverse; }

.msg-avatar { flex-shrink: 0; }
.msg-avatar.user { background: var(--el-color-primary); }
.msg-avatar.assistant { background: var(--el-color-success); }

.message-bubble { max-width: 70%; display: flex; flex-direction: column; gap: 4px; }

.bubble-content {
  padding: 10px 14px;
  border-radius: 12px;
  font-size: 14px;
  line-height: 1.6;
  white-space: pre-wrap;
  word-break: break-word;
  background: var(--el-fill-color);
  color: var(--el-text-color-primary);
}

.message-row.user .bubble-content {
  background: var(--el-color-primary);
  color: #fff;
  border-radius: 12px 2px 12px 12px;
}
.message-row.assistant .bubble-content { border-radius: 2px 12px 12px 12px; }

.bubble-content.bubble-markdown {
  white-space: normal;
  max-width: 100%;
}
.bubble-content.bubble-markdown :deep(.vmr-container) {
  font-size: 14px;
  line-height: 1.6;
  color: var(--el-text-color-primary);
}
.bubble-content.bubble-markdown :deep(pre) { border-radius: 6px; margin: 8px 0; }
.bubble-content.bubble-markdown :deep(p:last-child) { margin-bottom: 0; }

.bubble-files { display: flex; flex-wrap: wrap; gap: 4px; }
.bubble-metrics { font-size: 11px; color: var(--el-text-color-placeholder); padding: 0 2px; }

/* ── 输入区域 ── */
.chat-input-area {
  padding: 12px 16px;
  border-top: 1px solid var(--el-border-color-light);
  background: var(--el-bg-color);
}

.pending-files { display: flex; flex-wrap: wrap; gap: 6px; margin-bottom: 8px; }

.input-row { display: flex; gap: 10px; align-items: flex-end; }
.input-row :deep(.el-textarea) { flex: 1; }
.input-actions { display: flex; flex-direction: column; gap: 8px; align-items: center; }

/* ── 进度面板 ── */
.run-progress {
  margin-bottom: 6px;
  border: 1px solid var(--el-border-color-light);
  border-radius: 8px;
  overflow: hidden;
  font-size: 12px;
  background: var(--el-fill-color-extra-light);
}

.run-progress-header {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 10px;
  cursor: pointer;
  user-select: none;
  transition: background 0.15s;
}
.run-progress-header:hover { background: var(--el-fill-color); }

.progress-icon { color: var(--el-color-primary); flex-shrink: 0; }
.progress-title { flex: 1; color: var(--el-text-color-secondary); font-size: 12px; }
.progress-chevron {
  color: var(--el-text-color-placeholder);
  transition: transform 0.2s;
  transform: rotate(0deg);
}
.progress-chevron.expanded { transform: rotate(90deg); }

.run-progress-body {
  border-top: 1px solid var(--el-border-color-light);
  padding: 6px 8px;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.progress-item {
  display: flex;
  align-items: flex-start;
  gap: 6px;
  padding: 3px 4px;
  border-radius: 4px;
}
.progress-item.running { color: var(--el-color-primary); }
.progress-item.done { color: var(--el-color-success); }
.progress-item.error { color: var(--el-color-danger); }

.item-icon { flex-shrink: 0; margin-top: 1px; }
.item-body { display: flex; flex-wrap: wrap; align-items: center; gap: 4px; min-width: 0; }
.item-label { color: var(--el-text-color-primary); font-size: 12px; }
.item-meta { color: var(--el-text-color-placeholder); font-size: 11px; }
.item-detail {
  width: 100%;
  color: var(--el-text-color-secondary);
  font-size: 11px;
  font-family: monospace;
  white-space: pre-wrap;
  word-break: break-all;
  max-height: 60px;
  overflow-y: auto;
  background: var(--el-fill-color);
  border-radius: 3px;
  padding: 2px 4px;
  margin-top: 2px;
}

.progress-collapse-enter-active,
.progress-collapse-leave-active { transition: all 0.2s ease; overflow: hidden; }
.progress-collapse-enter-from,
.progress-collapse-leave-to { max-height: 0; opacity: 0; }
.progress-collapse-enter-to,
.progress-collapse-leave-from { max-height: 400px; opacity: 1; }

@keyframes spin { to { transform: rotate(360deg); } }
.spinning { animation: spin 1s linear infinite; }

/* ── 空状态 ── */
.chat-empty { flex: 1; display: flex; align-items: center; justify-content: center; }
</style>
