import { apiClient } from "./client";
import {
  APIResponse,
  Source,
  SourceListResponse,
  SourceStatistics,
  SourceRefreshResponse,
  IngestionItemResult,
} from "@/types";

export const sourcesApi = {
  /**
   * Fetch aggregate knowledge base statistics
   */
  async getStatistics(): Promise<SourceStatistics> {
    const res = await apiClient.get<APIResponse<SourceStatistics>>(
      "/api/v1/sources/statistics"
    );
    return res.data.data;
  },

  /**
   * List indexed sources with pagination
   */
  async listSources(limit = 100, offset = 0): Promise<SourceListResponse> {
    const res = await apiClient.get<APIResponse<SourceListResponse>>(
      "/api/v1/sources",
      {
        params: { limit, offset },
      }
    );
    return res.data.data;
  },

  /**
   * Directly ingest a single source URL
   */
  async createSource(url: string, forceRefresh = false): Promise<IngestionItemResult> {
    const res = await apiClient.post<APIResponse<IngestionItemResult>>(
      "/api/v1/sources",
      {
        url,
        force_refresh: forceRefresh,
      }
    );
    return res.data.data;
  },

  /**
   * Fetch specific source metadata by ID
   */
  async getSource(sourceId: string): Promise<Source> {
    const res = await apiClient.get<APIResponse<Source>>(
      `/api/v1/sources/${encodeURIComponent(sourceId)}`
    );
    return res.data.data;
  },

  /**
   * Delete a source and purge its embeddings from vector database
   */
  async deleteSource(sourceId: string): Promise<{ source_id: string; deleted: boolean }> {
    const res = await apiClient.delete<APIResponse<{ source_id: string; deleted: boolean }>>(
      `/api/v1/sources/${encodeURIComponent(sourceId)}`
    );
    return res.data.data;
  },

  /**
   * Re-scrape and refresh embeddings for a source URL
   */
  async refreshSource(sourceId: string): Promise<SourceRefreshResponse> {
    const res = await apiClient.put<APIResponse<SourceRefreshResponse>>(
      `/api/v1/sources/${encodeURIComponent(sourceId)}/refresh`
    );
    return res.data.data;
  },
};
