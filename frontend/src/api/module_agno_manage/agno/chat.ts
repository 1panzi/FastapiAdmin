import agnoRequest from "./agnoRequest";
import { Auth } from "@/utils/auth";

// ─────────────────────────────────────────
// 共享 SSE 流式辅助函数
// ─────────────────────────────────────────

export function createRunStream(
  path: string,
  body: RunForm,
  onChunk: (event: string, data: AgentStreamEvent) => void,
  onDone: () => void,
  onError: (err: Error) => void
): AbortController {
  const controller = new AbortController();
  const formData = new FormData();
  formData.append("message", body.message);
  formData.append("stream", "true");
  formData.append("session_id", body.session_id);
  formData.append("user_id", String(body.user_id));
  formData.append("background", "false");
  formData.append("version", body.version ?? "");
  if (body.files?.length) {
    body.files.forEach((f) => formData.append("files", f));
  }

  const token = Auth.getAccessToken();
  const baseURL = import.meta.env.VITE_APP_BASE_API ?? "";

  fetch(`${baseURL}${path}`, {
    method: "POST",
    headers: token ? { Authorization: `Bearer ${token}` } : {},
    body: formData,
    signal: controller.signal,
  })
    .then(async (res) => {
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      if (!res.body) throw new Error("Response body is null");
      const reader = res.body.getReader();
      const decoder = new TextDecoder();
      let buffer = "";
      let eventName = "";

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split("\n");
        buffer = lines.pop() ?? "";

        for (const line of lines) {
          if (line.startsWith("event:")) {
            eventName = line.slice(6).trim();
          } else if (line.startsWith("data:")) {
            try {
              const data = JSON.parse(line.slice(5).trim());
              onChunk(eventName, data);
            } catch {
              // ignore parse errors
            }
            eventName = "";
          } else if (line === "") {
            eventName = "";
          }
        }
      }
      onDone();
    })
    .catch((err) => {
      if (err.name !== "AbortError") onError(err);
    });

  return controller;
}

// ─────────────────────────────────────────
// Agent Chat API
// ─────────────────────────────────────────

const AGENT_PATH = "/agents";

const AgnoAgentChatAPI = {
  runAgent(agentId: number, body: RunForm) {
    const formData = new FormData();
    formData.append("message", body.message);
    formData.append("stream", "false");
    formData.append("session_id", body.session_id);
    formData.append("user_id", String(body.user_id));
    formData.append("background", "false");
    if (body.version !== undefined) formData.append("version", body.version ?? "");
    if (body.files?.length) {
      body.files.forEach((f) => formData.append("files", f));
    }
    return agnoRequest<AgentRunResponse>({
      url: `${AGENT_PATH}/${agentId}/runs`,
      method: "post",
      data: formData,
      headers: { "Content-Type": "multipart/form-data" },
    });
  },

  runAgentStream(
    agentId: number,
    body: RunForm,
    onChunk: (event: string, data: AgentStreamEvent) => void,
    onDone: () => void,
    onError: (err: Error) => void
  ): AbortController {
    return createRunStream(`${AGENT_PATH}/${agentId}/runs`, body, onChunk, onDone, onError);
  },
};

export default AgnoAgentChatAPI;

// ─────────────────────────────────────────
// TS 类型声明
// ─────────────────────────────────────────

export interface RunForm {
  message: string;
  session_id: string;
  user_id: number;
  stream?: boolean;
  version?: string;
  files?: File[];
}

/** @deprecated 使用 RunForm */
export type AgentRunForm = RunForm;

export interface AgentRunResponse {
  run_id: string;
  agent_id: string;
  agent_name: string;
  session_id: string;
  user_id: string;
  content: string;
  content_type: string;
  model: string;
  model_provider: string;
  session_state: Record<string, any>;
  created_at: number;
  status: string;
  metrics: AgentMetrics;
  messages: AgentMessage[];
  tools: any[];
  input: Record<string, any>;
}

export interface AgentMessage {
  id: string;
  content: string;
  role: "user" | "assistant";
  from_history: boolean;
  created_at: number;
  files?: AgentFile[];
  metrics?: AgentMetrics;
}

export interface AgentFile {
  id: string;
  content: string;
  mime_type: string;
  filename: string;
  format: string;
}

export interface AgentMetrics {
  input_tokens?: number;
  output_tokens?: number;
  total_tokens?: number;
  time_to_first_token?: number;
  duration?: number;
  details?: Record<string, any>;
}

export interface AgentStreamEvent {
  event?: string;
  agent_id?: string;
  agent_name?: string;
  run_id?: string;
  session_id?: string;
  content?: string;
  content_type?: string;
  reasoning_content?: string;
  model?: string;
  model_provider?: string;
  input_tokens?: number;
  output_tokens?: number;
  total_tokens?: number;
  reasoning_tokens?: number;
  metrics?: AgentMetrics;
  session_state?: Record<string, any>;
  created_at?: number;
  error?: string;
  tool?: {
    tool_name?: string;
    tool_args?: Record<string, any>;
    tool_call_error?: boolean | null;
    result?: string | null;
    metrics?: {
      start_time?: number;
      end_time?: number;
      duration?: number;
    } | null;
  };
}

// 会话（支持服务端持久化）
export interface ChatSession {
  id: string;
  name: string;
  componentId: number;   // agent/team/workflow 的 admin DB integer id
  componentName: string; // 显示名
  createdAt: number;
  messages: ChatMessage[];
  loaded?: boolean;      // 是否已从服务端加载消息历史
}

export interface RunProgressItem {
  event: string;
  label: string;
  status: "running" | "done" | "error";
  detail?: string;
  duration?: number;
  tokens?: number;
}

export interface ChatMessage {
  id: string;
  role: "user" | "assistant";
  content: string;
  createdAt: number;
  files?: { name: string; size: number }[];
  metrics?: AgentMetrics;
  streaming?: boolean;
  progress?: RunProgressItem[];
}

export type SessionType = "agent" | "team" | "workflow";
