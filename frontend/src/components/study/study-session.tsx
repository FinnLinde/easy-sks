"use client";

import { useCallback, useEffect, useState } from "react";
import { Flashcard } from "@/components/study/flashcard";
import { RatingButtons } from "@/components/study/rating-buttons";
import { TopicFilter } from "@/components/study/topic-filter";
import { Skeleton } from "@/components/ui/skeleton";
import {
  getDueCards,
  getPracticeCards,
  reviewCard,
  type Rating,
  type StudyCard,
  type TopicValue,
} from "@/services/study/study-service";

type StudyMode = "due" | "practice";

export function StudySession() {
  const [topic, setTopic] = useState<TopicValue | undefined>(undefined);
  const [mode, setMode] = useState<StudyMode>("due");
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
      const nextCards =
        mode === "practice"
          ? await getPracticeCards(selectedTopic)
          : await getDueCards(selectedTopic);
      setCards(nextCards);
      setCurrentIndex(0);
      setRevealed(false);
    } catch {
      setError("Fehler beim Laden der Karten. Ist der Server gestartet?");
    } finally {
      setLoading(false);
    }
  }, [mode]);

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
      <div className="flex flex-wrap items-center justify-between gap-3 w-full max-w-2xl">
        <h1 className="hidden text-2xl font-bold sm:block">Easy SKS</h1>
        <TopicFilter value={topic} onChange={handleTopicChange} />
      </div>

      {mode === "practice" && (
        <p className="text-xs text-muted-foreground">
          Practice-Modus: Du lernst auch Karten, die noch nicht fällig sind.
        </p>
      )}

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
          <p className="text-xl font-medium">
            {mode === "practice" ? "Keine Übungskarten verfügbar" : "Keine Karten fällig"}
          </p>
          <p className="text-sm text-muted-foreground mt-2">
            {mode === "practice"
              ? "Aktuell sind für diese Auswahl keine Karten vorhanden."
              : topic
                ? "Wechsle das Thema, starte Practice oder komme später zurück."
                : "Alle Karten sind auf dem neuesten Stand."}
          </p>
          {mode !== "practice" && (
            <button
              onClick={() => setMode("practice")}
              className="mt-4 text-sm text-muted-foreground underline"
            >
              Practice starten
            </button>
          )}
          {mode === "practice" && (
            <button
              onClick={() => setMode("due")}
              className="mt-4 text-sm text-muted-foreground underline"
            >
              Zurück zu fälligen Karten
            </button>
          )}
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
