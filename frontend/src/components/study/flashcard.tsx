"use client";

import { Card, CardContent, CardHeader } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import type { StudyCard } from "@/services/study/study-service";

interface FlashcardProps {
  studyCard: StudyCard;
  revealed: boolean;
  onReveal: () => void;
}

export function Flashcard({ studyCard, revealed, onReveal }: FlashcardProps) {
  const { card, scheduling_info } = studyCard;

  return (
    <Card
      className="w-full max-w-3xl cursor-pointer select-none border-white/10 bg-card/80 shadow-xl transition-all hover:border-sky-400/30"
      onClick={!revealed ? onReveal : undefined}
    >
      <CardHeader className="flex flex-row items-center justify-between gap-2">
        <div className="flex gap-2 flex-wrap">
          {card.tags.map((tag) => (
            <Badge key={tag} variant="secondary">
              {tag}
            </Badge>
          ))}
        </div>
        <Badge variant="outline">{scheduling_info.state}</Badge>
      </CardHeader>

      <CardContent className="min-h-[320px] space-y-6 md:min-h-[360px]">
        {/* Question */}
        <div>
          <p className="text-xs font-medium uppercase tracking-wide text-muted-foreground mb-2">
            Frage
          </p>
              <p className="text-lg leading-relaxed text-foreground md:text-xl">{card.front.text}</p>
            </div>

        {/* Answer (revealed) */}
        {revealed ? (
          <div className="space-y-4 border-t pt-4">
            <div>
              <p className="text-xs font-medium uppercase tracking-wide text-muted-foreground mb-2">
                Antwort
              </p>
              <p className="leading-relaxed text-foreground/90">{card.answer.text}</p>
            </div>

            {card.short_answer.length > 0 && (
              <div>
                <p className="text-xs font-medium uppercase tracking-wide text-muted-foreground mb-2">
                  Kurzantwort
                </p>
                <ul className="list-disc list-inside space-y-1 text-sm">
                  {card.short_answer.map((point, i) => (
                    <li key={i}>{point}</li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        ) : (
          <p className="text-center text-sm text-muted-foreground py-4">
            Tippen zum Aufdecken
          </p>
        )}
      </CardContent>
    </Card>
  );
}
