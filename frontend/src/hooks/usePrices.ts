import { useQuery } from "@tanstack/react-query";
import { api } from "../lib/api";

export function useCandles(instrumentId: number, fromISO?: string) {
  const url = `/prices/${instrumentId}${fromISO ? `?from=${encodeURIComponent(fromISO)}` : ""}`;
  return useQuery({
    queryKey: ["candles", instrumentId, fromISO],
    queryFn: async () => (await api.get(url)).data,
    enabled: !!instrumentId,
  });
}
