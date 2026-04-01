import request from "@/utils/request";

const API_PATH = "/agno_manage/sess_summary_configs";

const AgSessSummaryConfigAPI = {
  // 列表查询
  listAgSessSummaryConfig(query: AgSessSummaryConfigPageQuery) {
    return request<ApiResponse<PageResult<AgSessSummaryConfigTable[]>>>({
      url: `${API_PATH}/list`,
      method: "get",
      params: query,
    });
  },

  // 详情查询
  detailAgSessSummaryConfig(id: number) {
    return request<ApiResponse<AgSessSummaryConfigTable>>({
      url: `${API_PATH}/detail/${id}`,
      method: "get",
    });
  },

  // 新增
  createAgSessSummaryConfig(body: AgSessSummaryConfigForm) {
    return request<ApiResponse>({
      url: `${API_PATH}/create`,
      method: "post",
      data: body,
    });
  },

  // 修改（带主键）
  updateAgSessSummaryConfig(id: number, body: AgSessSummaryConfigForm) {
    return request<ApiResponse>({
      url: `${API_PATH}/update/${id}`,
      method: "put",
      data: body,
    });
  },

  // 删除（支持批量）
  deleteAgSessSummaryConfig(ids: number[]) {
    return request<ApiResponse>({
      url: `${API_PATH}/delete`,
      method: "delete",
      data: ids,
    });
  },

  // 批量启用/停用
  batchAgSessSummaryConfig(body: BatchType) {
    return request<ApiResponse>({
      url: `${API_PATH}/available/setting`,
      method: "patch",
      data: body,
    });
  },

  // 导出
  exportAgSessSummaryConfig(query: AgSessSummaryConfigPageQuery) {
    return request<Blob>({
      url: `${API_PATH}/export`,
      method: "post",
      data: query,
      responseType: "blob",
    });
  },

  // 下载导入模板
  downloadTemplateAgSessSummaryConfig() {
    return request<Blob>({
      url: `${API_PATH}/download/template`,
      method: "post",
      responseType: "blob",
    });
  },

  // 导入
  importAgSessSummaryConfig(body: FormData) {
    return request<ApiResponse>({
      url: `${API_PATH}/import`,
      method: "post",
      data: body,
      headers: { "Content-Type": "multipart/form-data" },
    });
  },
};

export default AgSessSummaryConfigAPI;

// ------------------------------
// TS 类型声明
// ------------------------------

// 列表查询参数
export interface AgSessSummaryConfigPageQuery extends PageQuery {
  name?: string;
  model_id?: string;
  session_summary_prompt?: string;
  summary_request_message?: string;
  status?: string;
  created_id?: number;
  updated_id?: number;
  created_time?: string[];
  updated_time?: string[];
}

// 列表展示项
export interface AgSessSummaryConfigTable extends BaseType {
  name?: string;
  model_id?: string;
  session_summary_prompt?: string;
  summary_request_message?: string;
  created_id?: string;
  updated_id?: string;
  created_by?: CommonType;
  updated_by?: CommonType;
}

// 新增/修改/详情表单参数
export interface AgSessSummaryConfigForm extends BaseFormType {
  name?: string;
  model_id?: string;
  session_summary_prompt?: string;
  summary_request_message?: string;
}
