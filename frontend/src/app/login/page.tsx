// app/login/page.tsx
"use client";

import { useState } from "react";
import { useAuth } from "@/features/auth/useAuth";

export default function LoginPage() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const { handleLogin, error } = useAuth();

  const onSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    handleLogin(email, password);
  };

  return (
    <main className="min-h-screen flex items-center justify-center bg-gray-50">
      <form
        onSubmit={onSubmit}
        className="bg-white p-8 rounded shadow-md w-full max-w-md"
      >
        <h1 className="text-2xl font-semibold mb-6 text-center">로그인</h1>

        <label className="block mb-4">
          <span className="text-gray-700">이메일</span>
          <input
            type="email"
            className="mt-1 block w-full border px-4 py-2 rounded"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
          />
        </label>

        <label className="block mb-4">
          <span className="text-gray-700">비밀번호</span>
          <input
            type="password"
            className="mt-1 block w-full border px-4 py-2 rounded"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
          />
        </label>

        {error && <p className="text-red-500 text-sm mb-4">{error}</p>}

        <button
          type="submit"
          className="w-full bg-blue-600 text-white py-2 rounded hover:bg-blue-700"
        >
          로그인
        </button>
      </form>
    </main>
  );
}
