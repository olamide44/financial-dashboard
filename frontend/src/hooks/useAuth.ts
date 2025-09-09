import { useMutation } from "@tanstack/react-query";
import { api } from "../lib/api";
import { setAccessToken } from "../lib/auth";

export function useLogin() {
  return useMutation({
    mutationFn: async (payload: { username: string; password: string }) => {
      const params = new URLSearchParams();
      params.append("username", payload.username);
      params.append("password", payload.password);
      const res = await api.post("/auth/login", params, {
        headers: { "Content-Type": "application/x-www-form-urlencoded" },
      });
      return res.data;
    },
    onSuccess: (data) => {
      if (data?.access_token) setAccessToken(data.access_token);
    },
  });
}

export async function getMe() {
  const { data } = await api.get("/auth/me");
  return data;
}
