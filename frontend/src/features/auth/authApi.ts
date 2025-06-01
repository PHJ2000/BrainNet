import { apiClient } from "@/lib/apiClient";

export const login = async (email: string, password: string) => {
  const form = new URLSearchParams();
  form.append("username", email); // FastAPI는 "username" key 사용함
  form.append("password", password);

  const res = await apiClient.post("/auth/login", form, {
    headers: {
      "Content-Type": "application/x-www-form-urlencoded",
    },
  });

  return res.data as { access_token: string; token_type: string };
};

export const register = async (email: string, password: string, name?: string) => {
  const res = await apiClient.post("/auth/register", { email, password, name });
  return res.data as { id: string; email: string; name?: string };
};
