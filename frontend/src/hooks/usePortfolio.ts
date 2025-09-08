import { useQuery } from "@tanstack/react-query";
import { api } from "../lib/api";

export function usePortfolioPerformance(id: string, fromISO?: string, benchmark?: string) {
  const params = new URLSearchParams();
  if (fromISO) params.set("from", fromISO);
  if (benchmark) params.set("benchmark", benchmark);
  const url = `/analytics/portfolios/${id}/performance?${params.toString()}`;
  return useQuery({
    queryKey: ["portfolioPerf", id, fromISO, benchmark],
    queryFn: async () => (await api.get(url)).data,
    enabled: !!id,
  });
}