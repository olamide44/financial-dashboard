export function setJSON(key: string, val: unknown) {
  localStorage.setItem(key, JSON.stringify(val));
}
export function getJSON<T = any>(key: string): T | null {
  try {
    const s = localStorage.getItem(key);
    return s ? (JSON.parse(s) as T) : null;
  } catch {
    return null;
  }
}
