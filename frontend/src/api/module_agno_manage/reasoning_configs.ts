import request from "@/utils/request";

const API_PATH = "/agno_manage/reasoning_configs";

const AgReasoningConfigAPI = {
  // 列表查询
  listAgReasoningConfig(query: AgReasoningConfigPageQuery) {
    return request<ApiResponse<PageResult<AgReasoningConfigTable[]>>>({
      url: `${API_PATH}/list`,
      method: "get",
      params: query,
    });
  },

  // 详情查询
  detailAgReasoningConfig(id: number) {
    return request<ApiResponse<AgReasoningConfigTable>>({
      url: `${API_PATH}/detail/${id}`,
      method: "get",
    });
  },

  // 新增
  createAgReasoningConfig(body: AgReasoningConfigForm) {
    return request<ApiResponse>({
      url: `${API_PATH}/create`,
      method: "post",
      data: body,
    });
  },

  // 修改（带主键）
  updateAgReasoningConfig(id: number, body: AgReasoningConfigForm) {
    return request<ApiResponse>({
      url: `${API_PATH}/update/${id}`,
      method: "put",
      data: body,
    });
  },

  // 删除（支持批量）
  deleteAgReasoningConfig(ids: number[]) {
    return request<ApiResponse>({
      url: `${API_PATH}/delete`,
      method: "delete",
      data: ids,
    });
  },

  // 批量启用/停用
  batchAgReasoningConfig(body: BatchType) {
    return request<ApiResponse>({
      url: `${API_PATH}/available/setting`,
      method: "patch",
      data: body,
    });
  },

  // 导出
  exportAgReasoningConfig(query: AgReasoningConfigPageQuery) {
    return request<Blob>({
      url: `${API_PATH}/export`,
      method: "post",
      data: query,
      responseType: "blob",
    });
  },

  // 下载导入模板
  downloadTemplateAgReasoningConfig() {
    return request<Blob>({
      url: `${API_PATH}/download/template`,
      method: "post",
      responseType: "blob",
    });
  },

  // 导入
  importAgReasoningConfig(body: FormData) {
    return request<ApiResponse>({
      url: `${API_PATH}/import`,
      method: "post",
      data: body,
      headers: { "Content-Type": "multipart/form-data" },
    });
  },
};

export default AgReasoningConfigAPI;

// ------------------------------
// TS 类型声明
// ------------------------------

// 列表查询参数
export interface AgReasoningConfigPageQuery extends PageQuery {
  name?: string;
  model_id?: string;
  min_steps?: string;
  max_steps?: string;
  use_json_mode?: string;
  tool_call_limit?: string;
  debug_mode?: string;
  status?: string;
  created_id?: number;
  updated_id?: number;
  created_time?: string[];
  updated_time?: string[];
}

// 列表展示项
export interface AgReasoningConfigTable extends BaseType {
  name?: string;
  model_id?: string;
  min_steps?: string;
  max_steps?: string;
  use_json_mode?: string;
  tool_call_limit?: string;
  debug_mode?: string;
  created_id?: string;
  updated_id?: string;
  created_by?: CommonType;
  updated_by?: CommonType;
}

// 新增/修改/详情表单参数
export interface AgReasoningConfigForm extends BaseFormType {
  name?: string;
  model_id?: string;
  min_steps?: string;
  max_steps?: string;
  use_json_mode?: string;
  tool_call_limit?: string;
  debug_mode?: string;
}
