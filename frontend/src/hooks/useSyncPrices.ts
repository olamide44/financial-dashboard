import { useMutation } from "@tanstack/react-query";
import { api } from "../lib/api";
import { queryClient } from "../lib/queryClient";

export function useSyncPrices(instrumentId: number) {
  return useMutation({
    mutationFn: async (vars: { symbol: string; backfill_days?: number }) => {
      const { symbol, backfill_days = 365 } = vars;
      const { data } = await api.post("/prices/sync", { symbols: [symbol], backfill_days });
      return data as { inserted: number; errors?: any[] };
    },
    onSuccess: (_data) => {
      queryClient.invalidateQueries({ queryKey: ["candles", instrumentId] });
      queryClient.invalidateQueries({ queryKey: ["indicators", instrumentId] });
    },
  });
}
