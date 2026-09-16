import { apiClient } from "./client";
import { APIResponse, HealthStatus } from "@/types";

export const healthApi = {
  /**
   * Check system health, vectorstore diagnostics, and active models
   */
  async checkHealth(): Promise<HealthStatus> {
    const res = await apiClient.get<APIResponse<HealthStatus>>("/health");
    return res.data.data;
  },
};
