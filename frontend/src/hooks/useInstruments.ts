import { useQuery } from "@tanstack/react-query";
import { api } from "../lib/api";

export function useInstrument(id: number) {
  return useQuery({
    queryKey: ["instrument", id],
    queryFn: async () => (await api.get(`/instruments/${id}`)).data,
  });
}

export function useSearchInstruments(q: string) {
  return useQuery({
    queryKey: ["search", q],
    queryFn: async () => (await api.get(`/instruments/search?q=${q}`)).data as { id:number; symbol:string; name?:string }[],
    enabled: q.length >= 2,
  });
}
