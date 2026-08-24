import { apiClient } from "@/lib/api-client";
import type { College } from "@/types";

export interface CollegeCreatePayload {
  name: string;
  city: string;
  state?: string;
  address?: string;
  latitude: number;
  longitude: number;
  nearby_landmarks?: { name: string; type: string; distance_km?: number }[];
  emergency_contacts?: { label: string; phone: string }[];
  website?: string;
  tags?: string[];
}

export const collegesApi = {
  list: (q?: string) => apiClient.get<College[]>("/colleges", { params: q ? { q } : {} }).then((r) => r.data),
  get: (id: string) => apiClient.get<College>(`/colleges/${id}`).then((r) => r.data),
  create: (payload: CollegeCreatePayload) => apiClient.post<College>("/colleges", payload).then((r) => r.data),
  update: (id: string, payload: Partial<CollegeCreatePayload>) =>
    apiClient.patch<College>(`/colleges/${id}`, payload).then((r) => r.data),
  remove: (id: string) => apiClient.delete(`/colleges/${id}`),
};
