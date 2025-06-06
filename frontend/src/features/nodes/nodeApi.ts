// features/projects/nodeApi.ts
import { apiClient } from "@/lib/apiClient";

/* ─────────────────────────────
   공통 타입
   ────────────────────────────*/
export interface NodeOut {
  id: number;
  project_id: number;
  author_id: number;
  content: string;
  state: "ACTIVE" | "GHOST";
  pos_x: number;
  pos_y: number;
  depth: number;
  order_index: number;
  parent_id?: number | null;
  created_at: string;
  updated_at: string;
}

export interface NodePayload {
  content?: string;
  pos_x?: number;
  pos_y?: number;
  depth?: number;
  order?: number;
  parent_id?: number | null;
}

type NodeUpdatePayload = Partial<NodePayload>;

/* ────────── GET: 노드 목록 ──────────*/
export async function fetchNodes(
  projectId: number | string,
  tagIds?: (number | string)[]
): Promise<NodeOut[]> {
  const query =
    tagIds && tagIds.length ? `?tag_ids=${tagIds.join(",")}` : "";
  const { data } = await apiClient.get(
    `/projects/${projectId}/nodes${query}`
  );
  return data;
}

/* ────────── POST: 일반 노드 생성 ──────────*/
export async function createNode(
  projectId: number | string,
  payload: NodePayload
): Promise<NodeOut> {
  const { data } = await apiClient.post(
    `/projects/${projectId}/nodes`,
    payload
  );
  // 백엔드가 [NodeOut] 배열을 돌려주므로 첫 원소만 반환
  return Array.isArray(data) ? data[0] : data;
}

/* ────────── POST: AI 제안(GHOST) 노드 ──────────*/
export async function createAINodes(
  projectId: number | string,
  aiPrompt: string,
  opts: {
    pos_x?: number;
    pos_y?: number;
    depth?: number;
    order?: number;
    parent_id?: number | string | null;
  } = {}
): Promise<NodeOut[]> {
  const payload = { ai_prompt: aiPrompt, ...opts };
  const { data } = await apiClient.post(
    `/projects/${projectId}/nodes`,
    payload
  );
  return data;
}

/* ────────── PATCH: 노드 수정 ──────────*/
export async function updateNode(
  projectId: number | string,
  nodeId: number | string,
  payload: NodeUpdatePayload
): Promise<NodeOut> {
  const { data } = await apiClient.patch(
    `/projects/${projectId}/nodes/${nodeId}`,
    payload
  );
  return data;
}

/* ────────── DELETE: 노드 삭제 ──────────*/
export async function deleteNode(
  projectId: number | string,
  nodeId: number | string
) {
  await apiClient.delete(`/projects/${projectId}/nodes/${nodeId}`);
}

/* ────────── POST: GHOST → ACTIVE ──────────*/
export async function activateNode(
  projectId: number | string,
  nodeId: number | string
): Promise<NodeOut> {
  const { data } = await apiClient.post(
    `/projects/${projectId}/nodes/${nodeId}/activate`
  );
  return data;
}

/* ────────── POST: ACTIVE → GHOST ──────────*/
export async function deactivateNode(
  projectId: number | string,
  nodeId: number | string
): Promise<NodeOut> {
  const { data } = await apiClient.post(
    `/projects/${projectId}/nodes/${nodeId}/deactivate`
  );
  return data;
}
