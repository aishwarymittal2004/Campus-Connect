import { apiClient } from "@/lib/api-client";
import type { PlatformAnalytics, User, UserRole } from "@/types";

export const adminApi = {
  listUsers: (role?: UserRole) => apiClient.get<User[]>("/admin/users", { params: { role } }).then((r) => r.data),
  updateUser: (id: string, payload: { role?: UserRole; is_active?: boolean }) =>
    apiClient.patch<User>(`/admin/users/${id}`, payload).then((r) => r.data),
  removeUser: (id: string) => apiClient.delete(`/admin/users/${id}`),
  analytics: () => apiClient.get<PlatformAnalytics>("/admin/analytics").then((r) => r.data),
};
