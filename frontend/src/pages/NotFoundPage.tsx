import { Link } from "react-router-dom";
import { MapPinned } from "lucide-react";
import { Button } from "@/components/ui/button";

export function NotFoundPage() {
  return (
    <div className="flex min-h-[60vh] flex-col items-center justify-center text-center">
      <MapPinned className="h-10 w-10 text-muted-foreground" />
      <h1 className="mt-4 font-display text-2xl font-bold">You've wandered off route</h1>
      <p className="mt-1 text-muted-foreground">We couldn't find the page you're looking for.</p>
      <Link to="/" className="mt-6">
        <Button>Back to Route Finder</Button>
      </Link>
    </div>
  );
}
