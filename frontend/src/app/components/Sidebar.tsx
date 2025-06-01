// app/components/Sidebar.tsx
"use client";

import { useProjects } from "@/features/projects/useProjects";
import Link from "next/link";
import { Plus } from "lucide-react";
import { JSXElementConstructor, Key, ReactElement, ReactNode, ReactPortal, useState } from "react";
import ProjectFormModal from "./ProjectFormModal";

export default function Sidebar() {
  const { data: projects = [], isLoading } = useProjects();
  const [modalOpen, setModalOpen] = useState(false);

  return (
    <div className="flex flex-col h-full p-4">
      <h2 className="text-lg font-bold mb-4">내 프로젝트</h2>

      <div className="flex-1 space-y-2 overflow-y-auto">
        {/* 프로젝트 목록 */}
        {isLoading ? (
          <div className="text-sm text-gray-400">불러오는 중...</div>
        ) : (
          projects.map((p: { id: Key | null | undefined; name: string | number | bigint | boolean | ReactElement<unknown, string | JSXElementConstructor<any>> | Iterable<ReactNode> | ReactPortal | Promise<string | number | bigint | boolean | ReactPortal | ReactElement<unknown, string | JSXElementConstructor<any>> | Iterable<ReactNode> | null | undefined> | null | undefined; }) => (
            <Link
              key={p.id}
              href={`/dashboard/projects/${p.id}`}
              className="block text-sm text-gray-700 hover:text-black px-2 py-1 rounded hover:bg-gray-100"
            >
              {p.name}
            </Link>
          ))
        )}

        {/* + 버튼도 같은 목록 안에 배치 */}
        <button
          onClick={() => setModalOpen(true)}
          className="flex items-center text-sm text-gray-500 hover:text-black px-2 py-1 rounded hover:bg-gray-100 border border-dashed border-gray-300 mt-2"
        >
          <Plus size={16} className="mr-1" />
          새 프로젝트
        </button>
      </div>

      {/* 모달 */}
      {modalOpen && <ProjectFormModal onClose={() => setModalOpen(false)} />}
    </div>
  );
}
