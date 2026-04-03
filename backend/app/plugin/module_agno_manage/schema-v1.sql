-- ============================================================
-- Platform Schema — 统一建表规范
-- 规则：SERIAL主键 + uuid + status(0启用/1禁用) + timestamp without time zone + created_id/updated_id
-- ============================================================

-- ──────────────────────────────────────────────────────────
-- 5.1 ag_models（模型管理）
-- ──────────────────────────────────────────────────────────
CREATE TABLE ag_models (
    id            SERIAL NOT NULL,
    uuid          varchar(64) NOT NULL,
    name          varchar(255) NOT NULL,
    model_id      varchar(255) NOT NULL,
    provider      varchar(50) NOT NULL,
    api_key       text,
    base_url      varchar(500),
    config        jsonb NOT NULL DEFAULT '{}',
    status        varchar(10) NOT NULL DEFAULT '0',
    description   text,
    created_time  timestamp without time zone NOT NULL,
    updated_time  timestamp without time zone NOT NULL,
    created_id    integer,
    updated_id    integer,
    PRIMARY KEY(id),
    CONSTRAINT ag_models_created_id_fkey FOREIGN KEY(created_id) REFERENCES sys_user(id),
    CONSTRAINT ag_models_updated_id_fkey FOREIGN KEY(updated_id) REFERENCES sys_user(id)
);
CREATE UNIQUE INDEX ag_models_uuid_key      ON public.ag_models USING btree (uuid);
CREATE INDEX ix_ag_models_provider          ON public.ag_models USING btree (provider);
CREATE INDEX ix_ag_models_status            ON public.ag_models USING btree (status);
CREATE INDEX ix_ag_models_created_id        ON public.ag_models USING btree (created_id);
CREATE INDEX ix_ag_models_updated_id        ON public.ag_models USING btree (updated_id);

COMMENT ON TABLE  ag_models                 IS '平台模型管理表';
COMMENT ON COLUMN ag_models.id              IS '主键ID';
COMMENT ON COLUMN ag_models.uuid            IS 'UUID全局唯一标识';
COMMENT ON COLUMN ag_models.name            IS '模型名称';
COMMENT ON COLUMN ag_models.model_id        IS '模型标识符（传给Agno Model的id参数）';
COMMENT ON COLUMN ag_models.provider        IS '模型提供商(openai/anthropic/google/ollama/deepseek)';
COMMENT ON COLUMN ag_models.api_key         IS 'API密钥（明文存储）';
COMMENT ON COLUMN ag_models.base_url        IS '自定义API地址（用于ollama/vllm/lmstudio）';
COMMENT ON COLUMN ag_models.config          IS '模型配置参数（temperature/max_tokens/top_p等）';
COMMENT ON COLUMN ag_models.status          IS '是否启用(0:启用 1:禁用)';
COMMENT ON COLUMN ag_models.description     IS '备注/描述';
COMMENT ON COLUMN ag_models.created_time    IS '创建时间';
COMMENT ON COLUMN ag_models.updated_time    IS '更新时间';
COMMENT ON COLUMN ag_models.created_id      IS '创建人ID';
COMMENT ON COLUMN ag_models.updated_id      IS '更新人ID';


-- ──────────────────────────────────────────────────────────
-- 5.2 ag_embedders（嵌入模型管理）
-- ──────────────────────────────────────────────────────────
CREATE TABLE ag_embedders (
    id            SERIAL NOT NULL,
    uuid          varchar(64) NOT NULL,
    name          varchar(255) NOT NULL,
    provider      varchar(50) NOT NULL,
    model_id      varchar(255) NOT NULL,
    api_key       text,
    base_url      varchar(500),
    dimensions    integer,
    config        jsonb NOT NULL DEFAULT '{}',
    status        varchar(10) NOT NULL DEFAULT '0',
    description   text,
    created_time  timestamp without time zone NOT NULL,
    updated_time  timestamp without time zone NOT NULL,
    created_id    integer,
    updated_id    integer,
    PRIMARY KEY(id),
    CONSTRAINT ag_embedders_created_id_fkey FOREIGN KEY(created_id) REFERENCES sys_user(id),
    CONSTRAINT ag_embedders_updated_id_fkey FOREIGN KEY(updated_id) REFERENCES sys_user(id)
);
CREATE UNIQUE INDEX ag_embedders_uuid_key   ON public.ag_embedders USING btree (uuid);
CREATE INDEX ix_ag_embedders_provider       ON public.ag_embedders USING btree (provider);
CREATE INDEX ix_ag_embedders_status         ON public.ag_embedders USING btree (status);
CREATE INDEX ix_ag_embedders_created_id     ON public.ag_embedders USING btree (created_id);
CREATE INDEX ix_ag_embedders_updated_id     ON public.ag_embedders USING btree (updated_id);

COMMENT ON TABLE  ag_embedders              IS '嵌入模型管理表';
COMMENT ON COLUMN ag_embedders.id           IS '主键ID';
COMMENT ON COLUMN ag_embedders.uuid         IS 'UUID全局唯一标识';
COMMENT ON COLUMN ag_embedders.name         IS '嵌入器名称';
COMMENT ON COLUMN ag_embedders.provider     IS '提供商(openai/azure/ollama/cohere/google/huggingface等)';
COMMENT ON COLUMN ag_embedders.model_id     IS '嵌入模型标识（如text-embedding-3-small）';
COMMENT ON COLUMN ag_embedders.api_key      IS 'API密钥';
COMMENT ON COLUMN ag_embedders.base_url     IS '自定义端点地址（openai_like/ollama/vllm）';
COMMENT ON COLUMN ag_embedders.dimensions   IS '向量维度';
COMMENT ON COLUMN ag_embedders.config       IS '其他构造参数（azure api_version/cohere input_type等）';
COMMENT ON COLUMN ag_embedders.status       IS '是否启用(0:启用 1:禁用)';
COMMENT ON COLUMN ag_embedders.description  IS '备注/描述';
COMMENT ON COLUMN ag_embedders.created_time IS '创建时间';
COMMENT ON COLUMN ag_embedders.updated_time IS '更新时间';
COMMENT ON COLUMN ag_embedders.created_id   IS '创建人ID';
COMMENT ON COLUMN ag_embedders.updated_id   IS '更新人ID';


-- ──────────────────────────────────────────────────────────
-- 5.3 ag_vectordbs（向量数据库管理）
-- ──────────────────────────────────────────────────────────
CREATE TABLE ag_vectordbs (
    id            SERIAL NOT NULL,
    uuid          varchar(64) NOT NULL,
    name          varchar(255) NOT NULL,
    provider      varchar(50) NOT NULL,
    embedder_id   integer NOT NULL,
    config        jsonb NOT NULL DEFAULT '{}',
    status        varchar(10) NOT NULL DEFAULT '0',
    description   text,
    created_time  timestamp without time zone NOT NULL,
    updated_time  timestamp without time zone NOT NULL,
    created_id    integer,
    updated_id    integer,
    PRIMARY KEY(id),
    CONSTRAINT ag_vectordbs_embedder_id_fkey FOREIGN KEY(embedder_id) REFERENCES ag_embedders(id),
    CONSTRAINT ag_vectordbs_created_id_fkey  FOREIGN KEY(created_id)  REFERENCES sys_user(id),
    CONSTRAINT ag_vectordbs_updated_id_fkey  FOREIGN KEY(updated_id)  REFERENCES sys_user(id)
);
CREATE UNIQUE INDEX ag_vectordbs_uuid_key   ON public.ag_vectordbs USING btree (uuid);
CREATE INDEX ix_ag_vectordbs_provider       ON public.ag_vectordbs USING btree (provider);
CREATE INDEX ix_ag_vectordbs_embedder_id    ON public.ag_vectordbs USING btree (embedder_id);
CREATE INDEX ix_ag_vectordbs_status         ON public.ag_vectordbs USING btree (status);
CREATE INDEX ix_ag_vectordbs_created_id     ON public.ag_vectordbs USING btree (created_id);
CREATE INDEX ix_ag_vectordbs_updated_id     ON public.ag_vectordbs USING btree (updated_id);

COMMENT ON TABLE  ag_vectordbs              IS '向量数据库管理表';
COMMENT ON COLUMN ag_vectordbs.id           IS '主键ID';
COMMENT ON COLUMN ag_vectordbs.uuid         IS 'UUID全局唯一标识';
COMMENT ON COLUMN ag_vectordbs.name         IS '向量库名称';
COMMENT ON COLUMN ag_vectordbs.provider     IS '向量库类型(pgvector/qdrant/chroma/pinecone/milvus等)';
COMMENT ON COLUMN ag_vectordbs.embedder_id  IS '关联嵌入模型ID';
COMMENT ON COLUMN ag_vectordbs.config       IS '连接配置（table_name/collection/url等，按provider不同）';
COMMENT ON COLUMN ag_vectordbs.status       IS '是否启用(0:启用 1:禁用)';
COMMENT ON COLUMN ag_vectordbs.description  IS '备注/描述';
COMMENT ON COLUMN ag_vectordbs.created_time IS '创建时间';
COMMENT ON COLUMN ag_vectordbs.updated_time IS '更新时间';
COMMENT ON COLUMN ag_vectordbs.created_id   IS '创建人ID';
COMMENT ON COLUMN ag_vectordbs.updated_id   IS '更新人ID';


-- ──────────────────────────────────────────────────────────
-- 5.4 ag_mcp_servers（MCP服务管理）
-- ──────────────────────────────────────────────────────────
CREATE TABLE ag_mcp_servers (
    id                 SERIAL NOT NULL,
    uuid               varchar(64) NOT NULL,
    name               varchar(255) NOT NULL,
    transport          varchar(20) NOT NULL,
    command            text,
    url                varchar(500),
    env_config         jsonb NOT NULL DEFAULT '{}',
    include_tools      jsonb,
    exclude_tools      jsonb,
    tool_name_prefix   varchar(100),
    timeout_seconds    integer NOT NULL DEFAULT 10,
    refresh_connection boolean NOT NULL DEFAULT false,
    status             varchar(10) NOT NULL DEFAULT '0',
    description        text,
    created_time       timestamp without time zone NOT NULL,
    updated_time       timestamp without time zone NOT NULL,
    created_id         integer,
    updated_id         integer,
    PRIMARY KEY(id),
    CONSTRAINT ag_mcp_servers_created_id_fkey FOREIGN KEY(created_id) REFERENCES sys_user(id),
    CONSTRAINT ag_mcp_servers_updated_id_fkey FOREIGN KEY(updated_id) REFERENCES sys_user(id)
);
CREATE UNIQUE INDEX ag_mcp_servers_uuid_key   ON public.ag_mcp_servers USING btree (uuid);
CREATE INDEX ix_ag_mcp_servers_transport      ON public.ag_mcp_servers USING btree (transport);
CREATE INDEX ix_ag_mcp_servers_status         ON public.ag_mcp_servers USING btree (status);
CREATE INDEX ix_ag_mcp_servers_created_id     ON public.ag_mcp_servers USING btree (created_id);
CREATE INDEX ix_ag_mcp_servers_updated_id     ON public.ag_mcp_servers USING btree (updated_id);

COMMENT ON TABLE  ag_mcp_servers                  IS 'MCP服务管理表';
COMMENT ON COLUMN ag_mcp_servers.id               IS '主键ID';
COMMENT ON COLUMN ag_mcp_servers.uuid             IS 'UUID全局唯一标识';
COMMENT ON COLUMN ag_mcp_servers.name             IS 'MCP服务名称';
COMMENT ON COLUMN ag_mcp_servers.transport        IS '传输协议(stdio/sse/streamable-http)';
COMMENT ON COLUMN ag_mcp_servers.command          IS 'stdio启动命令';
COMMENT ON COLUMN ag_mcp_servers.url              IS 'HTTP/SSE服务地址';
COMMENT ON COLUMN ag_mcp_servers.env_config       IS '环境变量配置';
COMMENT ON COLUMN ag_mcp_servers.include_tools    IS '仅包含的工具列表';
COMMENT ON COLUMN ag_mcp_servers.exclude_tools    IS '排除的工具列表';
COMMENT ON COLUMN ag_mcp_servers.tool_name_prefix IS '工具名称前缀';
COMMENT ON COLUMN ag_mcp_servers.timeout_seconds  IS '连接超时秒数';
COMMENT ON COLUMN ag_mcp_servers.refresh_connection IS '是否刷新连接';
COMMENT ON COLUMN ag_mcp_servers.status           IS '是否启用(0:启用 1:禁用)';
COMMENT ON COLUMN ag_mcp_servers.description      IS '备注/描述';
COMMENT ON COLUMN ag_mcp_servers.created_time     IS '创建时间';
COMMENT ON COLUMN ag_mcp_servers.updated_time     IS '更新时间';
COMMENT ON COLUMN ag_mcp_servers.created_id       IS '创建人ID';
COMMENT ON COLUMN ag_mcp_servers.updated_id       IS '更新人ID';


-- ──────────────────────────────────────────────────────────
-- 5.5 ag_toolkits（工具包管理）
-- ──────────────────────────────────────────────────────────
CREATE TABLE ag_toolkits (
    id                    SERIAL NOT NULL,
    uuid                  varchar(64) NOT NULL,
    name                  varchar(255) NOT NULL,
    type                  varchar(20) NOT NULL,
    module_path           varchar(500) NOT NULL,
    class_name            varchar(255),
    func_name             varchar(255),
    config                jsonb NOT NULL DEFAULT '{}',
    instructions          text,
    requires_confirmation boolean NOT NULL DEFAULT false,
    approval_type         varchar(20),
    stop_after_call       boolean NOT NULL DEFAULT false,
    show_result           boolean NOT NULL DEFAULT false,
    cache_results         boolean NOT NULL DEFAULT false,
    cache_ttl             integer NOT NULL DEFAULT 3600,
    status                varchar(10) NOT NULL DEFAULT '0',
    description           text,
    created_time          timestamp without time zone NOT NULL,
    updated_time          timestamp without time zone NOT NULL,
    created_id            integer,
    updated_id            integer,
    PRIMARY KEY(id),
    CONSTRAINT ag_toolkits_created_id_fkey FOREIGN KEY(created_id) REFERENCES sys_user(id),
    CONSTRAINT ag_toolkits_updated_id_fkey FOREIGN KEY(updated_id) REFERENCES sys_user(id)
);
CREATE UNIQUE INDEX ag_toolkits_uuid_key    ON public.ag_toolkits USING btree (uuid);
CREATE INDEX ix_ag_toolkits_type            ON public.ag_toolkits USING btree (type);
CREATE INDEX ix_ag_toolkits_status          ON public.ag_toolkits USING btree (status);
CREATE INDEX ix_ag_toolkits_created_id      ON public.ag_toolkits USING btree (created_id);
CREATE INDEX ix_ag_toolkits_updated_id      ON public.ag_toolkits USING btree (updated_id);

