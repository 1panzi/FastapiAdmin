import request from "@/utils/request";

const API_PATH = "/agno_manage/user_roles";

const AgUserRoleAPI = {
  // 列表查询
  listAgUserRole(query: AgUserRolePageQuery) {
    return request<ApiResponse<PageResult<AgUserRoleTable[]>>>({
      url: `${API_PATH}/list`,
      method: "get",
      params: query,
    });
  },

  // 详情查询
  detailAgUserRole(id: number) {
    return request<ApiResponse<AgUserRoleTable>>({
      url: `${API_PATH}/detail/${id}`,
      method: "get",
    });
  },

  // 新增
  createAgUserRole(body: AgUserRoleForm) {
    return request<ApiResponse>({
      url: `${API_PATH}/create`,
      method: "post",
      data: body,
    });
  },

  // 修改（带主键）
  updateAgUserRole(id: number, body: AgUserRoleForm) {
    return request<ApiResponse>({
      url: `${API_PATH}/update/${id}`,
      method: "put",
      data: body,
    });
  },

  // 删除（支持批量）
  deleteAgUserRole(ids: number[]) {
    return request<ApiResponse>({
      url: `${API_PATH}/delete`,
      method: "delete",
      data: ids,
    });
  },

  // 批量启用/停用
  batchAgUserRole(body: BatchType) {
    return request<ApiResponse>({
      url: `${API_PATH}/available/setting`,
      method: "patch",
      data: body,
    });
  },

  // 导出
  exportAgUserRole(query: AgUserRolePageQuery) {
    return request<Blob>({
      url: `${API_PATH}/export`,
      method: "post",
      data: query,
      responseType: "blob",
    });
  },

  // 下载导入模板
  downloadTemplateAgUserRole() {
    return request<Blob>({
      url: `${API_PATH}/download/template`,
      method: "post",
      responseType: "blob",
    });
  },

  // 导入
  importAgUserRole(body: FormData) {
    return request<ApiResponse>({
      url: `${API_PATH}/import`,
      method: "post",
      data: body,
      headers: { "Content-Type": "multipart/form-data" },
    });
  },
};

export default AgUserRoleAPI;

// ------------------------------
// TS 类型声明
// ------------------------------

// 列表查询参数
export interface AgUserRolePageQuery extends PageQuery {
  user_id?: string;
  role_id?: string;
  created_id?: number;
  updated_id?: number;
  created_time?: string[];
  updated_time?: string[];
}

// 列表展示项
export interface AgUserRoleTable extends BaseType {
  user_id?: string;
  role_id?: string;
  created_id?: string;
  updated_id?: string;
  created_by?: CommonType;
  updated_by?: CommonType;
}

// 新增/修改/详情表单参数
export interface AgUserRoleForm extends BaseFormType {
  user_id?: string;
  role_id?: string;
}
