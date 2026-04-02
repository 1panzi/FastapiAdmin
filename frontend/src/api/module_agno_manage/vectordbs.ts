import request from "@/utils/request";

const API_PATH = "/agno_manage/vectordbs";

const AgVectordbAPI = {
  // 列表查询
  listAgVectordb(query: AgVectordbPageQuery) {
    return request<ApiResponse<PageResult<AgVectordbTable[]>>>({
      url: `${API_PATH}/list`,
      method: "get",
      params: query,
    });
  },

  // 详情查询
  detailAgVectordb(id: number) {
    return request<ApiResponse<AgVectordbTable>>({
      url: `${API_PATH}/detail/${id}`,
      method: "get",
    });
  },

  // 新增
  createAgVectordb(body: AgVectordbForm) {
    return request<ApiResponse>({
      url: `${API_PATH}/create`,
      method: "post",
      data: body,
    });
  },

  // 修改（带主键）
  updateAgVectordb(id: number, body: AgVectordbForm) {
    return request<ApiResponse>({
      url: `${API_PATH}/update/${id}`,
      method: "put",
      data: body,
    });
  },

  // 删除（支持批量）
  deleteAgVectordb(ids: number[]) {
    return request<ApiResponse>({
      url: `${API_PATH}/delete`,
      method: "delete",
      data: ids,
    });
  },

  // 批量启用/停用
  batchAgVectordb(body: BatchType) {
    return request<ApiResponse>({
      url: `${API_PATH}/available/setting`,
      method: "patch",
      data: body,
    });
  },

  // 导出
  exportAgVectordb(query: AgVectordbPageQuery) {
    return request<Blob>({
      url: `${API_PATH}/export`,
      method: "post",
      data: query,
      responseType: "blob",
    });
  },

  // 下载导入模板
  downloadTemplateAgVectordb() {
    return request<Blob>({
      url: `${API_PATH}/download/template`,
      method: "post",
      responseType: "blob",
    });
  },

  // 导入
  importAgVectordb(body: FormData) {
    return request<ApiResponse>({
      url: `${API_PATH}/import`,
      method: "post",
      data: body,
      headers: { "Content-Type": "multipart/form-data" },
    });
  },
};

export default AgVectordbAPI;

// ------------------------------
// TS 类型声明
// ------------------------------

// 列表查询参数
export interface AgVectordbPageQuery extends PageQuery {
  name?: string;
  provider?: string;
  embedder_id?: string;
  config?: string;
  status?: string;
  created_id?: number;
  updated_id?: number;
  created_time?: string[];
  updated_time?: string[];
}

// 列表展示项
export interface AgVectordbTable extends BaseType {
  name?: string;
  provider?: string;
  embedder_id?: string;
  config?: Record<string, any>;
  created_id?: string;
  updated_id?: string;
  created_by?: CommonType;
  updated_by?: CommonType;
}

// 新增/修改/详情表单参数
export interface AgVectordbForm extends BaseFormType {
  name?: string;
  provider?: string;
  embedder_id?: string;
  config?: Record<string, any>;
}
