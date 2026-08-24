import { apiClient } from "@/lib/api-client";
import type { RouteSearchResponse, SavedRoute, SourceType } from "@/types";

export interface RouteSearchPayload {
  source_location: string;
  source_type: SourceType;
  college_id: string;
  source_latitude?: number;
  source_longitude?: number;
}

export const routesApi = {
  search: (payload: RouteSearchPayload) =>
    apiClient.post<RouteSearchResponse>("/routes/search", payload).then((r) => r.data),
  history: (bookmarkedOnly = false) =>
    apiClient
      .get<SavedRoute[]>("/routes/history", { params: { bookmarked_only: bookmarkedOnly } })
      .then((r) => r.data),
  toggleBookmark: (routeId: string, isBookmarked: boolean) =>
    apiClient.patch<SavedRoute>(`/routes/${routeId}/bookmark`, { is_bookmarked: isBookmarked }).then((r) => r.data),
  remove: (routeId: string) => apiClient.delete(`/routes/${routeId}`),
};
