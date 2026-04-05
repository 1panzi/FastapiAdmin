import request from "@/utils/request";

const API_PATH = "/agno_manage/bindings";

const AgBindingAPI = {
  // 获取绑定元数据（拥有者类型 → 可绑资源类型映射）
  getBindingMeta() {
    return request<ApiResponse<BindingMeta>>({
      url: `${API_PATH}/meta`,
      method: "get",
    });
  },

  // 列表查询
  listAgBinding(query: AgBindingPageQuery) {
    return request<ApiResponse<PageResult<AgBindingTable[]>>>({
      url: `${API_PATH}/list`,
      method: "get",
      params: query,
    });
  },

  // 详情查询
  detailAgBinding(id: number) {
    return request<ApiResponse<AgBindingTable>>({
      url: `${API_PATH}/detail/${id}`,
      method: "get",
    });
  },

  // 新增
  createAgBinding(body: AgBindingForm) {
    return request<ApiResponse>({
      url: `${API_PATH}/create`,
      method: "post",
      data: body,
    });
  },

  // 修改（带主键）
  updateAgBinding(id: number, body: AgBindingForm) {
    return request<ApiResponse>({
      url: `${API_PATH}/update/${id}`,
      method: "put",
      data: body,
    });
  },

  // 删除（支持批量）
  deleteAgBinding(ids: number[]) {
    return request<ApiResponse>({
      url: `${API_PATH}/delete`,
      method: "delete",
      data: ids,
    });
  },

  // 批量启用/停用
  batchAgBinding(body: BatchType) {
    return request<ApiResponse>({
      url: `${API_PATH}/available/setting`,
      method: "patch",
      data: body,
    });
  },

  // 导出
  exportAgBinding(query: AgBindingPageQuery) {
    return request<Blob>({
      url: `${API_PATH}/export`,
      method: "post",
      data: query,
      responseType: "blob",
    });
  },

  // 下载导入模板
  downloadTemplateAgBinding() {
    return request<Blob>({
      url: `${API_PATH}/download/template`,
      method: "post",
      responseType: "blob",
    });
  },

  // 导入
  importAgBinding(body: FormData) {
    return request<ApiResponse>({
      url: `${API_PATH}/import`,
      method: "post",
      data: body,
      headers: { "Content-Type": "multipart/form-data" },
    });
  },
};

export default AgBindingAPI;

// ------------------------------
// TS 类型声明
// ------------------------------

// 列表查询参数
export interface AgBindingPageQuery extends PageQuery {
  owner_type?: string;
  owner_id?: number;
  resource_type?: string;
  resource_id?: number;
  priority?: number;
  status?: string;
  created_id?: number;
  updated_id?: number;
  created_time?: string[];
  updated_time?: string[];
}

// 列表展示项
export interface AgBindingTable extends BaseType {
  owner_type?: string;
  owner_id?: number;
  resource_type?: string;
  resource_id?: number;
  priority?: number;
  config_override?: Record<string, any> | null;
  created_id?: string;
  updated_id?: string;
  created_by?: CommonType;
  updated_by?: CommonType;
}

// 新增/修改/详情表单参数
export interface AgBindingForm extends BaseFormType {
  owner_type?: string;
  owner_id?: number;
  resource_type?: string;
  resource_id?: number;
  priority?: number;
  config_override?: Record<string, any>;
}

// 绑定元数据类型
export interface BindingResourceInfo {
  label: string;
  api_path: string;
}

export interface BindingOwnerInfo {
  label: string;
  api_path: string;
  allowed_resources: Record<string, BindingResourceInfo>;
}

export type BindingMeta = Record<string, BindingOwnerInfo>;
