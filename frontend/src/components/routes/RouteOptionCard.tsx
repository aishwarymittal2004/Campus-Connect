import { Bookmark, ChevronDown, IndianRupee, Clock, MapPin, Plane } from "lucide-react";
import { useState } from "react";
import { cn } from "@/lib/utils";
import { TRANSPORT_META } from "@/components/routes/TransportMeta";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import type { RouteOption } from "@/types";

const MODE_BORDER_COLOR: Record<string, string> = {
  metro: "border-l-transit-metro",
  bus: "border-l-transit-bus",
  cab: "border-l-transit-cab",
  auto: "border-l-transit-auto",
  walk: "border-l-transit-walk",
  mixed: "border-l-transit-mixed",
  train: "border-l-blue-500",
  flight: "border-l-purple-500",
};

interface RouteOptionCardProps {
  option: RouteOption;
  sourceLocation?: string;
  destinationName?: string;
  onToggleBookmark?: (isBookmarked: boolean) => void;
  bookmarkPending?: boolean;
  defaultOpen?: boolean;
}

function formatDuration(minutes: number) {
  if (minutes < 60) return `${Math.round(minutes)} min`;
  const h = Math.floor(minutes / 60);
  const m = Math.round(minutes % 60);
  return m > 0 ? `${h}h ${m}m` : `${h}h`;
}

export function RouteOptionCard({ option, sourceLocation, destinationName, onToggleBookmark, bookmarkPending, defaultOpen = false }: RouteOptionCardProps) {
  const [open, setOpen] = useState(defaultOpen);
  const meta = TRANSPORT_META[option.transport_type];
  const Icon = meta.icon;

  return (
    <div
      className={cn(
        "overflow-hidden rounded-xl border border-l-4 border-border bg-card shadow-sm transition-shadow hover:shadow-md",
        MODE_BORDER_COLOR[option.transport_type]
      )}
    >
      <button
        onClick={() => setOpen((o) => !o)}
        className="flex w-full items-center gap-4 p-4 text-left"
        aria-expanded={open}
      >
        <div className={cn("flex h-11 w-11 shrink-0 items-center justify-center rounded-lg bg-secondary", meta.colorClass)}>
          <Icon className="h-5 w-5" />
        </div>

        <div className="min-w-0 flex-1">
          <div className="flex items-center gap-2">
            <span className="font-display font-semibold">{meta.label}</span>
            <Badge
  variant={
    ["default", "secondary", "outline", "destructive", "accent"].includes(
      meta.badgeVariant
    )
      ? (meta.badgeVariant as
          | "default"
          | "secondary"
          | "outline"
          | "destructive"
          | "accent")
      : "secondary"
  }
  className="hidden sm:inline-flex"
>
              {option.distance_km.toFixed(1)} km
            </Badge>
          </div>
          <div className="mt-1 flex flex-wrap items-center gap-x-4 gap-y-1 text-sm text-muted-foreground">
            <span className="stat-mono flex items-center gap-1">
              <Clock className="h-3.5 w-3.5" /> {formatDuration(option.duration_minutes)}
            </span>
            <span className="stat-mono flex items-center gap-1">
              <IndianRupee className="h-3.5 w-3.5" />
              {option.estimated_cost_inr === 0 ? "Free" : option.estimated_cost_inr.toFixed(0)}
            </span>
            <span className="stat-mono flex items-center gap-1 sm:hidden">
              <MapPin className="h-3.5 w-3.5" /> {option.distance_km.toFixed(1)} km
            </span>
          </div>
        </div>

        <div className="flex items-center gap-1">
          {onToggleBookmark && option.id && (
            <Button
              variant="ghost"
              size="icon"
              disabled={bookmarkPending}
              onClick={(e) => {
                e.stopPropagation();
                onToggleBookmark(!option.is_bookmarked);
              }}
              aria-label={option.is_bookmarked ? "Remove bookmark" : "Bookmark this route"}
            >
              <Bookmark className={cn("h-4 w-4", option.is_bookmarked && "fill-primary text-primary")} />
            </Button>
          )}
          <ChevronDown className={cn("h-4 w-4 text-muted-foreground transition-transform", open && "rotate-180")} />
        </div>
      </button>

      {open && (
        <div className="border-t border-border bg-secondary/40 px-4 py-3">
          <ol className="space-y-2">
            {option.steps.map((step, idx) => (
              <li key={idx} className="flex gap-3 text-sm">
                <span className="stat-mono flex h-5 w-5 shrink-0 items-center justify-center rounded-full bg-card text-xs text-muted-foreground">
                  {idx + 1}
                </span>
                <span className="flex-1 text-foreground/90">{step.instruction}</span>
                {step.duration_minutes != null && (
                  <span className="stat-mono shrink-0 text-xs text-muted-foreground">
                    {formatDuration(step.duration_minutes)}
                  </span>
                )}
              </li>
            ))}
          </ol>

          {option.transport_type === "train" && sourceLocation && destinationName && (
            <div className="mt-4 border-t border-border pt-3 flex justify-end gap-2">
              <Button
                variant="outline"
                size="sm"
                className="gap-2"
                onClick={() => {
                  window.location.href = `/train-schedules?source=${encodeURIComponent(sourceLocation)}&dest=${encodeURIComponent(destinationName)}`;
                }}
              >
                <Clock className="h-4 w-4 text-muted-foreground" />
                View Train Schedules
              </Button>
            </div>
          )}

          {option.transport_type === "flight" && sourceLocation && destinationName && (
            <div className="mt-4 border-t border-border pt-3 flex justify-end gap-2">
              <Button
                variant="outline"
                size="sm"
                className="gap-2"
                onClick={() => {
                  window.location.href = `/flight-schedules?source=${encodeURIComponent(sourceLocation)}&dest=${encodeURIComponent(destinationName)}`;
                }}
              >
                <Plane className="h-4 w-4 text-muted-foreground" />
                View Flight Schedules
              </Button>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
