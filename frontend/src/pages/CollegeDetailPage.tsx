import { useParams } from "react-router-dom";
import { MapPin, Phone, Landmark as LandmarkIcon, Home, Stethoscope, Landmark, ShoppingBasket, Lightbulb, ThumbsUp, Coffee, Bed } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { Button } from "@/components/ui/button";
import { useCollege } from "@/hooks/useColleges";
import { usePGListings, useLocalServices } from "@/hooks/useServices";
import { useStudentTips, useUpvoteTip } from "@/hooks/useTips";
import { ReviewSection } from "@/components/reviews/ReviewSection";
import type { LocalServiceCategory } from "@/types";

const LOCAL_SERVICE_META: Record<LocalServiceCategory, { label: string; icon: typeof Stethoscope }> = {
  medical_store: { label: "Medical Stores", icon: Stethoscope },
  atm: { label: "ATMs", icon: Landmark },
  grocery: { label: "Grocery Stores", icon: ShoppingBasket },
  mess: { label: "Mess Facilities", icon: Home },
  cafe: { label: "Cafes & Restaurants", icon: Coffee },
  hotel: { label: "Hotels & Lodges", icon: Bed },
};

export function CollegeDetailPage() {
  const { collegeId } = useParams<{ collegeId: string }>();
  const { data: college, isLoading } = useCollege(collegeId);
  const { data: pgListings, isLoading: pgLoading } = usePGListings(collegeId);
  const { data: localServices, isLoading: servicesLoading } = useLocalServices(collegeId);
  const { data: tips, isLoading: tipsLoading } = useStudentTips(collegeId);
  const upvoteTip = useUpvoteTip();

  if (isLoading) {
    return (
      <div className="mx-auto max-w-3xl space-y-4">
        <Skeleton className="h-10 w-2/3" />
        <Skeleton className="h-40 w-full rounded-xl" />
      </div>
    );
  }

  if (!college) {
    return <p className="py-12 text-center text-muted-foreground">College not found.</p>;
  }

  return (
    <div className="mx-auto max-w-3xl">
      <h1 className="font-display text-3xl font-bold tracking-tight">{college.name}</h1>
      <p className="mt-1 flex items-center gap-1.5 text-muted-foreground">
        <MapPin className="h-4 w-4" />
        {college.address || `${college.city}${college.state ? `, ${college.state}` : ""}`}
      </p>
      {college.tags.length > 0 && (
        <div className="mt-3 flex flex-wrap gap-1.5">
          {college.tags.map((tag) => (
            <Badge key={tag} variant="secondary">
              {tag}
            </Badge>
          ))}
        </div>
      )}

      <Tabs defaultValue="info" className="mt-6">
        <TabsList className="flex-wrap">
          <TabsTrigger value="info">Info</TabsTrigger>
          <TabsTrigger value="stay">PGs &amp; Hostels</TabsTrigger>
          <TabsTrigger value="services">Local Services</TabsTrigger>
          <TabsTrigger value="tips">Student Tips</TabsTrigger>
          <TabsTrigger value="reviews">Reviews</TabsTrigger>
        </TabsList>

        <TabsContent value="info" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-base">
                <LandmarkIcon className="h-4 w-4 text-primary" /> Nearby Landmarks
              </CardTitle>
            </CardHeader>
            <CardContent>
              {college.nearby_landmarks.length === 0 ? (
                <p className="text-sm text-muted-foreground">No landmarks added yet.</p>
              ) : (
                <ul className="space-y-2">
                  {college.nearby_landmarks.map((landmark, i) => (
                    <li key={i} className="flex items-center justify-between text-sm">
                      <span>{landmark.name}</span>
                      {landmark.distance_km != null && (
                        <span className="stat-mono text-muted-foreground">{landmark.distance_km} km</span>
                      )}
                    </li>
                  ))}
                </ul>
              )}
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-base">
                <Phone className="h-4 w-4 text-destructive" /> Emergency Contacts
              </CardTitle>
            </CardHeader>
            <CardContent>
              {college.emergency_contacts.length === 0 ? (
                <p className="text-sm text-muted-foreground">No emergency contacts added yet.</p>
              ) : (
                <ul className="space-y-2">
                  {college.emergency_contacts.map((contact, i) => (
                    <li key={i} className="flex items-center justify-between text-sm">
                      <span>{contact.label}</span>
                      <a href={`tel:${contact.phone}`} className="stat-mono font-medium text-primary hover:underline">
                        {contact.phone}
                      </a>
                    </li>
                  ))}
                </ul>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="stay" className="space-y-3">
          {pgLoading && [...Array(2)].map((_, i) => <Skeleton key={i} className="h-24 w-full rounded-xl" />)}
          {!pgLoading && pgListings?.length === 0 && (
            <p className="py-8 text-center text-sm text-muted-foreground">No PG/hostel listings yet.</p>
          )}
          {pgListings?.map((listing) => (
            <Card key={listing.id}>
              <CardContent className="p-5">
                <div className="flex items-start justify-between">
                  <div>
                    <h3 className="font-display font-semibold">{listing.name}</h3>
                    <p className="text-sm text-muted-foreground">{listing.address}</p>
                  </div>
                  <span className="stat-mono whitespace-nowrap font-semibold text-primary">₹{listing.rent}/mo</span>
                </div>
                <div className="mt-3 flex flex-wrap items-center gap-1.5">
                  <Badge variant="secondary">{listing.accommodation_type}</Badge>
                  {listing.has_mess && <Badge variant="secondary">Mess included</Badge>}
                  {listing.gender_preference && <Badge variant="secondary">{listing.gender_preference}</Badge>}
                  {listing.is_verified && <Badge variant="metro">Verified</Badge>}
                  {listing.amenities.map((a) => (
                    <Badge key={a} variant="outline">
                      {a}
                    </Badge>
                  ))}
                </div>
                <a href={`tel:${listing.contact}`} className="mt-3 inline-block text-sm font-medium text-primary hover:underline">
                  Contact: {listing.contact}
                </a>
              </CardContent>
            </Card>
          ))}
        </TabsContent>

        <TabsContent value="services" className="space-y-4">
          {servicesLoading && <Skeleton className="h-32 w-full rounded-xl" />}
          {(["mess", "medical_store", "atm", "grocery", "cafe", "hotel"] as LocalServiceCategory[]).map((category) => {
            const items = localServices?.filter((s) => s.category === category) ?? [];
            if (items.length === 0) return null;
            const { label, icon: Icon } = LOCAL_SERVICE_META[category];
            return (
              <Card key={category}>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2 text-base">
                    <Icon className="h-4 w-4 text-primary" /> {label}
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <ul className="space-y-2">
                    {items.map((item) => (
                      <li key={item.id} className="flex items-center justify-between text-sm">
                        <div>
                          <p>{item.name}</p>
                          {item.address && <p className="text-xs text-muted-foreground">{item.address}</p>}
                        </div>
                        {item.distance_from_college_km != null && (
                          <span className="stat-mono text-muted-foreground">{item.distance_from_college_km} km</span>
                        )}
                      </li>
                    ))}
                  </ul>
                </CardContent>
              </Card>
            );
          })}
          {!servicesLoading && (localServices?.length ?? 0) === 0 && (
            <p className="py-8 text-center text-sm text-muted-foreground">No local services listed yet.</p>
          )}
        </TabsContent>

        <TabsContent value="tips" className="space-y-3">
          {tipsLoading && [...Array(2)].map((_, i) => <Skeleton key={i} className="h-20 w-full rounded-xl" />)}
          {!tipsLoading && tips?.length === 0 && (
            <div className="flex flex-col items-center gap-2 py-8 text-center text-sm text-muted-foreground">
              <Lightbulb className="h-6 w-6" />
              No student tips yet. Share what you know from the community page.
            </div>
          )}
          {tips?.map((tip) => (
            <Card key={tip.id}>
              <CardContent className="p-4">
                <h4 className="font-medium">{tip.title}</h4>
                <p className="mt-1 text-sm text-muted-foreground">{tip.content}</p>
                <Button
                  variant="ghost"
                  size="sm"
                  className="mt-2"
                  onClick={() => upvoteTip.mutate(tip.id)}
                  disabled={upvoteTip.isPending}
                >
                  <ThumbsUp className="h-3.5 w-3.5" /> {tip.upvotes}
                </Button>
              </CardContent>
            </Card>
          ))}
        </TabsContent>

        <TabsContent value="reviews">
          <ReviewSection reviewType="college" targetId={college.id} />
        </TabsContent>
      </Tabs>
    </div>
  );
}
