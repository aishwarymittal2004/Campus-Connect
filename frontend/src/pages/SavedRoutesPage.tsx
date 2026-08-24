import { useState } from "react";
import { Trash2 } from "lucide-react";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Skeleton } from "@/components/ui/skeleton";
import { Button } from "@/components/ui/button";
import { RouteOptionCard } from "@/components/routes/RouteOptionCard";
import { useDeleteRoute, useRouteHistory, useToggleBookmark } from "@/hooks/useRoutes";
import { useToast } from "@/components/ui/toast";
import type { SavedRoute } from "@/types";

function savedRouteToOption(route: SavedRoute) {
  return {
    id: route.id,
    transport_type: route.transport_type,
    distance_km: route.distance_km,
    duration_minutes: route.duration_minutes,
    estimated_cost_inr: route.estimated_cost_inr,
    steps: route.steps,
    polyline: null,
    is_bookmarked: route.is_bookmarked,
  };
}

function RouteHistoryList({ bookmarkedOnly }: { bookmarkedOnly: boolean }) {
  const { data: routes, isLoading } = useRouteHistory(bookmarkedOnly);
  const toggleBookmark = useToggleBookmark();
  const deleteRoute = useDeleteRoute();
  const { toast } = useToast();

  if (isLoading) {
    return (
      <div className="space-y-3">
        {[...Array(3)].map((_, i) => (
          <Skeleton key={i} className="h-20 w-full rounded-xl" />
        ))}
      </div>
    );
  }

  if (!routes || routes.length === 0) {
    return (
      <p className="py-12 text-center text-sm text-muted-foreground">
        {bookmarkedOnly ? "No bookmarked routes yet." : "No route searches yet — try the route finder!"}
      </p>
    );
  }

  return (
    <div className="space-y-3">
      {routes.map((route) => (
        <div key={route.id} className="group relative">
          <RouteOptionCard
            option={savedRouteToOption(route)}
            onToggleBookmark={(isBookmarked) =>
              toggleBookmark.mutate(
                { routeId: route.id, isBookmarked },
                { onError: () => toast({ title: "Couldn't update bookmark", variant: "error" }) }
              )
            }
            bookmarkPending={toggleBookmark.isPending}
          />
          <Button
            variant="ghost"
            size="icon"
            className="absolute right-12 top-3 text-muted-foreground opacity-0 transition-opacity hover:text-destructive group-hover:opacity-100"
            onClick={() =>
              deleteRoute.mutate(route.id, {
                onSuccess: () => toast({ title: "Route removed", variant: "success" }),
              })
            }
            aria-label="Delete route"
          >
            <Trash2 className="h-4 w-4" />
          </Button>
          <p className="mt-1 pl-1 text-xs text-muted-foreground">From {route.source_location}</p>
        </div>
      ))}
    </div>
  );
}

export function SavedRoutesPage() {
  const [tab, setTab] = useState<"bookmarked" | "history">("bookmarked");

  return (
    <div className="mx-auto max-w-3xl">
      <h1 className="font-display text-2xl font-bold tracking-tight">Saved Routes</h1>
      <p className="mt-1 text-muted-foreground">Your bookmarked routes and full search history.</p>

      <Tabs value={tab} onValueChange={(v) => setTab(v as typeof tab)} className="mt-6">
        <TabsList>
          <TabsTrigger value="bookmarked">Bookmarked</TabsTrigger>
          <TabsTrigger value="history">All History</TabsTrigger>
        </TabsList>
        <TabsContent value="bookmarked">
          <RouteHistoryList bookmarkedOnly={true} />
        </TabsContent>
        <TabsContent value="history">
          <RouteHistoryList bookmarkedOnly={false} />
        </TabsContent>
      </Tabs>
    </div>
  );
}
