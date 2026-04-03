import agnoRequest from "./agnoRequest";
import { createRunStream } from "./chat";
import type { RunForm, AgentRunResponse, AgentStreamEvent } from "./chat";

const WORKFLOW_PATH = "/workflows";

const AgnoWorkflowChatAPI = {
  runWorkflow(workflowId: number, body: RunForm) {
    const formData = new FormData();
    formData.append("message", body.message);
    formData.append("stream", "false");
    formData.append("session_id", body.session_id);
    formData.append("user_id", String(body.user_id));
    formData.append("background", "false");
    if (body.version !== undefined) formData.append("version", body.version ?? "");
    if (body.files?.length) {
      body.files.forEach((f) => formData.append("files", f));
    }
    return agnoRequest<AgentRunResponse>({
      url: `${WORKFLOW_PATH}/${workflowId}/runs`,
      method: "post",
      data: formData,
      headers: { "Content-Type": "multipart/form-data" },
    });
  },

  runWorkflowStream(
    workflowId: number,
    body: RunForm,
    onChunk: (event: string, data: AgentStreamEvent) => void,
    onDone: () => void,
    onError: (err: Error) => void
  ): AbortController {
    return createRunStream(`${WORKFLOW_PATH}/${workflowId}/runs`, body, onChunk, onDone, onError);
  },
};

export default AgnoWorkflowChatAPI;
