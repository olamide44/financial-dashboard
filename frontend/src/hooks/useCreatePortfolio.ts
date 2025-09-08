import { useMutation } from "@tanstack/react-query";
import { api } from "../lib/api";
import { queryClient } from "../lib/queryClient";

export function useCreatePortfolio() {
  return useMutation({
    mutationFn: async (payload: { name: string; base_currency: string }) => {
      const { data } = await api.post("/portfolios/", payload);
      return data as { id: number | string };
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["portfolios"] });
    },
  });
}
