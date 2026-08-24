import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { servicesApi } from "@/lib/api/services";
import type { LocalServiceCategory } from "@/types";

export function usePGListings(collegeId: string | undefined, maxRent?: number) {
  return useQuery({
    queryKey: ["pg-listings", collegeId, maxRent],
    queryFn: () => servicesApi.listPGListings(collegeId as string, maxRent),
    enabled: Boolean(collegeId),
  });
}

export function useLocalServices(collegeId: string | undefined, category?: LocalServiceCategory) {
  return useQuery({
    queryKey: ["local-services", collegeId, category],
    queryFn: () => servicesApi.listLocalServices(collegeId as string, category),
    enabled: Boolean(collegeId),
  });
}

export function useCreatePGListing() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: servicesApi.createPGListing,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["pg-listings"] }),
  });
}
