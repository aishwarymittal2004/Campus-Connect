import { useState } from "react";
import { formatDistanceToNow } from "date-fns";
import { MessageSquare, Loader2 } from "lucide-react";
import { StarRating } from "@/components/reviews/StarRating";
import { Textarea } from "@/components/ui/textarea";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { useAuth } from "@/context/AuthContext";
import { useCreateReview, useReviews } from "@/hooks/useReviews";
import { useToast } from "@/components/ui/toast";
import { getApiErrorMessage } from "@/lib/api-client";
import type { ReviewType } from "@/types";

interface ReviewSectionProps {
  reviewType: ReviewType;
  targetId: string;
}

export function ReviewSection({ reviewType, targetId }: ReviewSectionProps) {
  const { isAuthenticated } = useAuth();
  const { data: reviews, isLoading } = useReviews(reviewType, targetId);
  const createReview = useCreateReview();
  const { toast } = useToast();

  const [rating, setRating] = useState(0);
  const [comment, setComment] = useState("");

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (rating === 0 || comment.trim().length < 3) return;

    const payload = { review_type: reviewType, rating, comment: comment.trim(), [`${reviewType === "hostel" ? "college" : reviewType}_id`]: targetId };
    createReview.mutate(payload as never, {
      onSuccess: () => {
        setRating(0);
        setComment("");
        toast({ title: "Review posted", variant: "success" });
      },
      onError: (error) => toast({ title: "Couldn't post review", description: getApiErrorMessage(error), variant: "error" }),
    });
  };

  return (
    <div className="space-y-6">
      {isAuthenticated && (
        <form onSubmit={handleSubmit} className="space-y-3 rounded-lg border border-border p-4">
          <StarRating value={rating} onChange={setRating} />
          <Textarea
            placeholder="Share your experience..."
            value={comment}
            onChange={(e) => setComment(e.target.value)}
            rows={3}
          />
          <Button type="submit" size="sm" disabled={createReview.isPending || rating === 0 || comment.trim().length < 3}>
            {createReview.isPending && <Loader2 className="h-3.5 w-3.5 animate-spin" />}
            Post review
          </Button>
        </form>
      )}

      <div className="space-y-4">
        {isLoading && [...Array(2)].map((_, i) => <Skeleton key={i} className="h-16 w-full rounded-lg" />)}

        {!isLoading && reviews?.length === 0 && (
          <div className="flex flex-col items-center gap-2 py-8 text-center text-sm text-muted-foreground">
            <MessageSquare className="h-6 w-6" />
            No reviews yet. Be the first to share your experience.
          </div>
        )}

        {reviews?.map((review) => (
          <div key={review.id} className="border-b border-border pb-4 last:border-0">
            <div className="flex items-center justify-between">
              <StarRating value={review.rating} readOnly size={14} />
              <span className="text-xs text-muted-foreground">
                {formatDistanceToNow(new Date(review.created_at), { addSuffix: true })}
              </span>
            </div>
            <p className="mt-1.5 text-sm text-foreground/90">{review.comment}</p>
          </div>
        ))}
      </div>
    </div>
  );
}
