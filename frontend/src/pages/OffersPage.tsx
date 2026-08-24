import { useState } from "react";
import { ExternalLink, Tag, Copy, Check } from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { useOffers } from "@/hooks/useOffers";
import { cn } from "@/lib/utils";
import type { OfferCategory, OfferPlatform } from "@/types";

const PLATFORM_FILTERS: { value: OfferPlatform | "all"; label: string }[] = [
  { value: "all", label: "All" },
  { value: "zomato", label: "Zomato" },
  { value: "swiggy", label: "Swiggy" },
  { value: "amazon", label: "Amazon" },
  { value: "flipkart", label: "Flipkart" },
];

const CATEGORY_FILTERS: { value: OfferCategory | "all"; label: string }[] = [
  { value: "all", label: "All categories" },
  { value: "food", label: "Food" },
  { value: "shopping", label: "Shopping" },
  { value: "student", label: "Student-only" },
];

const PLATFORM_COLOR: Record<OfferPlatform, string> = {
  zomato: "bg-red-50 text-red-700 border-red-200",
  swiggy: "bg-orange-50 text-orange-700 border-orange-200",
  amazon: "bg-amber-50 text-amber-800 border-amber-200",
  flipkart: "bg-blue-50 text-blue-700 border-blue-200",
  other: "bg-secondary text-secondary-foreground border-border",
};

function CopyCodeButton({ code }: { code: string }) {
  const [copied, setCopied] = useState(false);
  return (
    <button
      onClick={() => {
        navigator.clipboard.writeText(code);
        setCopied(true);
        setTimeout(() => setCopied(false), 1500);
      }}
      className="flex items-center gap-1 rounded-md border border-dashed border-border px-2 py-1 font-mono text-xs hover:bg-secondary"
    >
      {copied ? <Check className="h-3 w-3" /> : <Copy className="h-3 w-3" />}
      {code}
    </button>
  );
}

export function OffersPage() {
  const [platform, setPlatform] = useState<OfferPlatform | "all">("all");
  const [category, setCategory] = useState<OfferCategory | "all">("all");

  const { data: offers, isLoading } = useOffers({
    platform: platform === "all" ? undefined : platform,
    category: category === "all" ? undefined : category,
  });

  return (
    <div className="mx-auto max-w-3xl">
      <h1 className="font-display text-2xl font-bold tracking-tight">Student Offers</h1>
      <p className="mt-1 text-muted-foreground">Food and shopping deals curated for students, updated regularly.</p>

      <div className="mt-6 flex flex-wrap gap-2">
        {PLATFORM_FILTERS.map((f) => (
          <button
            key={f.value}
            onClick={() => setPlatform(f.value)}
            className={cn(
              "rounded-full border px-3 py-1.5 text-sm font-medium transition-colors",
              platform === f.value ? "border-primary bg-primary text-primary-foreground" : "border-input hover:bg-secondary"
            )}
          >
            {f.label}
          </button>
        ))}
      </div>
      <div className="mt-2 flex flex-wrap gap-2">
        {CATEGORY_FILTERS.map((f) => (
          <button
            key={f.value}
            onClick={() => setCategory(f.value)}
            className={cn(
              "rounded-full border px-3 py-1 text-xs font-medium transition-colors",
              category === f.value ? "border-accent bg-accent/10 text-accent" : "border-input text-muted-foreground hover:bg-secondary"
            )}
          >
            {f.label}
          </button>
        ))}
      </div>

      <div className="mt-6 grid gap-3 sm:grid-cols-2">
        {isLoading && [...Array(4)].map((_, i) => <Skeleton key={i} className="h-40 w-full rounded-xl" />)}

        {!isLoading && offers?.length === 0 && (
          <p className="col-span-2 py-12 text-center text-sm text-muted-foreground">No active offers match these filters.</p>
        )}

        {offers?.map((offer) => (
          <Card key={offer.id}>
            <CardContent className="p-5">
              <div className="flex items-start justify-between gap-2">
                <span className={cn("rounded-md border px-2 py-0.5 text-xs font-semibold capitalize", PLATFORM_COLOR[offer.platform])}>
                  {offer.platform}
                </span>
                {offer.student_only && (
                  <Badge variant="accent">
                    <Tag className="mr-1 h-3 w-3" /> Student only
                  </Badge>
                )}
              </div>
              <h3 className="mt-3 font-display font-semibold leading-snug">{offer.title}</h3>
              {offer.description && <p className="mt-1 text-sm text-muted-foreground">{offer.description}</p>}
              <div className="mt-3 flex items-center justify-between">
                <span className="stat-mono text-lg font-bold text-primary">{offer.discount}</span>
                {offer.promo_code && <CopyCodeButton code={offer.promo_code} />}
              </div>
              <a href={offer.url} target="_blank" rel="noreferrer" className="mt-3 block">
                <Button variant="outline" size="sm" className="w-full">
                  Claim offer <ExternalLink className="h-3.5 w-3.5" />
                </Button>
              </a>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
}
