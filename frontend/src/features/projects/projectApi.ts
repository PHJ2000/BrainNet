// features/projects/projectApi.ts
import { apiClient } from "@/lib/apiClient";
import { Project } from "@/types/api";

export const fetchProjects = async (): Promise<Project[]> => {
  const res = await apiClient.get("/projects");
  return res.data;
};

export const createProject = async ({
  name,
  description,
}: {
  name: string;
  description?: string;
}): Promise<Project> => {
  const res = await apiClient.post("/projects", { name, description });
  return res.data;
};