COMMENT ON TABLE  ag_toolkits                      IS '工具包管理表';
COMMENT ON COLUMN ag_toolkits.id                   IS '主键ID';
COMMENT ON COLUMN ag_toolkits.uuid                 IS 'UUID全局唯一标识';
COMMENT ON COLUMN ag_toolkits.name                 IS '工具包名称';
COMMENT ON COLUMN ag_toolkits.type                 IS '类型(toolkit:整个类 function:单个函数)';
COMMENT ON COLUMN ag_toolkits.module_path          IS 'Python模块路径';
COMMENT ON COLUMN ag_toolkits.class_name           IS '类名（type=toolkit时使用）';
COMMENT ON COLUMN ag_toolkits.func_name            IS '函数名（type=function时使用）';
COMMENT ON COLUMN ag_toolkits.config               IS '初始化参数';
COMMENT ON COLUMN ag_toolkits.instructions         IS '工具使用说明';
COMMENT ON COLUMN ag_toolkits.requires_confirmation IS '是否需要确认';
COMMENT ON COLUMN ag_toolkits.approval_type        IS '审批类型(NULL/required/audit)';
COMMENT ON COLUMN ag_toolkits.stop_after_call      IS '调用后是否停止';
COMMENT ON COLUMN ag_toolkits.show_result          IS '是否展示结果';
COMMENT ON COLUMN ag_toolkits.cache_results        IS '是否缓存结果';
COMMENT ON COLUMN ag_toolkits.cache_ttl            IS '缓存TTL秒数';
COMMENT ON COLUMN ag_toolkits.status               IS '是否启用(0:启用 1:禁用)';
COMMENT ON COLUMN ag_toolkits.description          IS '备注/描述';
COMMENT ON COLUMN ag_toolkits.created_time         IS '创建时间';
COMMENT ON COLUMN ag_toolkits.updated_time         IS '更新时间';
COMMENT ON COLUMN ag_toolkits.created_id           IS '创建人ID';
COMMENT ON COLUMN ag_toolkits.updated_id           IS '更新人ID';


-- ──────────────────────────────────────────────────────────
-- 5.6 ag_skills（技能管理）
-- ──────────────────────────────────────────────────────────
CREATE TABLE ag_skills (
    id            SERIAL NOT NULL,
    uuid          varchar(64) NOT NULL,
    name          varchar(255) NOT NULL,
    instructions  text NOT NULL,
    source_path   varchar(500),
    scripts       jsonb NOT NULL DEFAULT '[]',
    "references"  jsonb NOT NULL DEFAULT '[]',
    allowed_tools jsonb,
    metadata_config      jsonb NOT NULL DEFAULT '{}',
    status        varchar(10) NOT NULL DEFAULT '0',
    description   text,
    created_time  timestamp without time zone NOT NULL,
    updated_time  timestamp without time zone NOT NULL,
    created_id    integer,
    updated_id    integer,
    PRIMARY KEY(id),
    CONSTRAINT ag_skills_created_id_fkey FOREIGN KEY(created_id) REFERENCES sys_user(id),
    CONSTRAINT ag_skills_updated_id_fkey FOREIGN KEY(updated_id) REFERENCES sys_user(id)
);
CREATE UNIQUE INDEX ag_skills_uuid_key   ON public.ag_skills USING btree (uuid);
CREATE INDEX ix_ag_skills_status         ON public.ag_skills USING btree (status);
CREATE INDEX ix_ag_skills_created_id     ON public.ag_skills USING btree (created_id);
CREATE INDEX ix_ag_skills_updated_id     ON public.ag_skills USING btree (updated_id);

COMMENT ON TABLE  ag_skills                IS '技能管理表';
COMMENT ON COLUMN ag_skills.id             IS '主键ID';
COMMENT ON COLUMN ag_skills.uuid           IS 'UUID全局唯一标识';
COMMENT ON COLUMN ag_skills.name           IS '技能名称';
COMMENT ON COLUMN ag_skills.instructions   IS '注入Agent system prompt的技能指令';
COMMENT ON COLUMN ag_skills.source_path    IS '本地磁盘路径（可选）';
COMMENT ON COLUMN ag_skills.scripts        IS '脚本文件名列表';
COMMENT ON COLUMN ag_skills."references"   IS '参考文件名列表';
COMMENT ON COLUMN ag_skills.allowed_tools  IS '允许使用的工具列表';
COMMENT ON COLUMN ag_skills.metadata_config       IS '元数据';
COMMENT ON COLUMN ag_skills.status         IS '是否启用(0:启用 1:禁用)';
COMMENT ON COLUMN ag_skills.description    IS '备注/描述';
COMMENT ON COLUMN ag_skills.created_time   IS '创建时间';
COMMENT ON COLUMN ag_skills.updated_time   IS '更新时间';
COMMENT ON COLUMN ag_skills.created_id     IS '创建人ID';
COMMENT ON COLUMN ag_skills.updated_id     IS '更新人ID';


-- ──────────────────────────────────────────────────────────
-- 5.7 ag_knowledge_bases（知识库管理）
-- ──────────────────────────────────────────────────────────
CREATE TABLE ag_knowledge_bases (
    id                      SERIAL NOT NULL,
    uuid                    varchar(64) NOT NULL,
    name                    varchar(255) NOT NULL,
    vectordb_id             integer NOT NULL,
    max_results             integer NOT NULL DEFAULT 10,
    isolate_vector_search   boolean NOT NULL DEFAULT false,
    status                  varchar(10) NOT NULL DEFAULT '0',
    description             text,
    created_time            timestamp without time zone NOT NULL,
    updated_time            timestamp without time zone NOT NULL,
    created_id              integer,
    updated_id              integer,
    PRIMARY KEY(id),
    CONSTRAINT ag_knowledge_bases_vectordb_id_fkey FOREIGN KEY(vectordb_id) REFERENCES ag_vectordbs(id),
    CONSTRAINT ag_knowledge_bases_created_id_fkey  FOREIGN KEY(created_id)  REFERENCES sys_user(id),
    CONSTRAINT ag_knowledge_bases_updated_id_fkey  FOREIGN KEY(updated_id)  REFERENCES sys_user(id)
);
CREATE UNIQUE INDEX ag_knowledge_bases_uuid_key  ON public.ag_knowledge_bases USING btree (uuid);
CREATE INDEX ix_ag_knowledge_bases_vectordb_id   ON public.ag_knowledge_bases USING btree (vectordb_id);
CREATE INDEX ix_ag_knowledge_bases_status        ON public.ag_knowledge_bases USING btree (status);
CREATE INDEX ix_ag_knowledge_bases_created_id    ON public.ag_knowledge_bases USING btree (created_id);
CREATE INDEX ix_ag_knowledge_bases_updated_id    ON public.ag_knowledge_bases USING btree (updated_id);

COMMENT ON TABLE  ag_knowledge_bases                         IS '知识库管理表';
COMMENT ON COLUMN ag_knowledge_bases.id                      IS '主键ID';
COMMENT ON COLUMN ag_knowledge_bases.uuid                    IS 'UUID全局唯一标识';
COMMENT ON COLUMN ag_knowledge_bases.name                    IS '知识库名称';
COMMENT ON COLUMN ag_knowledge_bases.vectordb_id             IS '关联向量数据库ID';
COMMENT ON COLUMN ag_knowledge_bases.max_results             IS '最大检索结果数（Knowledge.max_results）';
COMMENT ON COLUMN ag_knowledge_bases.isolate_vector_search   IS '是否启用向量搜索隔离（多知识库共享同一向量库时按name隔离）';
COMMENT ON COLUMN ag_knowledge_bases.status                  IS '是否启用(0:启用 1:禁用)';
COMMENT ON COLUMN ag_knowledge_bases.description             IS '备注/描述';
COMMENT ON COLUMN ag_knowledge_bases.created_time            IS '创建时间';
COMMENT ON COLUMN ag_knowledge_bases.updated_time            IS '更新时间';
COMMENT ON COLUMN ag_knowledge_bases.created_id              IS '创建人ID';
COMMENT ON COLUMN ag_knowledge_bases.updated_id              IS '更新人ID';


-- ──────────────────────────────────────────────────────────
-- 5.7b ag_readers（文档读取器管理）
-- ──────────────────────────────────────────────────────────
-- Reader 配置独立管理，通过 ag_bindings(resource_type='reader') 关联到知识库。
-- 绑定时可在 config_override 字段中覆盖基础配置，实现知识库级别的参数差异化。
-- Reader 运行时由 registry 在知识库 build 时一次性实例化，不常驻内存缓存。
-- ──────────────────────────────────────────────────────────
CREATE TABLE ag_readers (
    id                  SERIAL NOT NULL,
    uuid                varchar(64) NOT NULL,
    name                varchar(255) NOT NULL,

    -- Reader 类型
    reader_type         varchar(30) NOT NULL,

    -- 基类通用参数（Reader base class）
    chunk               boolean NOT NULL DEFAULT true,
    chunk_size          integer NOT NULL DEFAULT 5000,
    encoding            varchar(30),

    -- Chunking 策略
    -- 枚举值: FixedSizeChunker/RecursiveChunker/DocumentChunker/
    --         MarkdownChunker/RowChunker/SemanticChunker/AgenticChunker/CodeChunker
    chunking_strategy   varchar(30),
    chunk_overlap       integer NOT NULL DEFAULT 0,

    -- Reader 专属参数（按 reader_type 不同而异）
    -- pdf:              {"split_on_pages": true, "sanitize_content": true, "password": null}
    -- excel:            {"sheets": null}
    -- website:          {"max_depth": 3, "max_links": 10, "timeout": 10, "proxy": null}
    -- firecrawl:        {"api_key": "", "mode": "scrape", "params": null}
    -- tavily:           {"api_key": "", "extract_format": "markdown", "extract_depth": "basic"}
    -- arxiv:            {"sort_by": "Relevance"}
    -- wikipedia:        {"auto_suggest": true}
    -- field_labeled_csv:{"chunk_title": null, "field_names": [], "format_headers": true, "skip_empty_fields": true}
    reader_config       jsonb NOT NULL DEFAULT '{}',

    -- 运行时对象引用（可选，用于需要外部模型的 Chunking 策略）
    embedder_id         integer,    -- SemanticChunker 使用
    model_id            integer,    -- AgenticChunker 使用

    status              varchar(10) NOT NULL DEFAULT '0',
    description         text,
    created_time        timestamp without time zone NOT NULL,
    updated_time        timestamp without time zone NOT NULL,
    created_id          integer,
    updated_id          integer,
    PRIMARY KEY(id),
    CONSTRAINT ag_readers_embedder_id_fkey  FOREIGN KEY(embedder_id) REFERENCES ag_embedders(id),
    CONSTRAINT ag_readers_model_id_fkey     FOREIGN KEY(model_id)    REFERENCES ag_models(id),
    CONSTRAINT ag_readers_created_id_fkey   FOREIGN KEY(created_id)  REFERENCES sys_user(id),
    CONSTRAINT ag_readers_updated_id_fkey   FOREIGN KEY(updated_id)  REFERENCES sys_user(id)
);
CREATE UNIQUE INDEX ag_readers_uuid_key         ON public.ag_readers USING btree (uuid);
CREATE INDEX ix_ag_readers_reader_type          ON public.ag_readers USING btree (reader_type);
CREATE INDEX ix_ag_readers_embedder_id          ON public.ag_readers USING btree (embedder_id);
CREATE INDEX ix_ag_readers_model_id             ON public.ag_readers USING btree (model_id);
CREATE INDEX ix_ag_readers_status               ON public.ag_readers USING btree (status);
CREATE INDEX ix_ag_readers_created_id           ON public.ag_readers USING btree (created_id);
CREATE INDEX ix_ag_readers_updated_id           ON public.ag_readers USING btree (updated_id);

COMMENT ON TABLE  ag_readers                    IS '文档读取器管理表（Reader+Chunking配置，通过ag_bindings关联知识库）';
COMMENT ON COLUMN ag_readers.id                 IS '主键ID';
COMMENT ON COLUMN ag_readers.uuid               IS 'UUID全局唯一标识';
COMMENT ON COLUMN ag_readers.name               IS 'Reader名称';
COMMENT ON COLUMN ag_readers.reader_type        IS 'Reader类型(pdf/csv/excel/docx/pptx/json/markdown/text/website/firecrawl/tavily/youtube/arxiv/wikipedia/web_search/field_labeled_csv)';
COMMENT ON COLUMN ag_readers.chunk              IS '是否对内容分块';
COMMENT ON COLUMN ag_readers.chunk_size         IS '分块大小（字符数）';
COMMENT ON COLUMN ag_readers.encoding           IS '文本编码（utf-8/gbk等，文本类Reader使用）';
COMMENT ON COLUMN ag_readers.chunking_strategy  IS 'Chunking策略(FixedSizeChunker/RecursiveChunker/DocumentChunker/MarkdownChunker/RowChunker/SemanticChunker/AgenticChunker/CodeChunker)';
COMMENT ON COLUMN ag_readers.chunk_overlap      IS 'Chunk重叠字符数（FixedSize/Recursive/Document/Markdown策略支持）';
COMMENT ON COLUMN ag_readers.reader_config      IS 'Reader专属参数（按reader_type不同，见表注释）';
COMMENT ON COLUMN ag_readers.embedder_id        IS '关联Embedder ID（SemanticChunker使用）';
COMMENT ON COLUMN ag_readers.model_id           IS '关联Model ID（AgenticChunker使用）';
COMMENT ON COLUMN ag_readers.status             IS '是否启用(0:启用 1:禁用)';
COMMENT ON COLUMN ag_readers.description        IS '备注/描述';
COMMENT ON COLUMN ag_readers.created_time       IS '创建时间';
COMMENT ON COLUMN ag_readers.updated_time       IS '更新时间';
COMMENT ON COLUMN ag_readers.created_id         IS '创建人ID';
COMMENT ON COLUMN ag_readers.updated_id         IS '更新人ID';


