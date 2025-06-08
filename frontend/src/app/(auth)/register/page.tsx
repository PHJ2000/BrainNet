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
    <form onSubmit={onSubmit} className="space-y-7">
      <h1 className="text-2xl font-bold text-center text-gray-800 mb-2">
        회원가입
      </h1>

      <div>
        <label className="block text-gray-700 mb-1.5">이메일</label>
        <input
          type="email"
          className="w-full border border-gray-200 rounded-lg px-4 py-2 bg-gray-50 focus:outline-none focus:ring-2 focus:ring-blue-400 focus:border-blue-400 transition"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          placeholder="your@email.com"
          required
        />
      </div>

      <div>
        <label className="block text-gray-700 mb-1.5">비밀번호</label>
        <input
          type="password"
          className="w-full border border-gray-200 rounded-lg px-4 py-2 bg-gray-50 focus:outline-none focus:ring-2 focus:ring-blue-400 focus:border-blue-400 transition"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          placeholder="비밀번호"
          required
        />
      </div>

      <div>
        <label className="block text-gray-700 mb-1.5">이름 (선택)</label>
        <input
          type="text"
          className="w-full border border-gray-200 rounded-lg px-4 py-2 bg-gray-50 focus:outline-none focus:ring-2 focus:ring-blue-400 focus:border-blue-400 transition"
          value={name}
          onChange={(e) => setName(e.target.value)}
          placeholder="이름 (선택)"
        />
      </div>

      {error && (
        <div className="bg-red-50 border border-red-300 text-red-600 text-sm rounded p-2 text-center mb-2">
          {error}
        </div>
      )}

      <button
        type="submit"
        className="w-full bg-gradient-to-r from-green-500 to-blue-500 hover:from-green-600 hover:to-blue-600 text-white font-bold py-2.5 rounded-lg shadow-md transition-all"
      >
        회원가입
      </button>

      <div className="text-center text-sm text-gray-400 mt-2">
        이미 계정이 있으신가요?{" "}
        <a href="/login" className="text-blue-700 font-semibold hover:underline">
          로그인
        </a>
      </div>
    </form>
  );
}