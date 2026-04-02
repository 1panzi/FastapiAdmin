import request from "@/utils/request";

const API_PATH = "/agno_manage/integrations";

const AgIntegrationAPI = {
  // 列表查询
  listAgIntegration(query: AgIntegrationPageQuery) {
    return request<ApiResponse<PageResult<AgIntegrationTable[]>>>({
      url: `${API_PATH}/list`,
      method: "get",
      params: query,
    });
  },

  // 详情查询
  detailAgIntegration(id: number) {
    return request<ApiResponse<AgIntegrationTable>>({
      url: `${API_PATH}/detail/${id}`,
      method: "get",
    });
  },

  // 新增
  createAgIntegration(body: AgIntegrationForm) {
    return request<ApiResponse>({
      url: `${API_PATH}/create`,
      method: "post",
      data: body,
    });
  },

  // 修改（带主键）
  updateAgIntegration(id: number, body: AgIntegrationForm) {
    return request<ApiResponse>({
      url: `${API_PATH}/update/${id}`,
      method: "put",
      data: body,
    });
  },

  // 删除（支持批量）
  deleteAgIntegration(ids: number[]) {
    return request<ApiResponse>({
      url: `${API_PATH}/delete`,
      method: "delete",
      data: ids,
    });
  },

  // 批量启用/停用
  batchAgIntegration(body: BatchType) {
    return request<ApiResponse>({
      url: `${API_PATH}/available/setting`,
      method: "patch",
      data: body,
    });
  },

  // 导出
  exportAgIntegration(query: AgIntegrationPageQuery) {
    return request<Blob>({
      url: `${API_PATH}/export`,
      method: "post",
      data: query,
      responseType: "blob",
    });
  },

  // 下载导入模板
  downloadTemplateAgIntegration() {
    return request<Blob>({
      url: `${API_PATH}/download/template`,
      method: "post",
      responseType: "blob",
    });
  },

  // 导入
  importAgIntegration(body: FormData) {
    return request<ApiResponse>({
      url: `${API_PATH}/import`,
      method: "post",
      data: body,
      headers: { "Content-Type": "multipart/form-data" },
    });
  },
};

export default AgIntegrationAPI;

// ------------------------------
// TS 类型声明
// ------------------------------

// 列表查询参数
export interface AgIntegrationPageQuery extends PageQuery {
  name?: string;
  type?: string;
  agent_id?: string;
  team_id?: string;
  workflow_id?: string;
  token?: string;
  signing_secret?: string;
  prefix?: string;
  config?: Record<string, any>;
  status?: string;
  created_id?: number;
  updated_id?: number;
  created_time?: string[];
  updated_time?: string[];
}

// 列表展示项
export interface AgIntegrationTable extends BaseType {
  name?: string;
  type?: string;
  agent_id?: string;
  team_id?: string;
  workflow_id?: string;
  token?: string;
  signing_secret?: string;
  prefix?: string;
  config?: Record<string, any>;
  created_id?: string;
  updated_id?: string;
  created_by?: CommonType;
  updated_by?: CommonType;
}

// 新增/修改/详情表单参数
export interface AgIntegrationForm extends BaseFormType {
  name?: string;
  type?: string;
  agent_id?: string;
  team_id?: string;
  workflow_id?: string;
  token?: string;
  signing_secret?: string;
  prefix?: string;
  config?: Record<string, any>;
}
