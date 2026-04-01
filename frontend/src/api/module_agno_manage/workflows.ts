import request from "@/utils/request";

const API_PATH = "/agno_manage/workflows";

const AgWorkflowAPI = {
  // 列表查询
  listAgWorkflow(query: AgWorkflowPageQuery) {
    return request<ApiResponse<PageResult<AgWorkflowTable[]>>>({
      url: `${API_PATH}/list`,
      method: "get",
      params: query,
    });
  },

  // 详情查询
  detailAgWorkflow(id: number) {
    return request<ApiResponse<AgWorkflowTable>>({
      url: `${API_PATH}/detail/${id}`,
      method: "get",
    });
  },

  // 新增
  createAgWorkflow(body: AgWorkflowForm) {
    return request<ApiResponse>({
      url: `${API_PATH}/create`,
      method: "post",
      data: body,
    });
  },

  // 修改（带主键）
  updateAgWorkflow(id: number, body: AgWorkflowForm) {
    return request<ApiResponse>({
      url: `${API_PATH}/update/${id}`,
      method: "put",
      data: body,
    });
  },

  // 删除（支持批量）
  deleteAgWorkflow(ids: number[]) {
    return request<ApiResponse>({
      url: `${API_PATH}/delete`,
      method: "delete",
      data: ids,
    });
  },

  // 批量启用/停用
  batchAgWorkflow(body: BatchType) {
    return request<ApiResponse>({
      url: `${API_PATH}/available/setting`,
      method: "patch",
      data: body,
    });
  },

  // 导出
  exportAgWorkflow(query: AgWorkflowPageQuery) {
    return request<Blob>({
      url: `${API_PATH}/export`,
      method: "post",
      data: query,
      responseType: "blob",
    });
  },

  // 下载导入模板
  downloadTemplateAgWorkflow() {
    return request<Blob>({
      url: `${API_PATH}/download/template`,
      method: "post",
      responseType: "blob",
    });
  },

  // 导入
  importAgWorkflow(body: FormData) {
    return request<ApiResponse>({
      url: `${API_PATH}/import`,
      method: "post",
      data: body,
      headers: { "Content-Type": "multipart/form-data" },
    });
  },
};

export default AgWorkflowAPI;

// ------------------------------
// TS 类型声明
// ------------------------------

// 列表查询参数
export interface AgWorkflowPageQuery extends PageQuery {
  name?: string;
  stream?: string;
  stream_events?: string;
  stream_executor_events?: string;
  store_events?: string;
  store_executor_outputs?: string;
  add_workflow_history_to_steps?: string;
  num_history_runs?: string;
  add_session_state_to_context?: string;
  debug_mode?: string;
  input_schema?: string;
  metadata?: string;
  status?: string;
  created_id?: number;
  updated_id?: number;
  created_time?: string[];
  updated_time?: string[];
}

// 列表展示项
export interface AgWorkflowTable extends BaseType {
  name?: string;
  stream?: string;
  stream_events?: string;
  stream_executor_events?: string;
  store_events?: string;
  store_executor_outputs?: string;
  add_workflow_history_to_steps?: string;
  num_history_runs?: string;
  add_session_state_to_context?: string;
  debug_mode?: string;
  input_schema?: string;
  metadata?: string;
  created_id?: string;
  updated_id?: string;
  created_by?: CommonType;
  updated_by?: CommonType;
}

// 新增/修改/详情表单参数
export interface AgWorkflowForm extends BaseFormType {
  name?: string;
  stream?: string;
  stream_events?: string;
  stream_executor_events?: string;
  store_events?: string;
  store_executor_outputs?: string;
  add_workflow_history_to_steps?: string;
  num_history_runs?: string;
  add_session_state_to_context?: string;
  debug_mode?: string;
  input_schema?: string;
  metadata?: string;
}
