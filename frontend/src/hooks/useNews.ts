import { useQuery } from "@tanstack/react-query";
import { api } from "../lib/api";

export function useNews(instrumentId: number, windowDays = 7) {
  return useQuery({
    queryKey: ["news", instrumentId, windowDays],
    queryFn: async () => (await api.get(`/news/${instrumentId}?window_days=${windowDays}`)).data,
    enabled: !!instrumentId,
  });
}
