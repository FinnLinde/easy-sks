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
  const progressPercent = cards.length > 0 ? ((currentIndex + 1) / cards.length) * 100 : 0;

  return (
    <div className="mx-auto flex w-full max-w-6xl flex-col items-center gap-6 px-4">
      <div className="w-full max-w-3xl rounded-2xl border border-white/10 bg-card/70 p-4 shadow-xl md:p-5">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div>
            <h1 className="text-xl font-semibold md:text-2xl">Lernsession</h1>
            <p className="text-sm text-muted-foreground">Fokussiert lernen im Dark Mode.</p>
          </div>
          <TopicFilter value={topic} onChange={handleTopicChange} />
        </div>

        <div className="mt-4 inline-flex rounded-xl border border-white/10 bg-background/40 p-1">
          <button
            type="button"
            onClick={() => setMode("due")}
            className={`rounded-lg px-4 py-2 text-sm font-medium transition-colors ${
              mode === "due"
                ? "bg-sky-500/20 text-sky-200"
                : "text-muted-foreground hover:text-foreground"
            }`}
          >
            Wiederholung
          </button>
          <button
            type="button"
            onClick={() => setMode("practice")}
            className={`rounded-lg px-4 py-2 text-sm font-medium transition-colors ${
              mode === "practice"
                ? "bg-emerald-500/20 text-emerald-200"
                : "text-muted-foreground hover:text-foreground"
            }`}
          >
            Practice
          </button>
        </div>
      </div>

      {mode === "practice" && (
        <p className="text-xs text-muted-foreground">
          Practice-Modus: Du lernst auch Karten, die noch nicht fällig sind.
        </p>
      )}

      <div className="w-full max-w-3xl">
        {cards.length > 0 ? (
          <>
            <div className="mb-2 flex items-center justify-between text-sm text-muted-foreground">
              <span>
                Karte {currentIndex + 1} von {cards.length}
              </span>
              <span>{Math.round(progressPercent)}%</span>
            </div>
            <div className="h-2 overflow-hidden rounded-full bg-white/10">
              <div
                className="h-full rounded-full bg-sky-400 transition-[width] duration-200"
                style={{ width: `${progressPercent}%` }}
              />
            </div>
          </>
        ) : null}
      </div>

      {/* Content */}
      {loading ? (
        <div className="w-full max-w-3xl space-y-4">
          <Skeleton className="h-8 w-32" />
          <Skeleton className="h-72 w-full" />
        </div>
      ) : error ? (
        <div className="w-full max-w-3xl rounded-2xl border border-red-500/30 bg-red-500/10 p-10 text-center">
          <p className="text-destructive">{error}</p>
          <button
            onClick={() => fetchCards(topic)}
            className="mt-4 text-sm text-muted-foreground underline"
          >
            Erneut versuchen
          </button>
        </div>
      ) : !currentCard ? (
        <div className="w-full max-w-3xl rounded-2xl border border-emerald-500/30 bg-emerald-500/10 p-10 text-center">
          <p className="text-xl font-medium">
            {mode === "practice" ? "Keine Übungskarten verfügbar" : "Keine Karten fällig"}
          </p>
          <p className="mt-2 text-sm text-muted-foreground">
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
