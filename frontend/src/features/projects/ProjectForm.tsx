// features/projects/ProjectForm.tsx
import { useState } from "react";
import { useCreateProject } from "./useProjects";

export default function ProjectForm() {
  const [name, setName] = useState("");
  const [desc, setDesc] = useState("");
  const createProject = useCreateProject();

  const onSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (name.trim()) createProject.mutate({ name, description: desc });
  };

  return (
    <form onSubmit={onSubmit} className="mb-6">
      <input
        className="border px-4 py-2 mr-2 rounded w-1/3"
        placeholder="프로젝트 이름"
        value={name}
        onChange={(e) => setName(e.target.value)}
        required
      />
      <input
        className="border px-4 py-2 mr-2 rounded w-1/3"
        placeholder="설명 (선택)"
        value={desc}
        onChange={(e) => setDesc(e.target.value)}
      />
      <button className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700">
        생성
      </button>
    </form>
  );
}
