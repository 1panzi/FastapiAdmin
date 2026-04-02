import request from "@/utils/request";

const API_PATH = "/agno_manage/agents";

const AgAgentAPI = {
  // 列表查询
  listAgAgent(query: AgAgentPageQuery) {
    return request<ApiResponse<PageResult<AgAgentTable[]>>>({
      url: `${API_PATH}/list`,
      method: "get",
      params: query,
    });
  },

  // 详情查询
  detailAgAgent(id: number) {
    return request<ApiResponse<AgAgentTable>>({
      url: `${API_PATH}/detail/${id}`,
      method: "get",
    });
  },

  // 新增
  createAgAgent(body: AgAgentForm) {
    return request<ApiResponse>({
      url: `${API_PATH}/create`,
      method: "post",
      data: body,
    });
  },

  // 修改（带主键）
  updateAgAgent(id: number, body: AgAgentForm) {
    return request<ApiResponse>({
      url: `${API_PATH}/update/${id}`,
      method: "put",
      data: body,
    });
  },

  // 删除（支持批量）
  deleteAgAgent(ids: number[]) {
    return request<ApiResponse>({
      url: `${API_PATH}/delete`,
      method: "delete",
      data: ids,
    });
  },

  // 批量启用/停用
  batchAgAgent(body: BatchType) {
    return request<ApiResponse>({
      url: `${API_PATH}/available/setting`,
      method: "patch",
      data: body,
    });
  },

  // 导出
  exportAgAgent(query: AgAgentPageQuery) {
    return request<Blob>({
      url: `${API_PATH}/export`,
      method: "post",
      data: query,
      responseType: "blob",
    });
  },

  // 下载导入模板
  downloadTemplateAgAgent() {
    return request<Blob>({
      url: `${API_PATH}/download/template`,
      method: "post",
      responseType: "blob",
    });
  },

  // 导入
  importAgAgent(body: FormData) {
    return request<ApiResponse>({
      url: `${API_PATH}/import`,
      method: "post",
      data: body,
      headers: { "Content-Type": "multipart/form-data" },
    });
  },
};

export default AgAgentAPI;

// ------------------------------
// TS 类型声明
// ------------------------------

// 列表查询参数
export interface AgAgentPageQuery extends PageQuery {
  name?: string;
  model_id?: string;
  reasoning_model_id?: string;
  output_model_id?: string;
  parser_model_id?: string;
  memory_manager_id?: string;
  learning_config_id?: string;
  reasoning_config_id?: string;
  compression_config_id?: string;
  session_summary_config_id?: string;
  culture_config_id?: string;
  instructions?: string;
  expected_output?: string;
  additional_context?: string;
  reasoning?: string;
  reasoning_min_steps?: string;
  reasoning_max_steps?: string;
  learning?: string;
  search_knowledge?: string;
  update_knowledge?: string;
  add_knowledge_to_context?: string;
  enable_agentic_knowledge_filters?: string;
  enable_agentic_state?: string;
  enable_agentic_memory?: string;
  update_memory_on_run?: string;
  add_memories_to_context?: string;
  add_history_to_context?: string;
  num_history_runs?: string;
  num_history_messages?: string;
  search_past_sessions?: string;
  num_past_sessions_to_search?: string;
  enable_session_summaries?: string;
  add_session_summary_to_context?: string;
  tool_call_limit?: string;
  tool_choice?: string;
  output_schema?: string;
  input_schema?: string;
  use_json_mode?: string;
  structured_outputs?: string;
  parse_response?: string;
  retries?: string;
  delay_between_retries?: string;
  exponential_backoff?: string;
  add_datetime_to_context?: string;
  add_name_to_context?: string;
  compress_tool_results?: string;
  stream?: string;
  stream_events?: string;
  store_events?: string;
  markdown?: string;
  followups?: string;
  num_followups?: string;
  debug_mode?: string;
  debug_level?: string;
  a2a_enabled?: string;
  is_remote?: string;
  remote_url?: string;
  remote_agent_id?: string;
  metadata?: string;
  status?: string;
  created_id?: number;
  updated_id?: number;
  created_time?: string[];
  updated_time?: string[];
}

