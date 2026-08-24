import { apiClient } from "@/lib/api-client";
import type { Review, ReviewType } from "@/types";

export interface ReviewCreatePayload {
  review_type: ReviewType;
  rating: number;
  comment: string;
  college_id?: string;
  pg_listing_id?: string;
  route_id?: string;
}

export const reviewsApi = {
  listForTarget: (reviewType: ReviewType, targetId: string) =>
    apiClient
      .get<Review[]>("/reviews", { params: { review_type: reviewType, target_id: targetId } })
      .then((r) => r.data),
  create: (payload: ReviewCreatePayload) => apiClient.post<Review>("/reviews", payload).then((r) => r.data),
  update: (id: string, payload: { rating?: number; comment?: string }) =>
    apiClient.patch<Review>(`/reviews/${id}`, payload).then((r) => r.data),
  remove: (id: string) => apiClient.delete(`/reviews/${id}`),
};
