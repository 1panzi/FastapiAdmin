/**
 * Agno 代理接口专用请求实例
 *
 * Agno API 响应不遵循后台管理的 { code, data, msg } 格式，
 * 直接返回业务数据（如 { data: [], meta: {} }），
 * 因此跳过 code 检查，只处理 HTTP 级别的错误。
 */
import axios, {
  type InternalAxiosRequestConfig,
  type AxiosResponse,
  type AxiosError,
} from "axios";
import qs from "qs";
import { Auth } from "@/utils/auth";

const agnoRequest = axios.create({
  baseURL: import.meta.env.VITE_APP_BASE_API,
  timeout: import.meta.env.VITE_TIMEOUT,
  headers: { "Content-Type": "application/json;charset=utf-8" },
  paramsSerializer: (params) => qs.stringify(params, { indices: false }),
});

// 注入 Bearer token
agnoRequest.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    const accessToken = Auth.getAccessToken();
    if (accessToken) config.headers.Authorization = `Bearer ${accessToken}`;
    return config;
  },
  (error) => Promise.reject(error)
);

// 响应拦截：只处理 HTTP 错误，直接返回数据
agnoRequest.interceptors.response.use(
  (response: AxiosResponse) => response,
  (error: AxiosError) => {
    const status = error.response?.status;
    const detail = (error.response?.data as any)?.detail;
    const msg = detail
      ? typeof detail === "string" ? detail : JSON.stringify(detail)
      : `请求失败 (${status ?? "网络错误"})`;
    ElMessage.error(msg);
    return Promise.reject(error);
  }
);

export default agnoRequest;
