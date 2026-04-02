import request from "@/utils/request";

const API_PATH = "/agno_manage/models/agno/providers";

const ProviderAPI = {
  // 列表查询
  listProvider(query: ProviderPageQuery) {
    return request<ApiResponse<Provider[]>>({
      url: `${API_PATH}/`,
      method: "get",
      params: query,
    });
  },
};

export default ProviderAPI;

// ------------------------------
// TS 类型声明
// ------------------------------

// 列表查询参数
export interface ProviderPageQuery {
  // 目前API返回固定数据，查询参数可能不需要
}

// 模型提供商信息
export interface Provider {
  provider: string;
  label: string;
  agno_class: string;
  agno_module: string;
  needs_api_key: boolean;
  needs_base_url: boolean;
  base_url_label: string;
  description: string;
  popular_models: string[];
}

// 新增/修改/详情表单参数（暂时保留，如需使用可根据实际需求调整）
export interface ProviderForm {
  name?: string;
  model_id?: string;
  api_key?: string;
  base_url?: string;
}
