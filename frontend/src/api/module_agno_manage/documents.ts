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

  // 上传文件并向量化
  uploadDocument(body: FormData) {
    return request<ApiResponse<AgDocumentTable>>({
      url: `${API_PATH}/upload`,
      method: "post",
      data: body,
      headers: { "Content-Type": "multipart/form-data" },
    });
  },

  // 插入 URL 或文本并向量化
  insertDocument(body: DocInsertBody) {
    return request<ApiResponse<AgDocumentTable>>({
      url: `${API_PATH}/insert`,
      method: "post",
      data: body,
    });
  },

  // 重新向量化文档
  reprocessDocument(id: number) {
    return request<ApiResponse<AgDocumentTable>>({
      url: `${API_PATH}/${id}/reprocess`,
      method: "post",
    });
  },
};

export default AgDocumentAPI;

// ------------------------------
// TS 类型声明
// ------------------------------

// 列表查询参数
export interface AgDocumentPageQuery extends PageQuery {
  kb_id?: number;
  name?: string;
  storage_type?: string;
  storage_path?: string;
  doc_status?: string;
  error_msg?: string;
  status?: string;
  created_id?: number;
  updated_id?: number;
  created_time?: string[];
  updated_time?: string[];
}

// 列表展示项
export interface AgDocumentTable extends BaseType {
  kb_id?: number;
  name?: string;
  storage_type?: string;
  storage_path?: string;
  doc_status?: string;
  error_msg?: string;
  content_id?: string;
  metadata_config?: Record<string, any>;
  reader_id?: number;
  created_id?: string;
  updated_id?: string;
  created_by?: CommonType;
  updated_by?: CommonType;
}

// 新增/修改/详情表单参数
export interface AgDocumentForm extends BaseFormType {
  kb_id?: number;
  name?: string;
  storage_type?: string;
  storage_path?: string;
  doc_status?: string;
  error_msg?: string;
  metadata_config?: Record<string, any>;
  reader_id?: number;
}

// 插入 URL/文本的请求体
export interface DocInsertBody {
  kb_id?: number;
  url?: string;
  text_content?: string;
  name?: string;
  description?: string;
  metadata_config?: Record<string, any>;
  reader_id?: number;
}
