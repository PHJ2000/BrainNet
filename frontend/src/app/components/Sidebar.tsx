"use client";

import { useProjects } from "@/features/projects/useProjects";
import Link from "next/link";
import { Plus } from "lucide-react";
import { useState } from "react";
import ProjectFormModal from "./ProjectFormModal";

export default function Sidebar() {
  const { data: projects = [], isLoading } = useProjects();
  const [modalOpen, setModalOpen] = useState(false);

  return (
    <div className="flex flex-col h-full px-4 py-6">
      {/* 타이틀 */}
      <div className="mb-7 flex items-center justify-between">
        <h2 className="text-lg font-extrabold tracking-tight text-gray-700">
          내 프로젝트
        </h2>
        {/* + 버튼 (작은 원 버튼 스타일) */}
        <button
          onClick={() => setModalOpen(true)}
          className="ml-2 flex items-center justify-center bg-blue-50 text-blue-700 hover:bg-blue-100 rounded-full p-2 shadow-sm transition-all"
          aria-label="새 프로젝트"
        >
          <Plus size={20} />
        </button>
      </div>

      {/* 목록 */}
      <div className="flex-1 space-y-2 overflow-y-auto">
        {isLoading ? (
          <div className="text-sm text-gray-400 py-2">불러오는 중...</div>
        ) : projects.length === 0 ? (
          <div className="text-sm text-gray-400 py-2">아직 프로젝트가 없습니다.</div>
        ) : (
          projects.map((p: { id: number; name: string }) => (
            <Link
              key={p.id}
              href={`/dashboard/projects/${p.id}`}
              className="block font-medium text-gray-700/90 hover:text-blue-700 px-3 py-2 rounded-lg hover:bg-blue-50 transition-all group"
            >
              <span className="group-hover:font-bold">{p.name}</span>
            </Link>
          ))
        )}
      </div>

      {/* 하단: 팁/브랜드/서브 정보 */}
      <div className="pt-8 pb-3 text-xs text-center text-gray-300 select-none">
        <span className="text-[15px] font-bold text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-purple-400">
          BrainNet
        </span>
        <br />
        <span className="text-[11px]">for creative notes</span>
      </div>

      {/* 프로젝트 추가 모달 */}
      {modalOpen && <ProjectFormModal onClose={() => setModalOpen(false)} />}
    </div>
  );
}