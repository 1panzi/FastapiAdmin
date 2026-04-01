import request from "@/utils/request";

const API_PATH = "/agno_manage/learning_configs";

const AgLearningConfigAPI = {
  // 列表查询
  listAgLearningConfig(query: AgLearningConfigPageQuery) {
    return request<ApiResponse<PageResult<AgLearningConfigTable[]>>>({
      url: `${API_PATH}/list`,
      method: "get",
      params: query,
    });
  },

  // 详情查询
  detailAgLearningConfig(id: number) {
    return request<ApiResponse<AgLearningConfigTable>>({
      url: `${API_PATH}/detail/${id}`,
      method: "get",
    });
  },

  // 新增
  createAgLearningConfig(body: AgLearningConfigForm) {
    return request<ApiResponse>({
      url: `${API_PATH}/create`,
      method: "post",
      data: body,
    });
  },

  // 修改（带主键）
  updateAgLearningConfig(id: number, body: AgLearningConfigForm) {
    return request<ApiResponse>({
      url: `${API_PATH}/update/${id}`,
      method: "put",
      data: body,
    });
  },

  // 删除（支持批量）
  deleteAgLearningConfig(ids: number[]) {
    return request<ApiResponse>({
      url: `${API_PATH}/delete`,
      method: "delete",
      data: ids,
    });
  },

  // 批量启用/停用
  batchAgLearningConfig(body: BatchType) {
    return request<ApiResponse>({
      url: `${API_PATH}/available/setting`,
      method: "patch",
      data: body,
    });
  },

  // 导出
  exportAgLearningConfig(query: AgLearningConfigPageQuery) {
    return request<Blob>({
      url: `${API_PATH}/export`,
      method: "post",
      data: query,
      responseType: "blob",
    });
  },

  // 下载导入模板
  downloadTemplateAgLearningConfig() {
    return request<Blob>({
      url: `${API_PATH}/download/template`,
      method: "post",
      responseType: "blob",
    });
  },

  // 导入
  importAgLearningConfig(body: FormData) {
    return request<ApiResponse>({
      url: `${API_PATH}/import`,
      method: "post",
      data: body,
      headers: { "Content-Type": "multipart/form-data" },
    });
  },
};

export default AgLearningConfigAPI;

// ------------------------------
// TS 类型声明
// ------------------------------

// 列表查询参数
export interface AgLearningConfigPageQuery extends PageQuery {
  name?: string;
  model_id?: string;
  namespace?: string;
  user_profile?: string;
  user_memory?: string;
  session_context?: string;
  entity_memory?: string;
  learned_knowledge?: string;
  decision_log?: string;
  status?: string;
  created_id?: number;
  updated_id?: number;
  created_time?: string[];
  updated_time?: string[];
}

// 列表展示项
export interface AgLearningConfigTable extends BaseType {
  name?: string;
  model_id?: string;
  namespace?: string;
  user_profile?: string;
  user_memory?: string;
  session_context?: string;
  entity_memory?: string;
  learned_knowledge?: string;
  decision_log?: string;
  created_id?: string;
  updated_id?: string;
  created_by?: CommonType;
  updated_by?: CommonType;
}

// 新增/修改/详情表单参数
export interface AgLearningConfigForm extends BaseFormType {
  name?: string;
  model_id?: string;
  namespace?: string;
  user_profile?: string;
  user_memory?: string;
  session_context?: string;
  entity_memory?: string;
  learned_knowledge?: string;
  decision_log?: string;
}
