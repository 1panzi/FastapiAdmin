import request from "@/utils/request";

const API_PATH = "/agno_manage/hooks";

const AgHookAPI = {
  // 列表查询
  listAgHook(query: AgHookPageQuery) {
    return request<ApiResponse<PageResult<AgHookTable[]>>>({
      url: `${API_PATH}/list`,
      method: "get",
      params: query,
    });
  },

  // 详情查询
  detailAgHook(id: number) {
    return request<ApiResponse<AgHookTable>>({
      url: `${API_PATH}/detail/${id}`,
      method: "get",
    });
  },

  // 新增
  createAgHook(body: AgHookForm) {
    return request<ApiResponse>({
      url: `${API_PATH}/create`,
      method: "post",
      data: body,
    });
  },

  // 修改（带主键）
  updateAgHook(id: number, body: AgHookForm) {
    return request<ApiResponse>({
      url: `${API_PATH}/update/${id}`,
      method: "put",
      data: body,
    });
  },

  // 删除（支持批量）
  deleteAgHook(ids: number[]) {
    return request<ApiResponse>({
      url: `${API_PATH}/delete`,
      method: "delete",
      data: ids,
    });
  },

  // 批量启用/停用
  batchAgHook(body: BatchType) {
    return request<ApiResponse>({
      url: `${API_PATH}/available/setting`,
      method: "patch",
      data: body,
    });
  },

  // 导出
  exportAgHook(query: AgHookPageQuery) {
    return request<Blob>({
      url: `${API_PATH}/export`,
      method: "post",
      data: query,
      responseType: "blob",
    });
  },

  // 下载导入模板
  downloadTemplateAgHook() {
    return request<Blob>({
      url: `${API_PATH}/download/template`,
      method: "post",
      responseType: "blob",
    });
  },

  // 导入
  importAgHook(body: FormData) {
    return request<ApiResponse>({
      url: `${API_PATH}/import`,
      method: "post",
      data: body,
      headers: { "Content-Type": "multipart/form-data" },
    });
  },
};

export default AgHookAPI;

// ------------------------------
// TS 类型声明
// ------------------------------

// 列表查询参数
export interface AgHookPageQuery extends PageQuery {
  name?: string;
  hook_type?: string;
  module_path?: string;
  func_name?: string;
  config?: Record<string, any>;
  run_in_background?: string;
  status?: string;
  created_id?: number;
  updated_id?: number;
  created_time?: string[];
  updated_time?: string[];
}

// 列表展示项
export interface AgHookTable extends BaseType {
  name?: string;
  hook_type?: string;
  module_path?: string;
  func_name?: string;
  config?: Record<string, any>;
  run_in_background?: string;
  created_id?: string;
  updated_id?: string;
  created_by?: CommonType;
  updated_by?: CommonType;
}

// 新增/修改/详情表单参数
export interface AgHookForm extends BaseFormType {
  name?: string;
  hook_type?: string;
  module_path?: string;
  func_name?: string;
  config?: Record<string, any>;
  run_in_background?: string;
}
