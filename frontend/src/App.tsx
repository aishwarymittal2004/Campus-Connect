import { BrowserRouter, Routes, Route } from "react-router-dom";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { AuthProvider } from "@/context/AuthContext";
import { ToastProvider } from "@/components/ui/toast";
import { AppLayout } from "@/components/layout/AppLayout";
import { ProtectedRoute, AdminRoute } from "@/routes/guards";

import { LoginPage } from "@/pages/LoginPage";
import { SignupPage } from "@/pages/SignupPage";
import { RouteFinderPage } from "@/pages/RouteFinderPage";
import { CollegesPage } from "@/pages/CollegesPage";
import { CollegeDetailPage } from "@/pages/CollegeDetailPage";
import { OffersPage } from "@/pages/OffersPage";
import { SavedRoutesPage } from "@/pages/SavedRoutesPage";
import { ProfilePage } from "@/pages/ProfilePage";
import { AdminDashboardPage } from "@/pages/AdminDashboardPage";
import { NotFoundPage } from "@/pages/NotFoundPage";
import { TrainSchedulesPage } from "@/pages/TrainSchedulesPage";
import { FlightSchedulesPage } from "@/pages/FlightSchedulesPage";

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 1,
      refetchOnWindowFocus: false,
      staleTime: 30 * 1000,
    },
  },
});

export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <ToastProvider>
        <AuthProvider>
          <BrowserRouter>
            <Routes>
              <Route element={<AppLayout />}>
                <Route path="/" element={<RouteFinderPage />} />
                <Route path="/train-schedules" element={<TrainSchedulesPage />} />
                <Route path="/flight-schedules" element={<FlightSchedulesPage />} />
                <Route path="/login" element={<LoginPage />} />
                <Route path="/signup" element={<SignupPage />} />
                <Route path="/colleges" element={<CollegesPage />} />
                <Route path="/colleges/:collegeId" element={<CollegeDetailPage />} />
                <Route path="/offers" element={<OffersPage />} />

                <Route element={<ProtectedRoute />}>
                  <Route path="/saved-routes" element={<SavedRoutesPage />} />
                  <Route path="/profile" element={<ProfilePage />} />
                </Route>

                <Route element={<AdminRoute />}>
                  <Route path="/admin" element={<AdminDashboardPage />} />
                </Route>

                <Route path="*" element={<NotFoundPage />} />
              </Route>
            </Routes>
          </BrowserRouter>
        </AuthProvider>
      </ToastProvider>
    </QueryClientProvider>
  );
}
