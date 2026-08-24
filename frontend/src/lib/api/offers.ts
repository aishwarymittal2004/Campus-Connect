import { apiClient } from "@/lib/api-client";
import type { Offer, OfferCategory, OfferPlatform } from "@/types";

export interface OfferFilters {
  platform?: OfferPlatform;
  category?: OfferCategory;
}

export interface OfferCreatePayload {
  platform: OfferPlatform;
  category: OfferCategory;
  title: string;
  description?: string;
  discount: string;
  promo_code?: string;
  url: string;
  expiry_date?: string;
  student_only?: boolean;
  is_active?: boolean;
}

export const offersApi = {
  list: (filters: OfferFilters = {}) => apiClient.get<Offer[]>("/offers", { params: filters }).then((r) => r.data),
  create: (payload: OfferCreatePayload) => apiClient.post<Offer>("/offers", payload).then((r) => r.data),
  update: (id: string, payload: Partial<OfferCreatePayload>) =>
    apiClient.patch<Offer>(`/offers/${id}`, payload).then((r) => r.data),
  remove: (id: string) => apiClient.delete(`/offers/${id}`),
};
