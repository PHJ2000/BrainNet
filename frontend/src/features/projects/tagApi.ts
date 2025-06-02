// features/projects/tagApi.ts
import { apiClient } from "@/lib/apiClient";
export const listTags   = (pid: string) => apiClient.get(`/projects/${pid}/tags`).then(r=>r.data);
export const createTag  = (pid: string, body: any) => apiClient.post(`/projects/${pid}/tags`, body).then(r=>r.data);
export const updateTag  = (pid: string, tid: string, body: any) => apiClient.patch(`/projects/${pid}/tags/${tid}`, body).then(r=>r.data);
export const deleteTag  = (pid: string, tid: string) => apiClient.delete(`/projects/${pid}/tags/${tid}`);
export const attachTag  = (pid: string, tid: string, nid: string) => apiClient.post(`/projects/${pid}/tags/${tid}/nodes/${nid}`).then(r=>r.data);
export const detachTag  = (pid: string, tid: string, nid: string) => apiClient.delete(`/projects/${pid}/tags/${tid}/nodes/${nid}`).then(r=>r.data);