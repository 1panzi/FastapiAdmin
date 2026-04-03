import agnoRequest from "./agnoRequest";
import { createRunStream } from "./chat";
import type { RunForm, AgentRunResponse, AgentStreamEvent } from "./chat";

const TEAM_PATH = "/teams";

const AgnoTeamChatAPI = {
  runTeam(teamId: number, body: RunForm) {
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
      url: `${TEAM_PATH}/${teamId}/runs`,
      method: "post",
      data: formData,
      headers: { "Content-Type": "multipart/form-data" },
    });
  },

  runTeamStream(
    teamId: number,
    body: RunForm,
    onChunk: (event: string, data: AgentStreamEvent) => void,
    onDone: () => void,
    onError: (err: Error) => void
  ): AbortController {
    return createRunStream(`${TEAM_PATH}/${teamId}/runs`, body, onChunk, onDone, onError);
  },
};

export default AgnoTeamChatAPI;
