import request from "@/utils/request";

const API_PATH = "/agno_manage_v2/v2/resources";
const SCHEMA_PATH = "/agno_manage_v2/v2/schema";

const ResourceAPI = {
  // ── 资源 CRUD ──────────────────────────────────────────────────

  listResources(query: ResourcePageQuery) {
    return request<ApiResponse<PageResult<ResourceTable[]>>>({
      url: `${API_PATH}/list`,
      method: "get",
      params: query,
    });
  },

  detailResource(id: number) {
    return request<ApiResponse<ResourceTable>>({
      url: `${API_PATH}/detail/${id}`,
      method: "get",
    });
  },

  createResource(body: ResourceForm) {
    return request<ApiResponse<ResourceTable>>({
      url: `${API_PATH}/create`,
      method: "post",
      data: body,
    });
  },

  updateResource(id: number, body: ResourceForm) {
    return request<ApiResponse<ResourceTable>>({
      url: `${API_PATH}/update/${id}`,
      method: "put",
      data: body,
    });
  },

  deleteResources(ids: number[]) {
    return request<ApiResponse>({
      url: `${API_PATH}/delete`,
      method: "delete",
      data: ids,
    });
  },

  batchSetAvailable(body: BatchType) {
    return request<ApiResponse>({
      url: `${API_PATH}/available/setting`,
      method: "patch",
      data: body,
    });
  },

  // ── Schema ────────────────────────────────────────────────────

  /** 不传参数 → 所有 category 列表 */
  getSchemaCategories() {
    return request<ApiResponse<{ category: string[] }>>({
      url: SCHEMA_PATH,
      method: "get",
    });
  },

  /** 只传 category → 该 category 下的 type 列表 */
  getSchemaTypes(category: string) {
    return request<ApiResponse<{ category: string; types: SchemaType[] }>>({
      url: SCHEMA_PATH,
      method: "get",
      params: { category },
    });
  },

  /** category + type → 完整字段 schema */
  getSchemaFields(category: string, type: string) {
    return request<ApiResponse<SchemaResult>>({
      url: SCHEMA_PATH,
      method: "get",
      params: { category, type },
    });
  },
};

export default ResourceAPI;

// ═══════════════════════════════════════════════════════════════
// TS 类型声明
// ═══════════════════════════════════════════════════════════════

export interface ResourcePageQuery extends PageQuery {
  name?: string;
  category?: string;
  type?: string;
  status?: string;
  uuid?: string;
}

export interface ResourceTable extends BaseType {
  name?: string;
  category?: string;
  type?: string;
  config?: Record<string, any>;
  created_by?: CommonType;
  updated_by?: CommonType;
}

export interface ResourceForm {
  id?: number;
  name: string;
  category: string;
  type: string;
  config: Record<string, any>;
  status?: string;
  description?: string;
}

export interface SchemaType {
  type: string;
  label: string;
}

export interface FieldSchema {
  name: string;
  /** str | int | float | bool | password | select | ref_or_inline | ref_or_inline_array */
  type: string;
  label?: string;
  group?: string;
  order?: number;
  /** el-col span 1-24 */
  span?: number;
  hidden?: boolean;
  placeholder?: string;
  tooltip?: string;
  required?: boolean;
  default?: any;
  omit_if_default?: boolean;
  min?: number;
  max?: number;
  step?: number;
  min_length?: number;
  max_length?: number;
  options?: Array<{ value: string | number; label: string }>;
  /** ref_or_inline: 资源来源 category */
  source?: string;
  /** ref_or_inline: override 时允许覆盖的字段 */
  overridable_fields?: string[];
  /** select 联动：选项值 → 显示的字段名列表 */
  affects?: Record<string, string[]>;
  /** 条件显示：{ 字段名: 期望值 } */
  depends_on?: Record<string, any>;
}

export interface SchemaResult {
  category: string;
  type: string;
  label: string;
  fields: FieldSchema[];
}