-- ──────────────────────────────────────────────────────────
-- 5.7 ag_documents（文档管理）
-- ──────────────────────────────────────────────────────────
CREATE TABLE ag_documents (
    id            SERIAL NOT NULL,
    uuid          varchar(64) NOT NULL,
    kb_id         integer NOT NULL,
    name          varchar(500),
    storage_type  varchar(20) NOT NULL DEFAULT 'local',
    storage_path  text NOT NULL,
    doc_status    varchar(20) NOT NULL DEFAULT 'pending',
    error_msg     text,
    metadata_config      jsonb NOT NULL DEFAULT '{}',
    status        varchar(10) NOT NULL DEFAULT '0',
    description   text,
    created_time  timestamp without time zone NOT NULL,
    updated_time  timestamp without time zone NOT NULL,
    created_id    integer,
    updated_id    integer,
    PRIMARY KEY(id),
    CONSTRAINT ag_documents_kb_id_fkey         FOREIGN KEY(kb_id)      REFERENCES ag_knowledge_bases(id) ON DELETE CASCADE,
    CONSTRAINT ag_documents_created_id_fkey    FOREIGN KEY(created_id) REFERENCES sys_user(id),
    CONSTRAINT ag_documents_updated_id_fkey    FOREIGN KEY(updated_id) REFERENCES sys_user(id)
);
CREATE UNIQUE INDEX ag_documents_uuid_key   ON public.ag_documents USING btree (uuid);
CREATE INDEX ix_ag_documents_kb_id          ON public.ag_documents USING btree (kb_id);
CREATE INDEX ix_ag_documents_doc_status     ON public.ag_documents USING btree (kb_id, doc_status);
CREATE INDEX ix_ag_documents_status         ON public.ag_documents USING btree (status);
CREATE INDEX ix_ag_documents_created_id     ON public.ag_documents USING btree (created_id);
CREATE INDEX ix_ag_documents_updated_id     ON public.ag_documents USING btree (updated_id);

COMMENT ON TABLE  ag_documents               IS '知识库文档管理表';
COMMENT ON COLUMN ag_documents.id            IS '主键ID';
COMMENT ON COLUMN ag_documents.uuid          IS 'UUID全局唯一标识';
COMMENT ON COLUMN ag_documents.kb_id         IS '所属知识库ID';
COMMENT ON COLUMN ag_documents.name          IS '文档名称';
COMMENT ON COLUMN ag_documents.storage_type  IS '存储类型(local/s3/gcs/url)';
COMMENT ON COLUMN ag_documents.storage_path  IS '存储路径或URL';
COMMENT ON COLUMN ag_documents.doc_status    IS '处理状态(pending/processing/indexed/failed)';
COMMENT ON COLUMN ag_documents.error_msg     IS '处理失败错误信息';
COMMENT ON COLUMN ag_documents.metadata_config      IS '文档元数据';
COMMENT ON COLUMN ag_documents.status        IS '是否启用(0:启用 1:禁用)';
COMMENT ON COLUMN ag_documents.description   IS '备注/描述';
COMMENT ON COLUMN ag_documents.created_time  IS '创建时间';
COMMENT ON COLUMN ag_documents.updated_time  IS '更新时间';
COMMENT ON COLUMN ag_documents.created_id    IS '创建人ID';
COMMENT ON COLUMN ag_documents.updated_id    IS '更新人ID';


-- ──────────────────────────────────────────────────────────
-- 5.8 ag_hooks（钩子中间件管理）
-- ──────────────────────────────────────────────────────────
CREATE TABLE ag_hooks (
    id                  SERIAL NOT NULL,
    uuid                varchar(64) NOT NULL,
    name                varchar(255) NOT NULL,
    hook_type           varchar(20) NOT NULL,
    module_path         varchar(500) NOT NULL,
    func_name           varchar(255) NOT NULL,
    config              jsonb NOT NULL DEFAULT '{}',
    run_in_background   boolean NOT NULL DEFAULT false,
    status              varchar(10) NOT NULL DEFAULT '0',
    description         text,
    created_time        timestamp without time zone NOT NULL,
    updated_time        timestamp without time zone NOT NULL,
    created_id          integer,
    updated_id          integer,
    PRIMARY KEY(id),
    CONSTRAINT ag_hooks_created_id_fkey FOREIGN KEY(created_id) REFERENCES sys_user(id),
    CONSTRAINT ag_hooks_updated_id_fkey FOREIGN KEY(updated_id) REFERENCES sys_user(id)
);
CREATE UNIQUE INDEX ag_hooks_uuid_key   ON public.ag_hooks USING btree (uuid);
CREATE INDEX ix_ag_hooks_hook_type      ON public.ag_hooks USING btree (hook_type);
CREATE INDEX ix_ag_hooks_status         ON public.ag_hooks USING btree (status);
CREATE INDEX ix_ag_hooks_created_id     ON public.ag_hooks USING btree (created_id);
CREATE INDEX ix_ag_hooks_updated_id     ON public.ag_hooks USING btree (updated_id);

COMMENT ON TABLE  ag_hooks                    IS '钩子中间件管理表';
COMMENT ON COLUMN ag_hooks.id                 IS '主键ID';
COMMENT ON COLUMN ag_hooks.uuid               IS 'UUID全局唯一标识';
COMMENT ON COLUMN ag_hooks.name               IS 'Hook名称';
COMMENT ON COLUMN ag_hooks.hook_type          IS 'Hook类型(pre/post/tool)';
COMMENT ON COLUMN ag_hooks.module_path        IS 'Python模块路径';
COMMENT ON COLUMN ag_hooks.func_name          IS '函数名';
COMMENT ON COLUMN ag_hooks.config             IS '额外配置参数';
COMMENT ON COLUMN ag_hooks.run_in_background  IS '是否后台运行（不阻塞响应）';
COMMENT ON COLUMN ag_hooks.status             IS '是否启用(0:启用 1:禁用)';
COMMENT ON COLUMN ag_hooks.description        IS '备注/描述';
COMMENT ON COLUMN ag_hooks.created_time       IS '创建时间';
COMMENT ON COLUMN ag_hooks.updated_time       IS '更新时间';
COMMENT ON COLUMN ag_hooks.created_id         IS '创建人ID';
COMMENT ON COLUMN ag_hooks.updated_id         IS '更新人ID';


-- ──────────────────────────────────────────────────────────
-- 5.9 ag_guardrails（护栏管理）
-- ──────────────────────────────────────────────────────────
CREATE TABLE ag_guardrails (
    id            SERIAL NOT NULL,
    uuid          varchar(64) NOT NULL,
    name          varchar(255) NOT NULL,
    type          varchar(50) NOT NULL,
    hook_type     varchar(20) NOT NULL,
    config        jsonb NOT NULL DEFAULT '{}',
    module_path   varchar(500),
    class_name    varchar(255),
    status        varchar(10) NOT NULL DEFAULT '0',
    description   text,
    created_time  timestamp without time zone NOT NULL,
    updated_time  timestamp without time zone NOT NULL,
    created_id    integer,
    updated_id    integer,
    PRIMARY KEY(id),
    CONSTRAINT ag_guardrails_created_id_fkey FOREIGN KEY(created_id) REFERENCES sys_user(id),
    CONSTRAINT ag_guardrails_updated_id_fkey FOREIGN KEY(updated_id) REFERENCES sys_user(id)
);
CREATE UNIQUE INDEX ag_guardrails_uuid_key   ON public.ag_guardrails USING btree (uuid);
CREATE INDEX ix_ag_guardrails_type           ON public.ag_guardrails USING btree (type);
CREATE INDEX ix_ag_guardrails_hook_type      ON public.ag_guardrails USING btree (hook_type);
CREATE INDEX ix_ag_guardrails_status         ON public.ag_guardrails USING btree (status);
CREATE INDEX ix_ag_guardrails_created_id     ON public.ag_guardrails USING btree (created_id);
CREATE INDEX ix_ag_guardrails_updated_id     ON public.ag_guardrails USING btree (updated_id);

COMMENT ON TABLE  ag_guardrails              IS '护栏管理表';
COMMENT ON COLUMN ag_guardrails.id           IS '主键ID';
COMMENT ON COLUMN ag_guardrails.uuid         IS 'UUID全局唯一标识';
COMMENT ON COLUMN ag_guardrails.name         IS '护栏名称';
COMMENT ON COLUMN ag_guardrails.type         IS '护栏类型(openai_moderation/pii/prompt_injection/custom)';
COMMENT ON COLUMN ag_guardrails.hook_type    IS '作用阶段(pre/post)';
COMMENT ON COLUMN ag_guardrails.config       IS '护栏配置参数';
COMMENT ON COLUMN ag_guardrails.module_path  IS '自定义护栏模块路径（type=custom时使用）';
COMMENT ON COLUMN ag_guardrails.class_name   IS '自定义护栏类名（type=custom时使用）';
COMMENT ON COLUMN ag_guardrails.status       IS '是否启用(0:启用 1:禁用)';
COMMENT ON COLUMN ag_guardrails.description  IS '备注/描述';
COMMENT ON COLUMN ag_guardrails.created_time IS '创建时间';
COMMENT ON COLUMN ag_guardrails.updated_time IS '更新时间';
COMMENT ON COLUMN ag_guardrails.created_id   IS '创建人ID';
COMMENT ON COLUMN ag_guardrails.updated_id   IS '更新人ID';


-- ──────────────────────────────────────────────────────────
-- 5.10 ag_memory_managers（记忆管理器配置）
-- ──────────────────────────────────────────────────────────
CREATE TABLE ag_memory_managers (
    id                            SERIAL NOT NULL,
    uuid                          varchar(64) NOT NULL,
    name                          varchar(255) NOT NULL,
    model_id                      integer,
    delete_memories               boolean NOT NULL DEFAULT false,
    update_memories               boolean NOT NULL DEFAULT true,
    add_memories                  boolean NOT NULL DEFAULT true,
    clear_memories                boolean NOT NULL DEFAULT false,
    memory_capture_instructions   text,
    additional_instructions       text,
    status                        varchar(10) NOT NULL DEFAULT '0',
    description                   text,
    created_time                  timestamp without time zone NOT NULL,
    updated_time                  timestamp without time zone NOT NULL,
    created_id                    integer,
    updated_id                    integer,
    PRIMARY KEY(id),
    CONSTRAINT ag_memory_managers_model_id_fkey      FOREIGN KEY(model_id)    REFERENCES ag_models(id),
    CONSTRAINT ag_memory_managers_created_id_fkey    FOREIGN KEY(created_id)  REFERENCES sys_user(id),
    CONSTRAINT ag_memory_managers_updated_id_fkey    FOREIGN KEY(updated_id)  REFERENCES sys_user(id)
);
CREATE UNIQUE INDEX ag_memory_managers_uuid_key  ON public.ag_memory_managers USING btree (uuid);
CREATE INDEX ix_ag_memory_managers_model_id      ON public.ag_memory_managers USING btree (model_id);
CREATE INDEX ix_ag_memory_managers_status        ON public.ag_memory_managers USING btree (status);
CREATE INDEX ix_ag_memory_managers_created_id    ON public.ag_memory_managers USING btree (created_id);
CREATE INDEX ix_ag_memory_managers_updated_id    ON public.ag_memory_managers USING btree (updated_id);

COMMENT ON TABLE  ag_memory_managers                         IS '记忆管理器配置表';
COMMENT ON COLUMN ag_memory_managers.id                      IS '主键ID';
COMMENT ON COLUMN ag_memory_managers.uuid                    IS 'UUID全局唯一标识';
COMMENT ON COLUMN ag_memory_managers.name                    IS '记忆管理器名称';
COMMENT ON COLUMN ag_memory_managers.model_id                IS '关联模型ID（用于记忆处理）';
COMMENT ON COLUMN ag_memory_managers.delete_memories         IS '是否允许删除记忆';
COMMENT ON COLUMN ag_memory_managers.update_memories         IS '是否允许更新记忆';
COMMENT ON COLUMN ag_memory_managers.add_memories            IS '是否允许新增记忆';
COMMENT ON COLUMN ag_memory_managers.clear_memories          IS '是否允许清空记忆';
COMMENT ON COLUMN ag_memory_managers.memory_capture_instructions IS '记忆捕获指令';
COMMENT ON COLUMN ag_memory_managers.additional_instructions IS '附加指令';
COMMENT ON COLUMN ag_memory_managers.status                  IS '是否启用(0:启用 1:禁用)';
COMMENT ON COLUMN ag_memory_managers.description             IS '备注/描述';
COMMENT ON COLUMN ag_memory_managers.created_time            IS '创建时间';
COMMENT ON COLUMN ag_memory_managers.updated_time            IS '更新时间';
COMMENT ON COLUMN ag_memory_managers.created_id              IS '创建人ID';
COMMENT ON COLUMN ag_memory_managers.updated_id              IS '更新人ID';


-- ──────────────────────────────────────────────────────────
-- 5.11 ag_learning_configs（学习机配置）
-- ──────────────────────────────────────────────────────────
CREATE TABLE ag_learning_configs (
    id                 SERIAL NOT NULL,
    uuid               varchar(64) NOT NULL,
    name               varchar(255) NOT NULL,
    model_id           integer,
    namespace          varchar(255) NOT NULL DEFAULT 'global',
    user_profile       jsonb,
    user_memory        jsonb,
    session_context    jsonb,
    entity_memory      jsonb,
    learned_knowledge  jsonb,
    decision_log       jsonb,
    status             varchar(10) NOT NULL DEFAULT '0',
    description        text,
    created_time       timestamp without time zone NOT NULL,
    updated_time       timestamp without time zone NOT NULL,
    created_id         integer,
    updated_id         integer,
    PRIMARY KEY(id),
    CONSTRAINT ag_learning_configs_model_id_fkey     FOREIGN KEY(model_id)   REFERENCES ag_models(id),
    CONSTRAINT ag_learning_configs_created_id_fkey   FOREIGN KEY(created_id) REFERENCES sys_user(id),
    CONSTRAINT ag_learning_configs_updated_id_fkey   FOREIGN KEY(updated_id) REFERENCES sys_user(id)
);
CREATE UNIQUE INDEX ag_learning_configs_uuid_key  ON public.ag_learning_configs USING btree (uuid);
CREATE INDEX ix_ag_learning_configs_model_id      ON public.ag_learning_configs USING btree (model_id);
CREATE INDEX ix_ag_learning_configs_status        ON public.ag_learning_configs USING btree (status);
CREATE INDEX ix_ag_learning_configs_created_id    ON public.ag_learning_configs USING btree (created_id);
CREATE INDEX ix_ag_learning_configs_updated_id    ON public.ag_learning_configs USING btree (updated_id);

