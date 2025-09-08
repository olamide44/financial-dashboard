import { useMutation, useQuery } from "@tanstack/react-query";
import { api } from "../lib/api";

export function useStartForecast() {
  return useMutation({
    mutationFn: async (vars: { instrumentId: number; horizon?: number; lookback?: number; model?: "ridge" | "lasso" }) => {
      const { instrumentId, horizon, lookback, model } = vars;
      const params = new URLSearchParams();
      if (horizon) params.set("horizon_days", String(horizon));
      if (lookback) params.set("lookback_days", String(lookback));
      if (model) params.set("model", model);
      const { data } = await api.post(`/ml/forecast/instrument/${instrumentId}?${params.toString()}`);
      return data as { run_id: number; instrument_id: number };
    },
  });
}

export function useForecast(runId?: number) {
  return useQuery({
    queryKey: ["forecast", runId],
    queryFn: async () => (await api.get(`/ml/forecast/results/${runId}`)).data,
    enabled: !!runId,
  });
}
