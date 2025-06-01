// app/dashboard/page.tsx
"use client";

import ProjectForm from "@/features/projects/ProjectForm";
import ProjectList from "@/features/projects/ProjectList";

export default function DashboardPage() {
  return (
    <main className="max-w-3xl mx-auto p-8">
      <h1 className="text-2xl font-bold mb-6">내 프로젝트</h1>
      <ProjectForm />
      <ProjectList />
    </main>
  );
}
