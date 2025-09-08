import { getJSON, setJSON } from "./storage";

const KEY = "recent_instruments"; // array of { id, symbol, name? }

export type RecentItem = { id: number; symbol: string; name?: string };

export function pushRecentInstrument(item: RecentItem, limit = 8) {
  const cur = (getJSON<RecentItem[]>(KEY) || []).filter((x) => x.id !== item.id);
  const next = [item, ...cur].slice(0, limit);
  setJSON(KEY, next);
}

export function getRecentInstruments(): RecentItem[] {
  return getJSON<RecentItem[]>(KEY) || [];
}
