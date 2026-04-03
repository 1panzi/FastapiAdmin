import agnoRequest from "./agnoRequest";

const API_PATH = "/agents";

const AgnoAgentAPI = {
  // 获取所有 Agent 列表（来自 Agno 服务器）
  listAgents() {
    return agnoRequest<AgnoAgent[]>({
      url: API_PATH,
      method: "get",
    });
  },

  // 获取单个 Agent 详情
  getAgent(agentId: string | number) {
    return agnoRequest<AgnoAgent>({
      url: `${API_PATH}/${agentId}`,
      method: "get",
    });
  },
};

export default AgnoAgentAPI;

// TS 类型声明

export interface AgnoAgent {
  id: string;
  name?: string;
  description?: string;
  db_id?: string;
  model?: {
    id?: string;
    name?: string;
    provider?: string;
  };
  sessions?: Record<string, any>;
  knowledge?: Record<string, any>;
  memory?: Record<string, any>;
  system_message?: Record<string, any>;
  tools?: any[];
}
