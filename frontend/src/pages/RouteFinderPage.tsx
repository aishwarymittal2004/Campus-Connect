import { useState } from "react";
import { MapPinned, GraduationCap } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { RouteSearchForm, type RouteSearchFormValues } from "@/components/routes/RouteSearchForm";
import { RouteOptionCard } from "@/components/routes/RouteOptionCard";
import { Skeleton } from "@/components/ui/skeleton";
import { useRouteSearch, useToggleBookmark } from "@/hooks/useRoutes";
import { useToast } from "@/components/ui/toast";
import { getApiErrorMessage } from "@/lib/api-client";
import type { RouteSearchResponse } from "@/types";

export function RouteFinderPage() {
  const [results, setResults] = useState<RouteSearchResponse | null>(null);
  const searchMutation = useRouteSearch();
  const bookmarkMutation = useToggleBookmark();
  const { toast } = useToast();

  const handleSearch = (values: RouteSearchFormValues) => {
    searchMutation.mutate(
      {
        source_location: values.sourceLocation,
        source_type: values.sourceType,
        college_id: values.collegeId,
      },
      {
        onSuccess: (data) => setResults(data),
        onError: (error) => toast({ title: "Couldn't find routes", description: getApiErrorMessage(error), variant: "error" }),
      }
    );
  };

  const handleToggleBookmark = (routeId: string, isBookmarked: boolean) => {
    bookmarkMutation.mutate(
      { routeId, isBookmarked },
      {
        onSuccess: () => {
          setResults((prev) =>
            prev
              ? { ...prev, options: prev.options.map((o) => (o.id === routeId ? { ...o, is_bookmarked: isBookmarked } : o)) }
              : prev
          );
          toast({
            title: isBookmarked ? "Route bookmarked" : "Bookmark removed",
            variant: "success",
          });
        },
        onError: (error) => toast({ title: "Couldn't update bookmark", description: getApiErrorMessage(error), variant: "error" }),
      }
    );
  };

  return (
    <div className="mx-auto max-w-3xl">
      <div className="mb-8 text-center">
        <h1 className="font-display text-3xl font-bold tracking-tight sm:text-4xl">
          Find your way to <span className="text-primary">campus</span>
        </h1>
        <p className="mt-2 text-muted-foreground">
          New to the city? Get metro, bus, cab, auto, walking, and mixed route options — with real cost and time estimates.
        </p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-base">
            <MapPinned className="h-4 w-4 text-primary" /> Plan your journey
          </CardTitle>
          <CardDescription>Tell us where you're arriving and which college you're heading to.</CardDescription>
        </CardHeader>
        <CardContent>
          <RouteSearchForm onSearch={handleSearch} isSearching={searchMutation.isPending} />
        </CardContent>
      </Card>

      {searchMutation.isPending && (
        <div className="mt-8 space-y-3">
          {[...Array(4)].map((_, i) => (
            <Skeleton key={i} className="h-20 w-full rounded-xl" />
          ))}
        </div>
      )}

      {results && !searchMutation.isPending && (
        <div className="mt-8">
          <div className="mb-4 flex items-center gap-2 text-sm text-muted-foreground">
            <GraduationCap className="h-4 w-4" />
            <span>
              From <strong className="text-foreground">{results.source_location}</strong> to{" "}
              <strong className="text-foreground">{results.college_name}</strong>
            </span>
          </div>
          <div className="space-y-3">
            {results.options.map((option, idx) => (
              <RouteOptionCard
                key={option.id ?? idx}
                option={option}
                sourceLocation={results.source_location}
                destinationName={results.college_name}
                defaultOpen={idx === 0}
                bookmarkPending={bookmarkMutation.isPending}
                onToggleBookmark={(isBookmarked) => option.id && handleToggleBookmark(option.id, isBookmarked)}
              />
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
