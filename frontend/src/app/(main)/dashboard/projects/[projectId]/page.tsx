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
    <div className="space-y-4">
      <h1 className="text-2xl font-bold">{project.name}</h1>
      <p className="text-gray-600">{project.description}</p>

      {/* key 속성을 줘서 프로젝트가 바뀔 때 Graph를 완전히 새로 마운트 */}
      <Graph key={pid} projectId={pid} />
    </div>
  );
}
