import request from "@/utils/request";

const API_PATH = "/agno_manage/schedules";

const AgScheduleAPI = {
  // 列表查询
  listAgSchedule(query: AgSchedulePageQuery) {
    return request<ApiResponse<PageResult<AgScheduleTable[]>>>({
      url: `${API_PATH}/list`,
      method: "get",
      params: query,
    });
  },

  // 详情查询
  detailAgSchedule(id: number) {
    return request<ApiResponse<AgScheduleTable>>({
      url: `${API_PATH}/detail/${id}`,
      method: "get",
    });
  },

  // 新增
  createAgSchedule(body: AgScheduleForm) {
    return request<ApiResponse>({
      url: `${API_PATH}/create`,
      method: "post",
      data: body,
    });
  },

  // 修改（带主键）
  updateAgSchedule(id: number, body: AgScheduleForm) {
    return request<ApiResponse>({
      url: `${API_PATH}/update/${id}`,
      method: "put",
      data: body,
    });
  },

  // 删除（支持批量）
  deleteAgSchedule(ids: number[]) {
    return request<ApiResponse>({
      url: `${API_PATH}/delete`,
      method: "delete",
      data: ids,
    });
  },

  // 批量启用/停用
  batchAgSchedule(body: BatchType) {
    return request<ApiResponse>({
      url: `${API_PATH}/available/setting`,
      method: "patch",
      data: body,
    });
  },

  // 导出
  exportAgSchedule(query: AgSchedulePageQuery) {
    return request<Blob>({
      url: `${API_PATH}/export`,
      method: "post",
      data: query,
      responseType: "blob",
    });
  },

  // 下载导入模板
  downloadTemplateAgSchedule() {
    return request<Blob>({
      url: `${API_PATH}/download/template`,
      method: "post",
      responseType: "blob",
    });
  },

  // 导入
  importAgSchedule(body: FormData) {
    return request<ApiResponse>({
      url: `${API_PATH}/import`,
      method: "post",
      data: body,
      headers: { "Content-Type": "multipart/form-data" },
    });
  },
};

export default AgScheduleAPI;

// ------------------------------
// TS 类型声明
// ------------------------------

// 列表查询参数
export interface AgSchedulePageQuery extends PageQuery {
  name?: string;
  agent_id?: string;
  team_id?: string;
  payload?: string;
  cron_expr?: string;
  timezone?: string;
  timeout_seconds?: string;
  max_retries?: string;
  retry_delay_seconds?: string;
  status?: string;
  created_id?: number;
  updated_id?: number;
  created_time?: string[];
  updated_time?: string[];
}

// 列表展示项
export interface AgScheduleTable extends BaseType {
  name?: string;
  agent_id?: string;
  team_id?: string;
  payload?: string;
  cron_expr?: string;
  timezone?: string;
  timeout_seconds?: string;
  max_retries?: string;
  retry_delay_seconds?: string;
  created_id?: string;
  updated_id?: string;
  created_by?: CommonType;
  updated_by?: CommonType;
}

// 新增/修改/详情表单参数
export interface AgScheduleForm extends BaseFormType {
  name?: string;
  agent_id?: string;
  team_id?: string;
  payload?: string;
  cron_expr?: string;
  timezone?: string;
  timeout_seconds?: string;
  max_retries?: string;
  retry_delay_seconds?: string;
}
