import { apiClient } from "@/lib/api-client";
import type { TokenPair, User } from "@/types";

export interface SignupPayload {
  name: string;
  email: string;
  password: string;
  phone?: string;
}

export interface LoginPayload {
  email: string;
  password: string;
}

export interface ProfileUpdatePayload {
  name?: string;
  phone?: string;
  college_id?: string;
}

export const authApi = {
  signup: (payload: SignupPayload) => apiClient.post<User>("/auth/signup", payload).then((r) => r.data),
  login: (payload: LoginPayload) => apiClient.post<TokenPair>("/auth/login", payload).then((r) => r.data),
  logout: (refreshToken: string) => apiClient.post("/auth/logout", { refresh_token: refreshToken }),
  me: () => apiClient.get<User>("/auth/me").then((r) => r.data),
  updateProfile: (payload: ProfileUpdatePayload) => apiClient.patch<User>("/auth/me", payload).then((r) => r.data),
  changePassword: (current_password: string, new_password: string) =>
    apiClient.post("/auth/me/change-password", { current_password, new_password }),
};
