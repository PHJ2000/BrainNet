// features/projects/ProjectList.tsx
import Link from "next/link";
import { useProjects } from "./useProjects";

export default function ProjectList() {
  const { data: projects, isLoading } = useProjects();

  if (isLoading) return <p>로딩 중...</p>;

  return (
    <div className="grid gap-4">
      {projects?.map((p) => (
        <Link
          key={p.id}
          href={`/project/${p.id}`}
          className="border p-4 rounded hover:bg-gray-50"
        >
          <h3 className="text-lg font-semibold">{p.name}</h3>
          <p className="text-sm text-gray-500">{p.description}</p>
        </Link>
      ))}
    </div>
  );
}
