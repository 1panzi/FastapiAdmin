import request from "@/utils/request";

const API_PATH = "/agno_manage/knowledge_bases";

const AgKnowledgeBaseAPI = {
  // 列表查询
  listAgKnowledgeBase(query: AgKnowledgeBasePageQuery) {
    return request<ApiResponse<PageResult<AgKnowledgeBaseTable[]>>>({
      url: `${API_PATH}/list`,
      method: "get",
      params: query,
    });
  },

  // 详情查询
  detailAgKnowledgeBase(id: number) {
    return request<ApiResponse<AgKnowledgeBaseTable>>({
      url: `${API_PATH}/detail/${id}`,
      method: "get",
    });
  },

  // 新增
  createAgKnowledgeBase(body: AgKnowledgeBaseForm) {
    return request<ApiResponse>({
      url: `${API_PATH}/create`,
      method: "post",
      data: body,
    });
  },

  // 修改（带主键）
  updateAgKnowledgeBase(id: number, body: AgKnowledgeBaseForm) {
    return request<ApiResponse>({
      url: `${API_PATH}/update/${id}`,
      method: "put",
      data: body,
    });
  },

  // 删除（支持批量）
  deleteAgKnowledgeBase(ids: number[]) {
    return request<ApiResponse>({
      url: `${API_PATH}/delete`,
      method: "delete",
      data: ids,
    });
  },

  // 批量启用/停用
  batchAgKnowledgeBase(body: BatchType) {
    return request<ApiResponse>({
      url: `${API_PATH}/available/setting`,
      method: "patch",
      data: body,
    });
  },

  // 导出
  exportAgKnowledgeBase(query: AgKnowledgeBasePageQuery) {
    return request<Blob>({
      url: `${API_PATH}/export`,
      method: "post",
      data: query,
      responseType: "blob",
    });
  },

  // 下载导入模板
  downloadTemplateAgKnowledgeBase() {
    return request<Blob>({
      url: `${API_PATH}/download/template`,
      method: "post",
      responseType: "blob",
    });
  },

  // 导入
  importAgKnowledgeBase(body: FormData) {
    return request<ApiResponse>({
      url: `${API_PATH}/import`,
      method: "post",
      data: body,
      headers: { "Content-Type": "multipart/form-data" },
    });
  },

  // ── 文档管理子路由 ──────────────────────────────────────────────────────

  // 上传文件到知识库（异步向量化）
  uploadKBDoc(kb_id: number, body: FormData) {
    return request<ApiResponse<AgKBDocumentItem>>({
      url: `${API_PATH}/${kb_id}/docs/upload`,
      method: "post",
      data: body,
      headers: { "Content-Type": "multipart/form-data" },
    });
  },

  // 插入 URL 或文本到知识库
  insertKBDoc(kb_id: number, body: KBDocInsertBody) {
    return request<ApiResponse<AgKBDocumentItem>>({
      url: `${API_PATH}/${kb_id}/docs`,
      method: "post",
      data: body,
    });
  },

  // 查询知识库文档列表（分页）
  listKBDocs(kb_id: number, query: { page_no?: number; page_size?: number; doc_status?: string; name?: string }) {
    return request<ApiResponse<PageResult<AgKBDocumentItem[]>>>({
      url: `${API_PATH}/${kb_id}/docs`,
      method: "get",
      params: query,
    });
  },

  // 删除文档（同时删除向量）
  deleteKBDoc(kb_id: number, doc_id: number) {
    return request<ApiResponse>({
      url: `${API_PATH}/${kb_id}/docs/${doc_id}`,
      method: "delete",
    });
  },

  // 重新向量化文档
  reprocessKBDoc(kb_id: number, doc_id: number) {
    return request<ApiResponse<AgKBDocumentItem>>({
      url: `${API_PATH}/${kb_id}/docs/${doc_id}/reprocess`,
      method: "post",
    });
  },

  // 知识库向量检索
  searchKB(kb_id: number, body: { query: string; limit?: number }) {
    return request<ApiResponse<KBSearchResult[]>>({
      url: `${API_PATH}/${kb_id}/search`,
      method: "post",
      data: body,
    });
  },
};

export default AgKnowledgeBaseAPI;

// ------------------------------
// TS 类型声明
// ------------------------------

// 列表查询参数
export interface AgKnowledgeBasePageQuery extends PageQuery {
  name?: string;
  vectordb_id?: string;
  max_results?: string;
  reader_type?: string;
  reader_config?: string;
  default_filters?: string;
  status?: string;
  created_id?: number;
  updated_id?: number;
  created_time?: string[];
  updated_time?: string[];
}

// 列表展示项
export interface AgKnowledgeBaseTable extends BaseType {
  name?: string;
  vectordb_id?: string;
  max_results?: string;
  reader_type?: string;
  reader_config?: Record<string, any>;
  default_filters?: string;
  created_id?: string;
  updated_id?: string;
  created_by?: CommonType;
  updated_by?: CommonType;
}

// 新增/修改/详情表单参数
export interface AgKnowledgeBaseForm extends BaseFormType {
  name?: string;
  vectordb_id?: string;
  max_results?: string;
  reader_type?: string;
  reader_config?: Record<string, any>;
  default_filters?: string;
}

// ── 文档管理相关类型 ──────────────────────────────────────────────────────

// 知识库文档条目
export interface AgKBDocumentItem {
  id?: number;
  uuid?: string;
  kb_id?: number;
  name?: string;
  storage_type?: string;
  storage_path?: string;
  doc_status?: string;
  error_msg?: string;
  content_id?: string;
  metadata_config?: Record<string, any>;
  reader_id?: number;
  description?: string;
  created_time?: string;
  updated_time?: string;
}

// 插入 URL/文本的请求体
export interface KBDocInsertBody {
  url?: string;
  text_content?: string;
  name?: string;
  description?: string;
  metadata_config?: Record<string, any>;
  reader_id?: number;
}

// 向量检索结果条目
export interface KBSearchResult {
  name?: string;
  content?: string;
  meta_data?: Record<string, any>;
  reranking_score?: number | null;
}
