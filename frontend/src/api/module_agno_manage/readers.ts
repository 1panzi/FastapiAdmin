import request from "@/utils/request";

const API_PATH = "/agno_manage/readers";

const AgReaderAPI = {
  // 列表查询
  listAgReader(query: AgReaderPageQuery) {
    return request<ApiResponse<PageResult<AgReaderTable[]>>>({
      url: `${API_PATH}/list`,
      method: "get",
      params: query,
    });
  },

  // 详情查询
  detailAgReader(id: number) {
    return request<ApiResponse<AgReaderTable>>({
      url: `${API_PATH}/detail/${id}`,
      method: "get",
    });
  },

  // 新增
  createAgReader(body: AgReaderForm) {
    return request<ApiResponse>({
      url: `${API_PATH}/create`,
      method: "post",
      data: body,
    });
  },

  // 修改（带主键）
  updateAgReader(id: number, body: AgReaderForm) {
    return request<ApiResponse>({
      url: `${API_PATH}/update/${id}`,
      method: "put",
      data: body,
    });
  },

  // 删除（支持批量）
  deleteAgReader(ids: number[]) {
    return request<ApiResponse>({
      url: `${API_PATH}/delete`,
      method: "delete",
      data: ids,
    });
  },

  // 批量启用/停用
  batchAgReader(body: BatchType) {
    return request<ApiResponse>({
      url: `${API_PATH}/available/setting`,
      method: "patch",
      data: body,
    });
  },

  // 获取Reader类型列表
  listReaderTypes() {
    return request<ApiResponse<AgReaderType[]>>({
      url: `${API_PATH}/agno/reader_types`,
      method: "get",
    });
  },

  // 获取Chunking策略列表
  listChunkingStrategies() {
    return request<ApiResponse<AgChunkingStrategy[]>>({
      url: `${API_PATH}/agno/chunking_strategies`,
      method: "get",
    });
  },

  // 导出
  exportAgReader(query: AgReaderPageQuery) {
    return request<Blob>({
      url: `${API_PATH}/export`,
      method: "post",
      data: query,
      responseType: "blob",
    });
  },

  // 下载导入模板
  downloadTemplateAgReader() {
    return request<Blob>({
      url: `${API_PATH}/download/template`,
      method: "post",
      responseType: "blob",
    });
  },

  // 导入
  importAgReader(body: FormData) {
    return request<ApiResponse>({
      url: `${API_PATH}/import`,
      method: "post",
      data: body,
      headers: { "Content-Type": "multipart/form-data" },
    });
  },
};

export default AgReaderAPI;

// ------------------------------
// TS 类型声明
// ------------------------------

// 列表查询参数
export interface AgReaderPageQuery extends PageQuery {
  name?: string;
  reader_type?: string;
  chunk?: string;
  encoding?: string;
  chunking_strategy?: string;
  embedder_id?: string;
  model_id?: string;
  status?: string;
  created_id?: number;
  updated_id?: number;
  created_time?: string[];
  updated_time?: string[];
}

// 列表展示项
export interface AgReaderTable extends BaseType {
  name?: string;
  reader_type?: string;
  chunk?: boolean | null;
  chunk_size?: number | null;
  encoding?: string;
  chunking_strategy?: string;
  chunk_overlap?: number | null;
  reader_config?: Record<string, any> | null;
  embedder_id?: string;
  model_id?: string;
  created_id?: string;
  updated_id?: string;
  created_by?: CommonType;
  updated_by?: CommonType;
}

// 新增/修改/详情表单参数
export interface AgReaderForm extends BaseFormType {
  name?: string;
  reader_type?: string;
  chunk?: boolean | null;
  chunk_size?: number | null;
  encoding?: string;
  chunking_strategy?: string;
  chunk_overlap?: number | null;
  reader_config?: Record<string, any>;
  embedder_id?: string;
  model_id?: string;
}

// Reader类型元数据
export interface AgReaderType {
  reader_type: string;
  label: string;
  description: string;
}

// Chunking策略元数据
export interface AgChunkingStrategy {
  strategy: string;
  label: string;
  description: string;
}
