import request from "@/utils/request";

const API_PATH = "/agno_manage/guardrails";

const AgGuardrailAPI = {
  // 列表查询
  listAgGuardrail(query: AgGuardrailPageQuery) {
    return request<ApiResponse<PageResult<AgGuardrailTable[]>>>({
      url: `${API_PATH}/list`,
      method: "get",
      params: query,
    });
  },

  // 详情查询
  detailAgGuardrail(id: number) {
    return request<ApiResponse<AgGuardrailTable>>({
      url: `${API_PATH}/detail/${id}`,
      method: "get",
    });
  },

  // 新增
  createAgGuardrail(body: AgGuardrailForm) {
    return request<ApiResponse>({
      url: `${API_PATH}/create`,
      method: "post",
      data: body,
    });
  },

  // 修改（带主键）
  updateAgGuardrail(id: number, body: AgGuardrailForm) {
    return request<ApiResponse>({
      url: `${API_PATH}/update/${id}`,
      method: "put",
      data: body,
    });
  },

  // 删除（支持批量）
  deleteAgGuardrail(ids: number[]) {
    return request<ApiResponse>({
      url: `${API_PATH}/delete`,
      method: "delete",
      data: ids,
    });
  },

  // 批量启用/停用
  batchAgGuardrail(body: BatchType) {
    return request<ApiResponse>({
      url: `${API_PATH}/available/setting`,
      method: "patch",
      data: body,
    });
  },

  // 导出
  exportAgGuardrail(query: AgGuardrailPageQuery) {
    return request<Blob>({
      url: `${API_PATH}/export`,
      method: "post",
      data: query,
      responseType: "blob",
    });
  },

  // 下载导入模板
  downloadTemplateAgGuardrail() {
    return request<Blob>({
      url: `${API_PATH}/download/template`,
      method: "post",
      responseType: "blob",
    });
  },

  // 导入
  importAgGuardrail(body: FormData) {
    return request<ApiResponse>({
      url: `${API_PATH}/import`,
      method: "post",
      data: body,
      headers: { "Content-Type": "multipart/form-data" },
    });
  },
};

export default AgGuardrailAPI;

// ------------------------------
// TS 类型声明
// ------------------------------

// 列表查询参数
export interface AgGuardrailPageQuery extends PageQuery {
  name?: string;
  type?: string;
  hook_type?: string;
  config?: string;
  module_path?: string;
  class_name?: string;
  status?: string;
  created_id?: number;
  updated_id?: number;
  created_time?: string[];
  updated_time?: string[];
}

// 列表展示项
export interface AgGuardrailTable extends BaseType {
  name?: string;
  type?: string;
  hook_type?: string;
  config?: Record<string, any>;
  module_path?: string;
  class_name?: string;
  created_id?: string;
  updated_id?: string;
  created_by?: CommonType;
  updated_by?: CommonType;
}

// 新增/修改/详情表单参数
export interface AgGuardrailForm extends BaseFormType {
  name?: string;
  type?: string;
  hook_type?: string;
  config?: Record<string, any>;
  module_path?: string;
  class_name?: string;
}
