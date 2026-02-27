"use client";

import { Button } from "@/components/ui/button";
import type { Rating } from "@/services/study/study-service";

interface RatingButtonsProps {
  onRate: (rating: Rating) => void;
  disabled?: boolean;
}

const RATINGS: {
  rating: Rating;
  label: string;
  hint: string;
  variant: "destructive" | "outline" | "secondary" | "default";
  className?: string;
}[] = [
  { rating: 1, label: "Nochmal", hint: "< 1 Tag", variant: "destructive", className: "border-red-400/30" },
  { rating: 2, label: "Schwer", hint: "~ 1 Tag", variant: "outline", className: "border-amber-400/30 hover:bg-amber-500/10" },
  { rating: 3, label: "Gut", hint: "~ 3 Tage", variant: "secondary", className: "border-emerald-400/30" },
  { rating: 4, label: "Leicht", hint: "~ 1 Woche", variant: "default", className: "border-sky-400/30" },
];

export function RatingButtons({ onRate, disabled }: RatingButtonsProps) {
  return (
    <div className="w-full max-w-3xl">
      <p className="mb-3 text-center text-sm text-muted-foreground">Wie gut konntest du die Antwort abrufen?</p>
      <div className="grid grid-cols-2 gap-3 md:grid-cols-4">
      {RATINGS.map(({ rating, label, hint, variant, className }) => (
        <Button
          key={rating}
          variant={variant}
          size="lg"
          className={`h-auto flex-col gap-1 py-3 ${className ?? ""}`}
          onClick={() => onRate(rating)}
          disabled={disabled}
        >
          <span className="font-semibold">{label}</span>
          <span className="text-[11px] text-muted-foreground">{hint}</span>
        </Button>
      ))}
      </div>
    </div>
  );
}