COMMENT ON TABLE  ag_learning_configs                   IS '学习机配置表';
COMMENT ON COLUMN ag_learning_configs.id                IS '主键ID';
COMMENT ON COLUMN ag_learning_configs.uuid              IS 'UUID全局唯一标识';
COMMENT ON COLUMN ag_learning_configs.name              IS '学习机配置名称';
COMMENT ON COLUMN ag_learning_configs.model_id          IS '关联模型ID';
COMMENT ON COLUMN ag_learning_configs.namespace         IS '命名空间（用于隔离不同租户/场景的学习数据）';
COMMENT ON COLUMN ag_learning_configs.user_profile      IS '用户画像配置（UserProfileConfig JSON）';
COMMENT ON COLUMN ag_learning_configs.user_memory       IS '用户记忆配置（UserMemoryConfig JSON）';
COMMENT ON COLUMN ag_learning_configs.session_context   IS '会话上下文配置（SessionContextConfig JSON）';
COMMENT ON COLUMN ag_learning_configs.entity_memory     IS '实体记忆配置（EntityMemoryConfig JSON）';
COMMENT ON COLUMN ag_learning_configs.learned_knowledge IS '学习知识配置（LearnedKnowledgeConfig JSON）';
COMMENT ON COLUMN ag_learning_configs.decision_log      IS '决策日志配置（DecisionLogConfig JSON）';
COMMENT ON COLUMN ag_learning_configs.status            IS '是否启用(0:启用 1:禁用)';
COMMENT ON COLUMN ag_learning_configs.description       IS '备注/描述';
COMMENT ON COLUMN ag_learning_configs.created_time      IS '创建时间';
COMMENT ON COLUMN ag_learning_configs.updated_time      IS '更新时间';
COMMENT ON COLUMN ag_learning_configs.created_id        IS '创建人ID';
COMMENT ON COLUMN ag_learning_configs.updated_id        IS '更新人ID';


-- ──────────────────────────────────────────────────────────
-- 5.12 ag_reasoning_configs（推理配置）
-- ──────────────────────────────────────────────────────────
CREATE TABLE ag_reasoning_configs (
    id              SERIAL NOT NULL,
    uuid            varchar(64) NOT NULL,
    name            varchar(255) NOT NULL,
    model_id        integer,
    min_steps       integer NOT NULL DEFAULT 1,
    max_steps       integer NOT NULL DEFAULT 10,
    use_json_mode   boolean NOT NULL DEFAULT false,
    tool_call_limit integer,
    debug_mode      boolean NOT NULL DEFAULT false,
    status          varchar(10) NOT NULL DEFAULT '0',
    description     text,
    created_time    timestamp without time zone NOT NULL,
    updated_time    timestamp without time zone NOT NULL,
    created_id      integer,
    updated_id      integer,
    PRIMARY KEY(id),
    CONSTRAINT ag_reasoning_configs_model_id_fkey    FOREIGN KEY(model_id)   REFERENCES ag_models(id),
    CONSTRAINT ag_reasoning_configs_created_id_fkey  FOREIGN KEY(created_id) REFERENCES sys_user(id),
    CONSTRAINT ag_reasoning_configs_updated_id_fkey  FOREIGN KEY(updated_id) REFERENCES sys_user(id)
);
CREATE UNIQUE INDEX ag_reasoning_configs_uuid_key  ON public.ag_reasoning_configs USING btree (uuid);
CREATE INDEX ix_ag_reasoning_configs_model_id      ON public.ag_reasoning_configs USING btree (model_id);
CREATE INDEX ix_ag_reasoning_configs_status        ON public.ag_reasoning_configs USING btree (status);
CREATE INDEX ix_ag_reasoning_configs_created_id    ON public.ag_reasoning_configs USING btree (created_id);
CREATE INDEX ix_ag_reasoning_configs_updated_id    ON public.ag_reasoning_configs USING btree (updated_id);

COMMENT ON TABLE  ag_reasoning_configs                IS '推理配置表';
COMMENT ON COLUMN ag_reasoning_configs.id             IS '主键ID';
COMMENT ON COLUMN ag_reasoning_configs.uuid           IS 'UUID全局唯一标识';
COMMENT ON COLUMN ag_reasoning_configs.name           IS '推理配置名称';
COMMENT ON COLUMN ag_reasoning_configs.model_id       IS '关联推理模型ID';
COMMENT ON COLUMN ag_reasoning_configs.min_steps      IS '最少推理步数';
COMMENT ON COLUMN ag_reasoning_configs.max_steps      IS '最多推理步数';
COMMENT ON COLUMN ag_reasoning_configs.use_json_mode  IS '是否使用JSON模式';
COMMENT ON COLUMN ag_reasoning_configs.tool_call_limit IS '工具调用次数上限';
COMMENT ON COLUMN ag_reasoning_configs.debug_mode     IS '是否开启调试模式';
COMMENT ON COLUMN ag_reasoning_configs.status         IS '是否启用(0:启用 1:禁用)';
COMMENT ON COLUMN ag_reasoning_configs.description    IS '备注/描述';
COMMENT ON COLUMN ag_reasoning_configs.created_time   IS '创建时间';
COMMENT ON COLUMN ag_reasoning_configs.updated_time   IS '更新时间';
COMMENT ON COLUMN ag_reasoning_configs.created_id     IS '创建人ID';
COMMENT ON COLUMN ag_reasoning_configs.updated_id     IS '更新人ID';


-- ──────────────────────────────────────────────────────────
-- 5.12 ag_compression_configs（压缩管理器配置）
-- ──────────────────────────────────────────────────────────
CREATE TABLE ag_compression_configs (
    id                               SERIAL NOT NULL,
    uuid                             varchar(64) NOT NULL,
    name                             varchar(255) NOT NULL,
    model_id                         integer,
    compress_tool_results_limit      integer,
    compress_token_limit             integer,
    compress_tool_call_instructions  text,
    status                           varchar(10) NOT NULL DEFAULT '0',
    description                      text,
    created_time                     timestamp without time zone NOT NULL,
    updated_time                     timestamp without time zone NOT NULL,
    created_id                       integer,
    updated_id                       integer,
    PRIMARY KEY(id),
    CONSTRAINT ag_compression_configs_model_id_fkey    FOREIGN KEY(model_id)   REFERENCES ag_models(id),
    CONSTRAINT ag_compression_configs_created_id_fkey  FOREIGN KEY(created_id) REFERENCES sys_user(id),
    CONSTRAINT ag_compression_configs_updated_id_fkey  FOREIGN KEY(updated_id) REFERENCES sys_user(id)
);
CREATE UNIQUE INDEX ag_compression_configs_uuid_key  ON public.ag_compression_configs USING btree (uuid);
CREATE INDEX ix_ag_compression_configs_model_id      ON public.ag_compression_configs USING btree (model_id);
CREATE INDEX ix_ag_compression_configs_status        ON public.ag_compression_configs USING btree (status);
CREATE INDEX ix_ag_compression_configs_created_id    ON public.ag_compression_configs USING btree (created_id);
CREATE INDEX ix_ag_compression_configs_updated_id    ON public.ag_compression_configs USING btree (updated_id);

COMMENT ON TABLE  ag_compression_configs                               IS '压缩管理器配置表';
COMMENT ON COLUMN ag_compression_configs.id                            IS '主键ID';
COMMENT ON COLUMN ag_compression_configs.uuid                          IS 'UUID全局唯一标识';
COMMENT ON COLUMN ag_compression_configs.name                          IS '压缩配置名称';
COMMENT ON COLUMN ag_compression_configs.model_id                      IS '关联压缩模型ID';
COMMENT ON COLUMN ag_compression_configs.compress_tool_results_limit   IS '触发工具结果压缩的条数阈值';
COMMENT ON COLUMN ag_compression_configs.compress_token_limit          IS '触发压缩的Token数阈值';
COMMENT ON COLUMN ag_compression_configs.compress_tool_call_instructions IS '工具调用压缩指令';
COMMENT ON COLUMN ag_compression_configs.status                        IS '是否启用(0:启用 1:禁用)';
COMMENT ON COLUMN ag_compression_configs.description                   IS '备注/描述';
COMMENT ON COLUMN ag_compression_configs.created_time                  IS '创建时间';
COMMENT ON COLUMN ag_compression_configs.updated_time                  IS '更新时间';
COMMENT ON COLUMN ag_compression_configs.created_id                    IS '创建人ID';
COMMENT ON COLUMN ag_compression_configs.updated_id                    IS '更新人ID';


-- ──────────────────────────────────────────────────────────
-- 5.12 ag_sess_summary_configs（会话摘要配置）
-- ──────────────────────────────────────────────────────────
CREATE TABLE ag_sess_summary_configs (
    id                      SERIAL NOT NULL,
    uuid                    varchar(64) NOT NULL,
    name                    varchar(255) NOT NULL,
    model_id                integer,
    session_summary_prompt  text,
    summary_request_message text DEFAULT 'Provide the summary of the conversation.',
    status                  varchar(10) NOT NULL DEFAULT '0',
    description             text,
    created_time            timestamp without time zone NOT NULL,
    updated_time            timestamp without time zone NOT NULL,
    created_id              integer,
    updated_id              integer,
    PRIMARY KEY(id),
    CONSTRAINT ag_sess_summary_configs_model_id_fkey    FOREIGN KEY(model_id)   REFERENCES ag_models(id),
    CONSTRAINT ag_sess_summary_configs_created_id_fkey  FOREIGN KEY(created_id) REFERENCES sys_user(id),
    CONSTRAINT ag_sess_summary_configs_updated_id_fkey  FOREIGN KEY(updated_id) REFERENCES sys_user(id)
);
CREATE UNIQUE INDEX ag_sess_summary_configs_uuid_key  ON public.ag_sess_summary_configs USING btree (uuid);
CREATE INDEX ix_ag_sess_summary_configs_model_id      ON public.ag_sess_summary_configs USING btree (model_id);
CREATE INDEX ix_ag_sess_summary_configs_status        ON public.ag_sess_summary_configs USING btree (status);
CREATE INDEX ix_ag_sess_summary_configs_created_id    ON public.ag_sess_summary_configs USING btree (created_id);
CREATE INDEX ix_ag_sess_summary_configs_updated_id    ON public.ag_sess_summary_configs USING btree (updated_id);

COMMENT ON TABLE  ag_sess_summary_configs                      IS '会话摘要配置表';
COMMENT ON COLUMN ag_sess_summary_configs.id                   IS '主键ID';
COMMENT ON COLUMN ag_sess_summary_configs.uuid                 IS 'UUID全局唯一标识';
COMMENT ON COLUMN ag_sess_summary_configs.name                 IS '会话摘要配置名称';
COMMENT ON COLUMN ag_sess_summary_configs.model_id             IS '关联摘要模型ID';
COMMENT ON COLUMN ag_sess_summary_configs.session_summary_prompt IS '摘要生成提示词';
COMMENT ON COLUMN ag_sess_summary_configs.summary_request_message IS '摘要请求消息';
COMMENT ON COLUMN ag_sess_summary_configs.status               IS '是否启用(0:启用 1:禁用)';
COMMENT ON COLUMN ag_sess_summary_configs.description          IS '备注/描述';
COMMENT ON COLUMN ag_sess_summary_configs.created_time         IS '创建时间';
COMMENT ON COLUMN ag_sess_summary_configs.updated_time         IS '更新时间';
COMMENT ON COLUMN ag_sess_summary_configs.created_id           IS '创建人ID';
COMMENT ON COLUMN ag_sess_summary_configs.updated_id           IS '更新人ID';


-- ──────────────────────────────────────────────────────────
-- 5.12 ag_culture_configs（文化管理器配置）
-- ──────────────────────────────────────────────────────────
CREATE TABLE ag_culture_configs (
    id                            SERIAL NOT NULL,
    uuid                          varchar(64) NOT NULL,
    name                          varchar(255) NOT NULL,
    model_id                      integer,
    add_knowledge                 boolean NOT NULL DEFAULT true,
    update_knowledge              boolean NOT NULL DEFAULT true,
    delete_knowledge              boolean NOT NULL DEFAULT true,
    clear_knowledge               boolean NOT NULL DEFAULT true,
    culture_capture_instructions  text,
    additional_instructions       text,
    debug_mode                    boolean NOT NULL DEFAULT false,
    status                        varchar(10) NOT NULL DEFAULT '0',
    description                   text,
    created_time                  timestamp without time zone NOT NULL,
    updated_time                  timestamp without time zone NOT NULL,
    created_id                    integer,
    updated_id                    integer,
    PRIMARY KEY(id),
    CONSTRAINT ag_culture_configs_model_id_fkey    FOREIGN KEY(model_id)   REFERENCES ag_models(id),
    CONSTRAINT ag_culture_configs_created_id_fkey  FOREIGN KEY(created_id) REFERENCES sys_user(id),
    CONSTRAINT ag_culture_configs_updated_id_fkey  FOREIGN KEY(updated_id) REFERENCES sys_user(id)
);
CREATE UNIQUE INDEX ag_culture_configs_uuid_key  ON public.ag_culture_configs USING btree (uuid);
CREATE INDEX ix_ag_culture_configs_model_id      ON public.ag_culture_configs USING btree (model_id);
CREATE INDEX ix_ag_culture_configs_status        ON public.ag_culture_configs USING btree (status);
CREATE INDEX ix_ag_culture_configs_created_id    ON public.ag_culture_configs USING btree (created_id);
CREATE INDEX ix_ag_culture_configs_updated_id    ON public.ag_culture_configs USING btree (updated_id);

