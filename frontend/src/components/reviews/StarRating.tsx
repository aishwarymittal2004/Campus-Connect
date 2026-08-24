import { Star } from "lucide-react";
import { cn } from "@/lib/utils";

interface StarRatingProps {
  value: number;
  onChange?: (value: number) => void;
  size?: number;
  readOnly?: boolean;
}

export function StarRating({ value, onChange, size = 18, readOnly = false }: StarRatingProps) {
  return (
    <div className="flex items-center gap-0.5">
      {[1, 2, 3, 4, 5].map((star) => (
        <button
          key={star}
          type="button"
          disabled={readOnly}
          onClick={() => onChange?.(star)}
          className={cn(!readOnly && "cursor-pointer", readOnly && "cursor-default")}
          aria-label={`${star} star${star > 1 ? "s" : ""}`}
        >
          <Star
            width={size}
            height={size}
            className={cn(star <= value ? "fill-accent text-accent" : "fill-transparent text-muted-foreground")}
          />
        </button>
      ))}
    </div>
  );
}
