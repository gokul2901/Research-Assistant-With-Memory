import { apiClient } from "./client";
import {
  APIResponse,
  ChatRequest,
  ChatResponse,
  ChatSessionHistoryResponse,
} from "@/types";

export const chatApi = {
  /**
   * Ask a question across all ingested sources with grounded citations
   */
  async askQuestion(payload: ChatRequest): Promise<ChatResponse> {
    const res = await apiClient.post<APIResponse<ChatResponse>>(
      "/api/v1/chat",
      payload
    );
    return res.data.data;
  },

  /**
   * Retrieve session conversation history and grounded citations
   */
  async getSessionHistory(sessionId: string): Promise<ChatSessionHistoryResponse> {
    const res = await apiClient.get<APIResponse<ChatSessionHistoryResponse>>(
      `/api/v1/chat/history/${encodeURIComponent(sessionId)}`
    );
    return res.data.data;
  },
};
