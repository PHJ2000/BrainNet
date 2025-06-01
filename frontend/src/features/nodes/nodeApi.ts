// features/projects/nodeApi.ts
import {apiClient} from "@/lib/apiClient";

export async function fetchNodes(projectId: string) {
  const res = await apiClient.get(`/projects/${projectId}/nodes`);
  return res.data;
}

export async function createNode(projectId: string, payload: any) {
  const res = await apiClient.post(`/projects/${projectId}/nodes`, payload);
  return res.data;
}
