import request from "@/utils/request";

const API_PATH = "/agno_manage/embedders/agno/providers";

const EmbedderProviderAPI = {
  // 获取嵌入器提供商列表
  listEmbedderProvider() {
    return request<ApiResponse<EmbedderProvider[]>>({
      url: `${API_PATH}`,
      method: "get",
    });
  },
};

export default EmbedderProviderAPI;

// ------------------------------
// TS 类型声明
// ------------------------------

// 嵌入器提供商信息
export interface EmbedderProvider {
  provider: string;
  label: string;
  agno_class: string;
  agno_module: string;
  needs_api_key: boolean;
  needs_base_url: boolean;
  base_url_label: string;
  description: string;
  popular_models: string[];
  default_dimensions: number | null;
}
