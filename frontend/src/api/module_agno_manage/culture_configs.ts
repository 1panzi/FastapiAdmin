import request from "@/utils/request";

const API_PATH = "/agno_manage/culture_configs";

const AgCultureConfigAPI = {
  // 列表查询
  listAgCultureConfig(query: AgCultureConfigPageQuery) {
    return request<ApiResponse<PageResult<AgCultureConfigTable[]>>>({
      url: `${API_PATH}/list`,
      method: "get",
      params: query,
    });
  },

  // 详情查询
  detailAgCultureConfig(id: number) {
    return request<ApiResponse<AgCultureConfigTable>>({
      url: `${API_PATH}/detail/${id}`,
      method: "get",
    });
  },

  // 新增
  createAgCultureConfig(body: AgCultureConfigForm) {
    return request<ApiResponse>({
      url: `${API_PATH}/create`,
      method: "post",
      data: body,
    });
  },

  // 修改（带主键）
  updateAgCultureConfig(id: number, body: AgCultureConfigForm) {
    return request<ApiResponse>({
      url: `${API_PATH}/update/${id}`,
      method: "put",
      data: body,
    });
  },

  // 删除（支持批量）
  deleteAgCultureConfig(ids: number[]) {
    return request<ApiResponse>({
      url: `${API_PATH}/delete`,
      method: "delete",
      data: ids,
    });
  },

  // 批量启用/停用
  batchAgCultureConfig(body: BatchType) {
    return request<ApiResponse>({
      url: `${API_PATH}/available/setting`,
      method: "patch",
      data: body,
    });
  },

  // 导出
  exportAgCultureConfig(query: AgCultureConfigPageQuery) {
    return request<Blob>({
      url: `${API_PATH}/export`,
      method: "post",
      data: query,
      responseType: "blob",
    });
  },

  // 下载导入模板
  downloadTemplateAgCultureConfig() {
    return request<Blob>({
      url: `${API_PATH}/download/template`,
      method: "post",
      responseType: "blob",
    });
  },

  // 导入
  importAgCultureConfig(body: FormData) {
    return request<ApiResponse>({
      url: `${API_PATH}/import`,
      method: "post",
      data: body,
      headers: { "Content-Type": "multipart/form-data" },
    });
  },
};

export default AgCultureConfigAPI;

// ------------------------------
// TS 类型声明
// ------------------------------

// 列表查询参数
export interface AgCultureConfigPageQuery extends PageQuery {
  name?: string;
  model_id?: string;
  add_knowledge?: string;
  update_knowledge?: string;
  delete_knowledge?: string;
  clear_knowledge?: string;
  culture_capture_instructions?: string;
  additional_instructions?: string;
  debug_mode?: string;
  status?: string;
  created_id?: number;
  updated_id?: number;
  created_time?: string[];
  updated_time?: string[];
}

// 列表展示项
export interface AgCultureConfigTable extends BaseType {
  name?: string;
  model_id?: string;
  add_knowledge?: boolean;
  update_knowledge?: boolean;
  delete_knowledge?: boolean;
  clear_knowledge?: string;
  culture_capture_instructions?: string;
  additional_instructions?: string;
  debug_mode?: string;
  created_id?: string;
  updated_id?: string;
  created_by?: CommonType;
  updated_by?: CommonType;
}

// 新增/修改/详情表单参数
export interface AgCultureConfigForm extends BaseFormType {
  name?: string;
  model_id?: string;
  add_knowledge?: boolean;
  update_knowledge?: boolean;
  delete_knowledge?: boolean;
  clear_knowledge?: string;
  culture_capture_instructions?: string;
  additional_instructions?: string;
  debug_mode?: string;
}
