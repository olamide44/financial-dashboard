import { useMutation } from "@tanstack/react-query";
import { api } from "../lib/api";
import { queryClient } from "../lib/queryClient";

export function useBulkUpsertHoldings(portfolioId: string | number) {
  return useMutation({
    mutationFn: async (rows: Array<{ symbol: string; qty: number; cost_basis?: number }>) => {
      const { data } = await api.post(`/portfolios/${portfolioId}/holdings:bulk_upsert`, rows);
      return data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["holdings", portfolioId] });
      queryClient.invalidateQueries({ queryKey: ["portfolioPerf", portfolioId] });
    },
  });
}
