import request from "@/utils/request";

const API_PATH = "/agno_manage/workflow_nodes";

const AgWorkflowNodeAPI = {
  // 列表查询
  listAgWorkflowNode(query: AgWorkflowNodePageQuery) {
    return request<ApiResponse<PageResult<AgWorkflowNodeTable[]>>>({
      url: `${API_PATH}/list`,
      method: "get",
      params: query,
    });
  },

  // 详情查询
  detailAgWorkflowNode(id: number) {
    return request<ApiResponse<AgWorkflowNodeTable>>({
      url: `${API_PATH}/detail/${id}`,
      method: "get",
    });
  },

  // 新增
  createAgWorkflowNode(body: AgWorkflowNodeForm) {
    return request<ApiResponse>({
      url: `${API_PATH}/create`,
      method: "post",
      data: body,
    });
  },

  // 修改（带主键）
  updateAgWorkflowNode(id: number, body: AgWorkflowNodeForm) {
    return request<ApiResponse>({
      url: `${API_PATH}/update/${id}`,
      method: "put",
      data: body,
    });
  },

  // 删除（支持批量）
  deleteAgWorkflowNode(ids: number[]) {
    return request<ApiResponse>({
      url: `${API_PATH}/delete`,
      method: "delete",
      data: ids,
    });
  },

  // 批量启用/停用
  batchAgWorkflowNode(body: BatchType) {
    return request<ApiResponse>({
      url: `${API_PATH}/available/setting`,
      method: "patch",
      data: body,
    });
  },

  // 导出
  exportAgWorkflowNode(query: AgWorkflowNodePageQuery) {
    return request<Blob>({
      url: `${API_PATH}/export`,
      method: "post",
      data: query,
      responseType: "blob",
    });
  },

  // 下载导入模板
  downloadTemplateAgWorkflowNode() {
    return request<Blob>({
      url: `${API_PATH}/download/template`,
      method: "post",
      responseType: "blob",
    });
  },

  // 导入
  importAgWorkflowNode(body: FormData) {
    return request<ApiResponse>({
      url: `${API_PATH}/import`,
      method: "post",
      data: body,
      headers: { "Content-Type": "multipart/form-data" },
    });
  },
};

export default AgWorkflowNodeAPI;

// ------------------------------
// TS 类型声明
// ------------------------------

// 列表查询参数
export interface AgWorkflowNodePageQuery extends PageQuery {
  workflow_id?: string;
  parent_node_id?: string;
  node_type?: string;
  name?: string;
  executor_type?: string;
  agent_id?: string;
  team_id?: string;
  status?: string;
  created_id?: number;
  updated_id?: number;
  created_time?: string[];
  updated_time?: string[];
}

// 列表展示项
export interface AgWorkflowNodeTable extends BaseType {
  workflow_id?: number | null;
  parent_node_id?: number | null;
  node_order?: number | null;
  node_type?: string;
  name?: string;
  executor_type?: string;
  agent_id?: number | null;
  team_id?: number | null;
  executor_module?: string;
  add_workflow_history?: boolean | null;
  num_history_runs?: number | null;
  strict_input_validation?: boolean | null;
  max_retries?: number | null;
  skip_on_failure?: boolean | null;
  evaluator_type?: string;
  evaluator_value?: string;
  branch?: string;
  max_iterations?: number | null;
  end_condition_type?: string;
  end_condition_value?: string;
  forward_iteration_output?: boolean | null;
  selector_type?: string;
  selector_value?: string;
  allow_multiple_selections?: boolean | null;
  requires_confirmation?: boolean | null;
  confirmation_message?: string;
  requires_user_input?: boolean | null;
  user_input_message?: string;
  user_input_schema?: Record<string, any> | null;
  on_reject?: string;
  on_error?: string;
  created_id?: string;
  updated_id?: string;
  created_by?: CommonType;
  updated_by?: CommonType;
}

// 新增/修改/详情表单参数
export interface AgWorkflowNodeForm extends BaseFormType {
  workflow_id?: number | null;
  parent_node_id?: number | null;
  node_order?: number | null;
  node_type?: string;
  name?: string;
  executor_type?: string;
  agent_id?: number | null;
  team_id?: number | null;
  executor_module?: string;
  add_workflow_history?: boolean | null;
  num_history_runs?: number | null;
  strict_input_validation?: boolean | null;
  max_retries?: number | null;
  skip_on_failure?: boolean | null;
  evaluator_type?: string;
  evaluator_value?: string;
  branch?: string;
  max_iterations?: number | null;
  end_condition_type?: string;
  end_condition_value?: string;
  forward_iteration_output?: boolean | null;
  selector_type?: string;
  selector_value?: string;
  allow_multiple_selections?: boolean | null;
  requires_confirmation?: boolean | null;
  confirmation_message?: string;
  requires_user_input?: boolean | null;
  user_input_message?: string;
  user_input_schema?: Record<string, any>;
  on_reject?: string;
  on_error?: string;
}
