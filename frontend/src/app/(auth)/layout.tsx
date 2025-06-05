"use client";

export default function AuthLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-200 via-white to-purple-200">
      <div className="w-full max-w-md bg-white/80 shadow-2xl rounded-3xl px-8 py-10 flex flex-col items-center border border-gray-100">
        {/* 로고와 슬로건 */}
        <div className="flex flex-col items-center mb-8">
          <span className="text-4xl font-extrabold text-transparent bg-clip-text bg-gradient-to-r from-blue-600 via-indigo-500 to-purple-600 tracking-wider drop-shadow">BrainNet</span>
          <span className="text-gray-400 text-sm mt-2">아이디어를 시각화하는 공간</span>
        </div>
        {/* 실제 페이지 컨텐츠 */}
        <div className="w-full">{children}</div>
      </div>
    </div>
  );
}