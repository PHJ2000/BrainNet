// features/projects/tagApi.ts
import { apiClient } from "@/lib/apiClient";
export const listTags   = (pid: string | number) => apiClient.get(`/projects/${pid}/tags`).then(r=>r.data);
export const createTag  = (pid: string | number, body: any) => apiClient.post(`/projects/${pid}/tags`, body).then(r=>r.data);
export const updateTag  = (pid: string | number, tid: string | number, body: any) => apiClient.patch(`/projects/${pid}/tags/${tid}`, body).then(r=>r.data);
export const deleteTag  = (pid: string | number, tid: string | number) => apiClient.delete(`/projects/${pid}/tags/${tid}`);
export const attachTag  = (pid: string | number, tid: string | number, nid: string | number) => apiClient.post(`/projects/${pid}/tags/${tid}/nodes/${nid}`).then(r=>r.data);
export const detachTag  = (pid: string | number, tid: string | number, nid: string | number) => apiClient.delete(`/projects/${pid}/tags/${tid}/nodes/${nid}`).then(r=>r.data);