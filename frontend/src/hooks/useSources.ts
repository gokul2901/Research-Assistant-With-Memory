import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { sourcesApi } from "@/api/sources";
import { ingestApi } from "@/api/ingest";
import { toast } from "sonner";

export const SOURCES_QUERY_KEY = ["sources"];
export const STATS_QUERY_KEY = ["sources", "statistics"];

export function useSourceStatistics() {
  return useQuery({
    queryKey: STATS_QUERY_KEY,
    queryFn: () => sourcesApi.getStatistics(),
    refetchInterval: 15000, // keep stats fresh
  });
}

export function useSourcesList(limit = 100, offset = 0) {
  return useQuery({
    queryKey: [...SOURCES_QUERY_KEY, { limit, offset }],
    queryFn: () => sourcesApi.listSources(limit, offset),
  });
}

export function useSource(sourceId: string | null) {
  return useQuery({
    queryKey: ["sources", sourceId],
    queryFn: () => (sourceId ? sourcesApi.getSource(sourceId) : null),
    enabled: !!sourceId,
  });
}

export function useIngestUrls() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({
      urls,
      forceRefresh = false,
    }: {
      urls: string[];
      forceRefresh?: boolean;
    }) => ingestApi.ingestUrls(urls, forceRefresh),
    onSuccess: (summary) => {
      queryClient.invalidateQueries({ queryKey: SOURCES_QUERY_KEY });
      queryClient.invalidateQueries({ queryKey: STATS_QUERY_KEY });

      if (summary.successful_count > 0) {
        toast.success(`Successfully indexed ${summary.successful_count} source(s) into research memory.`);
      }
      if (summary.duplicate_count > 0) {
        toast.info(`${summary.duplicate_count} URL(s) were already up to date in the knowledge base.`);
      }
      if (summary.failed_count > 0) {
        toast.error(`Failed to ingest ${summary.failed_count} URL(s). Check logs or try again.`);
      }
    },
    onError: (error: Error) => {
      toast.error(error.message || "Failed to ingest URLs into knowledge base.");
    },
  });
}

export function useRefreshSource() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (sourceId: string) => sourcesApi.refreshSource(sourceId),
    onSuccess: (res) => {
      queryClient.invalidateQueries({ queryKey: SOURCES_QUERY_KEY });
      queryClient.invalidateQueries({ queryKey: STATS_QUERY_KEY });
      toast.success(res.message || "Source refreshed successfully.");
    },
    onError: (error: Error) => {
      toast.error(error.message || "Failed to refresh source.");
    },
  });
}

export function useDeleteSource() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (sourceId: string) => sourcesApi.deleteSource(sourceId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: SOURCES_QUERY_KEY });
      queryClient.invalidateQueries({ queryKey: STATS_QUERY_KEY });
      toast.success("Source permanently removed from knowledge base and vector store.");
    },
    onError: (error: Error) => {
      toast.error(error.message || "Failed to delete source.");
    },
  });
}
