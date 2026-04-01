import request from "@/utils/request";

const API_PATH = "/agno_manage/audit_logs";

const AgAuditLogAPI = {
  // 列表查询
  listAgAuditLog(query: AgAuditLogPageQuery) {
    return request<ApiResponse<PageResult<AgAuditLogTable[]>>>({
      url: `${API_PATH}/list`,
      method: "get",
      params: query,
    });
  },

  // 详情查询
  detailAgAuditLog(id: number) {
    return request<ApiResponse<AgAuditLogTable>>({
      url: `${API_PATH}/detail/${id}`,
      method: "get",
    });
  },

  // 新增
  createAgAuditLog(body: AgAuditLogForm) {
    return request<ApiResponse>({
      url: `${API_PATH}/create`,
      method: "post",
      data: body,
    });
  },

  // 修改（带主键）
  updateAgAuditLog(id: number, body: AgAuditLogForm) {
    return request<ApiResponse>({
      url: `${API_PATH}/update/${id}`,
      method: "put",
      data: body,
    });
  },

  // 删除（支持批量）
  deleteAgAuditLog(ids: number[]) {
    return request<ApiResponse>({
      url: `${API_PATH}/delete`,
      method: "delete",
      data: ids,
    });
  },

  // 批量启用/停用
  batchAgAuditLog(body: BatchType) {
    return request<ApiResponse>({
      url: `${API_PATH}/available/setting`,
      method: "patch",
      data: body,
    });
  },

  // 导出
  exportAgAuditLog(query: AgAuditLogPageQuery) {
    return request<Blob>({
      url: `${API_PATH}/export`,
      method: "post",
      data: query,
      responseType: "blob",
    });
  },

  // 下载导入模板
  downloadTemplateAgAuditLog() {
    return request<Blob>({
      url: `${API_PATH}/download/template`,
      method: "post",
      responseType: "blob",
    });
  },

  // 导入
  importAgAuditLog(body: FormData) {
    return request<ApiResponse>({
      url: `${API_PATH}/import`,
      method: "post",
      data: body,
      headers: { "Content-Type": "multipart/form-data" },
    });
  },
};

export default AgAuditLogAPI;

// ------------------------------
// TS 类型声明
// ------------------------------

// 列表查询参数
export interface AgAuditLogPageQuery extends PageQuery {
  actor_id?: string;
  action?: string;
  resource_type?: string;
  resource_id?: string;
  diff?: string;
  ip?: string;
  created_time?: string[];
  updated_time?: string[];
}

// 列表展示项
export interface AgAuditLogTable extends BaseType {
  actor_id?: string;
  action?: string;
  resource_type?: string;
  resource_id?: string;
  diff?: string;
  ip?: string;
  created_by?: CommonType;
  updated_by?: CommonType;
}

// 新增/修改/详情表单参数
export interface AgAuditLogForm extends BaseFormType {
  actor_id?: string;
  action?: string;
  resource_type?: string;
  resource_id?: string;
  diff?: string;
  ip?: string;
}
