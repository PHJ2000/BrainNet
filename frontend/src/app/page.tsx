"use client"; // ← 이거 꼭 필요 (React hook 쓰려면)

import { useState } from "react";

export default function Home() {
  const [message, setMessage] = useState("");

  const fetchHello = async () => {
    try {
      const res = await fetch("http://localhost:8000/api/hello");
      const data = await res.json();
      setMessage(data.message);
    } catch {
      setMessage("백엔드 연결 실패 😢");
    }
  };

  return (
    <div className="min-h-screen p-8 flex flex-col items-center justify-center gap-8">
      <h1 className="text-2xl font-bold">프론트엔드 - 백엔드 연동 예제</h1>

      <button
        onClick={fetchHello}
        className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700"
      >
        백엔드에서 메시지 받아오기
      </button>

      {message && (
        <p className="text-lg mt-4 text-center">👉 {message}</p>
      )}
    </div>
  );
}
