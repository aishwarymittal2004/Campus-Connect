import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { collegesApi, type CollegeCreatePayload } from "@/lib/api/colleges";

export function useColleges(search?: string) {
  return useQuery({
    queryKey: ["colleges", search ?? ""],
    queryFn: () => collegesApi.list(search),
  });
}

export function useCollege(id: string | undefined) {
  return useQuery({
    queryKey: ["colleges", id],
    queryFn: () => collegesApi.get(id as string),
    enabled: Boolean(id),
  });
}

export function useCreateCollege() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (payload: CollegeCreatePayload) => collegesApi.create(payload),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["colleges"] }),
  });
}

export function useUpdateCollege() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ id, payload }: { id: string; payload: Partial<CollegeCreatePayload> }) =>
      collegesApi.update(id, payload),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["colleges"] }),
  });
}

export function useDeleteCollege() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => collegesApi.remove(id),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["colleges"] }),
  });
}
