import { useMutation } from "@tanstack/react-query";
import { api } from "../lib/api";
import { setAccessToken } from "../lib/auth";

// Backend often expects form-encoded for signup. We'll send URLSearchParams.
export function useSignup() {
  return useMutation({
    mutationFn: async (payload: { email: string; password: string }) => {
      const body = new URLSearchParams({ email: payload.email, password: payload.password });
      const { data } = await api.post("/auth/signup", body, {
        headers: { "Content-Type": "application/x-www-form-urlencoded" },
      });
      return data as { access_token?: string };
    },
    onSuccess: (data) => {
      if (data?.access_token) setAccessToken(data.access_token);
    },
  });
}
