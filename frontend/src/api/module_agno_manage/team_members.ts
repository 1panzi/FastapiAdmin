import request from "@/utils/request";

const API_PATH = "/agno_manage/team_members";

const AgTeamMemberAPI = {
  // 列表查询
  listAgTeamMember(query: AgTeamMemberPageQuery) {
    return request<ApiResponse<PageResult<AgTeamMemberTable[]>>>({
      url: `${API_PATH}/list`,
      method: "get",
      params: query,
    });
  },

  // 详情查询
  detailAgTeamMember(id: number) {
    return request<ApiResponse<AgTeamMemberTable>>({
      url: `${API_PATH}/detail/${id}`,
      method: "get",
    });
  },

  // 新增
  createAgTeamMember(body: AgTeamMemberForm) {
    return request<ApiResponse>({
      url: `${API_PATH}/create`,
      method: "post",
      data: body,
    });
  },

  // 修改（带主键）
  updateAgTeamMember(id: number, body: AgTeamMemberForm) {
    return request<ApiResponse>({
      url: `${API_PATH}/update/${id}`,
      method: "put",
      data: body,
    });
  },

  // 删除（支持批量）
  deleteAgTeamMember(ids: number[]) {
    return request<ApiResponse>({
      url: `${API_PATH}/delete`,
      method: "delete",
      data: ids,
    });
  },

  // 批量启用/停用
  batchAgTeamMember(body: BatchType) {
    return request<ApiResponse>({
      url: `${API_PATH}/available/setting`,
      method: "patch",
      data: body,
    });
  },

  // 导出
  exportAgTeamMember(query: AgTeamMemberPageQuery) {
    return request<Blob>({
      url: `${API_PATH}/export`,
      method: "post",
      data: query,
      responseType: "blob",
    });
  },

  // 下载导入模板
  downloadTemplateAgTeamMember() {
    return request<Blob>({
      url: `${API_PATH}/download/template`,
      method: "post",
      responseType: "blob",
    });
  },

  // 导入
  importAgTeamMember(body: FormData) {
    return request<ApiResponse>({
      url: `${API_PATH}/import`,
      method: "post",
      data: body,
      headers: { "Content-Type": "multipart/form-data" },
    });
  },
};

export default AgTeamMemberAPI;

// ------------------------------
// TS 类型声明
// ------------------------------

// 列表查询参数
export interface AgTeamMemberPageQuery extends PageQuery {
  team_id?: string;
  member_type?: string;
  member_id?: string;
  role?: string;
  member_order?: string;
  status?: string;
  created_id?: number;
  updated_id?: number;
  created_time?: string[];
  updated_time?: string[];
}

// 列表展示项
export interface AgTeamMemberTable extends BaseType {
  team_id?: number | null;
  member_type?: string;
  member_id?: number | null;
  role?: string;
  member_order?: number | null;
  created_id?: string;
  updated_id?: string;
  created_by?: CommonType;
  updated_by?: CommonType;
}

// 新增/修改/详情表单参数
export interface AgTeamMemberForm extends BaseFormType {
  team_id?: string;
  member_type?: string;
  member_id?: string;
  role?: string;
  member_order?: number | null;
}
