import { useMutation } from "@tanstack/react-query";
import { api } from "../lib/api";

export function usePortfolioInsights() {
  return useMutation({
    mutationFn: async (vars: { portfolioId: string; fromISO?: string; benchmark?: string }) => {
      const { portfolioId, fromISO, benchmark } = vars;
      const params = new URLSearchParams();
      if (fromISO) params.set("from", fromISO);
      if (benchmark) params.set("benchmark", benchmark);
      const { data } = await api.post(`/ai/insights/portfolio/${portfolioId}?${params.toString()}`);
      return data as {
        portfolio_id: number;
        snapshot: any;
        insight: string;
        benchmark?: string;
        generated_at: string;
      };
    },
  });
}
