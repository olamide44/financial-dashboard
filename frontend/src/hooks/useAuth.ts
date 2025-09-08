import { useMutation } from "@tanstack/react-query";
import { api } from "../lib/api";
import { setAccessToken } from "../lib/auth";

export function useLogin() {
  return useMutation({
    mutationFn: async (payload: { email: string; password: string }) => {
      const res = await api.post("/auth/login", payload);
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
