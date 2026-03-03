"use client";

import { useCallback, useEffect, useMemo, useState } from "react";
import { AlertTriangle, CheckCircle2, Clock3, FileText, Loader2, XCircle } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import {
  getExamResult,
  listExamHistory,
  listExamTemplates,
  saveExamAnswer,
  startExamSession,
  submitExamSession,
  type ExamResult,
  type ExamSession,
  type ExamSessionHistory,
  type ExamTemplate,
} from "@/services/exam/exam-service";

type ExamView = "setup" | "active" | "result";

type SetupState = {
  templates: ExamTemplate[];
  history: ExamSessionHistory[];
};

export function ExamSimulator() {
  const [view, setView] = useState<ExamView>("setup");
  const [setupState, setSetupState] = useState<SetupState>({
    templates: [],
    history: [],
  });
  const [loadingSetup, setLoadingSetup] = useState(true);
  const [selectedSheet, setSelectedSheet] = useState<number | null>(null);
  const [activeSession, setActiveSession] = useState<ExamSession | null>(null);
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
  const [answersByCard, setAnswersByCard] = useState<Record<string, string>>({});
  const [dirtyCardIds, setDirtyCardIds] = useState<Set<string>>(new Set());
  const [submitting, setSubmitting] = useState(false);
  const [saving, setSaving] = useState(false);
  const [loadingResult, setLoadingResult] = useState(false);
  const [result, setResult] = useState<ExamResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [tick, setTick] = useState(Date.now());

  const loadSetup = useCallback(async () => {
    setLoadingSetup(true);
    setError(null);
    try {
      const [templates, history] = await Promise.all([
        listExamTemplates(),
        listExamHistory(),
      ]);
      setSetupState({ templates, history });
      setSelectedSheet((previous) => {
        if (previous && templates.some((template) => template.sheet_number === previous)) {
          return previous;
        }
        const withQuestions = templates.find((template) => template.question_count > 0);
        return withQuestions?.sheet_number ?? templates[0]?.sheet_number ?? null;
      });
    } catch {
      setError("Fehler beim Laden der Prüfungen.");
    } finally {
      setLoadingSetup(false);
    }
  }, []);

  useEffect(() => {
    void loadSetup();
  }, [loadSetup]);

  useEffect(() => {
    if (view !== "active") return;
    const intervalId = window.setInterval(() => setTick(Date.now()), 1000);
    return () => window.clearInterval(intervalId);
  }, [view]);

  const currentQuestion = useMemo(() => {
    if (!activeSession) return null;
    return activeSession.questions[currentQuestionIndex] ?? null;
  }, [activeSession, currentQuestionIndex]);

  const remainingSeconds = useMemo(() => {
    if (!activeSession) return 0;
    const deadline = new Date(activeSession.deadline_at).getTime();
    return Math.max(0, Math.floor((deadline - tick) / 1000));
  }, [activeSession, tick]);

  const isTimeOver = useMemo(() => {
    if (!activeSession) return false;
    return activeSession.time_over || remainingSeconds <= 0;
  }, [activeSession, remainingSeconds]);

  const selectedTemplate = useMemo(
    () => setupState.templates.find((template) => template.sheet_number === selectedSheet) ?? null,
    [setupState.templates, selectedSheet]
  );

  const canStart = Boolean(selectedTemplate && selectedTemplate.question_count === 30 && !submitting);

  const markCardClean = (cardId: string) => {
    setDirtyCardIds((current) => {
      const next = new Set(current);
      next.delete(cardId);
      return next;
    });
  };

  const flushCard = useCallback(
    async (cardId: string) => {
      if (!activeSession || !dirtyCardIds.has(cardId)) {
        return;
      }
      setSaving(true);
      try {
        const answerText = answersByCard[cardId] ?? "";
        await saveExamAnswer(activeSession.session_id, cardId, answerText);
        markCardClean(cardId);
      } finally {
        setSaving(false);
      }
    },
    [activeSession, answersByCard, dirtyCardIds]
  );

  const flushAllDirtyAnswers = useCallback(async () => {
    if (!activeSession) return;

    const dirtyIds = Array.from(dirtyCardIds);
    if (!dirtyIds.length) return;

    setSaving(true);
    try {
      for (const cardId of dirtyIds) {
        const answerText = answersByCard[cardId] ?? "";
        await saveExamAnswer(activeSession.session_id, cardId, answerText);
        markCardClean(cardId);
      }
    } finally {
      setSaving(false);
    }
  }, [activeSession, answersByCard, dirtyCardIds]);

  const handleStart = async () => {
    if (!selectedSheet) return;

    setError(null);
    setSubmitting(true);
    try {
      const session = await startExamSession(selectedSheet);
      setActiveSession(session);
      setCurrentQuestionIndex(0);
      const initialAnswers = Object.fromEntries(
        session.questions.map((question) => [question.card_id, question.student_answer])
      );
      setAnswersByCard(initialAnswers);
      setDirtyCardIds(new Set());
      setResult(null);
      setView("active");
      setTick(Date.now());
    } catch {
      setError("Prüfung konnte nicht gestartet werden.");
    } finally {
      setSubmitting(false);
    }
  };

  const handleQuestionChange = (cardId: string, value: string) => {
    setAnswersByCard((current) => ({ ...current, [cardId]: value }));
    setDirtyCardIds((current) => {
      const next = new Set(current);
      next.add(cardId);
      return next;
    });
  };

  const handleNavigateTo = async (nextIndex: number) => {
    if (!activeSession || !currentQuestion) return;

    try {
      await flushCard(currentQuestion.card_id);
      setCurrentQuestionIndex(nextIndex);
    } catch {
      setError("Antwort konnte nicht gespeichert werden.");
    }
  };

  const handleSubmit = async () => {
    if (!activeSession || !currentQuestion) return;

    setSubmitting(true);
    setError(null);
    try {
      await flushCard(currentQuestion.card_id);
      await flushAllDirtyAnswers();
      const evaluated = await submitExamSession(activeSession.session_id);
      setResult(evaluated);
      setView("result");
      await loadSetup();
    } catch {
      setError("Prüfung konnte nicht abgegeben werden.");
    } finally {
      setSubmitting(false);
    }
  };

  const handleOpenHistoryResult = async (sessionId: string) => {
    setLoadingResult(true);
    setError(null);
    try {
      const fetched = await getExamResult(sessionId);
      setResult(fetched);
      setView("result");
    } catch {
      setError("Ergebnis konnte nicht geladen werden.");
    } finally {
      setLoadingResult(false);
    }
  };

  const handleBackToSelection = async () => {
    setView("setup");
    setResult(null);
    setActiveSession(null);
    setCurrentQuestionIndex(0);
    setAnswersByCard({});
    setDirtyCardIds(new Set());
    await loadSetup();
  };

  return (
    <div className="mx-auto w-full max-w-7xl space-y-6 px-4 py-6 md:px-6 md:py-8">
      <div className="space-y-2">
        <h1 className="text-2xl font-semibold tracking-tight md:text-3xl">Prüfungssimulation</h1>
        <p className="text-sm text-muted-foreground">
          30 Fragen, je 2 Punkte. Bestanden ab 39 von 60 Punkten.
        </p>
      </div>

      {error ? (
        <Card className="border-red-500/30 bg-red-500/10">
          <CardContent className="p-4 text-sm text-red-200">{error}</CardContent>
        </Card>
      ) : null}

      {view === "setup" && (
        <div className="grid gap-6 lg:grid-cols-[1.2fr_1fr]">
          <Card className="border-white/10 bg-card/70">
            <CardHeader>
              <CardTitle>Prüfung starten</CardTitle>
            </CardHeader>
            <CardContent className="space-y-5">
              {loadingSetup ? (
                <div className="flex items-center gap-2 text-sm text-muted-foreground">
                  <Loader2 className="size-4 animate-spin" />
                  Lade Prüfungsbögen...
                </div>
              ) : (
                <>
                  <label className="flex flex-col gap-2 text-sm">
                    <span className="text-muted-foreground">Prüfungsbogen</span>
                    <select
                      value={selectedSheet ?? ""}
                      onChange={(event) => setSelectedSheet(Number(event.target.value))}
                      className="rounded-lg border border-white/15 bg-background/40 px-3 py-2"
                    >
                      {setupState.templates.map((template) => (
                        <option key={template.sheet_number} value={template.sheet_number}>
                          {template.display_name} ({template.question_count} Fragen)
                        </option>
                      ))}
                    </select>
                  </label>

                  <div className="rounded-lg border border-white/10 bg-background/40 p-4 text-sm">
                    <div className="flex items-center justify-between gap-3">
                      <span className="text-muted-foreground">Zeitlimit</span>
                      <span className="font-medium">{selectedTemplate?.time_limit_minutes ?? 90} Minuten</span>
                    </div>
                    <div className="mt-2 flex items-center justify-between gap-3">
                      <span className="text-muted-foreground">Fragen</span>
                      <span className="font-medium">{selectedTemplate?.question_count ?? 0}</span>
                    </div>
                    <div className="mt-2 flex items-center justify-between gap-3">
                      <span className="text-muted-foreground">Bestehen</span>
                      <span className="font-medium">39 / 60 Punkte</span>
                    </div>
                  </div>

                  {selectedTemplate && selectedTemplate.question_count !== 30 ? (
                    <p className="text-sm text-amber-200">
                      Dieser Bogen ist unvollständig ({selectedTemplate.question_count}/30 Fragen) und kann nicht gestartet werden.
                    </p>
                  ) : null}

                  <Button onClick={handleStart} disabled={!canStart} className="w-full" size="lg">
                    {submitting ? (
                      <span className="inline-flex items-center gap-2">
                        <Loader2 className="size-4 animate-spin" />
                        Starte...
                      </span>
                    ) : (
                      "Simulation starten"
                    )}
                  </Button>
                </>
              )}
            </CardContent>
          </Card>

          <Card className="border-white/10 bg-card/70">
            <CardHeader>
              <CardTitle>Prüfungshistorie</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              {!setupState.history.length ? (
                <p className="text-sm text-muted-foreground">Noch keine abgeschlossenen Prüfungen.</p>
              ) : (
                setupState.history.map((item) => (
                  <div
                    key={item.session_id}
                    className="rounded-lg border border-white/10 bg-background/40 p-3"
                  >
                    <div className="flex items-start justify-between gap-2">
                      <div>
                        <p className="text-sm font-medium">Prüfungsbogen {item.sheet_number}</p>
                        <p className="text-xs text-muted-foreground">
                          {new Date(item.started_at).toLocaleString("de-DE")}
                        </p>
                      </div>
                      <span
                        className={`rounded-full px-2 py-0.5 text-xs ${
                          item.passed
                            ? "bg-emerald-500/20 text-emerald-200"
                            : "bg-red-500/20 text-red-200"
                        }`}
                      >
                        {item.passed ? "Bestanden" : "Nicht bestanden"}
                      </span>
                    </div>

                    <div className="mt-2 flex items-center justify-between text-xs text-muted-foreground">
                      <span>
                        Punkte: {item.total_score ?? "-"} / {item.max_score ?? "-"}
                      </span>
                      {item.time_over ? <span>Zeit abgelaufen</span> : null}
                    </div>

                    <Button
                      size="sm"
                      variant="outline"
                      className="mt-3 w-full"
                      onClick={() => void handleOpenHistoryResult(item.session_id)}
                      disabled={loadingResult}
                    >
                      {loadingResult ? "Lade..." : "Ergebnis ansehen"}
                    </Button>
                  </div>
                ))
              )}
            </CardContent>
          </Card>
        </div>
      )}

      {view === "active" && activeSession && currentQuestion && (
        <div className="grid gap-6 lg:grid-cols-[280px_1fr]">
          <Card className="border-white/10 bg-card/70">
            <CardHeader>
              <CardTitle className="text-base">Prüfungsbogen {activeSession.sheet_number}</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="rounded-lg border border-white/10 bg-background/40 p-3">
                <div className="flex items-center justify-between text-sm">
                  <span className="inline-flex items-center gap-2 text-muted-foreground">
                    <Clock3 className="size-4" />
                    Restzeit
                  </span>
                  <span className={`font-semibold ${isTimeOver ? "text-red-200" : "text-foreground"}`}>
                    {formatDuration(remainingSeconds)}
                  </span>
                </div>
                {isTimeOver ? (
                  <p className="mt-2 text-xs text-red-200">
                    Zeit ist abgelaufen. Du kannst weiterschreiben, aber das Ergebnis wird als nicht bestanden markiert.
                  </p>
                ) : null}
              </div>

              <div className="grid grid-cols-5 gap-2">
                {activeSession.questions.map((question, index) => {
                  const hasAnswer = Boolean((answersByCard[question.card_id] ?? "").trim());
                  const isActive = index === currentQuestionIndex;
                  return (
                    <button
                      key={question.card_id}
                      type="button"
                      className={`rounded-md border px-0 py-2 text-xs transition-colors ${
                        isActive
                          ? "border-sky-400 bg-sky-500/20 text-sky-100"
                          : hasAnswer
                          ? "border-emerald-500/40 bg-emerald-500/15 text-emerald-100"
                          : "border-white/10 bg-background/40 text-muted-foreground hover:text-foreground"
                      }`}
                      onClick={() => void handleNavigateTo(index)}
                      disabled={saving || submitting}
                    >
                      {question.question_number}
                    </button>
                  );
                })}
              </div>
            </CardContent>
          </Card>

          <Card className="border-white/10 bg-card/70">
            <CardHeader>
              <CardTitle className="text-base">
                Frage {currentQuestion.question_number} von {activeSession.question_count}
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="rounded-lg border border-white/10 bg-background/40 p-4 text-sm leading-relaxed">
                {currentQuestion.question_text}
              </div>

              <label className="flex flex-col gap-2">
                <span className="text-sm text-muted-foreground">Deine Antwort</span>
                <textarea
                  value={answersByCard[currentQuestion.card_id] ?? ""}
                  onChange={(event) =>
                    handleQuestionChange(currentQuestion.card_id, event.target.value)
                  }
                  className="min-h-44 w-full rounded-lg border border-white/15 bg-background/50 p-3 text-sm outline-none transition-colors focus:border-sky-400"
                  placeholder="Schreibe hier deine Antwort..."
                  disabled={submitting}
                />
              </label>

              <div className="flex flex-wrap items-center justify-between gap-2">
                <div className="text-xs text-muted-foreground">
                  {saving ? "Speichere..." : dirtyCardIds.has(currentQuestion.card_id) ? "Nicht gespeichert" : "Gespeichert"}
                </div>
                <div className="flex items-center gap-2">
                  <Button
                    variant="outline"
                    onClick={() => void handleNavigateTo(Math.max(0, currentQuestionIndex - 1))}
                    disabled={currentQuestionIndex === 0 || saving || submitting}
                  >
                    Zurück
                  </Button>
                  <Button
                    variant="outline"
                    onClick={() => void handleNavigateTo(Math.min(activeSession.question_count - 1, currentQuestionIndex + 1))}
                    disabled={currentQuestionIndex >= activeSession.question_count - 1 || saving || submitting}
                  >
                    Weiter
                  </Button>
                  <Button onClick={() => void handleSubmit()} disabled={submitting || saving}>
                    {submitting ? (
                      <span className="inline-flex items-center gap-2">
                        <Loader2 className="size-4 animate-spin" />
                        Abgabe...
                      </span>
                    ) : (
                      "Prüfung abgeben"
                    )}
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {view === "result" && result && (
        <div className="space-y-4">
          <Card className="border-white/10 bg-card/70">
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-lg">
                <FileText className="size-5" />
                Ergebnis Prüfungsbogen {result.sheet_number}
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid gap-3 md:grid-cols-4">
                <ResultKpi label="Punktzahl" value={`${result.total_score} / ${result.max_score}`} />
                <ResultKpi label="Bestehen" value={`${result.pass_score_threshold} Punkte`} />
                <ResultKpi
                  label="Status"
                  value={result.passed ? "Bestanden" : "Nicht bestanden"}
                  accent={result.passed ? "success" : "danger"}
                />
                <ResultKpi
                  label="Zeitlimit"
                  value={result.time_over ? "Überschritten" : "Eingehalten"}
                  accent={result.time_over ? "danger" : "success"}
                />
              </div>

              {result.time_over ? (
                <div className="rounded-lg border border-red-500/40 bg-red-500/15 p-3 text-sm text-red-100">
                  Zeit war abgelaufen. Die Session wird unabhängig von der Punktzahl als nicht bestanden gewertet.
                </div>
              ) : null}

              <div className="space-y-3">
                {result.questions.map((question) => (
                  <div key={question.card_id} className="rounded-lg border border-white/10 bg-background/40 p-4">
                    <div className="mb-2 flex items-start justify-between gap-3">
                      <p className="text-sm font-medium">
                        Frage {question.question_number}: {question.question_text}
                      </p>
                      <span className="text-sm font-semibold">
                        {question.score} / 2
                      </span>
                    </div>

                    <p className="text-xs text-muted-foreground">Deine Antwort</p>
                    <p className="mt-1 whitespace-pre-wrap text-sm">{question.student_answer || "(Keine Antwort)"}</p>

                    <div className="mt-3 flex items-center gap-2 text-sm">
                      {question.is_correct ? (
                        <CheckCircle2 className="size-4 text-emerald-300" />
                      ) : (
                        <XCircle className="size-4 text-red-300" />
                      )}
                      <span>{question.feedback}</span>
                    </div>

                    {question.errors.length ? (
                      <ul className="mt-2 space-y-1 text-xs text-amber-100">
                        {question.errors.map((entry, index) => (
                          <li key={`${question.card_id}-${index}`} className="inline-flex items-start gap-1">
                            <AlertTriangle className="mt-0.5 size-3" />
                            <span>{entry}</span>
                          </li>
                        ))}
                      </ul>
                    ) : null}
                  </div>
                ))}
              </div>

              <div className="flex justify-end">
                <Button onClick={() => void handleBackToSelection()}>Zurück zur Auswahl</Button>
              </div>
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  );
}

function ResultKpi({
  label,
  value,
  accent = "neutral",
}: {
  label: string;
  value: string;
  accent?: "neutral" | "success" | "danger";
}) {
  const accentClass =
    accent === "success"
      ? "text-emerald-200"
      : accent === "danger"
      ? "text-red-200"
      : "text-foreground";

  return (
    <div className="rounded-lg border border-white/10 bg-background/40 p-3">
      <p className="text-xs text-muted-foreground">{label}</p>
      <p className={`mt-1 text-sm font-semibold ${accentClass}`}>{value}</p>
    </div>
  );
}

function formatDuration(totalSeconds: number): string {
  const minutes = Math.floor(totalSeconds / 60);
  const seconds = totalSeconds % 60;
  return `${String(minutes).padStart(2, "0")}:${String(seconds).padStart(2, "0")}`;
}
