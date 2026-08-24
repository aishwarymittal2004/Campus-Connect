export type UserRole = "student" | "admin";

export interface User {
  id: string;
  name: string;
  email: string;
  role: UserRole;
  college_id: string | null;
  phone: string | null;
  is_active: boolean;
  created_at: string;
}

export interface TokenPair {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

// --- Colleges ---
export interface Landmark {
  name: string;
  type: string;
  distance_km?: number | null;
}

export interface EmergencyContact {
  label: string;
  phone: string;
}

export interface College {
  id: string;
  name: string;
  city: string;
  state: string | null;
  address: string | null;
  latitude: number;
  longitude: number;
  nearby_landmarks: Landmark[];
  emergency_contacts: EmergencyContact[];
  website: string | null;
  tags: string[];
  created_at: string;
}

// --- Routes ---
export type SourceType = "railway_station" | "airport" | "bus_stand" | "other";
export type TransportType = "metro" | "bus" | "cab" | "auto" | "walk" | "mixed" | "train" | "flight";

export interface RouteStep {
  instruction: string;
  distance_km?: number | null;
  duration_minutes?: number | null;
}

export interface RouteOption {
  id: string | null;
  transport_type: TransportType;
  distance_km: number;
  duration_minutes: number;
  estimated_cost_inr: number;
  steps: RouteStep[];
  polyline: string | null;
  is_bookmarked: boolean;
}

export interface RouteSearchResponse {
  source_location: string;
  college_id: string;
  college_name: string;
  options: RouteOption[];
}

export interface SavedRoute {
  id: string;
  source_location: string;
  source_type: SourceType;
  transport_type: TransportType;
  distance_km: number;
  duration_minutes: number;
  estimated_cost_inr: number;
  steps: RouteStep[];
  is_bookmarked: boolean;
  created_at: string;
  college_id: string;
}

// --- Offers ---
export type OfferPlatform = "zomato" | "swiggy" | "amazon" | "flipkart" | "other";
export type OfferCategory = "food" | "shopping" | "student" | "other";

export interface Offer {
  id: string;
  platform: OfferPlatform;
  category: OfferCategory;
  title: string;
  description: string | null;
  discount: string;
  promo_code: string | null;
  url: string;
  expiry_date: string | null;
  is_active: boolean;
  student_only: boolean;
  created_at: string;
}

// --- Reviews ---
export type ReviewType = "college" | "pg" | "hostel" | "route";

export interface Review {
  id: string;
  user_id: string;
  review_type: ReviewType;
  rating: number;
  comment: string;
  college_id: string | null;
  pg_listing_id: string | null;
  route_id: string | null;
  created_at: string;
}

// --- PG / Local Services ---
export type AccommodationType = "pg" | "hostel";

export interface PGListing {
  id: string;
  college_id: string;
  name: string;
  accommodation_type: AccommodationType;
  address: string;
  latitude: number | null;
  longitude: number | null;
  rent: number;
  contact: string;
  amenities: string[];
  has_mess: boolean;
  gender_preference: string | null;
  distance_from_college_km: number | null;
  is_verified: boolean;
  created_at: string;
}

export type LocalServiceCategory = "mess" | "medical_store" | "atm" | "grocery" | "cafe" | "hotel";

export interface LocalService {
  id: string;
  college_id: string;
  category: LocalServiceCategory;
  name: string;
  address: string | null;
  latitude: number | null;
  longitude: number | null;
  contact: string | null;
  distance_from_college_km: number | null;
  opening_hours: string | null;
}

// --- Student Tips ---
export interface StudentTip {
  id: string;
  user_id: string;
  college_id: string | null;
  title: string;
  content: string;
  upvotes: number;
  created_at: string;
}

// --- Admin ---
export interface PlatformAnalytics {
  total_users: number;
  total_students: number;
  total_admins: number;
  total_colleges: number;
  total_route_searches: number;
  total_bookmarked_routes: number;
  total_reviews: number;
  average_rating: number | null;
  total_pg_listings: number;
  total_active_offers: number;
  most_searched_colleges: { college_id: string; search_count: number }[];
  transport_type_breakdown: Record<string, number>;
}

export interface ApiError {
  detail: string;
  error_type: string;
}
