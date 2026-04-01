import request from "@/utils/request";

const API_PATH = "/agno_manage/skills";

const AgSkillAPI = {
  // 列表查询
  listAgSkill(query: AgSkillPageQuery) {
    return request<ApiResponse<PageResult<AgSkillTable[]>>>({
      url: `${API_PATH}/list`,
      method: "get",
      params: query,
    });
  },

  // 详情查询
  detailAgSkill(id: number) {
    return request<ApiResponse<AgSkillTable>>({
      url: `${API_PATH}/detail/${id}`,
      method: "get",
    });
  },

  // 新增
  createAgSkill(body: AgSkillForm) {
    return request<ApiResponse>({
      url: `${API_PATH}/create`,
      method: "post",
      data: body,
    });
  },

  // 修改（带主键）
  updateAgSkill(id: number, body: AgSkillForm) {
    return request<ApiResponse>({
      url: `${API_PATH}/update/${id}`,
      method: "put",
      data: body,
    });
  },

  // 删除（支持批量）
  deleteAgSkill(ids: number[]) {
    return request<ApiResponse>({
      url: `${API_PATH}/delete`,
      method: "delete",
      data: ids,
    });
  },

  // 批量启用/停用
  batchAgSkill(body: BatchType) {
    return request<ApiResponse>({
      url: `${API_PATH}/available/setting`,
      method: "patch",
      data: body,
    });
  },

  // 导出
  exportAgSkill(query: AgSkillPageQuery) {
    return request<Blob>({
      url: `${API_PATH}/export`,
      method: "post",
      data: query,
      responseType: "blob",
    });
  },

  // 下载导入模板
  downloadTemplateAgSkill() {
    return request<Blob>({
      url: `${API_PATH}/download/template`,
      method: "post",
      responseType: "blob",
    });
  },

  // 导入
  importAgSkill(body: FormData) {
    return request<ApiResponse>({
      url: `${API_PATH}/import`,
      method: "post",
      data: body,
      headers: { "Content-Type": "multipart/form-data" },
    });
  },
};

export default AgSkillAPI;

// ------------------------------
// TS 类型声明
// ------------------------------

// 列表查询参数
export interface AgSkillPageQuery extends PageQuery {
  name?: string;
  instructions?: string;
  source_path?: string;
  scripts?: string;
  references?: string;
  allowed_tools?: string;
  metadata?: string;
  status?: string;
  created_id?: number;
  updated_id?: number;
  created_time?: string[];
  updated_time?: string[];
}

// 列表展示项
export interface AgSkillTable extends BaseType {
  name?: string;
  instructions?: string;
  source_path?: string;
  scripts?: string;
  references?: string;
  allowed_tools?: string;
  metadata?: string;
  created_id?: string;
  updated_id?: string;
  created_by?: CommonType;
  updated_by?: CommonType;
}

// 新增/修改/详情表单参数
export interface AgSkillForm extends BaseFormType {
  name?: string;
  instructions?: string;
  source_path?: string;
  scripts?: string;
  references?: string;
  allowed_tools?: string;
  metadata?: string;
}
