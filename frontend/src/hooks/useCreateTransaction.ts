import { useMutation } from "@tanstack/react-query";
import { api } from "../lib/api";
import { queryClient } from "../lib/queryClient";

export function useCreateTransaction(portfolioId: string | number) {
  return useMutation({
    mutationFn: async (payload: { symbol: string; side: "buy"|"sell"; qty: number; price: number; ts?: string }) => {
      const { data } = await api.post(`/portfolios/${portfolioId}/transactions`, payload);
      return data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["holdings", portfolioId] });
      queryClient.invalidateQueries({ queryKey: ["portfolioPerf", portfolioId] });
    },
  });
}
