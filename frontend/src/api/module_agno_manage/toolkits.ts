import request from "@/utils/request";

const API_PATH = "/agno_manage/toolkits";

const AgToolkitAPI = {
  // 列表查询
  listAgToolkit(query: AgToolkitPageQuery) {
    return request<ApiResponse<PageResult<AgToolkitTable[]>>>({
      url: `${API_PATH}/list`,
      method: "get",
      params: query,
    });
  },

  // 详情查询
  detailAgToolkit(id: number) {
    return request<ApiResponse<AgToolkitTable>>({
      url: `${API_PATH}/detail/${id}`,
      method: "get",
    });
  },

  // 新增
  createAgToolkit(body: AgToolkitForm) {
    return request<ApiResponse>({
      url: `${API_PATH}/create`,
      method: "post",
      data: body,
    });
  },

  // 修改（带主键）
  updateAgToolkit(id: number, body: AgToolkitForm) {
    return request<ApiResponse>({
      url: `${API_PATH}/update/${id}`,
      method: "put",
      data: body,
    });
  },

  // 删除（支持批量）
  deleteAgToolkit(ids: number[]) {
    return request<ApiResponse>({
      url: `${API_PATH}/delete`,
      method: "delete",
      data: ids,
    });
  },

  // 批量启用/停用
  batchAgToolkit(body: BatchType) {
    return request<ApiResponse>({
      url: `${API_PATH}/available/setting`,
      method: "patch",
      data: body,
    });
  },

  // 导出
  exportAgToolkit(query: AgToolkitPageQuery) {
    return request<Blob>({
      url: `${API_PATH}/export`,
      method: "post",
      data: query,
      responseType: "blob",
    });
  },

  // 下载导入模板
  downloadTemplateAgToolkit() {
    return request<Blob>({
      url: `${API_PATH}/download/template`,
      method: "post",
      responseType: "blob",
    });
  },

  // 导入
  importAgToolkit(body: FormData) {
    return request<ApiResponse>({
      url: `${API_PATH}/import`,
      method: "post",
      data: body,
      headers: { "Content-Type": "multipart/form-data" },
    });
  },
};

export default AgToolkitAPI;

// ------------------------------
// TS 类型声明
// ------------------------------

// 列表查询参数
export interface AgToolkitPageQuery extends PageQuery {
  name?: string;
  type?: string;
  module_path?: string;
  class_name?: string;
  func_name?: string;
  tool_from?: string;
  category?: string;
  global_enabled?: boolean;
  status?: string;
  created_id?: number;
  updated_id?: number;
  created_time?: string[];
  updated_time?: string[];
}

// 列表展示项
export interface AgToolkitTable extends BaseType {
  name?: string;
  type?: string;
  module_path?: string;
  class_name?: string;
  func_name?: string;
  config?: Record<string, any>;
  instructions?: string;
  requires_confirmation?: boolean;
  approval_type?: string;
  stop_after_call?: boolean;
  show_result?: boolean;
  cache_results?: boolean;
  cache_ttl?: number;
  tool_from?: string;
  category?: string;
  global_enabled?: boolean;
  source_code?: string;
  param_schema?: Array<{
    name: string;
    type: string;
    default: any;
    required: boolean;
  }>;
  created_id?: string;
  updated_id?: string;
  created_by?: CommonType;
  updated_by?: CommonType;
}

// 新增/修改/详情表单参数
export interface AgToolkitForm extends BaseFormType {
  name?: string;
  type?: string;
  module_path?: string;
  class_name?: string;
  func_name?: string;
  config?: Record<string, any>;
  instructions?: string;
  requires_confirmation?: boolean;
  approval_type?: string;
  stop_after_call?: boolean;
  show_result?: boolean;
  cache_results?: boolean;
  cache_ttl?: number;
  tool_from?: string;
  category?: string;
  global_enabled?: boolean;
  source_code?: string;
}
