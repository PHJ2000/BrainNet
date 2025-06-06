// app/(main)/dashboard/projects/[projectId]/page.tsx
"use client";

import { useParams } from "next/navigation";
import { useEffect, useState } from "react";
import { apiClient } from "@/lib/apiClient";
import Graph from "@/features/nodes/Graph";

export default function ProjectDetailPage() {
  // 👉 useParams() 값은 항상 **문자열**
  const { projectId } = useParams<{ projectId: string }>();
  const pid = Number(projectId);        // ← 숫자로 변환
  const [project, setProject] = useState<any>(null);

  useEffect(() => {
    const fetch = async () => {
      const { data } = await apiClient.get(`/projects/${pid}`);
      setProject(data);
    };
    fetch();
  }, [pid]);

  if (!project) return <div>로딩 중...</div>;

  return (
    <div className="h-full w-full flex flex-col">
      <h1 className="text-2xl font-bold mb-2">{project.name}</h1>
      <p className="text-gray-500 mb-4">{project.description}</p>
      <div className="flex-1 min-h-0">  {/* ⬅️ 여기서 그래프가 flex-1로 꽉 차도록! */}
        <Graph projectId={project.id} />
      </div>
    </div>
  );
}