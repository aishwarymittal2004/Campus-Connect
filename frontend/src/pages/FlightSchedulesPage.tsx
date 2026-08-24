import { useState, useEffect } from "react";
import { useSearchParams, useNavigate } from "react-router-dom";
import { Plane, Clock, ArrowLeft, ArrowRight, IndianRupee } from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { apiClient } from "@/lib/api-client";
import { Badge } from "@/components/ui/badge";

export function FlightSchedulesPage() {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const source = searchParams.get("source") || "";
  const dest = searchParams.get("dest") || "";
  
  const [schedules, setSchedules] = useState<any[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    if (!source || !dest) return;
    
    const fetchSchedules = async () => {
      try {
        const response = await apiClient.get(`/routes/flight-schedules?source=${encodeURIComponent(source)}&dest=${encodeURIComponent(dest)}`);
        setSchedules(response.data);
      } catch (error) {
        console.error("Failed to fetch flight schedules", error);
      } finally {
        setIsLoading(false);
      }
    };
    
    fetchSchedules();
  }, [source, dest]);

  return (
    <div className="mx-auto max-w-4xl pb-12">
      <div className="mb-6 flex items-center gap-4">
        <Button variant="ghost" size="icon" onClick={() => navigate(-1)}>
          <ArrowLeft className="h-5 w-5" />
        </Button>
        <div>
          <h1 className="font-display text-2xl font-bold tracking-tight">Flight Schedules</h1>
          <div className="flex items-center gap-2 text-muted-foreground mt-1 text-sm">
            <span>{source}</span>
            <ArrowRight className="h-3 w-3" />
            <span>{dest}</span>
          </div>
        </div>
      </div>

      {isLoading ? (
        <div className="space-y-4">
          {[1, 2, 3].map(i => (
            <Skeleton key={i} className="h-48 w-full rounded-xl" />
          ))}
        </div>
      ) : schedules.length === 0 ? (
        <Card>
          <CardContent className="flex flex-col items-center justify-center py-12">
            <Plane className="h-12 w-12 text-muted-foreground/50 mb-4" />
            <p className="text-lg font-medium">No flight schedules found</p>
            <p className="text-sm text-muted-foreground">Try searching for a different route.</p>
          </CardContent>
        </Card>
      ) : (
        <div className="space-y-6">
          {schedules.map((schedule, idx) => (
            <Card key={schedule.id || idx} className="overflow-hidden border-border/50 transition-all hover:border-primary/50">
              <div className="bg-muted/30 px-6 py-4 flex flex-wrap items-center justify-between border-b gap-4">
                <div className="flex items-center gap-2">
                  <div className="rounded-full bg-primary/10 p-2 text-primary">
                    <Plane className="h-5 w-5" />
                  </div>
                  <div>
                    <h3 className="font-semibold text-base">Option {idx + 1}</h3>
                    <p className="text-xs text-muted-foreground flex items-center gap-1">
                      <Clock className="h-3 w-3" /> Total time: {schedule.total_duration}
                    </p>
                  </div>
                </div>
                <div className="text-right">
                  <div className="flex items-center gap-1 text-lg font-bold text-emerald-600">
                    <IndianRupee className="h-4 w-4" />
                    {schedule.price_estimate?.replace('?', '') || 'N/A'}
                  </div>
                  <p className="text-xs text-muted-foreground">Est. total fare</p>
                </div>
              </div>
              
              <CardContent className="p-0">
                {schedule.legs.map((leg: any, legIdx: number) => (
                  <div key={legIdx} className="relative p-6">
                    {legIdx !== schedule.legs.length - 1 && (
                      <div className="absolute left-9 top-16 bottom-0 w-px bg-border z-0" />
                    )}
                    
                    <div className="flex flex-col md:flex-row gap-6 relative z-10">
                      <div className="flex-1">
                        <div className="flex justify-between items-start mb-4">
                          <div>
                            <span className="font-mono text-sm font-semibold bg-secondary px-2 py-1 rounded text-secondary-foreground inline-block mb-2">
                              {leg.airline} ({leg.flight_number})
                            </span>
                          </div>
                          <Badge variant="outline" className="font-normal text-xs bg-background">
                            {leg.duration}
                          </Badge>
                        </div>
                        
                        <div className="flex justify-between items-center relative">
                          <div className="w-1/3">
                            <p className="text-xl font-bold">{leg.departure_time}</p>
                            <p className="text-sm font-medium">{leg.departure_airport}</p>
                          </div>
                          
                          <div className="flex-1 px-4 flex flex-col items-center">
                            <div className="w-full h-px bg-border flex items-center justify-center relative">
                              <div className="absolute w-2 h-2 rounded-full bg-muted-foreground/30 left-0" />
                              <div className="absolute w-2 h-2 rounded-full border-2 border-primary bg-background right-0" />
                              <div className="bg-background px-2 text-muted-foreground text-xs relative -top-3">
                                {leg.duration}
                              </div>
                            </div>
                          </div>
                          
                          <div className="w-1/3 text-right">
                            <p className="text-xl font-bold">{leg.arrival_time}</p>
                            <p className="text-sm font-medium">{leg.arrival_airport}</p>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}
