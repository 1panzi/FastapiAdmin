import request from "@/utils/request";

const API_PATH = "/agno_manage/models";

const ModelAPI = {
  // 列表查询
  listModel(query: ModelPageQuery) {
    return request<ApiResponse<PageResult<ModelTable[]>>>({
      url: `${API_PATH}/list`,
      method: "get",
      params: query,
    });
  },

  // 详情查询
  detailModel(id: number) {
    return request<ApiResponse<ModelTable>>({
      url: `${API_PATH}/detail/${id}`,
      method: "get",
    });
  },

  // 新增
  createModel(body: ModelForm) {
    return request<ApiResponse>({
      url: `${API_PATH}/create`,
      method: "post",
      data: body,
    });
  },

  // 修改（带主键）
  updateModel(id: number, body: ModelForm) {
    return request<ApiResponse>({
      url: `${API_PATH}/update/${id}`,
      method: "put",
      data: body,
    });
  },

  // 删除（支持批量）
  deleteModel(ids: number[]) {
    return request<ApiResponse>({
      url: `${API_PATH}/delete`,
      method: "delete",
      data: ids,
    });
  },

  // 批量启用/停用
  batchModel(body: BatchType) {
    return request<ApiResponse>({
      url: `${API_PATH}/available/setting`,
      method: "patch",
      data: body,
    });
  },

  // 导出
  exportModel(query: ModelPageQuery) {
    return request<Blob>({
      url: `${API_PATH}/export`,
      method: "post",
      data: query,
      responseType: "blob",
    });
  },

  // 下载导入模板
  downloadTemplateModel() {
    return request<Blob>({
      url: `${API_PATH}/download/template`,
      method: "post",
      responseType: "blob",
    });
  },

  // 导入
  importModel(body: FormData) {
    return request<ApiResponse>({
      url: `${API_PATH}/import`,
      method: "post",
      data: body,
      headers: { "Content-Type": "multipart/form-data" },
    });
  },
};

export default ModelAPI;

// ------------------------------
// TS 类型声明
// ------------------------------

// 列表查询参数
export interface ModelPageQuery extends PageQuery {
  name?: string;
  model_id?: string;
  provider?: string;
  api_key?: string;
  base_url?: string;
  config?: string;
  status?: string;
  created_id?: number;
  updated_id?: number;
  created_time?: string[];
  updated_time?: string[];
}

// 列表展示项
export interface ModelTable extends BaseType {
  name?: string;
  model_id?: string;
  provider?: string;
  api_key?: string;
  base_url?: string;
  config?: string;
  created_id?: string;
  updated_id?: string;
  created_by?: CommonType;
  updated_by?: CommonType;
}

// 新增/修改/详情表单参数
export interface ModelForm extends BaseFormType {
  name?: string;
  model_id?: string;
  provider?: string;
  api_key?: string;
  base_url?: string;
  config?: string;
}
