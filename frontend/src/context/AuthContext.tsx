import * as React from "react";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { authApi, type LoginPayload, type SignupPayload } from "@/lib/api/auth";
import { tokenStorage } from "@/lib/api-client";
import type { User } from "@/types";

interface AuthContextValue {
  user: User | null;
  isLoading: boolean;
  isAuthenticated: boolean;
  login: (payload: LoginPayload) => Promise<void>;
  signup: (payload: SignupPayload) => Promise<void>;
  logout: () => Promise<void>;
}

const AuthContext = React.createContext<AuthContextValue | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const queryClient = useQueryClient();
  const [hasToken, setHasToken] = React.useState(() => Boolean(tokenStorage.getAccess()));

  const { data: user, isLoading } = useQuery({
    queryKey: ["me"],
    queryFn: authApi.me,
    enabled: hasToken,
    retry: false,
    staleTime: 5 * 60 * 1000,
  });

  const login = async (payload: LoginPayload) => {
    const tokens = await authApi.login(payload);
    tokenStorage.set(tokens);
    setHasToken(true);
    await queryClient.invalidateQueries({ queryKey: ["me"] });
  };

  const signup = async (payload: SignupPayload) => {
    await authApi.signup(payload);
    await login({ email: payload.email, password: payload.password });
  };

  const logout = async () => {
    const refreshToken = tokenStorage.getRefresh();
    if (refreshToken) {
      try {
        await authApi.logout(refreshToken);
      } catch {
        // best-effort revoke; clear local state regardless
      }
    }
    tokenStorage.clear();
    setHasToken(false);
    queryClient.setQueryData(["me"], null);
    queryClient.clear();
  };

  const value: AuthContextValue = {
    user: user ?? null,
    isLoading: hasToken && isLoading,
    isAuthenticated: Boolean(user),
    login,
    signup,
    logout,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const ctx = React.useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within an AuthProvider");
  return ctx;
}
