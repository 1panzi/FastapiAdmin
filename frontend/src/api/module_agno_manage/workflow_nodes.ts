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
  node_order?: string;
  node_type?: string;
  name?: string;
  executor_type?: string;
  agent_id?: string;
  team_id?: string;
  executor_module?: string;
  add_workflow_history?: string;
  num_history_runs?: string;
  strict_input_validation?: string;
  max_retries?: string;
  skip_on_failure?: string;
  evaluator_type?: string;
  evaluator_value?: string;
  branch?: string;
  max_iterations?: string;
  end_condition_type?: string;
  end_condition_value?: string;
  forward_iteration_output?: string;
  selector_type?: string;
  selector_value?: string;
  allow_multiple_selections?: string;
  requires_confirmation?: string;
  confirmation_message?: string;
  requires_user_input?: string;
  user_input_message?: string;
  user_input_schema?: string;
  on_reject?: string;
  on_error?: string;
  status?: string;
  created_id?: number;
  updated_id?: number;
  created_time?: string[];
  updated_time?: string[];
}

// 列表展示项
export interface AgWorkflowNodeTable extends BaseType {
  workflow_id?: string;
  parent_node_id?: string;
  node_order?: string;
  node_type?: string;
  name?: string;
  executor_type?: string;
  agent_id?: string;
  team_id?: string;
  executor_module?: string;
  add_workflow_history?: string;
  num_history_runs?: string;
  strict_input_validation?: string;
  max_retries?: string;
  skip_on_failure?: string;
  evaluator_type?: string;
  evaluator_value?: string;
  branch?: string;
  max_iterations?: string;
  end_condition_type?: string;
  end_condition_value?: string;
  forward_iteration_output?: string;
  selector_type?: string;
  selector_value?: string;
  allow_multiple_selections?: string;
  requires_confirmation?: string;
  confirmation_message?: string;
  requires_user_input?: string;
  user_input_message?: string;
  user_input_schema?: string;
  on_reject?: string;
  on_error?: string;
  created_id?: string;
  updated_id?: string;
  created_by?: CommonType;
  updated_by?: CommonType;
}

// 新增/修改/详情表单参数
export interface AgWorkflowNodeForm extends BaseFormType {
  workflow_id?: string;
  parent_node_id?: string;
  node_order?: string;
  node_type?: string;
  name?: string;
  executor_type?: string;
  agent_id?: string;
  team_id?: string;
  executor_module?: string;
  add_workflow_history?: string;
  num_history_runs?: string;
  strict_input_validation?: string;
  max_retries?: string;
  skip_on_failure?: string;
  evaluator_type?: string;
  evaluator_value?: string;
  branch?: string;
  max_iterations?: string;
  end_condition_type?: string;
  end_condition_value?: string;
  forward_iteration_output?: string;
  selector_type?: string;
  selector_value?: string;
  allow_multiple_selections?: string;
  requires_confirmation?: string;
  confirmation_message?: string;
  requires_user_input?: string;
  user_input_message?: string;
  user_input_schema?: string;
  on_reject?: string;
  on_error?: string;
}
