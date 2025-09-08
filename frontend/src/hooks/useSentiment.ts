import { useQuery } from "@tanstack/react-query";
import { api } from "../lib/api";

export function useSentiment(instrumentId: number, windowDays = 7) {
  return useQuery({
    queryKey: ["sentiment", instrumentId, windowDays],
    queryFn: async () => (await api.get(`/sentiment/${instrumentId}?window_days=${windowDays}`)).data,
    enabled: !!instrumentId,
  });
}
