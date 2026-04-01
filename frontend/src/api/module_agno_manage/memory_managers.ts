import request from "@/utils/request";

const API_PATH = "/agno_manage/memory_managers";

const AgMemoryManagerAPI = {
  // 列表查询
  listAgMemoryManager(query: AgMemoryManagerPageQuery) {
    return request<ApiResponse<PageResult<AgMemoryManagerTable[]>>>({
      url: `${API_PATH}/list`,
      method: "get",
      params: query,
    });
  },

  // 详情查询
  detailAgMemoryManager(id: number) {
    return request<ApiResponse<AgMemoryManagerTable>>({
      url: `${API_PATH}/detail/${id}`,
      method: "get",
    });
  },

  // 新增
  createAgMemoryManager(body: AgMemoryManagerForm) {
    return request<ApiResponse>({
      url: `${API_PATH}/create`,
      method: "post",
      data: body,
    });
  },

  // 修改（带主键）
  updateAgMemoryManager(id: number, body: AgMemoryManagerForm) {
    return request<ApiResponse>({
      url: `${API_PATH}/update/${id}`,
      method: "put",
      data: body,
    });
  },

  // 删除（支持批量）
  deleteAgMemoryManager(ids: number[]) {
    return request<ApiResponse>({
      url: `${API_PATH}/delete`,
      method: "delete",
      data: ids,
    });
  },

  // 批量启用/停用
  batchAgMemoryManager(body: BatchType) {
    return request<ApiResponse>({
      url: `${API_PATH}/available/setting`,
      method: "patch",
      data: body,
    });
  },

  // 导出
  exportAgMemoryManager(query: AgMemoryManagerPageQuery) {
    return request<Blob>({
      url: `${API_PATH}/export`,
      method: "post",
      data: query,
      responseType: "blob",
    });
  },

  // 下载导入模板
  downloadTemplateAgMemoryManager() {
    return request<Blob>({
      url: `${API_PATH}/download/template`,
      method: "post",
      responseType: "blob",
    });
  },

  // 导入
  importAgMemoryManager(body: FormData) {
    return request<ApiResponse>({
      url: `${API_PATH}/import`,
      method: "post",
      data: body,
      headers: { "Content-Type": "multipart/form-data" },
    });
  },
};

export default AgMemoryManagerAPI;

// ------------------------------
// TS 类型声明
// ------------------------------

// 列表查询参数
export interface AgMemoryManagerPageQuery extends PageQuery {
  name?: string;
  model_id?: string;
  delete_memories?: string;
  update_memories?: string;
  add_memories?: string;
  clear_memories?: string;
  memory_capture_instructions?: string;
  additional_instructions?: string;
  status?: string;
  created_id?: number;
  updated_id?: number;
  created_time?: string[];
  updated_time?: string[];
}

// 列表展示项
export interface AgMemoryManagerTable extends BaseType {
  name?: string;
  model_id?: string;
  delete_memories?: string;
  update_memories?: string;
  add_memories?: string;
  clear_memories?: string;
  memory_capture_instructions?: string;
  additional_instructions?: string;
  created_id?: string;
  updated_id?: string;
  created_by?: CommonType;
  updated_by?: CommonType;
}

// 新增/修改/详情表单参数
export interface AgMemoryManagerForm extends BaseFormType {
  name?: string;
  model_id?: string;
  delete_memories?: string;
  update_memories?: string;
  add_memories?: string;
  clear_memories?: string;
  memory_capture_instructions?: string;
  additional_instructions?: string;
}
