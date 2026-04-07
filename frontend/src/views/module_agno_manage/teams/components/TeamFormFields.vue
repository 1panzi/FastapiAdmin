<!-- Team 表单字段组件：供 teams/index.vue Dialog 和 team_builder 右侧面板复用 -->
<template>
  <el-form
    ref="formRef"
    :model="formData"
    :rules="rules"
    label-suffix=":"
    label-width="160px"
    label-position="right"
  >
    <el-tabs type="border-card" class="team-form-tabs">
      <!-- ══ Tab 1: 基本信息 ══ -->
      <el-tab-pane label="基本信息">
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="Team名称" prop="name">
              <el-input v-model="formData.name" placeholder="请输入Team名称" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="主模型" prop="model_id" :required="false">
              <LazySelect v-model="formData.model_id" :fetcher="modelFetcher" placeholder="请选择主模型" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="记忆管理器" prop="memory_manager_id" :required="false">
              <LazySelect v-model="formData.memory_manager_id" :fetcher="memoryManagerFetcher" placeholder="请选择记忆管理器" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="协作模式" prop="mode" :required="false">
              <el-select v-model="formData.mode" placeholder="请选择协作模式" clearable style="width: 100%">
                <el-option value="route" label="route（路由）" />
                <el-option value="coordinate" label="coordinate（协调）" />
                <el-option value="collaborate" label="collaborate（协作）" />
                <el-option value="tasks" label="tasks（任务）" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="状态" prop="status" :required="false">
              <el-radio-group v-model="formData.status">
                <el-radio value="0">启用</el-radio>
                <el-radio value="1">停用</el-radio>
              </el-radio-group>
            </el-form-item>
          </el-col>
          <el-col :span="24">
            <el-form-item label="Team指令" prop="instructions" :required="false">
              <el-input v-model="formData.instructions" placeholder="请输入Team指令（system prompt）" type="textarea" :rows="4" />
            </el-form-item>
          </el-col>
          <el-col :span="24">
            <el-form-item label="期望输出格式" prop="expected_output" :required="false">
              <el-input v-model="formData.expected_output" placeholder="请输入期望输出格式说明" type="textarea" :rows="2" />
            </el-form-item>
          </el-col>
          <el-col :span="24">
            <el-form-item label="描述" prop="description" :required="false">
              <el-input v-model="formData.description" :rows="3" :maxlength="100" show-word-limit type="textarea" placeholder="请输入描述" />
            </el-form-item>
          </el-col>
        </el-row>
      </el-tab-pane>

      <!-- ══ Tab 2: 成员协作 ══ -->
      <el-tab-pane label="成员协作">
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="是否直接响应" prop="respond_directly" :required="false">
              <el-select v-model="formData.respond_directly" placeholder="默认" clearable style="width:100%">
                <el-option label="开启" :value="true" />
                <el-option label="关闭" :value="false" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="分发给所有成员" prop="delegate_to_all_members" :required="false">
              <el-select v-model="formData.delegate_to_all_members" placeholder="默认" clearable style="width:100%">
                <el-option label="开启" :value="true" />
                <el-option label="关闭" :value="false" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="为成员决定输入" prop="determine_input_for_members" :required="false">
              <el-select v-model="formData.determine_input_for_members" placeholder="默认" clearable style="width:100%">
                <el-option label="开启" :value="true" />
                <el-option label="关闭" :value="false" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="最大迭代次数" prop="max_iterations" :required="false">
              <el-input-number v-model="formData.max_iterations" :min="1" :precision="0" style="width:100%" :controls="false" placeholder="默认" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="传Team历史给成员" prop="add_team_history_to_members" :required="false">
              <el-select v-model="formData.add_team_history_to_members" placeholder="默认" clearable style="width:100%">
                <el-option label="开启" :value="true" />
                <el-option label="关闭" :value="false" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="传给成员历史次数" prop="num_team_history_runs" :required="false">
              <el-input-number v-model="formData.num_team_history_runs" :min="0" :precision="0" style="width:100%" :controls="false" placeholder="默认" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="共享成员交互" prop="share_member_interactions" :required="false">
              <el-select v-model="formData.share_member_interactions" placeholder="默认" clearable style="width:100%">
                <el-option label="开启" :value="true" />
                <el-option label="关闭" :value="false" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="成员工具加入上下文" prop="add_member_tools_to_context" :required="false">
              <el-select v-model="formData.add_member_tools_to_context" placeholder="默认" clearable style="width:100%">
                <el-option label="开启" :value="true" />
                <el-option label="关闭" :value="false" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="工具调用次数上限" prop="tool_call_limit" :required="false">
              <el-input-number v-model="formData.tool_call_limit" :min="0" :precision="0" style="width:100%" :controls="false" placeholder="不限制" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="流式输出" prop="stream" :required="false">
              <el-select v-model="formData.stream" placeholder="默认" clearable style="width:100%">
                <el-option label="开启" :value="true" />
                <el-option label="关闭" :value="false" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="流式推送事件" prop="stream_events" :required="false">
              <el-select v-model="formData.stream_events" placeholder="默认" clearable style="width:100%">
                <el-option label="开启" :value="true" />
                <el-option label="关闭" :value="false" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="输出Markdown" prop="markdown" :required="false">
              <el-select v-model="formData.markdown" placeholder="默认" clearable style="width:100%">
                <el-option label="开启" :value="true" />
                <el-option label="关闭" :value="false" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="调试模式" prop="debug_mode" :required="false">
              <el-select v-model="formData.debug_mode" placeholder="默认" clearable style="width:100%">
                <el-option label="开启" :value="true" />
                <el-option label="关闭" :value="false" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
      </el-tab-pane>

      <!-- ══ Tab 3: 历史与记忆 ══ -->
      <el-tab-pane label="历史与记忆">
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="读取聊天历史" prop="read_chat_history" :required="false">
              <el-select v-model="formData.read_chat_history" placeholder="默认" clearable style="width:100%">
                <el-option label="开启" :value="true" />
                <el-option label="关闭" :value="false" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="搜索历史会话" prop="search_past_sessions" :required="false">
              <el-select v-model="formData.search_past_sessions" placeholder="默认" clearable style="width:100%">
                <el-option label="开启" :value="true" />
                <el-option label="关闭" :value="false" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="搜索历史会话数量" prop="num_past_sessions_to_search" :required="false">
              <el-input-number v-model="formData.num_past_sessions_to_search" :min="0" :precision="0" style="width:100%" :controls="false" placeholder="默认" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="智能记忆" prop="enable_agentic_memory" :required="false">
              <el-select v-model="formData.enable_agentic_memory" placeholder="默认" clearable style="width:100%">
                <el-option label="开启" :value="true" />
                <el-option label="关闭" :value="false" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="运行后更新记忆" prop="update_memory_on_run" :required="false">
              <el-select v-model="formData.update_memory_on_run" placeholder="默认" clearable style="width:100%">
                <el-option label="开启" :value="true" />
                <el-option label="关闭" :value="false" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="开启会话摘要" prop="enable_session_summaries" :required="false">
              <el-select v-model="formData.enable_session_summaries" placeholder="默认" clearable style="width:100%">
                <el-option label="开启" :value="true" />
                <el-option label="关闭" :value="false" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="摘要加入上下文" prop="add_session_summary_to_context" :required="false">
              <el-select v-model="formData.add_session_summary_to_context" placeholder="默认" clearable style="width:100%">
                <el-option label="开启" :value="true" />
                <el-option label="关闭" :value="false" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
      </el-tab-pane>

      <!-- ══ Tab 4: 知识库 ══ -->
      <el-tab-pane label="知识库">
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="搜索知识库" prop="search_knowledge" :required="false">
              <el-select v-model="formData.search_knowledge" placeholder="默认" clearable style="width:100%">
                <el-option label="开启" :value="true" />
                <el-option label="关闭" :value="false" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="允许更新知识库" prop="update_knowledge" :required="false">
              <el-select v-model="formData.update_knowledge" placeholder="默认" clearable style="width:100%">
                <el-option label="开启" :value="true" />
                <el-option label="关闭" :value="false" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="智能知识过滤" prop="enable_agentic_knowledge_filters" :required="false">
              <el-select v-model="formData.enable_agentic_knowledge_filters" placeholder="默认" clearable style="width:100%">
                <el-option label="开启" :value="true" />
                <el-option label="关闭" :value="false" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="智能状态" prop="enable_agentic_state" :required="false">
              <el-select v-model="formData.enable_agentic_state" placeholder="默认" clearable style="width:100%">
                <el-option label="开启" :value="true" />
                <el-option label="关闭" :value="false" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
      </el-tab-pane>

      <!-- ══ Tab 5: 元数据 ══ -->
      <el-tab-pane label="元数据">
        <el-form-item label="元数据配置" prop="metadata_config" :required="false">
          <DictEditor v-model="formData.metadata_config" />
        </el-form-item>
      </el-tab-pane>
    </el-tabs>
  </el-form>
