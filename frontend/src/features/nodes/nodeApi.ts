// features/projects/nodeApi.ts
import { apiClient } from "@/lib/apiClient";

/* ───────── 일반 노드 ───────── */
export async function fetchNodes(projectId: string) {
  const res = await apiClient.get(`/projects/${projectId}/nodes`);
  return res.data;
}

export async function createNode(
  projectId: string,
  payload: Record<string, unknown>
) {
  const res = await apiClient.post(`/projects/${projectId}/nodes`, payload);
  return res.data;
}

/* ───────── AI 제안 노드 ───────── */
export async function createAINodes(
  projectId: string,
  aiPrompt: string,
  x: number,
  y: number,
  depth = 0,
  order = 0
) {
  const payload = { ai_prompt: aiPrompt, x, y, depth, order };

  // Axios 인스턴스 재사용 ─ withCredentials 는 apiClient 기본값에 있다면 생략 가능
  const res = await apiClient.post(
    `/projects/${projectId}/nodes`,
    payload,
    { withCredentials: true }  // ← 필요하면 명시
  );

  return res.data;             // GHOST 노드 배열
}
