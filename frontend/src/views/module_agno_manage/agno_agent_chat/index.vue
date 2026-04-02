<template>
  <div class="chat-layout">
    <!-- 左侧：Agent 选择 + 会话列表 -->
    <div class="chat-sidebar">
      <div class="sidebar-header">
        <el-select
          v-model="selectedAgentId"
          placeholder="选择 Agent"
          filterable
          class="agent-select"
        >
          <el-option
            v-for="agent in agentList"
            :key="agent.id"
            :label="agent.name"
            :value="agent.id"
          />
        </el-select>
        <el-button type="primary" :icon="Plus" @click="createSession" :disabled="!selectedAgentId">
          新建会话
        </el-button>
      </div>

      <div class="session-list">
        <div
          v-for="session in sessions"
          :key="session.id"
          class="session-item"
          :class="{ active: currentSessionId === session.id }"
          @click="switchSession(session.id)"
        >
          <el-icon class="session-icon"><ChatDotRound /></el-icon>
          <div class="session-info">
            <div class="session-name">{{ session.name }}</div>
            <div class="session-meta">{{ session.agentName }}</div>
          </div>
          <el-button
            class="session-delete"
            :icon="Delete"
            size="small"
            text
            @click.stop="deleteSession(session.id)"
          />
        </div>
        <el-empty v-if="sessions.length === 0" description="暂无会话" :image-size="60" />
      </div>
    </div>

    <!-- 右侧：聊天区域 -->
    <div class="chat-main">
      <template v-if="currentSession">
        <!-- 顶部工具栏 -->
        <div class="chat-toolbar">
          <span class="chat-title">{{ currentSession.agentName }} · {{ currentSession.name }}</span>
          <div class="toolbar-options">
            <el-tooltip content="流式输出">
              <div class="option-item">
                <span class="option-label">流式</span>
                <el-switch v-model="options.stream" size="small" />
              </div>
            </el-tooltip>
            <el-tooltip content="Markdown 渲染">
              <div class="option-item">
                <span class="option-label">Markdown</span>
                <el-switch v-model="options.markdown" size="small" />
              </div>
            </el-tooltip>
          </div>
        </div>

        <!-- 消息列表 -->
        <div ref="messageListRef" class="message-list">
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
              <div class="bubble-content">
                <template v-if="msg.streaming">
                  <span>{{ msg.content }}</span>
                  <span class="typing-cursor">▋</span>
                </template>
                <template v-else>{{ msg.content }}</template>
              </div>
              <div v-if="msg.files?.length" class="bubble-files">
                <el-tag
                  v-for="f in msg.files"
                  :key="f.name"
                  size="small"
                  type="info"
                >
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

        <!-- 输入区域 -->
        <div class="chat-input-area">
          <!-- 附件预览 -->
          <div v-if="pendingFiles.length" class="pending-files">
            <el-tag
              v-for="(f, i) in pendingFiles"
              :key="i"
              closable
              size="small"
              @close="removeFile(i)"
            >
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
              <!-- 附件上传 -->
              <el-upload
                ref="uploadRef"
                :auto-upload="false"
                :show-file-list="false"
                multiple
                :on-change="onFileChange"
              >
                <el-button :icon="Paperclip" circle title="上传附件" />
              </el-upload>
              <el-button
                type="primary"
                :icon="Promotion"
                :loading="sending"
                @click="sendMessage"
              >
                发送
              </el-button>
            </div>
          </div>
        </div>
      </template>

      <!-- 未选择会话 -->
      <div v-else class="chat-empty">
        <el-empty description="请选择 Agent 并新建会话">
          <el-button type="primary" :disabled="!selectedAgentId" @click="createSession">
            新建会话
          </el-button>
        </el-empty>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, nextTick, onMounted, onUnmounted } from "vue";