</template>

<script setup lang="ts">
import { ref } from "vue";
import LazySelect from "@/views/module_agno_manage/components/LazySelect/index.vue";
import DictEditor from "@/views/module_agno_manage/components/DictEditor/index.vue";
import AgModelAPI from "@/api/module_agno_manage/models";
import AgMemoryManagerAPI from "@/api/module_agno_manage/memory_managers";
import type { AgTeamForm } from "@/api/module_agno_manage/teams";

defineOptions({ name: "TeamFormFields", inheritAttrs: false });

defineProps<{
  formData: AgTeamForm;
}>();

const formRef = ref();

// 代理暴露 validate/resetFields/clearValidate，父组件可直接调用 ref.validate()
defineExpose({
  formRef,
  validate: (...args: any[]) => formRef.value?.validate(...args),
  resetFields: () => formRef.value?.resetFields(),
  clearValidate: () => formRef.value?.clearValidate(),
});

const rules = {
  name: [{ required: true, message: "请输入Team名称", trigger: "blur" }],
};

// LazySelect fetchers
const modelFetcher = async (params: { page_no: number; page_size: number; name?: string }) => {
  const res = await AgModelAPI.listAgModel({ ...params });
  const items = (res.data?.data?.items || []).map((item: any) => ({
    value: String(item.id),
    label: item.name || String(item.id),
    raw: item,
  }));
  return { items, total: res.data?.data?.total || 0 };
};

const memoryManagerFetcher = async (params: { page_no: number; page_size: number; name?: string }) => {
  const res = await AgMemoryManagerAPI.listAgMemoryManager({ ...params });
  const items = (res.data?.data?.items || []).map((item: any) => ({
    value: String(item.id),
    label: item.name || String(item.id),
    raw: item,
  }));
  return { items, total: res.data?.data?.total || 0 };
};
</script>

<style lang="scss" scoped>
.team-form-tabs {
  width: 100%;
}
</style>
