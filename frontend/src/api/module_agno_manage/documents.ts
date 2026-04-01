import request from "@/utils/request";

const API_PATH = "/agno_manage/documents";

const AgDocumentAPI = {
  // 列表查询
  listAgDocument(query: AgDocumentPageQuery) {
    return request<ApiResponse<PageResult<AgDocumentTable[]>>>({
      url: `${API_PATH}/list`,
      method: "get",
      params: query,
    });
  },

  // 详情查询
  detailAgDocument(id: number) {
    return request<ApiResponse<AgDocumentTable>>({
      url: `${API_PATH}/detail/${id}`,
      method: "get",
    });
  },

  // 新增
  createAgDocument(body: AgDocumentForm) {
    return request<ApiResponse>({
      url: `${API_PATH}/create`,
      method: "post",
      data: body,
    });
  },

  // 修改（带主键）
  updateAgDocument(id: number, body: AgDocumentForm) {
    return request<ApiResponse>({
      url: `${API_PATH}/update/${id}`,
      method: "put",
      data: body,
    });
  },

  // 删除（支持批量）
  deleteAgDocument(ids: number[]) {
    return request<ApiResponse>({
      url: `${API_PATH}/delete`,
      method: "delete",
      data: ids,
    });
  },

  // 批量启用/停用
  batchAgDocument(body: BatchType) {
    return request<ApiResponse>({
      url: `${API_PATH}/available/setting`,
      method: "patch",
      data: body,
    });
  },

  // 导出
  exportAgDocument(query: AgDocumentPageQuery) {
    return request<Blob>({
      url: `${API_PATH}/export`,
      method: "post",
      data: query,
      responseType: "blob",
    });
  },

  // 下载导入模板
  downloadTemplateAgDocument() {
    return request<Blob>({
      url: `${API_PATH}/download/template`,
      method: "post",
      responseType: "blob",
    });
  },

  // 导入
  importAgDocument(body: FormData) {
    return request<ApiResponse>({
      url: `${API_PATH}/import`,
      method: "post",
      data: body,
      headers: { "Content-Type": "multipart/form-data" },
    });
  },
};

export default AgDocumentAPI;

// ------------------------------
// TS 类型声明
// ------------------------------

// 列表查询参数
export interface AgDocumentPageQuery extends PageQuery {
  kb_id?: string;
  name?: string;
  storage_type?: string;
  storage_path?: string;
  doc_status?: string;
  error_msg?: string;
  metadata?: string;
  status?: string;
  created_id?: number;
  updated_id?: number;
  created_time?: string[];
  updated_time?: string[];
}

// 列表展示项
export interface AgDocumentTable extends BaseType {
  kb_id?: string;
  name?: string;
  storage_type?: string;
  storage_path?: string;
  doc_status?: boolean;
  error_msg?: string;
  metadata?: string;
  created_id?: string;
  updated_id?: string;
  created_by?: CommonType;
  updated_by?: CommonType;
}

// 新增/修改/详情表单参数
export interface AgDocumentForm extends BaseFormType {
  kb_id?: string;
  name?: string;
  storage_type?: string;
  storage_path?: string;
  doc_status?: boolean;
  error_msg?: string;
  metadata?: string;
}
