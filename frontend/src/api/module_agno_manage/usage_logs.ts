import request from "@/utils/request";

const API_PATH = "/agno_manage/usage_logs";

const AgUsageLogAPI = {
  // 列表查询
  listAgUsageLog(query: AgUsageLogPageQuery) {
    return request<ApiResponse<PageResult<AgUsageLogTable[]>>>({
      url: `${API_PATH}/list`,
      method: "get",
      params: query,
    });
  },

  // 详情查询
  detailAgUsageLog(id: number) {
    return request<ApiResponse<AgUsageLogTable>>({
      url: `${API_PATH}/detail/${id}`,
      method: "get",
    });
  },

  // 新增
  createAgUsageLog(body: AgUsageLogForm) {
    return request<ApiResponse>({
      url: `${API_PATH}/create`,
      method: "post",
      data: body,
    });
  },

  // 修改（带主键）
  updateAgUsageLog(id: number, body: AgUsageLogForm) {
    return request<ApiResponse>({
      url: `${API_PATH}/update/${id}`,
      method: "put",
      data: body,
    });
  },

  // 删除（支持批量）
  deleteAgUsageLog(ids: number[]) {
    return request<ApiResponse>({
      url: `${API_PATH}/delete`,
      method: "delete",
      data: ids,
    });
  },

  // 批量启用/停用
  batchAgUsageLog(body: BatchType) {
    return request<ApiResponse>({
      url: `${API_PATH}/available/setting`,
      method: "patch",
      data: body,
    });
  },

  // 导出
  exportAgUsageLog(query: AgUsageLogPageQuery) {
    return request<Blob>({
      url: `${API_PATH}/export`,
      method: "post",
      data: query,
      responseType: "blob",
    });
  },

  // 下载导入模板
  downloadTemplateAgUsageLog() {
    return request<Blob>({
      url: `${API_PATH}/download/template`,
      method: "post",
      responseType: "blob",
    });
  },

  // 导入
  importAgUsageLog(body: FormData) {
    return request<ApiResponse>({
      url: `${API_PATH}/import`,
      method: "post",
      data: body,
      headers: { "Content-Type": "multipart/form-data" },
    });
  },
};

export default AgUsageLogAPI;

// ------------------------------
// TS 类型声明
// ------------------------------

// 列表查询参数
export interface AgUsageLogPageQuery extends PageQuery {
  agent_id?: string;
  user_id?: string;
  session_id?: string;
  model_id?: string;
  input_tokens?: string;
  output_tokens?: string;
  cost_usd?: string;
  latency_ms?: string;
  created_time?: string[];
  updated_time?: string[];
}

// 列表展示项
export interface AgUsageLogTable extends BaseType {
  agent_id?: string;
  user_id?: string;
  session_id?: string;
  model_id?: string;
  input_tokens?: string;
  output_tokens?: string;
  cost_usd?: string;
  latency_ms?: string;
  created_by?: CommonType;
  updated_by?: CommonType;
}

// 新增/修改/详情表单参数
export interface AgUsageLogForm extends BaseFormType {
  agent_id?: string;
  user_id?: string;
  session_id?: string;
  model_id?: string;
  input_tokens?: string;
  output_tokens?: string;
  cost_usd?: string;
  latency_ms?: string;
}
