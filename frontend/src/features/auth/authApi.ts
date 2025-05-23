// features/auth/authApi.ts
import { apiClient } from "@/lib/apiClient";

export const login = async (email: string, password: string) => {
  const res = await apiClient.post("/auth/login", { email, password });
  return res.data as { access_token: string; token_type: string };
};

export const register = async (email: string, password: string, name?: string) => {
  const res = await apiClient.post("/auth/register", { email, password, name });
  return res.data as { id: string; email: string; name?: string };
};
