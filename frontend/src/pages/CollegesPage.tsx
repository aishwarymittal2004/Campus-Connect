import { useState } from "react";
import { Link } from "react-router-dom";
import { Search, MapPin, GraduationCap } from "lucide-react";
import { Input } from "@/components/ui/input";
import { Card, CardContent } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { Badge } from "@/components/ui/badge";
import { useColleges } from "@/hooks/useColleges";

export function CollegesPage() {
  const [query, setQuery] = useState("");
  const { data: colleges, isLoading } = useColleges(query || undefined);

  return (
    <div className="mx-auto max-w-3xl">
      <h1 className="font-display text-2xl font-bold tracking-tight">Colleges</h1>
      <p className="mt-1 text-muted-foreground">Browse colleges on Campus Connect, or search by name or city.</p>

      <div className="relative mt-6">
        <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
        <Input placeholder="Search by college or city..." value={query} onChange={(e) => setQuery(e.target.value)} className="pl-9" />
      </div>

      <div className="mt-6 space-y-3">
        {isLoading && [...Array(4)].map((_, i) => <Skeleton key={i} className="h-24 w-full rounded-xl" />)}

        {!isLoading && colleges?.length === 0 && (
          <p className="py-8 text-center text-sm text-muted-foreground">No colleges found.</p>
        )}

        {colleges?.map((college) => (
          <Link key={college.id} to={`/colleges/${college.id}`}>
            <Card className="transition-shadow hover:shadow-md">
              <CardContent className="flex items-start gap-4 p-5">
                <div className="flex h-11 w-11 shrink-0 items-center justify-center rounded-lg bg-primary/10 text-primary">
                  <GraduationCap className="h-5 w-5" />
                </div>
                <div className="min-w-0 flex-1">
                  <h3 className="font-display font-semibold">{college.name}</h3>
                  <p className="mt-0.5 flex items-center gap-1 text-sm text-muted-foreground">
                    <MapPin className="h-3.5 w-3.5" /> {college.city}
                    {college.state ? `, ${college.state}` : ""}
                  </p>
                  {college.tags.length > 0 && (
                    <div className="mt-2 flex flex-wrap gap-1.5">
                      {college.tags.map((tag) => (
                        <Badge key={tag} variant="secondary">
                          {tag}
                        </Badge>
                      ))}
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>
          </Link>
        ))}
      </div>
    </div>
  );
}
