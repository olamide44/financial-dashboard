const ACCESS_KEY = "fd_access_token";

export function setAccessToken(tok: string) {
  localStorage.setItem(ACCESS_KEY, tok);
}
export function getAccessToken(): string | null {
  return localStorage.getItem(ACCESS_KEY);
}
export function logout() {
  localStorage.removeItem(ACCESS_KEY);
}