import { Plus, Delete, Paperclip, Promotion, UserFilled, Service, ChatDotRound } from "@element-plus/icons-vue";
import { ElMessage } from "element-plus";
import AgAgentAPI from "@/api/module_agno_manage/agents";
import AgnoAgentChatAPI, {
  type ChatSession,
  type ChatMessage,
} from "@/api/module_agno_manage/agno_agent_chat";
import { useUserStoreHook } from "@/store/modules/user.store";
import type { AgAgentTable } from "@/api/module_agno_manage/agents";

const uuidv4 = () => crypto.randomUUID();

const userStore = useUserStoreHook();
const userId = computed(() => userStore.basicInfo.id);

// Agent 列表
const agentList = ref<AgAgentTable[]>([]);
const selectedAgentId = ref<number | null>(null);

// 会话
const sessions = ref<ChatSession[]>([]);
const currentSessionId = ref<string | null>(null);
const currentSession = computed(() =>
  sessions.value.find((s) => s.id === currentSessionId.value) ?? null
);

// 输入
const inputText = ref("");
const pendingFiles = ref<File[]>([]);
const sending = ref(false);
const messageListRef = ref<HTMLElement | null>(null);
const bottomRef = ref<HTMLElement | null>(null);
const uploadRef = ref();

// 选项
const options = ref({ stream: true, markdown: false });

// 流式 abort controller
let streamController: AbortController | null = null;

onMounted(async () => {
  await loadAgents();
});

onUnmounted(() => {
  streamController?.abort();
});

async function loadAgents() {
  try {
    const res = await AgAgentAPI.listAgAgent({ page_no: 1, page_size: 100 });
    agentList.value = res.data.data?.items ?? [];
  } catch {
    ElMessage.error("加载 Agent 列表失败");
  }
}

function createSession() {
  if (!selectedAgentId.value) return;
  const agent = agentList.value.find((a) => a.id === selectedAgentId.value);
  const session: ChatSession = {
    id: uuidv4(),
    name: `会话 ${sessions.value.length + 1}`,
    agentId: selectedAgentId.value!,
    agentName: agent?.name ?? String(selectedAgentId.value),
    createdAt: Date.now(),
    messages: [],
  };
  sessions.value.unshift(session);
  currentSessionId.value = session.id;
}

function switchSession(id: string) {
  currentSessionId.value = id;
}

function deleteSession(id: string) {
  sessions.value = sessions.value.filter((s) => s.id !== id);
  if (currentSessionId.value === id) {
    currentSessionId.value = sessions.value[0]?.id ?? null;
  }
}

function onFileChange(file: any) {
  const raw = file.raw as File;
  const exists = pendingFiles.value.some((f) => f.name === raw.name && f.size === raw.size);
  if (!exists) pendingFiles.value.push(raw);
}

function removeFile(index: number) {
  pendingFiles.value.splice(index, 1);
}

async function sendMessage() {
  const text = inputText.value.trim();
  if (!text || !currentSession.value || sending.value) return;

  if (!userId.value) {
    ElMessage.warning("用户未登录，请重新登录");
    return;
  }

  // 中止上一条未完成的流式请求
  streamController?.abort();
  streamController = null;

  const session = currentSession.value;
  const files = [...pendingFiles.value];

  // 添加用户消息
  const userMsg: ChatMessage = {
    id: uuidv4(),
    role: "user",
    content: text,
    createdAt: Date.now(),
    files: files.map((f) => ({ name: f.name, size: f.size })),
  };
  session.messages.push(userMsg);
  inputText.value = "";
  pendingFiles.value = [];
  uploadRef.value?.clearFiles?.();
  await scrollToBottom();

  sending.value = true;

  if (options.value.stream) {
    await sendStream(session, text, files);
  } else {
    await sendNormal(session, text, files);
  }

  sending.value = false;
}

async function sendNormal(session: ChatSession, text: string, files: File[]) {
  try {
    const res = await AgnoAgentChatAPI.runAgent(session.agentId, {
      message: text,
      session_id: session.id,
      user_id: Number(userId.value),
      files,
    });
    const data = res.data.data;
    session.messages.push({
      id: uuidv4(),
      role: "assistant",
      content: data?.content ?? "",
      createdAt: Date.now(),
      metrics: data?.metrics,
    });
  } catch {
    ElMessage.error("发送失败");
  }
  await scrollToBottom();
}

