import { useQuery } from "@tanstack/react-query";
import { api } from "../lib/api";

export type Portfolio = { id: string | number; name?: string; base_currency?: string };

export function usePortfolios() {
  return useQuery<Portfolio[]>({
    queryKey: ["portfolios"],
    queryFn: async () => {
      const { data } = await api.get("/portfolios"); // expects an array
      return data;
    },
    staleTime: 60_000,
  });
}
