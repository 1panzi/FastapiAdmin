import request from "@/utils/request";

const API_PATH = "/agno_manage/embedders";

const AgEmbedderAPI = {
  // 列表查询
  listAgEmbedder(query: AgEmbedderPageQuery) {
    return request<ApiResponse<PageResult<AgEmbedderTable[]>>>({
      url: `${API_PATH}/list`,
      method: "get",
      params: query,
    });
  },

  // 详情查询
  detailAgEmbedder(id: number) {
    return request<ApiResponse<AgEmbedderTable>>({
      url: `${API_PATH}/detail/${id}`,
      method: "get",
    });
  },

  // 新增
  createAgEmbedder(body: AgEmbedderForm) {
    return request<ApiResponse>({
      url: `${API_PATH}/create`,
      method: "post",
      data: body,
    });
  },

  // 修改（带主键）
  updateAgEmbedder(id: number, body: AgEmbedderForm) {
    return request<ApiResponse>({
      url: `${API_PATH}/update/${id}`,
      method: "put",
      data: body,
    });
  },

  // 删除（支持批量）
  deleteAgEmbedder(ids: number[]) {
    return request<ApiResponse>({
      url: `${API_PATH}/delete`,
      method: "delete",
      data: ids,
    });
  },

  // 批量启用/停用
  batchAgEmbedder(body: BatchType) {
    return request<ApiResponse>({
      url: `${API_PATH}/available/setting`,
      method: "patch",
      data: body,
    });
  },

  // 导出
  exportAgEmbedder(query: AgEmbedderPageQuery) {
    return request<Blob>({
      url: `${API_PATH}/export`,
      method: "post",
      data: query,
      responseType: "blob",
    });
  },

  // 下载导入模板
  downloadTemplateAgEmbedder() {
    return request<Blob>({
      url: `${API_PATH}/download/template`,
      method: "post",
      responseType: "blob",
    });
  },

  // 导入
  importAgEmbedder(body: FormData) {
    return request<ApiResponse>({
      url: `${API_PATH}/import`,
      method: "post",
      data: body,
      headers: { "Content-Type": "multipart/form-data" },
    });
  },
};

export default AgEmbedderAPI;

// ------------------------------
// TS 类型声明
// ------------------------------

// 列表查询参数
export interface AgEmbedderPageQuery extends PageQuery {
  name?: string;
  provider?: string;
  model_id?: string;
  api_key?: string;
  base_url?: string;
  dimensions?: string;
  config?: string;
  status?: string;
  created_id?: number;
  updated_id?: number;
  created_time?: string[];
  updated_time?: string[];
}

// 列表展示项
export interface AgEmbedderTable extends BaseType {
  name?: string;
  provider?: string;
  model_id?: string;
  api_key?: string;
  base_url?: string;
  dimensions?: string;
  config?: Record<string, any>;
  created_id?: string;
  updated_id?: string;
  created_by?: CommonType;
  updated_by?: CommonType;
}

// 新增/修改/详情表单参数
export interface AgEmbedderForm extends BaseFormType {
  name?: string;
  provider?: string;
  model_id?: string;
  api_key?: string;
  base_url?: string;
  dimensions?: string;
  config?: Record<string, any>;
}
