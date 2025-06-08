"use client";

import { useCreateProject } from "@/features/projects/useProjects";
import { useState } from "react";

export default function ProjectFormModal({ onClose }: { onClose: () => void }) {
  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const createProject = useCreateProject();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!name.trim()) return;
    await createProject.mutateAsync({ name, description });
    onClose();
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/30">
      <div className="relative w-full max-w-md bg-white/90 backdrop-blur-xl shadow-2xl rounded-2xl px-8 py-8">
        {/* 닫기 버튼 */}
        <button
          onClick={onClose}
          className="absolute top-4 right-4 text-gray-400 hover:text-gray-600 rounded-full p-1 transition"
          aria-label="닫기"
        >
          <span className="text-xl font-bold">✕</span>
        </button>

        <h2 className="text-2xl font-bold text-gray-800 mb-2">새 프로젝트 만들기</h2>
        <p className="text-sm text-gray-400 mb-6">프로젝트 이름과 간단한 설명을 입력하세요.</p>
        <form onSubmit={handleSubmit} className="space-y-5">
          <div>
            <label className="block text-gray-700 mb-1.5">프로젝트 이름</label>
            <input
              type="text"
              autoFocus
              maxLength={40}
              placeholder="예: AI 메모, 창작노트 등"
              value={name}
              onChange={(e) => setName(e.target.value)}
              className="w-full border border-gray-200 rounded-lg px-4 py-2 bg-gray-50 focus:outline-none focus:ring-2 focus:ring-blue-400 focus:border-blue-400 transition"
              required
            />
          </div>
          <div>
            <label className="block text-gray-700 mb-1.5">설명 (선택)</label>
            <textarea
              maxLength={200}
              placeholder="이 프로젝트의 목적이나 참고 메모를 작성하세요."
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              className="w-full border border-gray-200 rounded-lg px-4 py-2 bg-gray-50 focus:outline-none focus:ring-2 focus:ring-blue-400 focus:border-blue-400 transition resize-none min-h-[70px]"
            />
          </div>
          <div className="flex justify-end space-x-2 pt-2">
            <button
              type="button"
              onClick={onClose}
              className="px-5 py-2 rounded-lg font-medium bg-gray-100 hover:bg-gray-200 text-gray-500 transition"
            >
              취소
            </button>
            <button
              type="submit"
              disabled={!name.trim()}
              className="px-5 py-2 rounded-lg font-semibold bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white shadow-md transition disabled:opacity-50 disabled:cursor-not-allowed"
            >
              생성
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}