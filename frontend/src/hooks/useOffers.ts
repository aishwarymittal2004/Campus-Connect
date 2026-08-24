import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { offersApi, type OfferCreatePayload, type OfferFilters } from "@/lib/api/offers";

export function useOffers(filters: OfferFilters = {}) {
  return useQuery({
    queryKey: ["offers", filters],
    queryFn: () => offersApi.list(filters),
  });
}

export function useCreateOffer() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (payload: OfferCreatePayload) => offersApi.create(payload),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["offers"] }),
  });
}

export function useUpdateOffer() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ id, payload }: { id: string; payload: Partial<OfferCreatePayload> }) =>
      offersApi.update(id, payload),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["offers"] }),
  });
}

export function useDeleteOffer() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => offersApi.remove(id),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["offers"] }),
  });
}
