import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { routesApi, type RouteSearchPayload } from "@/lib/api/routes";

export function useRouteSearch() {
  return useMutation({
    mutationFn: (payload: RouteSearchPayload) => routesApi.search(payload),
  });
}

export function useRouteHistory(bookmarkedOnly = false) {
  return useQuery({
    queryKey: ["route-history", bookmarkedOnly],
    queryFn: () => routesApi.history(bookmarkedOnly),
  });
}

export function useToggleBookmark() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ routeId, isBookmarked }: { routeId: string; isBookmarked: boolean }) =>
      routesApi.toggleBookmark(routeId, isBookmarked),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["route-history"] }),
  });
}

export function useDeleteRoute() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (routeId: string) => routesApi.remove(routeId),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["route-history"] }),
  });
}
