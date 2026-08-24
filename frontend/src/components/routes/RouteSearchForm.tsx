import { useState } from "react";
import { Search, TrainFront, Plane, Bus as BusIcon } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { useColleges } from "@/hooks/useColleges";
import type { SourceType } from "@/types";
import { cn } from "@/lib/utils";

const SOURCE_TYPES: { value: SourceType; label: string; icon: typeof TrainFront }[] = [
  { value: "railway_station", label: "Railway Station", icon: TrainFront },
  { value: "airport", label: "Airport", icon: Plane },
  { value: "bus_stand", label: "Bus Stand", icon: BusIcon },
];

export interface RouteSearchFormValues {
  sourceLocation: string;
  sourceType: SourceType;
  collegeId: string;
}

interface RouteSearchFormProps {
  onSearch: (values: RouteSearchFormValues) => void;
  isSearching?: boolean;
}

export function RouteSearchForm({ onSearch, isSearching }: RouteSearchFormProps) {
  const [sourceLocation, setSourceLocation] = useState("");
  const [sourceType, setSourceType] = useState<SourceType>("railway_station");
  const [collegeId, setCollegeId] = useState<string>("");
  const [collegeQuery, setCollegeQuery] = useState("");

  const { data: colleges, isLoading: collegesLoading } = useColleges(collegeQuery || undefined);

  const canSubmit = sourceLocation.trim().length >= 2 && Boolean(collegeId);

  return (
    <form
      onSubmit={(e) => {
        e.preventDefault();
        if (canSubmit) onSearch({ sourceLocation: sourceLocation.trim(), sourceType, collegeId });
      }}
      className="space-y-5"
    >
      <div>
        <Label className="mb-2 block">Where are you arriving from?</Label>
        <div className="grid grid-cols-3 gap-2">
          {SOURCE_TYPES.map(({ value, label, icon: Icon }) => (
            <button
              key={value}
              type="button"
              onClick={() => setSourceType(value)}
              className={cn(
                "flex flex-col items-center gap-1.5 rounded-lg border p-3 text-xs font-medium transition-colors",
                sourceType === value
                  ? "border-primary bg-primary/5 text-primary"
                  : "border-input text-muted-foreground hover:bg-secondary"
              )}
            >
              <Icon className="h-5 w-5" />
              {label}
            </button>
          ))}
        </div>
      </div>

      <div>
        <Label htmlFor="source-location" className="mb-2 block">
          Station / Airport / Bus Stand name
        </Label>
        <Input
          id="source-location"
          placeholder="e.g. Lucknow Charbagh Railway Station"
          value={sourceLocation}
          onChange={(e) => setSourceLocation(e.target.value)}
          required
        />
      </div>

      <div>
        <Label htmlFor="college" className="mb-2 block">
          Your College
        </Label>
        <Select value={collegeId} onValueChange={setCollegeId}>
          <SelectTrigger id="college">
            <SelectValue placeholder="Search and select your college" />
          </SelectTrigger>
          <SelectContent>
            <div className="p-2">
              <Input
                placeholder="Type to search colleges..."
                value={collegeQuery}
                onChange={(e) => setCollegeQuery(e.target.value)}
                onKeyDown={(e) => e.stopPropagation()}
              />
            </div>
            {collegesLoading && <div className="px-3 py-2 text-sm text-muted-foreground">Loading...</div>}
            {colleges?.length === 0 && (
              <div className="px-3 py-2 text-sm text-muted-foreground">No colleges found.</div>
            )}
            {colleges?.map((college) => (
              <SelectItem key={college.id} value={college.id}>
                {college.name} — {college.city}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>

      <Button type="submit" className="w-full" size="lg" disabled={!canSubmit || isSearching}>
        <Search className="h-4 w-4" />
        {isSearching ? "Finding routes..." : "Find Routes"}
      </Button>
    </form>
  );
}
