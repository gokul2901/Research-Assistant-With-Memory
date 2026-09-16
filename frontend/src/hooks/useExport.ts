import { useMutation } from "@tanstack/react-query";
import { exportApi } from "@/api/export";
import { ExportPDFRequest, ExportPDFResponse } from "@/types";
import { toast } from "sonner";
import { useState } from "react";

export function usePDFExport() {
  const [isExporting, setIsExporting] = useState<boolean>(false);

  const exportMutation = useMutation({
    mutationFn: async (payload: ExportPDFRequest) => {
      setIsExporting(true);
      return exportApi.generatePDF(payload);
    },
    onSuccess: (data: ExportPDFResponse) => {
      setIsExporting(false);
      toast.success("Intelligence Report PDF generated successfully.");

      // Initiate file download directly in browser
      const downloadUrl = exportApi.getPdfDownloadUrl(data.download_url);
      const link = document.createElement("a");
      link.href = downloadUrl;
      link.download = data.file_name || "research_report.pdf";
      link.target = "_blank";
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    },
    onError: (error: Error) => {
      setIsExporting(false);
      toast.error(error.message || "Failed to generate research report PDF.");
    },
  });

  return {
    exportPDF: exportMutation.mutateAsync,
    isExporting,
    error: exportMutation.error,
  };
}
