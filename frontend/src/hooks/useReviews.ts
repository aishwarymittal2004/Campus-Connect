import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { reviewsApi, type ReviewCreatePayload } from "@/lib/api/reviews";
import type { ReviewType } from "@/types";

export function useReviews(reviewType: ReviewType, targetId: string | undefined) {
  return useQuery({
    queryKey: ["reviews", reviewType, targetId],
    queryFn: () => reviewsApi.listForTarget(reviewType, targetId as string),
    enabled: Boolean(targetId),
  });
}

export function useCreateReview() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (payload: ReviewCreatePayload) => reviewsApi.create(payload),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["reviews"] }),
  });
}

export function useDeleteReview() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => reviewsApi.remove(id),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["reviews"] }),
  });
}