COMMENT ON TABLE  ag_culture_configs                          IS '文化管理器配置表（实验性）';
COMMENT ON COLUMN ag_culture_configs.id                       IS '主键ID';
COMMENT ON COLUMN ag_culture_configs.uuid                     IS 'UUID全局唯一标识';
COMMENT ON COLUMN ag_culture_configs.name                     IS '文化配置名称';
COMMENT ON COLUMN ag_culture_configs.model_id                 IS '关联模型ID';
COMMENT ON COLUMN ag_culture_configs.add_knowledge            IS '是否允许新增知识';
COMMENT ON COLUMN ag_culture_configs.update_knowledge         IS '是否允许更新知识';
COMMENT ON COLUMN ag_culture_configs.delete_knowledge         IS '是否允许删除知识';
COMMENT ON COLUMN ag_culture_configs.clear_knowledge          IS '是否允许清空知识';
COMMENT ON COLUMN ag_culture_configs.culture_capture_instructions IS '文化捕获指令';
COMMENT ON COLUMN ag_culture_configs.additional_instructions  IS '附加指令';
COMMENT ON COLUMN ag_culture_configs.debug_mode               IS '是否开启调试模式';
COMMENT ON COLUMN ag_culture_configs.status                   IS '是否启用(0:启用 1:禁用)';
COMMENT ON COLUMN ag_culture_configs.description              IS '备注/描述';
COMMENT ON COLUMN ag_culture_configs.created_time             IS '创建时间';
COMMENT ON COLUMN ag_culture_configs.updated_time             IS '更新时间';
COMMENT ON COLUMN ag_culture_configs.created_id               IS '创建人ID';
COMMENT ON COLUMN ag_culture_configs.updated_id               IS '更新人ID';


-- ──────────────────────────────────────────────────────────
-- 5.13 ag_agents（Agent核心表）
-- ──────────────────────────────────────────────────────────
CREATE TABLE ag_agents (
    id                                SERIAL NOT NULL,
    uuid                              varchar(64) NOT NULL,
    name                              varchar(255) NOT NULL,

    -- 模型
    model_id                          integer,
    reasoning_model_id                integer,
    output_model_id                   integer,
    parser_model_id                   integer,

    -- 子管理器
    memory_manager_id                 integer,
    learning_config_id                integer,
    reasoning_config_id               integer,
    compression_config_id             integer,
    session_summary_config_id         integer,
    culture_config_id                 integer,

    -- 提示词
    instructions                      text,
    expected_output                   text,
    additional_context                text,

    -- 推理
    reasoning                         boolean NOT NULL DEFAULT false,
    reasoning_min_steps               integer NOT NULL DEFAULT 1,
    reasoning_max_steps               integer NOT NULL DEFAULT 10,

    -- 学习
    learning                          boolean NOT NULL DEFAULT false,

    -- 知识库
    search_knowledge                  boolean NOT NULL DEFAULT true,
    update_knowledge                  boolean NOT NULL DEFAULT false,
    add_knowledge_to_context          boolean NOT NULL DEFAULT false,
    enable_agentic_knowledge_filters  boolean NOT NULL DEFAULT false,

    -- 记忆
    enable_agentic_state              boolean NOT NULL DEFAULT false,
    enable_agentic_memory             boolean NOT NULL DEFAULT false,
    update_memory_on_run              boolean NOT NULL DEFAULT false,
    add_memories_to_context           boolean NOT NULL DEFAULT false,

    -- 历史
    add_history_to_context            boolean NOT NULL DEFAULT false,
    num_history_runs                  integer,
    num_history_messages              integer,
    search_past_sessions              boolean NOT NULL DEFAULT false,
    num_past_sessions_to_search       integer,

    -- 会话摘要
    enable_session_summaries          boolean NOT NULL DEFAULT false,
    add_session_summary_to_context    boolean NOT NULL DEFAULT false,

    -- 工具控制
    tool_call_limit                   integer,
    tool_choice                       varchar(50),

    -- 输出格式
    output_schema                     jsonb,
    input_schema                      jsonb,
    use_json_mode                     boolean NOT NULL DEFAULT false,
    structured_outputs                boolean,
    parse_response                    boolean NOT NULL DEFAULT true,

    -- 重试
    retries                           integer NOT NULL DEFAULT 0,
    delay_between_retries             integer NOT NULL DEFAULT 1,
    exponential_backoff               boolean NOT NULL DEFAULT false,

    -- 上下文
    add_datetime_to_context           boolean NOT NULL DEFAULT false,
    add_name_to_context               boolean NOT NULL DEFAULT false,
    compress_tool_results             boolean NOT NULL DEFAULT false,

    -- 流式
    stream                            boolean NOT NULL DEFAULT false,
    stream_events                     boolean NOT NULL DEFAULT false,
    store_events                      boolean NOT NULL DEFAULT false,

    -- Markdown
    markdown                          boolean NOT NULL DEFAULT false,

    -- Follow-up
    followups                         boolean NOT NULL DEFAULT false,
    num_followups                     integer NOT NULL DEFAULT 3,

    -- 调试
    debug_mode                        boolean NOT NULL DEFAULT false,
    debug_level                       integer NOT NULL DEFAULT 1,

    -- A2A / Remote
    a2a_enabled                       boolean NOT NULL DEFAULT false,
    is_remote                         boolean NOT NULL DEFAULT false,
    remote_url                        varchar(500),
    remote_agent_id                   varchar(255),

    metadata_config                          jsonb NOT NULL DEFAULT '{}',
    status                            varchar(10) NOT NULL DEFAULT '0',
    description                       text,
    created_time                      timestamp without time zone NOT NULL,
    updated_time                      timestamp without time zone NOT NULL,
    created_id                        integer,
    updated_id                        integer,
    PRIMARY KEY(id),
    CONSTRAINT ag_agents_model_id_fkey               FOREIGN KEY(model_id)               REFERENCES ag_models(id),
    CONSTRAINT ag_agents_reasoning_model_id_fkey     FOREIGN KEY(reasoning_model_id)     REFERENCES ag_models(id),
    CONSTRAINT ag_agents_output_model_id_fkey        FOREIGN KEY(output_model_id)        REFERENCES ag_models(id),
    CONSTRAINT ag_agents_parser_model_id_fkey        FOREIGN KEY(parser_model_id)        REFERENCES ag_models(id),
    CONSTRAINT ag_agents_memory_manager_id_fkey      FOREIGN KEY(memory_manager_id)      REFERENCES ag_memory_managers(id),
    CONSTRAINT ag_agents_learning_config_id_fkey     FOREIGN KEY(learning_config_id)     REFERENCES ag_learning_configs(id),
    CONSTRAINT ag_agents_reasoning_config_id_fkey    FOREIGN KEY(reasoning_config_id)    REFERENCES ag_reasoning_configs(id),
    CONSTRAINT ag_agents_compression_config_id_fkey  FOREIGN KEY(compression_config_id)  REFERENCES ag_compression_configs(id),
    CONSTRAINT ag_agents_session_summary_config_fkey FOREIGN KEY(session_summary_config_id) REFERENCES ag_sess_summary_configs(id),
    CONSTRAINT ag_agents_culture_config_id_fkey      FOREIGN KEY(culture_config_id)      REFERENCES ag_culture_configs(id),
    CONSTRAINT ag_agents_created_id_fkey             FOREIGN KEY(created_id)             REFERENCES sys_user(id),
    CONSTRAINT ag_agents_updated_id_fkey             FOREIGN KEY(updated_id)             REFERENCES sys_user(id)
);
CREATE UNIQUE INDEX ag_agents_uuid_key              ON public.ag_agents USING btree (uuid);
CREATE INDEX ix_ag_agents_model_id                  ON public.ag_agents USING btree (model_id);
CREATE INDEX ix_ag_agents_status                    ON public.ag_agents USING btree (status);
CREATE INDEX ix_ag_agents_created_id                ON public.ag_agents USING btree (created_id);
CREATE INDEX ix_ag_agents_updated_id                ON public.ag_agents USING btree (updated_id);

COMMENT ON TABLE  ag_agents                                  IS 'Agent核心配置表';
COMMENT ON COLUMN ag_agents.id                               IS '主键ID';
COMMENT ON COLUMN ag_agents.uuid                             IS 'UUID全局唯一标识';
COMMENT ON COLUMN ag_agents.name                             IS 'Agent名称';
COMMENT ON COLUMN ag_agents.model_id                         IS '主模型ID';
COMMENT ON COLUMN ag_agents.reasoning_model_id               IS '推理模型ID';
COMMENT ON COLUMN ag_agents.output_model_id                  IS '输出模型ID（response_model）';
COMMENT ON COLUMN ag_agents.parser_model_id                  IS '解析模型ID';
COMMENT ON COLUMN ag_agents.memory_manager_id                IS '记忆管理器ID';
COMMENT ON COLUMN ag_agents.learning_config_id               IS '学习机配置ID';
COMMENT ON COLUMN ag_agents.reasoning_config_id              IS '推理配置ID';
COMMENT ON COLUMN ag_agents.compression_config_id            IS '压缩管理器配置ID';
COMMENT ON COLUMN ag_agents.session_summary_config_id        IS '会话摘要配置ID';
COMMENT ON COLUMN ag_agents.culture_config_id                IS '文化管理器配置ID';
COMMENT ON COLUMN ag_agents.instructions                     IS 'Agent指令（system prompt）';
COMMENT ON COLUMN ag_agents.expected_output                  IS '期望输出格式说明';
COMMENT ON COLUMN ag_agents.additional_context               IS '附加上下文';
COMMENT ON COLUMN ag_agents.reasoning                        IS '是否开启推理';
COMMENT ON COLUMN ag_agents.reasoning_min_steps              IS '最少推理步数';
COMMENT ON COLUMN ag_agents.reasoning_max_steps              IS '最多推理步数';
COMMENT ON COLUMN ag_agents.learning                         IS '是否开启学习';
COMMENT ON COLUMN ag_agents.search_knowledge                 IS '是否搜索知识库';
COMMENT ON COLUMN ag_agents.update_knowledge                 IS '是否允许更新知识库';
COMMENT ON COLUMN ag_agents.add_knowledge_to_context         IS '是否将知识库内容加入上下文';
COMMENT ON COLUMN ag_agents.enable_agentic_knowledge_filters IS '是否开启智能知识过滤';
COMMENT ON COLUMN ag_agents.enable_agentic_state             IS '是否开启智能状态';
COMMENT ON COLUMN ag_agents.enable_agentic_memory            IS '是否开启智能记忆';
COMMENT ON COLUMN ag_agents.update_memory_on_run             IS '是否每次运行后更新记忆';
COMMENT ON COLUMN ag_agents.add_memories_to_context          IS '是否将记忆加入上下文';
COMMENT ON COLUMN ag_agents.add_history_to_context           IS '是否将历史记录加入上下文';
COMMENT ON COLUMN ag_agents.num_history_runs                 IS '加入上下文的历史运行次数';
COMMENT ON COLUMN ag_agents.num_history_messages             IS '加入上下文的历史消息数';
COMMENT ON COLUMN ag_agents.search_past_sessions             IS '是否搜索历史会话';
COMMENT ON COLUMN ag_agents.num_past_sessions_to_search      IS '搜索历史会话数量';
COMMENT ON COLUMN ag_agents.enable_session_summaries         IS '是否开启会话摘要';
COMMENT ON COLUMN ag_agents.add_session_summary_to_context   IS '是否将会话摘要加入上下文';
COMMENT ON COLUMN ag_agents.tool_call_limit                  IS '工具调用次数上限';
COMMENT ON COLUMN ag_agents.tool_choice                      IS '工具选择策略(none/auto/specific)';
COMMENT ON COLUMN ag_agents.output_schema                    IS '输出结构体JSON Schema';
COMMENT ON COLUMN ag_agents.input_schema                     IS '输入结构体JSON Schema';
COMMENT ON COLUMN ag_agents.use_json_mode                    IS '是否使用JSON输出模式';
COMMENT ON COLUMN ag_agents.structured_outputs               IS '是否使用结构化输出';
COMMENT ON COLUMN ag_agents.parse_response                   IS '是否解析响应';
COMMENT ON COLUMN ag_agents.retries                          IS '失败重试次数';
COMMENT ON COLUMN ag_agents.delay_between_retries            IS '重试间隔秒数';
COMMENT ON COLUMN ag_agents.exponential_backoff              IS '是否指数退避重试';
COMMENT ON COLUMN ag_agents.add_datetime_to_context          IS '是否将当前时间加入上下文';
COMMENT ON COLUMN ag_agents.add_name_to_context              IS '是否将Agent名称加入上下文';
COMMENT ON COLUMN ag_agents.compress_tool_results            IS '是否压缩工具结果';
COMMENT ON COLUMN ag_agents.stream                           IS '是否开启流式输出';
COMMENT ON COLUMN ag_agents.stream_events                    IS '是否流式推送事件';
COMMENT ON COLUMN ag_agents.store_events                     IS '是否存储事件';
COMMENT ON COLUMN ag_agents.markdown                         IS '是否输出Markdown格式';
COMMENT ON COLUMN ag_agents.followups                        IS '是否生成追问';
COMMENT ON COLUMN ag_agents.num_followups                    IS '追问数量';
COMMENT ON COLUMN ag_agents.debug_mode                       IS '是否开启调试模式';
COMMENT ON COLUMN ag_agents.debug_level                      IS '调试级别';
COMMENT ON COLUMN ag_agents.a2a_enabled                      IS '是否对外暴露A2A接口';
COMMENT ON COLUMN ag_agents.is_remote                        IS '是否为远程Agent';
COMMENT ON COLUMN ag_agents.remote_url                       IS '远程Agent地址';
COMMENT ON COLUMN ag_agents.remote_agent_id                  IS '远程Agent标识符';
COMMENT ON COLUMN ag_agents.metadata_config                         IS '元数据';
COMMENT ON COLUMN ag_agents.status                           IS '是否启用(0:启用 1:禁用)';
COMMENT ON COLUMN ag_agents.description                      IS '备注/描述';
COMMENT ON COLUMN ag_agents.created_time                     IS '创建时间';
COMMENT ON COLUMN ag_agents.updated_time                     IS '更新时间';
COMMENT ON COLUMN ag_agents.created_id                       IS '创建人ID';
COMMENT ON COLUMN ag_agents.updated_id                       IS '更新人ID';


