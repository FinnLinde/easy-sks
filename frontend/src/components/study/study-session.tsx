"use client";

import { useCallback, useEffect, useMemo, useState } from "react";
import { ArrowRight } from "lucide-react";
import { useAuth } from "@/auth/auth-provider";
import { Flashcard } from "@/components/study/flashcard";
import { RatingButtons } from "@/components/study/rating-buttons";
import { SessionComplete } from "@/components/study/session-complete";
import { TopicFilter } from "@/components/study/topic-filter";
import { WelcomeOverlay } from "@/components/study/welcome-overlay";
import { Button } from "@/components/ui/button";
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
type SessionPhase = "setup" | "active" | "complete";

export function StudySession() {
  const { claims } = useAuth();
  const [topic, setTopic] = useState<TopicValue | undefined>(undefined);
  const [mode, setMode] = useState<StudyMode>("due");
  const [phase, setPhase] = useState<SessionPhase>("setup");
  const [cards, setCards] = useState<StudyCard[]>([]);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [cardsCompleted, setCardsCompleted] = useState(0);
  const [revealed, setRevealed] = useState(false);
  const [loading, setLoading] = useState(true);
  const [reviewing, setReviewing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [showWelcome, setShowWelcome] = useState(false);

  const welcomeKey = useMemo(
    () => `easy-sks-study-welcome-seen:${claims?.subject ?? "anonymous"}`,
    [claims?.subject]
  );

  const fetchCards = useCallback(
    async (selectedTopic?: TopicValue) => {
      setLoading(true);
      setError(null);
      try {
        const nextCards =
          mode === "practice"
            ? await getPracticeCards(selectedTopic)
            : await getDueCards(selectedTopic);
        setCards(nextCards);
      } catch {
        setError("Fehler beim Laden der Karten. Ist der Server gestartet?");
      } finally {
        setLoading(false);
      }
    },
    [mode]
  );

  useEffect(() => {
    void fetchCards(topic);
  }, [topic, fetchCards]);

  useEffect(() => {
    if (typeof window === "undefined") return;
    if (!localStorage.getItem(welcomeKey)) {
      setShowWelcome(true);
    }
  }, [welcomeKey]);

  const dismissWelcome = () => {
    if (typeof window !== "undefined") {
      localStorage.setItem(welcomeKey, "true");
    }
    setShowWelcome(false);
  };

  const handleTopicChange = (newTopic: TopicValue | undefined) => {
    setTopic(newTopic);
    setPhase("setup");
  };

  const handleReveal = () => {
    setRevealed(true);
  };

  const startSession = () => {
    if (!cards.length) return;
    setCurrentIndex(0);
    setRevealed(false);
    setCardsCompleted(0);
    setPhase("active");
  };

  const handleRate = async (rating: Rating) => {
    const current = cards[currentIndex];
    if (!current) return;

    setReviewing(true);
    try {
      await reviewCard(current.card.card_id, rating);
      const nextIndex = currentIndex + 1;

      if (nextIndex < cards.length) {
        setCurrentIndex(nextIndex);
        setRevealed(false);
      } else {
        setCardsCompleted(cards.length);
        setPhase("complete");
        setCurrentIndex(0);
        setRevealed(false);
        await fetchCards(topic);
      }
    } catch {
      setError("Fehler beim Bewerten der Karte.");
      setPhase("setup");
    } finally {
      setReviewing(false);
    }
  };

  const handleStartNewSession = async () => {
    setPhase("setup");
    setCurrentIndex(0);
    setRevealed(false);
    await fetchCards(topic);
  };

  const currentCard = cards[currentIndex];
  const progressPercent = cards.length > 0 ? ((currentIndex + 1) / cards.length) * 100 : 0;

  return (
    <>
      <div className="mx-auto flex w-full max-w-6xl flex-col items-center gap-6 px-4">
        <div className="w-full max-w-3xl rounded-2xl border border-white/10 bg-card/70 p-4 shadow-xl md:p-5">
          <div className="flex flex-wrap items-center justify-between gap-3">
            <div>
              <h1 className="text-xl font-semibold md:text-2xl">Lernsession</h1>
            </div>
            <TopicFilter value={topic} onChange={handleTopicChange} />
          </div>

          <div className="mt-4 inline-flex rounded-xl border border-white/10 bg-background/40 p-1">
            <button
              type="button"
              onClick={() => {
                setMode("due");
                setPhase("setup");
              }}
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
              onClick={() => {
                setMode("practice");
                setPhase("setup");
              }}
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

        {phase === "setup" && (
          <div className="w-full max-w-3xl space-y-4">
            {loading ? (
              <div className="space-y-4">
                <Skeleton className="h-8 w-32" />
                <Skeleton className="h-48 w-full" />
              </div>
            ) : error ? (
              <div className="rounded-2xl border border-red-500/30 bg-red-500/10 p-10 text-center">
                <p className="text-destructive">{error}</p>
                <button
                  onClick={() => fetchCards(topic)}
                  className="mt-4 text-sm text-muted-foreground underline"
                >
                  Erneut versuchen
                </button>
              </div>
            ) : (
              <div className="rounded-2xl border border-white/10 bg-card/80 p-6">
                <h2 className="text-lg font-semibold">Session vorbereiten</h2>
                <p className="mt-2 text-sm text-muted-foreground">
                  {mode === "due"
                    ? "Wiederholung priorisiert faellige Karten."
                    : "Practice nutzt deine verfuegbaren Karten unabhaengig von Faelligkeit."}
                </p>

                <div className="mt-5 flex items-center justify-between rounded-xl border border-white/10 bg-background/30 p-4">
                  <span className="text-sm text-muted-foreground">Karten in dieser Session</span>
                  <span className="text-lg font-semibold">{cards.length}</span>
                </div>

                {!cards.length ? (
                  <p className="mt-4 text-sm text-muted-foreground">
                    {mode === "practice"
                      ? "Keine Karten fuer diese Auswahl verfuegbar."
                      : "Keine faelligen Karten fuer diese Auswahl verfuegbar."}
                  </p>
                ) : null}

                <Button
                  className="mt-5 w-full gap-2"
                  size="lg"
                  onClick={startSession}
                  disabled={!cards.length}
                >
                  Session starten
                  <ArrowRight className="size-4" />
                </Button>
              </div>
            )}
          </div>
        )}

        {phase === "active" && currentCard && (
          <>
            <div className="w-full max-w-3xl">
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
            </div>

            <Flashcard studyCard={currentCard} revealed={revealed} onReveal={handleReveal} />
            {revealed && <RatingButtons onRate={handleRate} disabled={reviewing} />}
          </>
        )}

        {phase === "complete" && (
          <SessionComplete mode={mode} cardsCompleted={cardsCompleted} onStartNew={handleStartNewSession} />
        )}
      </div>

      {showWelcome && <WelcomeOverlay onDismiss={dismissWelcome} />}
    </>
  );
}
