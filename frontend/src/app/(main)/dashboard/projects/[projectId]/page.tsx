// app/(main)/dashboard/projects/[projectId]/page.tsx
"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import {apiClient} from "@/lib/apiClient";

export default function ProjectDetailPage() {
  const { projectId } = useParams();
  const [project, setProject] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchProject = async () => {
      try {
        const res = await apiClient.get(`/projects/${projectId}`);
        setProject(res.data);
      } catch (err) {
        console.error("프로젝트 로딩 실패", err);
      } finally {
        setLoading(false);
      }
    };

    fetchProject();
  }, [projectId]);

  if (loading) return <div>Loading...</div>;
  if (!project) return <div>프로젝트를 찾을 수 없습니다.</div>;

  return (
    <div className="space-y-4">
      <h1 className="text-2xl font-bold">{project.name}</h1>
      <p>{project.description}</p>
      <p className="text-sm text-gray-500">생성일: {new Date(project.created_at).toLocaleString()}</p>
    </div>
  );
}