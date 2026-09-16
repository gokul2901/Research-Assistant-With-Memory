import { apiClient, API_BASE_URL } from "./client";
import { APIResponse, ExportPDFRequest, ExportPDFResponse } from "@/types";

export const exportApi = {
  /**
   * Request backend to generate intelligence PDF report
   */
  async generatePDF(payload: ExportPDFRequest): Promise<ExportPDFResponse> {
    const res = await apiClient.post<APIResponse<ExportPDFResponse>>(
      "/api/v1/export/pdf",
      payload
    );
    return res.data.data;
  },

  /**
   * Get full download URL for generated PDF
   */
  getPdfDownloadUrl(relativeOrFullUrl: string): string {
    if (relativeOrFullUrl.startsWith("http://") || relativeOrFullUrl.startsWith("https://")) {
      return relativeOrFullUrl;
    }
    const cleanPath = relativeOrFullUrl.startsWith("/") ? relativeOrFullUrl : `/${relativeOrFullUrl}`;
    return `${API_BASE_URL}${cleanPath}`;
  },
};