-- ──────────────────────────────────────────────────────────
-- 5.14 ag_bindings（资源绑定关系表）
-- ──────────────────────────────────────────────────────────
CREATE TABLE ag_bindings (
    id              SERIAL NOT NULL,
    uuid            varchar(64) NOT NULL,
    owner_type      varchar(50) NOT NULL,
    owner_id        integer NOT NULL,
    resource_type   varchar(50) NOT NULL,
    resource_id     integer NOT NULL,
    priority        integer NOT NULL DEFAULT 0,
    config_override jsonb NOT NULL DEFAULT '{}',
    status          varchar(10) NOT NULL DEFAULT '0',
    description     text,
    created_time    timestamp without time zone NOT NULL,
    updated_time    timestamp without time zone NOT NULL,
    created_id      integer,
    updated_id      integer,
    PRIMARY KEY(id),
    CONSTRAINT ag_bindings_owner_resource_unique UNIQUE(owner_type, owner_id, resource_type, resource_id),
    CONSTRAINT ag_bindings_created_id_fkey FOREIGN KEY(created_id) REFERENCES sys_user(id),
    CONSTRAINT ag_bindings_updated_id_fkey FOREIGN KEY(updated_id) REFERENCES sys_user(id)
);
CREATE UNIQUE INDEX ag_bindings_uuid_key        ON public.ag_bindings USING btree (uuid);
CREATE INDEX ix_ag_bindings_owner               ON public.ag_bindings USING btree (owner_type, owner_id);
CREATE INDEX ix_ag_bindings_owner_type          ON public.ag_bindings USING btree (owner_type, owner_id, resource_type);
CREATE INDEX ix_ag_bindings_owner_status        ON public.ag_bindings USING btree (owner_id, status);
CREATE INDEX ix_ag_bindings_created_id          ON public.ag_bindings USING btree (created_id);
CREATE INDEX ix_ag_bindings_updated_id          ON public.ag_bindings USING btree (updated_id);

COMMENT ON TABLE  ag_bindings                IS '资源绑定关系表（Agent/Team与工具/知识库等资源的热插拔关联）';
COMMENT ON COLUMN ag_bindings.id             IS '主键ID';
COMMENT ON COLUMN ag_bindings.uuid           IS 'UUID全局唯一标识';
COMMENT ON COLUMN ag_bindings.owner_type     IS '拥有者类型(agent/team)';
COMMENT ON COLUMN ag_bindings.owner_id       IS '拥有者ID';
COMMENT ON COLUMN ag_bindings.resource_type  IS '资源类型(toolkit/skill/mcp/knowledge/hook/guardrail/reader)';
COMMENT ON COLUMN ag_bindings.resource_id    IS '资源ID';
COMMENT ON COLUMN ag_bindings.priority       IS '优先级（数字小优先）';
COMMENT ON COLUMN ag_bindings.config_override IS '覆盖资源默认配置（如特定Agent使用不同API Key）';
COMMENT ON COLUMN ag_bindings.status         IS '是否启用(0:启用 1:禁用)';
COMMENT ON COLUMN ag_bindings.description    IS '备注/描述';
COMMENT ON COLUMN ag_bindings.created_time   IS '创建时间';
COMMENT ON COLUMN ag_bindings.updated_time   IS '更新时间';
COMMENT ON COLUMN ag_bindings.created_id     IS '创建人ID';
COMMENT ON COLUMN ag_bindings.updated_id     IS '更新人ID';


-- ──────────────────────────────────────────────────────────
-- 5.15 ag_teams（Team管理）
-- ──────────────────────────────────────────────────────────
CREATE TABLE ag_teams (
    id                                SERIAL NOT NULL,
    uuid                              varchar(64) NOT NULL,
    name                              varchar(255) NOT NULL,

    model_id                          integer,
    memory_manager_id                 integer,

    mode                              varchar(20) NOT NULL DEFAULT 'route',
    respond_directly                  boolean NOT NULL DEFAULT false,
    delegate_to_all_members           boolean NOT NULL DEFAULT false,
    determine_input_for_members       boolean NOT NULL DEFAULT true,
    max_iterations                    integer NOT NULL DEFAULT 10,

    instructions                      text,
    expected_output                   text,
    markdown                          boolean NOT NULL DEFAULT false,

    add_team_history_to_members       boolean NOT NULL DEFAULT false,
    num_team_history_runs             integer NOT NULL DEFAULT 3,
    share_member_interactions         boolean NOT NULL DEFAULT false,
    add_member_tools_to_context       boolean NOT NULL DEFAULT false,
    read_chat_history                 boolean NOT NULL DEFAULT false,
    search_past_sessions              boolean NOT NULL DEFAULT false,
    num_past_sessions_to_search       integer,

    search_knowledge                  boolean NOT NULL DEFAULT true,
    update_knowledge                  boolean NOT NULL DEFAULT false,
    enable_agentic_knowledge_filters  boolean NOT NULL DEFAULT false,

    enable_agentic_state              boolean NOT NULL DEFAULT false,
    enable_agentic_memory             boolean NOT NULL DEFAULT false,
    update_memory_on_run              boolean NOT NULL DEFAULT false,

    enable_session_summaries          boolean NOT NULL DEFAULT false,
    add_session_summary_to_context    boolean NOT NULL DEFAULT false,

    tool_call_limit                   integer,
    stream                            boolean NOT NULL DEFAULT false,
    stream_events                     boolean NOT NULL DEFAULT false,
    debug_mode                        boolean NOT NULL DEFAULT false,

    metadata_config                          jsonb NOT NULL DEFAULT '{}',
    status                            varchar(10) NOT NULL DEFAULT '0',
    description                       text,
    created_time                      timestamp without time zone NOT NULL,
    updated_time                      timestamp without time zone NOT NULL,
    created_id                        integer,
    updated_id                        integer,
    PRIMARY KEY(id),
    CONSTRAINT ag_teams_model_id_fkey          FOREIGN KEY(model_id)          REFERENCES ag_models(id),
    CONSTRAINT ag_teams_memory_manager_id_fkey FOREIGN KEY(memory_manager_id) REFERENCES ag_memory_managers(id),
    CONSTRAINT ag_teams_created_id_fkey        FOREIGN KEY(created_id)        REFERENCES sys_user(id),
    CONSTRAINT ag_teams_updated_id_fkey        FOREIGN KEY(updated_id)        REFERENCES sys_user(id)
);
CREATE UNIQUE INDEX ag_teams_uuid_key       ON public.ag_teams USING btree (uuid);
CREATE INDEX ix_ag_teams_model_id           ON public.ag_teams USING btree (model_id);
CREATE INDEX ix_ag_teams_status             ON public.ag_teams USING btree (status);
CREATE INDEX ix_ag_teams_created_id         ON public.ag_teams USING btree (created_id);
CREATE INDEX ix_ag_teams_updated_id         ON public.ag_teams USING btree (updated_id);

COMMENT ON TABLE  ag_teams                                   IS 'Team管理表';
COMMENT ON COLUMN ag_teams.id                                IS '主键ID';
COMMENT ON COLUMN ag_teams.uuid                              IS 'UUID全局唯一标识';
COMMENT ON COLUMN ag_teams.name                              IS 'Team名称';
COMMENT ON COLUMN ag_teams.model_id                          IS '主模型ID';
COMMENT ON COLUMN ag_teams.memory_manager_id                 IS '记忆管理器ID';
COMMENT ON COLUMN ag_teams.mode                              IS '协作模式(route/coordinate/collaborate/tasks)';
COMMENT ON COLUMN ag_teams.respond_directly                  IS '是否直接响应（不经过协调）';
COMMENT ON COLUMN ag_teams.delegate_to_all_members           IS '是否分发给所有成员';
COMMENT ON COLUMN ag_teams.determine_input_for_members       IS '是否为成员决定输入内容';
COMMENT ON COLUMN ag_teams.max_iterations                    IS '最大迭代次数';
COMMENT ON COLUMN ag_teams.instructions                      IS 'Team指令';
COMMENT ON COLUMN ag_teams.expected_output                   IS '期望输出格式说明';
COMMENT ON COLUMN ag_teams.markdown                          IS '是否输出Markdown格式';
COMMENT ON COLUMN ag_teams.add_team_history_to_members       IS '是否将Team历史传给成员';
COMMENT ON COLUMN ag_teams.num_team_history_runs             IS '传给成员的历史运行次数';
COMMENT ON COLUMN ag_teams.share_member_interactions         IS '是否共享成员交互记录';
COMMENT ON COLUMN ag_teams.add_member_tools_to_context       IS '是否将成员工具加入上下文';
COMMENT ON COLUMN ag_teams.read_chat_history                 IS '是否读取聊天历史';
COMMENT ON COLUMN ag_teams.search_past_sessions              IS '是否搜索历史会话';
COMMENT ON COLUMN ag_teams.num_past_sessions_to_search       IS '搜索历史会话数量';
COMMENT ON COLUMN ag_teams.search_knowledge                  IS '是否搜索知识库';
COMMENT ON COLUMN ag_teams.update_knowledge                  IS '是否允许更新知识库';
COMMENT ON COLUMN ag_teams.enable_agentic_knowledge_filters  IS '是否开启智能知识过滤';
COMMENT ON COLUMN ag_teams.enable_agentic_state              IS '是否开启智能状态';
COMMENT ON COLUMN ag_teams.enable_agentic_memory             IS '是否开启智能记忆';
COMMENT ON COLUMN ag_teams.update_memory_on_run              IS '是否每次运行后更新记忆';
COMMENT ON COLUMN ag_teams.enable_session_summaries          IS '是否开启会话摘要';
COMMENT ON COLUMN ag_teams.add_session_summary_to_context    IS '是否将会话摘要加入上下文';
COMMENT ON COLUMN ag_teams.tool_call_limit                   IS '工具调用次数上限';
COMMENT ON COLUMN ag_teams.stream                            IS '是否开启流式输出';
COMMENT ON COLUMN ag_teams.stream_events                     IS '是否流式推送事件';
COMMENT ON COLUMN ag_teams.debug_mode                        IS '是否开启调试模式';
COMMENT ON COLUMN ag_teams.metadata_config                          IS '元数据';
COMMENT ON COLUMN ag_teams.status                            IS '是否启用(0:启用 1:禁用)';
COMMENT ON COLUMN ag_teams.description                       IS '备注/描述';
COMMENT ON COLUMN ag_teams.created_time                      IS '创建时间';
COMMENT ON COLUMN ag_teams.updated_time                      IS '更新时间';
COMMENT ON COLUMN ag_teams.created_id                        IS '创建人ID';
COMMENT ON COLUMN ag_teams.updated_id                        IS '更新人ID';


-- ──────────────────────────────────────────────────────────
-- 5.15 ag_team_members（Team成员关系）
-- ──────────────────────────────────────────────────────────
CREATE TABLE ag_team_members (
    id            SERIAL NOT NULL,
    uuid          varchar(64) NOT NULL,
    team_id       integer NOT NULL,
    member_type   varchar(20) NOT NULL,
    member_id     integer NOT NULL,
    role          varchar(255),
    member_order  integer NOT NULL DEFAULT 0,
    status        varchar(10) NOT NULL DEFAULT '0',
    description   text,
    created_time  timestamp without time zone NOT NULL,
    updated_time  timestamp without time zone NOT NULL,
    created_id    integer,
    updated_id    integer,
    PRIMARY KEY(id),
    CONSTRAINT ag_team_members_team_id_unique   UNIQUE(team_id, member_type, member_id),
    CONSTRAINT ag_team_members_team_id_fkey     FOREIGN KEY(team_id)    REFERENCES ag_teams(id) ON DELETE CASCADE,
    CONSTRAINT ag_team_members_created_id_fkey  FOREIGN KEY(created_id) REFERENCES sys_user(id),
    CONSTRAINT ag_team_members_updated_id_fkey  FOREIGN KEY(updated_id) REFERENCES sys_user(id)
);
CREATE UNIQUE INDEX ag_team_members_uuid_key   ON public.ag_team_members USING btree (uuid);
CREATE INDEX ix_ag_team_members_team_id        ON public.ag_team_members USING btree (team_id);
CREATE INDEX ix_ag_team_members_status         ON public.ag_team_members USING btree (status);
CREATE INDEX ix_ag_team_members_created_id     ON public.ag_team_members USING btree (created_id);
CREATE INDEX ix_ag_team_members_updated_id     ON public.ag_team_members USING btree (updated_id);

COMMENT ON TABLE  ag_team_members              IS 'Team成员关系表';
COMMENT ON COLUMN ag_team_members.id           IS '主键ID';
COMMENT ON COLUMN ag_team_members.uuid         IS 'UUID全局唯一标识';
COMMENT ON COLUMN ag_team_members.team_id      IS '所属TeamID';
COMMENT ON COLUMN ag_team_members.member_type  IS '成员类型(agent/team)';
COMMENT ON COLUMN ag_team_members.member_id    IS '成员ID（agent或嵌套team）';
COMMENT ON COLUMN ag_team_members.role         IS '成员角色描述';
COMMENT ON COLUMN ag_team_members.member_order IS '成员排序（数字小优先）';
COMMENT ON COLUMN ag_team_members.status       IS '是否启用(0:启用 1:禁用)';
COMMENT ON COLUMN ag_team_members.description  IS '备注/描述';
COMMENT ON COLUMN ag_team_members.created_time IS '创建时间';
COMMENT ON COLUMN ag_team_members.updated_time IS '更新时间';
COMMENT ON COLUMN ag_team_members.created_id   IS '创建人ID';
COMMENT ON COLUMN ag_team_members.updated_id   IS '更新人ID';


