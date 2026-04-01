import request from "@/utils/request";

const API_PATH = "/agno_manage/hooks";

const AgHooksAPI = {
  // 列表查询
  listAgHooks(query: AgHooksPageQuery) {
    return request<ApiResponse<PageResult<AgHooksTable[]>>>({
      url: `${API_PATH}/list`,
      method: "get",
      params: query,
    });
  },

  // 详情查询
  detailAgHooks(id: number) {
    return request<ApiResponse<AgHooksTable>>({
      url: `${API_PATH}/detail/${id}`,
      method: "get",
    });
  },

  // 新增
  createAgHooks(body: AgHooksForm) {
    return request<ApiResponse>({
      url: `${API_PATH}/create`,
      method: "post",
      data: body,
    });
  },

  // 修改（带主键）
  updateAgHooks(id: number, body: AgHooksForm) {
    return request<ApiResponse>({
      url: `${API_PATH}/update/${id}`,
      method: "put",
      data: body,
    });
  },

  // 删除（支持批量）
  deleteAgHooks(ids: number[]) {
    return request<ApiResponse>({
      url: `${API_PATH}/delete`,
      method: "delete",
      data: ids,
    });
  },

  // 批量启用/停用
  batchAgHooks(body: BatchType) {
    return request<ApiResponse>({
      url: `${API_PATH}/available/setting`,
      method: "patch",
      data: body,
    });
  },

  // 导出
  exportAgHooks(query: AgHooksPageQuery) {
    return request<Blob>({
      url: `${API_PATH}/export`,
      method: "post",
      data: query,
      responseType: "blob",
    });
  },

  // 下载导入模板
  downloadTemplateAgHooks() {
    return request<Blob>({
      url: `${API_PATH}/download/template`,
      method: "post",
      responseType: "blob",
    });
  },

  // 导入
  importAgHooks(body: FormData) {
    return request<ApiResponse>({
      url: `${API_PATH}/import`,
      method: "post",
      data: body,
      headers: { "Content-Type": "multipart/form-data" },
    });
  },
};

export default AgHooksAPI;

// ------------------------------
// TS 类型声明
// ------------------------------

// 列表查询参数
export interface AgHooksPageQuery extends PageQuery {
  name?: string;
  hook_type?: string;
  module_path?: string;
  func_name?: string;
  config?: string;
  run_in_background?: string;
  status?: string;
  created_id?: number;
  updated_id?: number;
  created_time?: string[];
  updated_time?: string[];
}

// 列表展示项
export interface AgHooksTable extends BaseType {
  name?: string;
  hook_type?: string;
  module_path?: string;
  func_name?: string;
  config?: string;
  run_in_background?: string;
  created_id?: string;
  updated_id?: string;
  created_by?: CommonType;
  updated_by?: CommonType;
}

// 新增/修改/详情表单参数
export interface AgHooksForm extends BaseFormType {
  name?: string;
  hook_type?: string;
  module_path?: string;
  func_name?: string;
  config?: string;
  run_in_background?: string;
}
