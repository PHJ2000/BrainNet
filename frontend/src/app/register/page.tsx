// app/register/page.tsx
"use client";

import { useState } from "react";
import { useAuth } from "@/features/auth/useAuth";

export default function RegisterPage() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [name, setName] = useState("");
  const { handleRegister, error } = useAuth();

  const onSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    handleRegister(email, password, name);
  };

  return (
    <main className="min-h-screen flex items-center justify-center bg-gray-50">
      <form
        onSubmit={onSubmit}
        className="bg-white p-8 rounded shadow-md w-full max-w-md"
      >
        <h1 className="text-2xl font-semibold mb-6 text-center">회원가입</h1>

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

        <label className="block mb-6">
          <span className="text-gray-700">이름 (선택)</span>
          <input
            type="text"
            className="mt-1 block w-full border px-4 py-2 rounded"
            value={name}
            onChange={(e) => setName(e.target.value)}
          />
        </label>

        {error && <p className="text-red-500 text-sm mb-4">{error}</p>}

        <button
          type="submit"
          className="w-full bg-green-600 text-white py-2 rounded hover:bg-green-700"
        >
          회원가입
        </button>
      </form>
    </main>
  );
}