-- ──────────────────────────────────────────────────────────
-- 5.16 ag_workflows（工作流管理）
-- ──────────────────────────────────────────────────────────
CREATE TABLE ag_workflows (
    id                               SERIAL NOT NULL,
    uuid                             varchar(64) NOT NULL,
    name                             varchar(255) NOT NULL,
    stream                           boolean NOT NULL DEFAULT false,
    stream_events                    boolean NOT NULL DEFAULT false,
    stream_executor_events           boolean NOT NULL DEFAULT true,
    store_events                     boolean NOT NULL DEFAULT false,
    store_executor_outputs           boolean NOT NULL DEFAULT true,
    add_workflow_history_to_steps    boolean NOT NULL DEFAULT false,
    num_history_runs                 integer NOT NULL DEFAULT 3,
    add_session_state_to_context     boolean NOT NULL DEFAULT false,
    debug_mode                       boolean NOT NULL DEFAULT false,
    input_schema                     jsonb,
    metadata_config                         jsonb NOT NULL DEFAULT '{}',
    status                           varchar(10) NOT NULL DEFAULT '0',
    description                      text,
    created_time                     timestamp without time zone NOT NULL,
    updated_time                     timestamp without time zone NOT NULL,
    created_id                       integer,
    updated_id                       integer,
    PRIMARY KEY(id),
    CONSTRAINT ag_workflows_created_id_fkey FOREIGN KEY(created_id) REFERENCES sys_user(id),
    CONSTRAINT ag_workflows_updated_id_fkey FOREIGN KEY(updated_id) REFERENCES sys_user(id)
);
CREATE UNIQUE INDEX ag_workflows_uuid_key   ON public.ag_workflows USING btree (uuid);
CREATE INDEX ix_ag_workflows_status         ON public.ag_workflows USING btree (status);
CREATE INDEX ix_ag_workflows_created_id     ON public.ag_workflows USING btree (created_id);
CREATE INDEX ix_ag_workflows_updated_id     ON public.ag_workflows USING btree (updated_id);

COMMENT ON TABLE  ag_workflows                               IS '工作流管理表';
COMMENT ON COLUMN ag_workflows.id                            IS '主键ID';
COMMENT ON COLUMN ag_workflows.uuid                          IS 'UUID全局唯一标识';
COMMENT ON COLUMN ag_workflows.name                          IS '工作流名称';
COMMENT ON COLUMN ag_workflows.stream                        IS '是否开启流式输出';
COMMENT ON COLUMN ag_workflows.stream_events                 IS '是否流式推送事件';
COMMENT ON COLUMN ag_workflows.stream_executor_events        IS '是否流式推送执行器事件';
COMMENT ON COLUMN ag_workflows.store_events                  IS '是否存储事件';
COMMENT ON COLUMN ag_workflows.store_executor_outputs        IS '是否存储执行器输出';
COMMENT ON COLUMN ag_workflows.add_workflow_history_to_steps IS '是否将工作流历史传给步骤';
COMMENT ON COLUMN ag_workflows.num_history_runs              IS '传给步骤的历史运行次数';
COMMENT ON COLUMN ag_workflows.add_session_state_to_context  IS '是否将会话状态加入上下文';
COMMENT ON COLUMN ag_workflows.debug_mode                    IS '是否开启调试模式';
COMMENT ON COLUMN ag_workflows.input_schema                  IS '输入结构体JSON Schema';
COMMENT ON COLUMN ag_workflows.metadata_config                      IS '元数据';
COMMENT ON COLUMN ag_workflows.status                        IS '是否启用(0:启用 1:禁用)';
COMMENT ON COLUMN ag_workflows.description                   IS '备注/描述';
COMMENT ON COLUMN ag_workflows.created_time                  IS '创建时间';
COMMENT ON COLUMN ag_workflows.updated_time                  IS '更新时间';
COMMENT ON COLUMN ag_workflows.created_id                    IS '创建人ID';
COMMENT ON COLUMN ag_workflows.updated_id                    IS '更新人ID';


-- ──────────────────────────────────────────────────────────
-- 5.16 ag_workflow_nodes（工作流节点）
-- ──────────────────────────────────────────────────────────
CREATE TABLE ag_workflow_nodes (
    id                        SERIAL NOT NULL,
    uuid                      varchar(64) NOT NULL,
    workflow_id               integer NOT NULL,
    parent_node_id            integer,
    node_order                integer NOT NULL,
    node_type                 varchar(20) NOT NULL,
    name                      varchar(255),

    -- step
    executor_type             varchar(20),
    agent_id                  integer,
    team_id                   integer,
    executor_module           varchar(500),
    add_workflow_history      boolean,
    num_history_runs          integer DEFAULT 3,
    strict_input_validation   boolean NOT NULL DEFAULT false,
    max_retries               integer NOT NULL DEFAULT 3,
    skip_on_failure           boolean NOT NULL DEFAULT false,

    -- condition
    evaluator_type            varchar(20),
    evaluator_value           text,
    branch                    varchar(10),

    -- loop
    max_iterations            integer DEFAULT 3,
    end_condition_type        varchar(20),
    end_condition_value       text,
    forward_iteration_output  boolean NOT NULL DEFAULT false,

    -- router
    selector_type             varchar(20),
    selector_value            text,
    allow_multiple_selections boolean NOT NULL DEFAULT false,

    -- HITL（所有节点共用）
    requires_confirmation     boolean NOT NULL DEFAULT false,
    confirmation_message      text,
    requires_user_input       boolean NOT NULL DEFAULT false,
    user_input_message        text,
    user_input_schema         jsonb,
    on_reject                 varchar(20) NOT NULL DEFAULT 'skip',
    on_error                  varchar(20) NOT NULL DEFAULT 'skip',

    status                    varchar(10) NOT NULL DEFAULT '0',
    description               text,
    created_time              timestamp without time zone NOT NULL,
    updated_time              timestamp without time zone NOT NULL,
    created_id                integer,
    updated_id                integer,
    PRIMARY KEY(id),
    CONSTRAINT ag_workflow_nodes_workflow_id_fkey    FOREIGN KEY(workflow_id)    REFERENCES ag_workflows(id) ON DELETE CASCADE,
    CONSTRAINT ag_workflow_nodes_parent_node_id_fkey FOREIGN KEY(parent_node_id) REFERENCES ag_workflow_nodes(id),
    CONSTRAINT ag_workflow_nodes_agent_id_fkey       FOREIGN KEY(agent_id)       REFERENCES ag_agents(id),
    CONSTRAINT ag_workflow_nodes_team_id_fkey        FOREIGN KEY(team_id)        REFERENCES ag_teams(id),
    CONSTRAINT ag_workflow_nodes_created_id_fkey     FOREIGN KEY(created_id)     REFERENCES sys_user(id),
    CONSTRAINT ag_workflow_nodes_updated_id_fkey     FOREIGN KEY(updated_id)     REFERENCES sys_user(id)
);
CREATE UNIQUE INDEX ag_workflow_nodes_uuid_key      ON public.ag_workflow_nodes USING btree (uuid);
CREATE INDEX ix_ag_workflow_nodes_workflow_id       ON public.ag_workflow_nodes USING btree (workflow_id);
CREATE INDEX ix_ag_workflow_nodes_parent_node_id    ON public.ag_workflow_nodes USING btree (parent_node_id);
CREATE INDEX ix_ag_workflow_nodes_status            ON public.ag_workflow_nodes USING btree (status);
CREATE INDEX ix_ag_workflow_nodes_created_id        ON public.ag_workflow_nodes USING btree (created_id);
CREATE INDEX ix_ag_workflow_nodes_updated_id        ON public.ag_workflow_nodes USING btree (updated_id);

COMMENT ON TABLE  ag_workflow_nodes                       IS '工作流节点管理表（step/condition/loop/parallel/router统一表）';
COMMENT ON COLUMN ag_workflow_nodes.id                    IS '主键ID';
COMMENT ON COLUMN ag_workflow_nodes.uuid                  IS 'UUID全局唯一标识';
COMMENT ON COLUMN ag_workflow_nodes.workflow_id           IS '所属工作流ID';
COMMENT ON COLUMN ag_workflow_nodes.parent_node_id        IS '父节点ID（NULL为顶层节点）';
COMMENT ON COLUMN ag_workflow_nodes.node_order            IS '节点顺序';
COMMENT ON COLUMN ag_workflow_nodes.node_type             IS '节点类型(step/condition/loop/parallel/router)';
COMMENT ON COLUMN ag_workflow_nodes.name                  IS '节点名称';
COMMENT ON COLUMN ag_workflow_nodes.executor_type         IS '执行器类型(agent/team/custom)';
COMMENT ON COLUMN ag_workflow_nodes.agent_id              IS '关联AgentID（executor_type=agent时）';
COMMENT ON COLUMN ag_workflow_nodes.team_id               IS '关联TeamID（executor_type=team时）';
COMMENT ON COLUMN ag_workflow_nodes.executor_module       IS '自定义执行器模块路径（executor_type=custom时）';
COMMENT ON COLUMN ag_workflow_nodes.add_workflow_history  IS '是否传入工作流历史';
COMMENT ON COLUMN ag_workflow_nodes.num_history_runs      IS '传入历史运行次数';
COMMENT ON COLUMN ag_workflow_nodes.strict_input_validation IS '是否严格校验输入';
COMMENT ON COLUMN ag_workflow_nodes.max_retries           IS '最大重试次数';
COMMENT ON COLUMN ag_workflow_nodes.skip_on_failure       IS '失败时是否跳过';
COMMENT ON COLUMN ag_workflow_nodes.evaluator_type        IS '条件评估器类型(bool/cel/function)';
COMMENT ON COLUMN ag_workflow_nodes.evaluator_value       IS '条件评估器值';
COMMENT ON COLUMN ag_workflow_nodes.branch                IS '分支标记(if/else)';
COMMENT ON COLUMN ag_workflow_nodes.max_iterations        IS '循环最大迭代次数';
COMMENT ON COLUMN ag_workflow_nodes.end_condition_type    IS '循环终止条件类型';
COMMENT ON COLUMN ag_workflow_nodes.end_condition_value   IS '循环终止条件值';
COMMENT ON COLUMN ag_workflow_nodes.forward_iteration_output IS '是否传递迭代输出';
COMMENT ON COLUMN ag_workflow_nodes.selector_type         IS '路由选择器类型';
COMMENT ON COLUMN ag_workflow_nodes.selector_value        IS '路由选择器值';
COMMENT ON COLUMN ag_workflow_nodes.allow_multiple_selections IS '是否允许多路由选择';
COMMENT ON COLUMN ag_workflow_nodes.requires_confirmation IS '是否需要用户确认（HITL）';
COMMENT ON COLUMN ag_workflow_nodes.confirmation_message  IS '确认提示消息';
COMMENT ON COLUMN ag_workflow_nodes.requires_user_input   IS '是否需要用户输入（HITL）';
COMMENT ON COLUMN ag_workflow_nodes.user_input_message    IS '用户输入提示消息';
COMMENT ON COLUMN ag_workflow_nodes.user_input_schema     IS '用户输入结构体Schema';
COMMENT ON COLUMN ag_workflow_nodes.on_reject             IS '用户拒绝时处理策略(skip/abort)';
COMMENT ON COLUMN ag_workflow_nodes.on_error              IS '节点出错时处理策略(skip/abort)';
COMMENT ON COLUMN ag_workflow_nodes.status                IS '是否启用(0:启用 1:禁用)';
COMMENT ON COLUMN ag_workflow_nodes.description           IS '备注/描述';
COMMENT ON COLUMN ag_workflow_nodes.created_time          IS '创建时间';
COMMENT ON COLUMN ag_workflow_nodes.updated_time          IS '更新时间';
COMMENT ON COLUMN ag_workflow_nodes.created_id            IS '创建人ID';
COMMENT ON COLUMN ag_workflow_nodes.updated_id            IS '更新人ID';


-- ──────────────────────────────────────────────────────────
-- 5.17 ag_integrations（渠道集成管理）
-- ──────────────────────────────────────────────────────────
CREATE TABLE ag_integrations (
    id              SERIAL NOT NULL,
    uuid            varchar(64) NOT NULL,
    name            varchar(255) NOT NULL,
    type            varchar(20) NOT NULL,
    agent_id        integer,
    team_id         integer,
    workflow_id     integer,
    token           text,
    signing_secret  text,
    prefix          varchar(100),
    config          jsonb NOT NULL DEFAULT '{}',
    status          varchar(10) NOT NULL DEFAULT '0',
    description     text,
    created_time    timestamp without time zone NOT NULL,
    updated_time    timestamp without time zone NOT NULL,
    created_id      integer,
    updated_id      integer,
    PRIMARY KEY(id),
    CONSTRAINT ag_integrations_agent_id_fkey    FOREIGN KEY(agent_id)    REFERENCES ag_agents(id),
    CONSTRAINT ag_integrations_team_id_fkey     FOREIGN KEY(team_id)     REFERENCES ag_teams(id),
    CONSTRAINT ag_integrations_workflow_id_fkey FOREIGN KEY(workflow_id) REFERENCES ag_workflows(id),
    CONSTRAINT ag_integrations_created_id_fkey  FOREIGN KEY(created_id)  REFERENCES sys_user(id),
    CONSTRAINT ag_integrations_updated_id_fkey  FOREIGN KEY(updated_id)  REFERENCES sys_user(id)
);
CREATE UNIQUE INDEX ag_integrations_uuid_key       ON public.ag_integrations USING btree (uuid);
CREATE INDEX ix_ag_integrations_type               ON public.ag_integrations USING btree (type);
CREATE INDEX ix_ag_integrations_agent_id           ON public.ag_integrations USING btree (agent_id);
CREATE INDEX ix_ag_integrations_team_id            ON public.ag_integrations USING btree (team_id);
CREATE INDEX ix_ag_integrations_workflow_id        ON public.ag_integrations USING btree (workflow_id);
CREATE INDEX ix_ag_integrations_status             ON public.ag_integrations USING btree (status);
CREATE INDEX ix_ag_integrations_created_id         ON public.ag_integrations USING btree (created_id);
CREATE INDEX ix_ag_integrations_updated_id         ON public.ag_integrations USING btree (updated_id);

