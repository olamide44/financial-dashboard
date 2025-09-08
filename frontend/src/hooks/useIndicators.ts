import { useQuery } from "@tanstack/react-query";
import { api } from "../lib/api";

export function useIndicators(instrumentId: number, fromISO?: string) {
  const url = `/analytics/indicators/${instrumentId}?sma=20,50&ema=200&rsi=14${fromISO ? `&from=${encodeURIComponent(fromISO)}` : ""}`;
  return useQuery({
    queryKey: ["indicators", instrumentId, fromISO],
    queryFn: async () => (await api.get(url)).data,
    enabled: !!instrumentId,
  });
}
