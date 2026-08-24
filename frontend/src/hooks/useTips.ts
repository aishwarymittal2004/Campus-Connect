import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { tipsApi } from "@/lib/api/tips";

export function useStudentTips(collegeId: string | undefined) {
  return useQuery({
    queryKey: ["tips", collegeId],
    queryFn: () => tipsApi.listForCollege(collegeId as string),
    enabled: Boolean(collegeId),
  });
}

export function useCreateTip() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: tipsApi.create,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["tips"] }),
  });
}

export function useUpvoteTip() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => tipsApi.upvote(id),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["tips"] }),
  });
}