COMMENT ON TABLE  ag_integrations                IS '渠道集成管理表';
COMMENT ON COLUMN ag_integrations.id             IS '主键ID';
COMMENT ON COLUMN ag_integrations.uuid           IS 'UUID全局唯一标识';
COMMENT ON COLUMN ag_integrations.name           IS '渠道名称';
COMMENT ON COLUMN ag_integrations.type           IS '渠道类型(slack/telegram/whatsapp/agui/discord)';
COMMENT ON COLUMN ag_integrations.agent_id       IS '绑定AgentID（三选一）';
COMMENT ON COLUMN ag_integrations.team_id        IS '绑定TeamID（三选一）';
COMMENT ON COLUMN ag_integrations.workflow_id    IS '绑定WorkflowID（三选一）';
COMMENT ON COLUMN ag_integrations.token          IS '渠道访问Token（Slack/Telegram等）';
COMMENT ON COLUMN ag_integrations.signing_secret IS '签名密钥（Slack校验用）';
COMMENT ON COLUMN ag_integrations.prefix         IS '路由前缀（如/slack /telegram）';
COMMENT ON COLUMN ag_integrations.config         IS '渠道扩展配置（streaming/reply_to_mentions_only等）';
COMMENT ON COLUMN ag_integrations.status         IS '是否启用(0:启用 1:禁用)';
COMMENT ON COLUMN ag_integrations.description    IS '备注/描述';
COMMENT ON COLUMN ag_integrations.created_time   IS '创建时间';
COMMENT ON COLUMN ag_integrations.updated_time   IS '更新时间';
COMMENT ON COLUMN ag_integrations.created_id     IS '创建人ID';
COMMENT ON COLUMN ag_integrations.updated_id     IS '更新人ID';


-- ──────────────────────────────────────────────────────────
-- 5.18 ag_schedules（定时任务管理）
-- ──────────────────────────────────────────────────────────
CREATE TABLE ag_schedules (
    id                    SERIAL NOT NULL,
    uuid                  varchar(64) NOT NULL,
    name                  varchar(255) NOT NULL,
    agent_id              integer,
    team_id               integer,
    payload               jsonb NOT NULL DEFAULT '{}',
    cron_expr             varchar(100) NOT NULL,
    timezone              varchar(100) NOT NULL DEFAULT 'UTC',
    timeout_seconds       integer NOT NULL DEFAULT 3600,
    max_retries           integer NOT NULL DEFAULT 0,
    retry_delay_seconds   integer NOT NULL DEFAULT 60,
    status                varchar(10) NOT NULL DEFAULT '0',
    description           text,
    created_time          timestamp without time zone NOT NULL,
    updated_time          timestamp without time zone NOT NULL,
    created_id            integer,
    updated_id            integer,
    PRIMARY KEY(id),
    CONSTRAINT ag_schedules_agent_id_fkey    FOREIGN KEY(agent_id)    REFERENCES ag_agents(id),
    CONSTRAINT ag_schedules_team_id_fkey     FOREIGN KEY(team_id)     REFERENCES ag_teams(id),
    CONSTRAINT ag_schedules_created_id_fkey  FOREIGN KEY(created_id)  REFERENCES sys_user(id),
    CONSTRAINT ag_schedules_updated_id_fkey  FOREIGN KEY(updated_id)  REFERENCES sys_user(id)
);
CREATE UNIQUE INDEX ag_schedules_uuid_key    ON public.ag_schedules USING btree (uuid);
CREATE INDEX ix_ag_schedules_agent_id        ON public.ag_schedules USING btree (agent_id);
CREATE INDEX ix_ag_schedules_team_id         ON public.ag_schedules USING btree (team_id);
CREATE INDEX ix_ag_schedules_status          ON public.ag_schedules USING btree (status);
CREATE INDEX ix_ag_schedules_created_id      ON public.ag_schedules USING btree (created_id);
CREATE INDEX ix_ag_schedules_updated_id      ON public.ag_schedules USING btree (updated_id);

COMMENT ON TABLE  ag_schedules                    IS '定时任务管理表';
COMMENT ON COLUMN ag_schedules.id                 IS '主键ID';
COMMENT ON COLUMN ag_schedules.uuid               IS 'UUID全局唯一标识';
COMMENT ON COLUMN ag_schedules.name               IS '定时任务名称';
COMMENT ON COLUMN ag_schedules.agent_id           IS '触发目标AgentID';
COMMENT ON COLUMN ag_schedules.team_id            IS '触发目标TeamID';
COMMENT ON COLUMN ag_schedules.payload            IS '触发时传入的消息/参数';
COMMENT ON COLUMN ag_schedules.cron_expr          IS 'Cron表达式（如0 9 * * 1-5）';
COMMENT ON COLUMN ag_schedules.timezone           IS '时区（如Asia/Shanghai）';
COMMENT ON COLUMN ag_schedules.timeout_seconds    IS '任务超时秒数';
COMMENT ON COLUMN ag_schedules.max_retries        IS '失败最大重试次数';
COMMENT ON COLUMN ag_schedules.retry_delay_seconds IS '重试间隔秒数';
COMMENT ON COLUMN ag_schedules.status             IS '是否启用(0:启用 1:禁用)';
COMMENT ON COLUMN ag_schedules.description        IS '备注/描述';
COMMENT ON COLUMN ag_schedules.created_time       IS '创建时间';
COMMENT ON COLUMN ag_schedules.updated_time       IS '更新时间';
COMMENT ON COLUMN ag_schedules.created_id         IS '创建人ID';
COMMENT ON COLUMN ag_schedules.updated_id         IS '更新人ID';


-- ──────────────────────────────────────────────────────────
-- 5.19 ag_roles（角色管理）
-- ──────────────────────────────────────────────────────────
CREATE TABLE ag_roles (
    id            SERIAL NOT NULL,
    uuid          varchar(64) NOT NULL,
    name          varchar(100) NOT NULL,
    scopes        jsonb NOT NULL,
    status        varchar(10) NOT NULL DEFAULT '0',
    description   text,
    created_time  timestamp without time zone NOT NULL,
    updated_time  timestamp without time zone NOT NULL,
    created_id    integer,
    updated_id    integer,
    PRIMARY KEY(id),
    CONSTRAINT ag_roles_name_unique        UNIQUE(name),
    CONSTRAINT ag_roles_created_id_fkey    FOREIGN KEY(created_id) REFERENCES sys_user(id),
    CONSTRAINT ag_roles_updated_id_fkey    FOREIGN KEY(updated_id) REFERENCES sys_user(id)
);
CREATE UNIQUE INDEX ag_roles_uuid_key   ON public.ag_roles USING btree (uuid);
CREATE INDEX ix_ag_roles_status         ON public.ag_roles USING btree (status);
CREATE INDEX ix_ag_roles_created_id     ON public.ag_roles USING btree (created_id);
CREATE INDEX ix_ag_roles_updated_id     ON public.ag_roles USING btree (updated_id);

COMMENT ON TABLE  ag_roles              IS '角色管理表';
COMMENT ON COLUMN ag_roles.id           IS '主键ID';
COMMENT ON COLUMN ag_roles.uuid         IS 'UUID全局唯一标识';
COMMENT ON COLUMN ag_roles.name         IS '角色名称（唯一，如admin/operator/viewer）';
COMMENT ON COLUMN ag_roles.scopes       IS 'AgentOS权限范围列表（JSON数组）';
COMMENT ON COLUMN ag_roles.status       IS '是否启用(0:启用 1:禁用)';
COMMENT ON COLUMN ag_roles.description  IS '角色描述';
COMMENT ON COLUMN ag_roles.created_time IS '创建时间';
COMMENT ON COLUMN ag_roles.updated_time IS '更新时间';
COMMENT ON COLUMN ag_roles.created_id   IS '创建人ID';
COMMENT ON COLUMN ag_roles.updated_id   IS '更新人ID';


-- ──────────────────────────────────────────────────────────
-- 5.19 ag_user_roles（用户角色关联）
-- ──────────────────────────────────────────────────────────
CREATE TABLE ag_user_roles (
    id            SERIAL NOT NULL,
    uuid          varchar(64) NOT NULL,
    user_id       varchar(255) NOT NULL,
    role_id       integer NOT NULL,
    created_time  timestamp without time zone NOT NULL,
    updated_time  timestamp without time zone NOT NULL,
    created_id    integer,
    updated_id    integer,
    PRIMARY KEY(id),
    CONSTRAINT ag_user_roles_user_role_unique  UNIQUE(user_id, role_id),
    CONSTRAINT ag_user_roles_role_id_fkey      FOREIGN KEY(role_id)    REFERENCES ag_roles(id) ON DELETE CASCADE,
    CONSTRAINT ag_user_roles_created_id_fkey   FOREIGN KEY(created_id) REFERENCES sys_user(id),
    CONSTRAINT ag_user_roles_updated_id_fkey   FOREIGN KEY(updated_id) REFERENCES sys_user(id)
);
CREATE UNIQUE INDEX ag_user_roles_uuid_key   ON public.ag_user_roles USING btree (uuid);
CREATE INDEX ix_ag_user_roles_user_id        ON public.ag_user_roles USING btree (user_id);
CREATE INDEX ix_ag_user_roles_role_id        ON public.ag_user_roles USING btree (role_id);
CREATE INDEX ix_ag_user_roles_created_id     ON public.ag_user_roles USING btree (created_id);
CREATE INDEX ix_ag_user_roles_updated_id     ON public.ag_user_roles USING btree (updated_id);

COMMENT ON TABLE  ag_user_roles              IS '用户角色关联表';
COMMENT ON COLUMN ag_user_roles.id           IS '主键ID';
COMMENT ON COLUMN ag_user_roles.uuid         IS 'UUID全局唯一标识';
COMMENT ON COLUMN ag_user_roles.user_id      IS '用户ID（来自外部Auth系统）';
COMMENT ON COLUMN ag_user_roles.role_id      IS '角色ID';
COMMENT ON COLUMN ag_user_roles.created_time IS '授权时间';
COMMENT ON COLUMN ag_user_roles.updated_time IS '更新时间';
COMMENT ON COLUMN ag_user_roles.created_id   IS '创建人ID';
COMMENT ON COLUMN ag_user_roles.updated_id   IS '更新人ID';


-- ──────────────────────────────────────────────────────────
-- 5.21 ag_usage_logs（用量日志，追加写）
-- ──────────────────────────────────────────────────────────
CREATE TABLE ag_usage_logs (
    id             BIGSERIAL NOT NULL,
    uuid           varchar(64) NOT NULL,
    agent_id       integer,
    user_id        varchar(255),
    session_id     varchar(255),
    model_id       integer,
    input_tokens   bigint NOT NULL DEFAULT 0,
    output_tokens  bigint NOT NULL DEFAULT 0,
    cost_usd       decimal(12, 6),
    latency_ms     integer,
    created_time   timestamp without time zone NOT NULL,
    PRIMARY KEY(id)
);
CREATE UNIQUE INDEX ag_usage_logs_uuid_key    ON public.ag_usage_logs USING btree (uuid);
CREATE INDEX ix_ag_usage_logs_user_id         ON public.ag_usage_logs USING btree (user_id,  created_time DESC);
CREATE INDEX ix_ag_usage_logs_agent_id        ON public.ag_usage_logs USING btree (agent_id, created_time DESC);
CREATE INDEX ix_ag_usage_logs_created_time    ON public.ag_usage_logs USING btree (created_time DESC);

COMMENT ON TABLE  ag_usage_logs              IS '用量日志表（追加写，BIGSERIAL避免UUID索引碎片）';
COMMENT ON COLUMN ag_usage_logs.id           IS '主键ID';
COMMENT ON COLUMN ag_usage_logs.uuid         IS 'UUID全局唯一标识';
COMMENT ON COLUMN ag_usage_logs.agent_id     IS '关联AgentID';
COMMENT ON COLUMN ag_usage_logs.user_id      IS '用户ID';
COMMENT ON COLUMN ag_usage_logs.session_id   IS '会话ID';
COMMENT ON COLUMN ag_usage_logs.model_id     IS '关联模型ID';
COMMENT ON COLUMN ag_usage_logs.input_tokens IS '输入Token数';
COMMENT ON COLUMN ag_usage_logs.output_tokens IS '输出Token数';
COMMENT ON COLUMN ag_usage_logs.cost_usd     IS '本次调用费用（美元）';
COMMENT ON COLUMN ag_usage_logs.latency_ms   IS '首Token延迟毫秒数';
COMMENT ON COLUMN ag_usage_logs.created_time IS '记录时间';


-- ──────────────────────────────────────────────────────────
-- 5.21 ag_audit_logs（审计日志，追加写）
-- ──────────────────────────────────────────────────────────
CREATE TABLE ag_audit_logs (
    id             BIGSERIAL NOT NULL,
    uuid           varchar(64) NOT NULL,
    actor_id       varchar(255),
    action         varchar(20) NOT NULL,
    resource_type  varchar(50) NOT NULL,
    resource_id    integer,
    diff           jsonb,
    ip             varchar(50),
    created_time   timestamp without time zone NOT NULL,
    PRIMARY KEY(id)
);
CREATE UNIQUE INDEX ag_audit_logs_uuid_key      ON public.ag_audit_logs USING btree (uuid);
CREATE INDEX ix_ag_audit_logs_resource          ON public.ag_audit_logs USING btree (resource_type, resource_id);
CREATE INDEX ix_ag_audit_logs_actor_id          ON public.ag_audit_logs USING btree (actor_id, created_time DESC);

COMMENT ON TABLE  ag_audit_logs               IS '审计日志表（追加写）';
COMMENT ON COLUMN ag_audit_logs.id            IS '主键ID';
COMMENT ON COLUMN ag_audit_logs.uuid          IS 'UUID全局唯一标识';
COMMENT ON COLUMN ag_audit_logs.actor_id      IS '操作人ID';
COMMENT ON COLUMN ag_audit_logs.action        IS '操作类型(CREATE/UPDATE/DELETE/RUN)';
COMMENT ON COLUMN ag_audit_logs.resource_type IS '资源类型';
COMMENT ON COLUMN ag_audit_logs.resource_id   IS '资源ID';
COMMENT ON COLUMN ag_audit_logs.diff          IS '变更前后数据对比（JSON）';
COMMENT ON COLUMN ag_audit_logs.ip            IS '操作来源IP';
COMMENT ON COLUMN ag_audit_logs.created_time  IS '操作时间';
