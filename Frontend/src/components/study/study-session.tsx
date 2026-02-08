"use client";

import { useCallback, useEffect, useState } from "react";
import { Flashcard } from "@/components/study/flashcard";
import { RatingButtons } from "@/components/study/rating-buttons";
import { TopicFilter } from "@/components/study/topic-filter";
import { Skeleton } from "@/components/ui/skeleton";
import {
  getDueCards,
  reviewCard,
  type Rating,
  type StudyCard,
  type TopicValue,
} from "@/services/study/study-service";

export function StudySession() {
  const [topic, setTopic] = useState<TopicValue | undefined>(undefined);
  const [cards, setCards] = useState<StudyCard[]>([]);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [revealed, setRevealed] = useState(false);
  const [loading, setLoading] = useState(true);
  const [reviewing, setReviewing] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchCards = useCallback(async (selectedTopic?: TopicValue) => {
    setLoading(true);
    setError(null);
    try {
      const due = await getDueCards(selectedTopic);
      setCards(due);
      setCurrentIndex(0);
      setRevealed(false);
    } catch {
      setError("Fehler beim Laden der Karten. Ist der Server gestartet?");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchCards(topic);
  }, [topic, fetchCards]);

  const handleTopicChange = (newTopic: TopicValue | undefined) => {
    setTopic(newTopic);
  };

  const handleReveal = () => {
    setRevealed(true);
  };

  const handleRate = async (rating: Rating) => {
    const current = cards[currentIndex];
    if (!current) return;

    setReviewing(true);
    try {
      await reviewCard(current.card.card_id, rating);

      if (currentIndex + 1 < cards.length) {
        setCurrentIndex((i) => i + 1);
        setRevealed(false);
      } else {
        // All cards reviewed -- re-fetch to see if more are due
        await fetchCards(topic);
      }
    } catch {
      setError("Fehler beim Bewerten der Karte.");
    } finally {
      setReviewing(false);
    }
  };

  const currentCard = cards[currentIndex];

  return (
    <div className="flex flex-col items-center gap-6 w-full px-4">
      {/* Header */}
      <div className="flex items-center justify-between w-full max-w-2xl">
        <h1 className="text-2xl font-bold">Easy SKS</h1>
        <TopicFilter value={topic} onChange={handleTopicChange} />
      </div>

      {/* Progress */}
      {cards.length > 0 && (
        <p className="text-sm text-muted-foreground">
          Karte {currentIndex + 1} von {cards.length}
        </p>
      )}

      {/* Content */}
      {loading ? (
        <div className="w-full max-w-2xl space-y-4">
          <Skeleton className="h-8 w-32" />
          <Skeleton className="h-48 w-full" />
        </div>
      ) : error ? (
        <div className="w-full max-w-2xl text-center py-12">
          <p className="text-destructive">{error}</p>
          <button
            onClick={() => fetchCards(topic)}
            className="mt-4 text-sm text-muted-foreground underline"
          >
            Erneut versuchen
          </button>
        </div>
      ) : !currentCard ? (
        <div className="w-full max-w-2xl text-center py-12">
          <p className="text-xl font-medium">Keine Karten fällig</p>
          <p className="text-sm text-muted-foreground mt-2">
            {topic
              ? "Wechsle das Thema oder komme später zurück."
              : "Alle Karten sind auf dem neuesten Stand."}
          </p>
        </div>
      ) : (
        <>
          <Flashcard
            studyCard={currentCard}
            revealed={revealed}
            onReveal={handleReveal}
          />

          {revealed && (
            <RatingButtons onRate={handleRate} disabled={reviewing} />
          )}
        </>
      )}
    </div>
  );
}
