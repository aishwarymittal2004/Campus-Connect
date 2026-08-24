import { apiClient } from "@/lib/api-client";
import type { LocalService, LocalServiceCategory, PGListing } from "@/types";

export interface PGListingCreatePayload {
  college_id: string;
  name: string;
  accommodation_type: "pg" | "hostel";
  address: string;
  latitude?: number;
  longitude?: number;
  rent: number;
  contact: string;
  amenities?: string[];
  has_mess?: boolean;
  gender_preference?: string;
  distance_from_college_km?: number;
}

export const servicesApi = {
  listPGListings: (collegeId: string, maxRent?: number) =>
    apiClient
      .get<PGListing[]>("/services/pg-listings", { params: { college_id: collegeId, max_rent: maxRent } })
      .then((r) => r.data),
  createPGListing: (payload: PGListingCreatePayload) =>
    apiClient.post<PGListing>("/services/pg-listings", payload).then((r) => r.data),
  removePGListing: (id: string) => apiClient.delete(`/services/pg-listings/${id}`),

  listLocalServices: (collegeId: string, category?: LocalServiceCategory) =>
    apiClient
      .get<LocalService[]>("/services/local", { params: { college_id: collegeId, category } })
      .then((r) => r.data),
  createLocalService: (payload: {
    college_id: string;
    category: LocalServiceCategory;
    name: string;
    address?: string;
    contact?: string;
    distance_from_college_km?: number;
    opening_hours?: string;
  }) => apiClient.post<LocalService>("/services/local", payload).then((r) => r.data),
};
