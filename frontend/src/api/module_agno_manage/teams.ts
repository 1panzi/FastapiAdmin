import request from "@/utils/request";

const API_PATH = "/agno_manage/teams";

const AgTeamAPI = {
  // 列表查询
  listAgTeam(query: AgTeamPageQuery) {
    return request<ApiResponse<PageResult<AgTeamTable[]>>>({
      url: `${API_PATH}/list`,
      method: "get",
      params: query,
    });
  },

  // 详情查询
  detailAgTeam(id: number) {
    return request<ApiResponse<AgTeamTable>>({
      url: `${API_PATH}/detail/${id}`,
      method: "get",
    });
  },

  // 新增
  createAgTeam(body: AgTeamForm) {
    return request<ApiResponse>({
      url: `${API_PATH}/create`,
      method: "post",
      data: body,
    });
  },

  // 修改（带主键）
  updateAgTeam(id: number, body: AgTeamForm) {
    return request<ApiResponse>({
      url: `${API_PATH}/update/${id}`,
      method: "put",
      data: body,
    });
  },

  // 删除（支持批量）
  deleteAgTeam(ids: number[]) {
    return request<ApiResponse>({
      url: `${API_PATH}/delete`,
      method: "delete",
      data: ids,
    });
  },

  // 批量启用/停用
  batchAgTeam(body: BatchType) {
    return request<ApiResponse>({
      url: `${API_PATH}/available/setting`,
      method: "patch",
      data: body,
    });
  },

  // 导出
  exportAgTeam(query: AgTeamPageQuery) {
    return request<Blob>({
      url: `${API_PATH}/export`,
      method: "post",
      data: query,
      responseType: "blob",
    });
  },

  // 下载导入模板
  downloadTemplateAgTeam() {
    return request<Blob>({
      url: `${API_PATH}/download/template`,
      method: "post",
      responseType: "blob",
    });
  },

  // 导入
  importAgTeam(body: FormData) {
    return request<ApiResponse>({
      url: `${API_PATH}/import`,
      method: "post",
      data: body,
      headers: { "Content-Type": "multipart/form-data" },
    });
  },
};

export default AgTeamAPI;

// ------------------------------
// TS 类型声明
// ------------------------------

// 列表查询参数
export interface AgTeamPageQuery extends PageQuery {
  name?: string;
  model_id?: string;
  memory_manager_id?: string;
  mode?: string;
  respond_directly?: string;
  delegate_to_all_members?: string;
  determine_input_for_members?: string;
  max_iterations?: string;
  instructions?: string;
  expected_output?: string;
  markdown?: string;
  add_team_history_to_members?: string;
  num_team_history_runs?: string;
  share_member_interactions?: string;
  add_member_tools_to_context?: string;
  read_chat_history?: string;
  search_past_sessions?: string;
  num_past_sessions_to_search?: string;
  search_knowledge?: string;
  update_knowledge?: string;
  enable_agentic_knowledge_filters?: string;
  enable_agentic_state?: string;
  enable_agentic_memory?: string;
  update_memory_on_run?: string;
  enable_session_summaries?: string;
  add_session_summary_to_context?: string;
  tool_call_limit?: string;
  stream?: string;
  stream_events?: string;
  debug_mode?: string;
  status?: string;
  created_id?: number;
  updated_id?: number;
  created_time?: string[];
  updated_time?: string[];
}

// 列表展示项
export interface AgTeamTable extends BaseType {
  name?: string;
  model_id?: string;
  memory_manager_id?: string;
  mode?: string;
  respond_directly?: boolean | null;
  delegate_to_all_members?: boolean | null;
  determine_input_for_members?: boolean | null;
  max_iterations?: number | null;
  instructions?: string;
  expected_output?: string;
  markdown?: boolean | null;
  add_team_history_to_members?: boolean | null;
  num_team_history_runs?: number | null;
  share_member_interactions?: boolean | null;
  add_member_tools_to_context?: boolean | null;
  read_chat_history?: boolean | null;
  search_past_sessions?: boolean | null;
  num_past_sessions_to_search?: number | null;
  search_knowledge?: boolean | null;
  update_knowledge?: boolean | null;
  enable_agentic_knowledge_filters?: boolean | null;
  enable_agentic_state?: boolean | null;
  enable_agentic_memory?: boolean | null;
  update_memory_on_run?: boolean | null;
  enable_session_summaries?: boolean | null;
  add_session_summary_to_context?: boolean | null;
  tool_call_limit?: number | null;
  stream?: boolean | null;
  stream_events?: boolean | null;
  debug_mode?: boolean | null;
  metadata_config?: Record<string, any> | null;
  created_id?: string;
  updated_id?: string;
  created_by?: CommonType;
  updated_by?: CommonType;
}

// 新增/修改/详情表单参数
export interface AgTeamForm extends BaseFormType {
  name?: string;
  model_id?: string;
  memory_manager_id?: string;
  mode?: string;
  respond_directly?: boolean | null;
  delegate_to_all_members?: boolean | null;
  determine_input_for_members?: boolean | null;
  max_iterations?: number | null;
  instructions?: string;
  expected_output?: string;
  markdown?: boolean | null;
  add_team_history_to_members?: boolean | null;
  num_team_history_runs?: number | null;
  share_member_interactions?: boolean | null;
  add_member_tools_to_context?: boolean | null;
  read_chat_history?: boolean | null;
  search_past_sessions?: boolean | null;
  num_past_sessions_to_search?: number | null;
  search_knowledge?: boolean | null;
  update_knowledge?: boolean | null;
  enable_agentic_knowledge_filters?: boolean | null;
  enable_agentic_state?: boolean | null;
  enable_agentic_memory?: boolean | null;
  update_memory_on_run?: boolean | null;
  enable_session_summaries?: boolean | null;
  add_session_summary_to_context?: boolean | null;
  tool_call_limit?: number | null;
  stream?: boolean | null;
  stream_events?: boolean | null;
  debug_mode?: boolean | null;
  metadata_config?: Record<string, any>;
}
