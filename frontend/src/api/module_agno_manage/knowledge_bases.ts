import request from "@/utils/request";

const API_PATH = "/agno_manage/knowledge_bases";

const AgKnowledgeBasesAPI = {
  // 列表查询
  listAgKnowledgeBases(query: AgKnowledgeBasesPageQuery) {
    return request<ApiResponse<PageResult<AgKnowledgeBasesTable[]>>>({
      url: `${API_PATH}/list`,
      method: "get",
      params: query,
    });
  },

  // 详情查询
  detailAgKnowledgeBases(id: number) {
    return request<ApiResponse<AgKnowledgeBasesTable>>({
      url: `${API_PATH}/detail/${id}`,
      method: "get",
    });
  },

  // 新增
  createAgKnowledgeBases(body: AgKnowledgeBasesForm) {
    return request<ApiResponse>({
      url: `${API_PATH}/create`,
      method: "post",
      data: body,
    });
  },

  // 修改（带主键）
  updateAgKnowledgeBases(id: number, body: AgKnowledgeBasesForm) {
    return request<ApiResponse>({
      url: `${API_PATH}/update/${id}`,
      method: "put",
      data: body,
    });
  },

  // 删除（支持批量）
  deleteAgKnowledgeBases(ids: number[]) {
    return request<ApiResponse>({
      url: `${API_PATH}/delete`,
      method: "delete",
      data: ids,
    });
  },

  // 批量启用/停用
  batchAgKnowledgeBases(body: BatchType) {
    return request<ApiResponse>({
      url: `${API_PATH}/available/setting`,
      method: "patch",
      data: body,
    });
  },

  // 导出
  exportAgKnowledgeBases(query: AgKnowledgeBasesPageQuery) {
    return request<Blob>({
      url: `${API_PATH}/export`,
      method: "post",
      data: query,
      responseType: "blob",
    });
  },

  // 下载导入模板
  downloadTemplateAgKnowledgeBases() {
    return request<Blob>({
      url: `${API_PATH}/download/template`,
      method: "post",
      responseType: "blob",
    });
  },

  // 导入
  importAgKnowledgeBases(body: FormData) {
    return request<ApiResponse>({
      url: `${API_PATH}/import`,
      method: "post",
      data: body,
      headers: { "Content-Type": "multipart/form-data" },
    });
  },
};

export default AgKnowledgeBasesAPI;

// ------------------------------
// TS 类型声明
// ------------------------------

// 列表查询参数
export interface AgKnowledgeBasesPageQuery extends PageQuery {
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
export interface AgKnowledgeBasesTable extends BaseType {
  name?: string;
  vectordb_id?: string;
  max_results?: string;
  reader_type?: string;
  reader_config?: string;
  default_filters?: string;
  created_id?: string;
  updated_id?: string;
  created_by?: CommonType;
  updated_by?: CommonType;
}

// 新增/修改/详情表单参数
export interface AgKnowledgeBasesForm extends BaseFormType {
  name?: string;
  vectordb_id?: string;
  max_results?: string;
  reader_type?: string;
  reader_config?: string;
  default_filters?: string;
}
