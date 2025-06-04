// app/(main)/dashboard/projects/[projectId]/page.tsx
"use client";

import { useParams } from "next/navigation";
import { useEffect, useState } from "react";
import {apiClient} from "@/lib/apiClient";
import Graph from "@/features/nodes/Graph";

export default function ProjectDetailPage() {
  const { projectId } = useParams();
  const [project, setProject] = useState<any>(null);

  useEffect(() => {
    const fetch = async () => {
      const res = await apiClient.get(`/projects/${projectId}`);
      setProject(res.data);
    };
    fetch();
  }, [projectId]);

  if (!project) return <div>로딩 중...</div>;

  return (
    <div className="space-y-4">
      <h1 className="text-2xl font-bold">{project.name}</h1>
      <p className="text-gray-600">{project.description}</p>

      {/* ✅ Cytoscape Graph */}
      <Graph projectId={project.id} />
    </div>
  );
}
