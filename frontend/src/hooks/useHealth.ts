import { useQuery } from "@tanstack/react-query";
import { healthApi } from "@/api/health";

export const HEALTH_QUERY_KEY = ["system", "health"];

export function useSystemHealth() {
  return useQuery({
    queryKey: HEALTH_QUERY_KEY,
    queryFn: () => healthApi.checkHealth(),
    refetchInterval: 30000,
    retry: 1,
  });
}