async function sendStream(session: ChatSession, text: string, files: File[]) {
  session.messages.push({
    id: uuidv4(),
    role: "assistant",
    content: "",
    createdAt: Date.now(),
    streaming: true,
  });
  await scrollToBottom();

  // 取 reactive 代理，确保修改能触发视图更新
  const msgIndex = session.messages.length - 1;
  const reactiveMsg = session.messages[msgIndex];

  return new Promise<void>((resolve) => {
    streamController = AgnoAgentChatAPI.runAgentStream(
      session.agentId,
      {
        message: text,
        session_id: session.id,
        user_id: Number(userId.value),
        files,
      },
      async (event, data) => {
        if (event === "RunContent" && data.content) {
          reactiveMsg.content += data.content;
          await scrollToBottom();
        } else if (event === "RunCompleted") {
          reactiveMsg.metrics = data.metrics;
        }
      },
      async () => {
        reactiveMsg.streaming = false;
        await scrollToBottom();
        resolve();
      },
      (err) => {
        reactiveMsg.streaming = false;
        reactiveMsg.content = reactiveMsg.content || `[错误: ${err.message}]`;
        resolve();
      }
    );
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

/* 左侧 */
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

.agent-select {
  width: 100%;
}

.session-list {
  flex: 1;
  overflow-y: auto;
  padding: 8px;
}

.session-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 10px;
  border-radius: 6px;
  cursor: pointer;
  transition: background 0.15s;
  position: relative;
}

.session-item:hover {
  background: var(--el-fill-color);
}

.session-item.active {
  background: var(--el-color-primary-light-9);
  color: var(--el-color-primary);
}

.session-icon {
  flex-shrink: 0;
  color: var(--el-text-color-secondary);
}

.session-info {
  flex: 1;
  min-width: 0;
}

.session-name {
  font-size: 13px;
  font-weight: 500;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.session-meta {
  font-size: 11px;
  color: var(--el-text-color-placeholder);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.session-delete {
  opacity: 0;
  transition: opacity 0.15s;
}

.session-item:hover .session-delete {
  opacity: 1;
}

/* 右侧 */
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
}

.toolbar-options {
  display: flex;
  align-items: center;
  gap: 16px;
}

.option-item {
  display: flex;
  align-items: center;
  gap: 6px;
}

.option-label {
  font-size: 12px;
  color: var(--el-text-color-secondary);
}

/* 消息列表 */
.message-list {
  flex: 1;
  overflow-y: auto;
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.message-row {
  display: flex;
  gap: 10px;
  align-items: flex-start;
}

.message-row.user {
  flex-direction: row-reverse;
}

.msg-avatar {
  flex-shrink: 0;
}

.msg-avatar.user {
  background: var(--el-color-primary);
}

.msg-avatar.assistant {
  background: var(--el-color-success);
}

.message-bubble {
  max-width: 70%;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

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

.message-row.assistant .bubble-content {
  border-radius: 2px 12px 12px 12px;
}

.typing-cursor {
  animation: blink 0.8s step-end infinite;
}

@keyframes blink {
  50% { opacity: 0; }
}

.bubble-files {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
}

.bubble-metrics {
  font-size: 11px;
  color: var(--el-text-color-placeholder);
  padding: 0 2px;
}

/* 输入区域 */
.chat-input-area {
  padding: 12px 16px;
  border-top: 1px solid var(--el-border-color-light);
  background: var(--el-bg-color);
}

.pending-files {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin-bottom: 8px;
}

.input-row {
  display: flex;
  gap: 10px;
  align-items: flex-end;
}

.input-row :deep(.el-textarea) {
  flex: 1;
}

.input-actions {
  display: flex;
  flex-direction: column;
  gap: 8px;
  align-items: center;
}

/* 空状态 */
.chat-empty {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
}
</style>
