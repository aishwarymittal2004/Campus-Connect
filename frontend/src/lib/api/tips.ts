import { apiClient } from "@/lib/api-client";
import type { StudentTip } from "@/types";

export const tipsApi = {
  listForCollege: (collegeId: string) =>
    apiClient.get<StudentTip[]>("/tips", { params: { college_id: collegeId } }).then((r) => r.data),
  create: (payload: { title: string; content: string; college_id?: string }) =>
    apiClient.post<StudentTip>("/tips", payload).then((r) => r.data),
  upvote: (id: string) => apiClient.post<StudentTip>(`/tips/${id}/upvote`).then((r) => r.data),
  remove: (id: string) => apiClient.delete(`/tips/${id}`),
};
