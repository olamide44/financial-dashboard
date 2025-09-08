import { useQuery } from "@tanstack/react-query";
import { api } from "../lib/api";

export type Holding = {
  id: number;
  instrument_id: number;
  symbol: string;
  qty: number;
  cost_basis?: number;
  market_value?: number;
  weight?: number;
};

export function usePortfolioHoldings(portfolioId: string | number) {
  return useQuery<Holding[]>({
    queryKey: ["holdings", portfolioId],
    queryFn: async () => {
      // adjust if your API wraps response
      const { data } = await api.get(`/portfolios/${portfolioId}/holdings`);
      return data;
    },
    enabled: !!portfolioId,
    staleTime: 30_000,
  });
}
