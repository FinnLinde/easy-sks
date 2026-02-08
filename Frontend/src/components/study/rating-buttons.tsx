"use client";

import { Button } from "@/components/ui/button";
import type { Rating } from "@/services/study/study-service";

interface RatingButtonsProps {
  onRate: (rating: Rating) => void;
  disabled?: boolean;
}

const RATINGS: { rating: Rating; label: string; variant: "destructive" | "outline" | "secondary" | "default" }[] = [
  { rating: 1, label: "Nochmal", variant: "destructive" },
  { rating: 2, label: "Schwer", variant: "outline" },
  { rating: 3, label: "Gut", variant: "secondary" },
  { rating: 4, label: "Leicht", variant: "default" },
];

export function RatingButtons({ onRate, disabled }: RatingButtonsProps) {
  return (
    <div className="flex gap-3 w-full max-w-2xl">
      {RATINGS.map(({ rating, label, variant }) => (
        <Button
          key={rating}
          variant={variant}
          size="lg"
          className="flex-1"
          onClick={() => onRate(rating)}
          disabled={disabled}
        >
          {label}
        </Button>
      ))}
    </div>
  );
}
