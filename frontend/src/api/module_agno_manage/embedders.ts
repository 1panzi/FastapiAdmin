import request from "@/utils/request";

const API_PATH = "/agno_manage/embedders";

const EmbedderAPI = {
  // 列表查询
  listEmbedder(query: EmbedderPageQuery) {
    return request<ApiResponse<PageResult<EmbedderTable[]>>>({
      url: `${API_PATH}/list`,
      method: "get",
      params: query,
    });
  },

  // 详情查询
  detailEmbedder(id: number) {
    return request<ApiResponse<EmbedderTable>>({
      url: `${API_PATH}/detail/${id}`,
      method: "get",
    });
  },

  // 新增
  createEmbedder(body: EmbedderForm) {
    return request<ApiResponse>({
      url: `${API_PATH}/create`,
      method: "post",
      data: body,
    });
  },

  // 修改（带主键）
  updateEmbedder(id: number, body: EmbedderForm) {
    return request<ApiResponse>({
      url: `${API_PATH}/update/${id}`,
      method: "put",
      data: body,
    });
  },

  // 删除（支持批量）
  deleteEmbedder(ids: number[]) {
    return request<ApiResponse>({
      url: `${API_PATH}/delete`,
      method: "delete",
      data: ids,
    });
  },

  // 批量启用/停用
  batchEmbedder(body: BatchType) {
    return request<ApiResponse>({
      url: `${API_PATH}/available/setting`,
      method: "patch",
      data: body,
    });
  },

  // 导出
  exportEmbedder(query: EmbedderPageQuery) {
    return request<Blob>({
      url: `${API_PATH}/export`,
      method: "post",
      data: query,
      responseType: "blob",
    });
  },

  // 下载导入模板
  downloadTemplateEmbedder() {
    return request<Blob>({
      url: `${API_PATH}/download/template`,
      method: "post",
      responseType: "blob",
    });
  },

  // 导入
  importEmbedder(body: FormData) {
    return request<ApiResponse>({
      url: `${API_PATH}/import`,
      method: "post",
      data: body,
      headers: { "Content-Type": "multipart/form-data" },
    });
  },
};

export default EmbedderAPI;

// ------------------------------
// TS 类型声明
// ------------------------------

// 列表查询参数
export interface EmbedderPageQuery extends PageQuery {
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
export interface EmbedderTable extends BaseType {
  name?: string;
  provider?: string;
  model_id?: string;
  api_key?: string;
  base_url?: string;
  dimensions?: string;
  config?: string;
  created_id?: string;
  updated_id?: string;
  created_by?: CommonType;
  updated_by?: CommonType;
}

// 新增/修改/详情表单参数
export interface EmbedderForm extends BaseFormType {
  name?: string;
  provider?: string;
  model_id?: string;
  api_key?: string;
  base_url?: string;
  dimensions?: string;
  config?: string;
}
