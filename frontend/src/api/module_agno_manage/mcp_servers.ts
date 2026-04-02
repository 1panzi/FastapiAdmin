import request from "@/utils/request";

const API_PATH = "/agno_manage/mcp_servers";

const AgMcpServerAPI = {
  // 列表查询
  listAgMcpServer(query: AgMcpServerPageQuery) {
    return request<ApiResponse<PageResult<AgMcpServerTable[]>>>({
      url: `${API_PATH}/list`,
      method: "get",
      params: query,
    });
  },

  // 详情查询
  detailAgMcpServer(id: number) {
    return request<ApiResponse<AgMcpServerTable>>({
      url: `${API_PATH}/detail/${id}`,
      method: "get",
    });
  },

  // 新增
  createAgMcpServer(body: AgMcpServerForm) {
    return request<ApiResponse>({
      url: `${API_PATH}/create`,
      method: "post",
      data: body,
    });
  },

  // 修改（带主键）
  updateAgMcpServer(id: number, body: AgMcpServerForm) {
    return request<ApiResponse>({
      url: `${API_PATH}/update/${id}`,
      method: "put",
      data: body,
    });
  },

  // 删除（支持批量）
  deleteAgMcpServer(ids: number[]) {
    return request<ApiResponse>({
      url: `${API_PATH}/delete`,
      method: "delete",
      data: ids,
    });
  },

  // 批量启用/停用
  batchAgMcpServer(body: BatchType) {
    return request<ApiResponse>({
      url: `${API_PATH}/available/setting`,
      method: "patch",
      data: body,
    });
  },

  // 导出
  exportAgMcpServer(query: AgMcpServerPageQuery) {
    return request<Blob>({
      url: `${API_PATH}/export`,
      method: "post",
      data: query,
      responseType: "blob",
    });
  },

  // 下载导入模板
  downloadTemplateAgMcpServer() {
    return request<Blob>({
      url: `${API_PATH}/download/template`,
      method: "post",
      responseType: "blob",
    });
  },

  // 导入
  importAgMcpServer(body: FormData) {
    return request<ApiResponse>({
      url: `${API_PATH}/import`,
      method: "post",
      data: body,
      headers: { "Content-Type": "multipart/form-data" },
    });
  },
};

export default AgMcpServerAPI;

// ------------------------------
// TS 类型声明
// ------------------------------

// 列表查询参数
export interface AgMcpServerPageQuery extends PageQuery {
  name?: string;
  transport?: string;
  command?: string;
  url?: string;
  env_config?: Record<string, any>;
  include_tools?: string;
  exclude_tools?: string;
  tool_name_prefix?: string;
  timeout_seconds?: string;
  refresh_connection?: string;
  status?: string;
  created_id?: number;
  updated_id?: number;
  created_time?: string[];
  updated_time?: string[];
}

// 列表展示项
export interface AgMcpServerTable extends BaseType {
  name?: string;
  transport?: string;
  command?: string;
  url?: string;
  env_config?: Record<string, any>;
  include_tools?: string;
  exclude_tools?: string;
  tool_name_prefix?: string;
  timeout_seconds?: string;
  refresh_connection?: string;
  created_id?: string;
  updated_id?: string;
  created_by?: CommonType;
  updated_by?: CommonType;
}

// 新增/修改/详情表单参数
export interface AgMcpServerForm extends BaseFormType {
  name?: string;
  transport?: string;
  command?: string;
  url?: string;
  env_config?: Record<string, any>;
  include_tools?: string;
  exclude_tools?: string;
  tool_name_prefix?: string;
  timeout_seconds?: string;
  refresh_connection?: string;
}
