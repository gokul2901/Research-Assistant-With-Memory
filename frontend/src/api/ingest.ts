import { apiClient } from "./client";
import {
  APIResponse,
  IngestUrlRequest,
  IngestionSummaryResponse,
} from "@/types";

export const ingestApi = {
  /**
   * Ingest single or batch URLs into the knowledge base
   */
  async ingestUrls(
    urls: string[],
    forceRefresh = false
  ): Promise<IngestionSummaryResponse> {
    const payload: IngestUrlRequest = {
      urls,
      force_refresh: forceRefresh,
    };
    const res = await apiClient.post<APIResponse<IngestionSummaryResponse>>(
      "/api/v1/ingest",
      payload
    );
    return res.data.data;
  },
};
