import request from "@/utils/request";

const API_PATH = "/agno_manage/compression_configs";

const AgCompressionConfigAPI = {
  // 列表查询
  listAgCompressionConfig(query: AgCompressionConfigPageQuery) {
    return request<ApiResponse<PageResult<AgCompressionConfigTable[]>>>({
      url: `${API_PATH}/list`,
      method: "get",
      params: query,
    });
  },

  // 详情查询
  detailAgCompressionConfig(id: number) {
    return request<ApiResponse<AgCompressionConfigTable>>({
      url: `${API_PATH}/detail/${id}`,
      method: "get",
    });
  },

  // 新增
  createAgCompressionConfig(body: AgCompressionConfigForm) {
    return request<ApiResponse>({
      url: `${API_PATH}/create`,
      method: "post",
      data: body,
    });
  },

  // 修改（带主键）
  updateAgCompressionConfig(id: number, body: AgCompressionConfigForm) {
    return request<ApiResponse>({
      url: `${API_PATH}/update/${id}`,
      method: "put",
      data: body,
    });
  },

  // 删除（支持批量）
  deleteAgCompressionConfig(ids: number[]) {
    return request<ApiResponse>({
      url: `${API_PATH}/delete`,
      method: "delete",
      data: ids,
    });
  },

  // 批量启用/停用
  batchAgCompressionConfig(body: BatchType) {
    return request<ApiResponse>({
      url: `${API_PATH}/available/setting`,
      method: "patch",
      data: body,
    });
  },

  // 导出
  exportAgCompressionConfig(query: AgCompressionConfigPageQuery) {
    return request<Blob>({
      url: `${API_PATH}/export`,
      method: "post",
      data: query,
      responseType: "blob",
    });
  },

  // 下载导入模板
  downloadTemplateAgCompressionConfig() {
    return request<Blob>({
      url: `${API_PATH}/download/template`,
      method: "post",
      responseType: "blob",
    });
  },

  // 导入
  importAgCompressionConfig(body: FormData) {
    return request<ApiResponse>({
      url: `${API_PATH}/import`,
      method: "post",
      data: body,
      headers: { "Content-Type": "multipart/form-data" },
    });
  },
};

export default AgCompressionConfigAPI;

// ------------------------------
// TS 类型声明
// ------------------------------

// 列表查询参数
export interface AgCompressionConfigPageQuery extends PageQuery {
  name?: string;
  model_id?: string;
  compress_tool_results_limit?: string;
  compress_token_limit?: string;
  compress_tool_call_instructions?: string;
  status?: string;
  created_id?: number;
  updated_id?: number;
  created_time?: string[];
  updated_time?: string[];
}

// 列表展示项
export interface AgCompressionConfigTable extends BaseType {
  name?: string;
  model_id?: string;
  compress_tool_results_limit?: string;
  compress_token_limit?: string;
  compress_tool_call_instructions?: string;
  created_id?: string;
  updated_id?: string;
  created_by?: CommonType;
  updated_by?: CommonType;
}

// 新增/修改/详情表单参数
export interface AgCompressionConfigForm extends BaseFormType {
  name?: string;
  model_id?: string;
  compress_tool_results_limit?: string;
  compress_token_limit?: string;
  compress_tool_call_instructions?: string;
}
