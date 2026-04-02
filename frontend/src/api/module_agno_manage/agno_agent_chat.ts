import request from "@/utils/request";
import { Auth } from "@/utils/auth";

const API_PATH = "/agents";

const AgnoAgentChatAPI = {
  // 非流式发送消息
  runAgent(agentId: number, body: AgentRunForm) {
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
    return request<ApiResponse<AgentRunResponse>>({
      url: `${API_PATH}/${agentId}/runs`,
      method: "post",
      data: formData,
      headers: { "Content-Type": "multipart/form-data" },
    });
  },

  // 流式发送消息（返回 ReadableStream）
  runAgentStream(
    agentId: number,
    body: AgentRunForm,
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

    fetch(`${baseURL}${API_PATH}/${agentId}/runs`, {
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
              // 只在空行（事件分隔符）时重置 eventName，保持跨行一致性
              // 但当前服务端每个 data 行后紧跟空行，data 处理后重置是安全的
              eventName = "";
            } else if (line === "") {
              // SSE 事件分隔符，确保 eventName 被重置
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
  },
};

export default AgnoAgentChatAPI;

// TS 类型声明

export interface AgentRunForm {
  message: string;
  session_id: string;
  user_id: number;
  stream?: boolean;
  version?: string;
  files?: File[];
}

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
  metrics?: AgentMetrics;
  session_state?: Record<string, any>;
}

// 会话（前端本地管理）
export interface ChatSession {
  id: string;
  name: string;
  agentId: number;
  agentName: string;
  createdAt: number;
  messages: ChatMessage[];
}

export interface ChatMessage {
  id: string;
  role: "user" | "assistant";
  content: string;
  createdAt: number;
  files?: { name: string; size: number }[];
  metrics?: AgentMetrics;
  streaming?: boolean;
}
