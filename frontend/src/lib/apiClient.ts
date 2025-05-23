// lib/apiClient.ts
import axios from "axios";

export const apiClient = axios.create({
  baseURL: "http://localhost:8000", // 환경변수 처리 가능
  headers: {
    "Content-Type": "application/json",
  },
});

// 요청 시 JWT 자동 첨부
apiClient.interceptors.request.use((config) => {
  const token = typeof window !== "undefined" ? localStorage.getItem("token") : null;
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});