// 列表展示项
export interface AgAgentTable extends BaseType {
  name?: string;
  model_id?: string;
  reasoning_model_id?: string;
  output_model_id?: string;
  parser_model_id?: string;
  memory_manager_id?: string;
  learning_config_id?: string;
  reasoning_config_id?: string;
  compression_config_id?: string;
  session_summary_config_id?: string;
  culture_config_id?: string;
  instructions?: string;
  expected_output?: string;
  additional_context?: string;
  reasoning?: boolean | null;
  reasoning_min_steps?: string;
  reasoning_max_steps?: string;
  learning?: boolean | null;
  search_knowledge?: boolean | null;
  update_knowledge?: boolean | null;
  add_knowledge_to_context?: boolean | null;
  enable_agentic_knowledge_filters?: boolean | null;
  enable_agentic_state?: boolean | null;
  enable_agentic_memory?: boolean | null;
  update_memory_on_run?: boolean | null;
  add_memories_to_context?: boolean | null;
  add_history_to_context?: boolean | null;
  num_history_runs?: string;
  num_history_messages?: string;
  search_past_sessions?: boolean | null;
  num_past_sessions_to_search?: string;
  enable_session_summaries?: boolean | null;
  add_session_summary_to_context?: boolean | null;
  tool_call_limit?: string;
  tool_choice?: string;
  output_schema?: Record<string, any> | null;
  input_schema?: Record<string, any> | null;
  use_json_mode?: boolean | null;
  structured_outputs?: boolean | null;
  parse_response?: boolean | null;
  retries?: string;
  delay_between_retries?: string;
  exponential_backoff?: boolean | null;
  add_datetime_to_context?: boolean | null;
  add_name_to_context?: boolean | null;
  compress_tool_results?: boolean | null;
  stream?: boolean | null;
  stream_events?: boolean | null;
  store_events?: boolean | null;
  markdown?: boolean | null;
  followups?: boolean | null;
  num_followups?: string;
  debug_mode?: boolean | null;
  debug_level?: string;
  a2a_enabled?: boolean | null;
  is_remote?: boolean | null;
  remote_url?: string;
  remote_agent_id?: string;
  metadata?: Record<string, any> | null;
  created_id?: string;
  updated_id?: string;
  created_by?: CommonType;
  updated_by?: CommonType;
}

// 新增/修改/详情表单参数
export interface AgAgentForm extends BaseFormType {
  name?: string;
  model_id?: string;
  reasoning_model_id?: string;
  output_model_id?: string;
  parser_model_id?: string;
  memory_manager_id?: string;
  learning_config_id?: string;
  reasoning_config_id?: string;
  compression_config_id?: string;
  session_summary_config_id?: string;
  culture_config_id?: string;
  instructions?: string;
  expected_output?: string;
  additional_context?: string;
  reasoning?: boolean | null;
  reasoning_min_steps?: string;
  reasoning_max_steps?: string;
  learning?: boolean | null;
  search_knowledge?: boolean | null;
  update_knowledge?: boolean | null;
  add_knowledge_to_context?: boolean | null;
  enable_agentic_knowledge_filters?: boolean | null;
  enable_agentic_state?: boolean | null;
  enable_agentic_memory?: boolean | null;
  update_memory_on_run?: boolean | null;
  add_memories_to_context?: boolean | null;
  add_history_to_context?: boolean | null;
  num_history_runs?: string;
  num_history_messages?: string;
  search_past_sessions?: boolean | null;
  num_past_sessions_to_search?: string;
  enable_session_summaries?: boolean | null;
  add_session_summary_to_context?: boolean | null;
  tool_call_limit?: string;
  tool_choice?: string;
  output_schema?: Record<string, any>;
  input_schema?: Record<string, any>;
  use_json_mode?: boolean | null;
  structured_outputs?: boolean | null;
  parse_response?: boolean | null;
  retries?: string;
  delay_between_retries?: string;
  exponential_backoff?: boolean | null;
  add_datetime_to_context?: boolean | null;
  add_name_to_context?: boolean | null;
  compress_tool_results?: boolean | null;
  stream?: boolean | null;
  stream_events?: boolean | null;
  store_events?: boolean | null;
  markdown?: boolean | null;
  followups?: boolean | null;
  num_followups?: string;
  debug_mode?: boolean | null;
  debug_level?: string;
  a2a_enabled?: boolean | null;
  is_remote?: boolean | null;
  remote_url?: string;
  remote_agent_id?: string;
  metadata?: Record<string, any>;
}
