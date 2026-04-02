import request from "@/utils/request";

const API_PATH = "/agno_manage/models";

const AgModelAPI = {
  // 列表查询
  listAgModel(query: AgModelPageQuery) {
    return request<ApiResponse<PageResult<AgModelTable[]>>>({
      url: `${API_PATH}/list`,
      method: "get",
      params: query,
    });
  },

  // 详情查询
  detailAgModel(id: number) {
    return request<ApiResponse<AgModelTable>>({
      url: `${API_PATH}/detail/${id}`,
      method: "get",
    });
  },

  // 新增
  createAgModel(body: AgModelForm) {
    return request<ApiResponse>({
      url: `${API_PATH}/create`,
      method: "post",
      data: body,
    });
  },

  // 修改（带主键）
  updateAgModel(id: number, body: AgModelForm) {
    return request<ApiResponse>({
      url: `${API_PATH}/update/${id}`,
      method: "put",
      data: body,
    });
  },

  // 删除（支持批量）
  deleteAgModel(ids: number[]) {
    return request<ApiResponse>({
      url: `${API_PATH}/delete`,
      method: "delete",
      data: ids,
    });
  },

  // 批量启用/停用
  batchAgModel(body: BatchType) {
    return request<ApiResponse>({
      url: `${API_PATH}/available/setting`,
      method: "patch",
      data: body,
    });
  },

  // 导出
  exportAgModel(query: AgModelPageQuery) {
    return request<Blob>({
      url: `${API_PATH}/export`,
      method: "post",
      data: query,
      responseType: "blob",
    });
  },

  // 下载导入模板
  downloadTemplateAgModel() {
    return request<Blob>({
      url: `${API_PATH}/download/template`,
      method: "post",
      responseType: "blob",
    });
  },

  // 导入
  importAgModel(body: FormData) {
    return request<ApiResponse>({
      url: `${API_PATH}/import`,
      method: "post",
      data: body,
      headers: { "Content-Type": "multipart/form-data" },
    });
  },
};

export default AgModelAPI;

// ------------------------------
// TS 类型声明
// ------------------------------

// 列表查询参数
export interface AgModelPageQuery extends PageQuery {
  name?: string;
  model_id?: string;
  provider?: string;
  api_key?: string;
  base_url?: string;
  config?: Record<string, any>;
  status?: string;
  created_id?: number;
  updated_id?: number;
  created_time?: string[];
  updated_time?: string[];
}

// 列表展示项
export interface AgModelTable extends BaseType {
  name?: string;
  model_id?: string;
  provider?: string;
  api_key?: string;
  base_url?: string;
  config?: Record<string, any>;
  created_id?: string;
  updated_id?: string;
  created_by?: CommonType;
  updated_by?: CommonType;
}

// 新增/修改/详情表单参数
export interface AgModelForm extends BaseFormType {
  name?: string;
  model_id?: string;
  provider?: string;
  api_key?: string;
  base_url?: string;
  config?: Record<string, any>;
}
