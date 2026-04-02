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
  reader_config?: Record<string, any>;
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
