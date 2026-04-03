import agnoRequest from "./agnoRequest";

const SESSION_PATH = "/sessions";

const AgnoSessionAPI = {
  // 获取会话列表
  listSessions(params: SessionListParams) {
    return agnoRequest<SessionListResponse>({
      url: SESSION_PATH,
      method: "get",
      params,
    });
  },

  // 创建会话
  createSession(body: CreateSessionRequest = {}, params?: { type?: string; db_id?: string }) {
    return agnoRequest<AgentSessionDetail>({
      url: SESSION_PATH,
      method: "post",
      data: body,
      params,
    });
  },

  // 获取单个会话详情
  getSession(sessionId: string, params?: { type?: string; user_id?: string }) {
    return agnoRequest<AgentSessionDetail>({
      url: `${SESSION_PATH}/${sessionId}`,
      method: "get",
      params,
    });
  },

  // 删除单个会话
  deleteSession(sessionId: string, params?: { user_id?: string }) {
    return agnoRequest({
      url: `${SESSION_PATH}/${sessionId}`,
      method: "delete",
      params,
    });
  },

  // 重命名会话
  renameSession(sessionId: string, name: string, params?: { type?: string; user_id?: string }) {
    return agnoRequest<AgentSessionDetail>({
      url: `${SESSION_PATH}/${sessionId}/rename`,
      method: "post",
      data: { name },
      params,
    });
  },

  // 获取会话的历史 runs（消息历史）
  getSessionRuns(sessionId: string, params?: { type?: string; user_id?: string }) {
    return agnoRequest<SessionRun[]>({
      url: `${SESSION_PATH}/${sessionId}/runs`,
      method: "get",
      params,
    });
  },
};

export default AgnoSessionAPI;

// TS 类型声明

export interface SessionListParams {
  type?: string;
  component_id?: string | number;
  user_id?: string;
  session_name?: string;
  limit?: number;
  page?: number;
  sort_by?: string;
  sort_order?: "asc" | "desc";
  db_id?: string;
  table?: string;
}

export interface SessionSchema {
  session_id: string;
  session_name?: string;
  session_state?: Record<string, any>;
  created_at?: string;
  updated_at?: string;
  agent_id?: string;
  user_id?: string;
}

export interface SessionListResponse {
  data: SessionSchema[];
  total?: number;
  page?: number;
  limit?: number;
}

export interface AgentSessionDetail extends SessionSchema {
  agent_session_id?: string;
  agent_data?: {
    name?: string;
    agent_id?: string;
    model?: { provider?: string; name?: string; id?: string };
  };
  metrics?: Record<string, any>;
  session_summary?: { summary: string; updated_at: string };
  total_tokens?: number;
}

export interface CreateSessionRequest {
  session_id?: string;
  session_name?: string;
  user_id?: string;
  agent_id?: string | number;
  session_state?: Record<string, any>;
  metadata?: Record<string, any>;
}

export interface SessionRun {
  run_id: string;
  agent_id?: string;
  user_id?: string;
  run_input?: string;
  content?: string;
  reasoning_content?: string;
  metrics?: Record<string, any>;
  messages?: SessionMessage[];
  status?: string;
  created_at?: number;
}

export interface SessionMessage {
  content: string;
  role: "user" | "assistant" | "system" | "tool";
  from_history?: boolean;
  created_at?: number;
  metrics?: Record<string, any>;
}
