import { Outlet } from "react-router-dom";
import { Navbar } from "@/components/layout/Navbar";

export function AppLayout() {
  return (
    <div className="min-h-screen bg-background">
      <Navbar />
      <main className="container py-8">
        <Outlet />
      </main>
      <footer className="border-t border-border py-6">
        <div className="container text-center text-sm text-muted-foreground">
          Campus Connect — helping students find their way, one route at a time.
        </div>
      </footer>
    </div>
  );
}
