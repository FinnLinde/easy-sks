"use client";

import { useCallback, useEffect, useMemo, useState } from "react";
import { CheckCircle2, Clock3, Compass, Info, Loader2, XCircle } from "lucide-react";
import Markdown from "react-markdown";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import {
  getNavigationResult,
  listNavigationHistory,
  listNavigationTemplates,
  saveNavigationAnswer,
  startNavigationSession,
  submitNavigationSession,
  type NavigationResult,
  type NavigationSession,
  type NavigationSessionHistory,
  type NavigationTemplate,
} from "@/services/navigation/navigation-service";

type NavigationView = "setup" | "active" | "result";

type SetupState = {
  templates: NavigationTemplate[];
  history: NavigationSessionHistory[];
};

export function NavigationSimulator() {
  const [view, setView] = useState<NavigationView>("setup");
  const [setupState, setSetupState] = useState<SetupState>({
    templates: [],
    history: [],
  });
  const [loadingSetup, setLoadingSetup] = useState(true);
  const [selectedSheet, setSelectedSheet] = useState<number | null>(null);
  const [activeSession, setActiveSession] = useState<NavigationSession | null>(null);
  const [currentTaskIndex, setCurrentTaskIndex] = useState(0);
  const [answersByTask, setAnswersByTask] = useState<Record<string, string>>({});
  const [dirtyTaskIds, setDirtyTaskIds] = useState<Set<string>>(new Set());
  const [submitting, setSubmitting] = useState(false);
  const [saving, setSaving] = useState(false);
  const [loadingResult, setLoadingResult] = useState(false);
  const [result, setResult] = useState<NavigationResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [tick, setTick] = useState(Date.now());

  const loadSetup = useCallback(async () => {
    setLoadingSetup(true);
    setError(null);
    try {
      const [templates, history] = await Promise.all([
        listNavigationTemplates(),
        listNavigationHistory(),
      ]);
      setSetupState({ templates, history });
      setSelectedSheet((previous) => {
        if (previous && templates.some((t) => t.sheet_number === previous)) {
          return previous;
        }
        const withTasks = templates.find((t) => t.task_count > 0);
        return withTasks?.sheet_number ?? templates[0]?.sheet_number ?? null;
      });
    } catch {
      setError("Fehler beim Laden der Navigationsaufgaben.");
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

  const currentTask = useMemo(() => {
    if (!activeSession) return null;
    return activeSession.questions[currentTaskIndex] ?? null;
  }, [activeSession, currentTaskIndex]);

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
    () => setupState.templates.find((t) => t.sheet_number === selectedSheet) ?? null,
    [setupState.templates, selectedSheet],
  );

  const canStart = Boolean(selectedTemplate && selectedTemplate.task_count > 0 && !submitting);

  const markTaskClean = (taskId: string) => {
    setDirtyTaskIds((current) => {
      const next = new Set(current);
      next.delete(taskId);
      return next;
    });
  };

  const flushTask = useCallback(
    async (taskId: string) => {
      if (!activeSession || !dirtyTaskIds.has(taskId)) return;
      setSaving(true);
      try {
        const answerText = answersByTask[taskId] ?? "";
        await saveNavigationAnswer(activeSession.session_id, taskId, answerText);
        markTaskClean(taskId);
      } finally {
        setSaving(false);
      }
    },
    [activeSession, answersByTask, dirtyTaskIds],
  );

  const flushAllDirtyAnswers = useCallback(async () => {
    if (!activeSession) return;
    const dirtyIds = Array.from(dirtyTaskIds);
    if (!dirtyIds.length) return;
    setSaving(true);
    try {
      for (const taskId of dirtyIds) {
        const answerText = answersByTask[taskId] ?? "";
        await saveNavigationAnswer(activeSession.session_id, taskId, answerText);
        markTaskClean(taskId);
      }
    } finally {
      setSaving(false);
    }
  }, [activeSession, answersByTask, dirtyTaskIds]);

  const handleStart = async () => {
    if (!selectedSheet) return;
    setError(null);
    setSubmitting(true);
    try {
      const session = await startNavigationSession(selectedSheet);
      setActiveSession(session);
      setCurrentTaskIndex(0);
      const initialAnswers = Object.fromEntries(
        session.questions.map((q) => [q.task_id, q.student_answer]),
      );
      setAnswersByTask(initialAnswers);
      setDirtyTaskIds(new Set());
      setResult(null);
      setView("active");
      setTick(Date.now());
    } catch {
      setError("Navigationsaufgabe konnte nicht gestartet werden.");
    } finally {
      setSubmitting(false);
    }
  };

  const handleAnswerChange = (taskId: string, value: string) => {
    setAnswersByTask((current) => ({ ...current, [taskId]: value }));
    setDirtyTaskIds((current) => {
      const next = new Set(current);
      next.add(taskId);
      return next;
    });
  };

  const handleNavigateTo = async (nextIndex: number) => {
    if (!activeSession || !currentTask) return;
    try {
      await flushTask(currentTask.task_id);
      setCurrentTaskIndex(nextIndex);
    } catch {
      setError("Antwort konnte nicht gespeichert werden.");
    }
  };

  const handleSubmit = async () => {
    if (!activeSession || !currentTask) return;
    setSubmitting(true);
    setError(null);
    try {
      await flushTask(currentTask.task_id);
      await flushAllDirtyAnswers();
      const evaluated = await submitNavigationSession(activeSession.session_id);
      setResult(evaluated);
      setView("result");
      await loadSetup();
    } catch {
      setError("Navigationsaufgabe konnte nicht abgegeben werden.");
    } finally {
      setSubmitting(false);
    }
  };

  const handleOpenHistoryResult = async (sessionId: string) => {
    setLoadingResult(true);
    setError(null);
    try {
      const fetched = await getNavigationResult(sessionId);
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
    setCurrentTaskIndex(0);
    setAnswersByTask({});
    setDirtyTaskIds(new Set());
    await loadSetup();
  };

  return (
    <div className="mx-auto w-full max-w-7xl space-y-6 px-4 py-6 md:px-6 md:py-8">
      <div className="space-y-2">
        <h1 className="text-2xl font-semibold tracking-tight md:text-3xl">Navigationsaufgaben</h1>
        <p className="text-sm text-muted-foreground">
          16–18 Aufgaben pro Bogen, 30 Punkte. Bestanden ab 21 Punkten.
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
              <CardTitle>Aufgabe starten</CardTitle>
            </CardHeader>
            <CardContent className="space-y-5">
              {loadingSetup ? (
                <div className="flex items-center gap-2 text-sm text-muted-foreground">
                  <Loader2 className="size-4 animate-spin" />
                  Lade Navigationsaufgaben...
                </div>
              ) : (
                <>
                  <label className="flex flex-col gap-2 text-sm">
                    <span className="text-muted-foreground">Aufgabenbogen</span>
                    <select
                      value={selectedSheet ?? ""}
                      onChange={(e) => setSelectedSheet(Number(e.target.value))}
                      className="rounded-lg border border-white/15 bg-background/40 px-3 py-2"
                    >
                      {setupState.templates.map((t) => (
                        <option key={t.sheet_number} value={t.sheet_number}>
                          {t.display_name} ({t.task_count} Aufgaben)
                        </option>
                      ))}
                    </select>
                  </label>

                  <div className="rounded-lg border border-white/10 bg-background/40 p-4 text-sm">
                    <div className="flex items-center justify-between gap-3">
                      <span className="text-muted-foreground">Zeitlimit</span>
                      <span className="font-medium">
                        {selectedTemplate?.time_limit_minutes ?? 90} Minuten
                      </span>
                    </div>
                    <div className="mt-2 flex items-center justify-between gap-3">
                      <span className="text-muted-foreground">Aufgaben</span>
                      <span className="font-medium">{selectedTemplate?.task_count ?? 0}</span>
                    </div>
                    <div className="mt-2 flex items-center justify-between gap-3">
                      <span className="text-muted-foreground">Punkte</span>
                      <span className="font-medium">{selectedTemplate?.total_points ?? 30}</span>
                    </div>
                    <div className="mt-2 flex items-center justify-between gap-3">
                      <span className="text-muted-foreground">Bestehen</span>
                      <span className="font-medium">21 / 30 Punkte</span>
                    </div>
                  </div>

                  <div className="flex items-start gap-3 rounded-lg border border-sky-500/30 bg-sky-500/10 p-4 text-sm text-sky-100">
                    <Info className="mt-0.5 size-4 shrink-0" />
                    <p>
                      Halte <strong>Übungskarte 49 (INT 1463)</strong>, Kursdreieck,
                      Anlegedreieck und Zirkel bereit.
                    </p>
                  </div>

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
              <CardTitle>Aufgabenhistorie</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              {!setupState.history.length ? (
                <p className="text-sm text-muted-foreground">
                  Noch keine abgeschlossenen Navigationsaufgaben.
                </p>
              ) : (
                setupState.history.map((item) => (
                  <div
                    key={item.session_id}
                    className="rounded-lg border border-white/10 bg-background/40 p-3"
                  >
                    <div className="flex items-start justify-between gap-2">
                      <div>
                        <p className="text-sm font-medium">
                          Navigationsaufgabe {item.sheet_number}
                        </p>
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

      {view === "active" && activeSession && currentTask && (
        <div className="grid gap-6 lg:grid-cols-[280px_1fr]">
          <Card className="border-white/10 bg-card/70">
            <CardHeader>
              <CardTitle className="text-base">
                Navigationsaufgabe {activeSession.sheet_number}
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="rounded-lg border border-white/10 bg-background/40 p-3">
                <div className="flex items-center justify-between text-sm">
                  <span className="inline-flex items-center gap-2 text-muted-foreground">
                    <Clock3 className="size-4" />
                    Restzeit
                  </span>
                  <span
                    className={`font-semibold ${isTimeOver ? "text-red-200" : "text-foreground"}`}
                  >
                    {formatDuration(remainingSeconds)}
                  </span>
                </div>
                {isTimeOver ? (
                  <p className="mt-2 text-xs text-red-200">
                    Zeit ist abgelaufen. Du kannst weiterschreiben, aber das Ergebnis wird als nicht
                    bestanden markiert.
                  </p>
                ) : null}
              </div>

              <div className="grid grid-cols-5 gap-2">
                {activeSession.questions.map((question, index) => {
                  const hasAnswer = Boolean((answersByTask[question.task_id] ?? "").trim());
                  const isActive = index === currentTaskIndex;
                  return (
                    <button
                      key={question.task_id}
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
                      {question.task_number}
                    </button>
                  );
                })}
              </div>
            </CardContent>
          </Card>

          <Card className="border-white/10 bg-card/70">
            <CardHeader>
              <div className="flex items-center justify-between gap-3">
                <CardTitle className="text-base">
                  Aufgabe {currentTask.task_number} von {activeSession.task_count}
                </CardTitle>
                <span className="rounded-full border border-white/10 bg-background/40 px-2.5 py-0.5 text-xs font-medium">
                  {currentTask.points} {currentTask.points === 1 ? "Punkt" : "Punkte"}
                </span>
              </div>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="rounded-lg border border-sky-500/20 bg-sky-500/5 p-4 text-sm leading-relaxed">
                {currentTask.context}
              </div>

              {currentTask.sub_questions.length > 0 && (
                <ul className="space-y-1.5 text-sm">
                  {currentTask.sub_questions.map((sq, i) => (
                    <li key={i} className="flex items-start gap-2">
                      <span className="shrink-0 rounded bg-white/10 px-1.5 py-0.5 text-xs font-medium">
                        {sq.points} Pt.
                      </span>
                      <span>{sq.text}</span>
                    </li>
                  ))}
                </ul>
              )}

              <label className="flex flex-col gap-2">
                <span className="text-sm text-muted-foreground">Deine Antwort</span>
                <textarea
                  value={answersByTask[currentTask.task_id] ?? ""}
                  onChange={(e) => handleAnswerChange(currentTask.task_id, e.target.value)}
                  className="min-h-24 w-full rounded-lg border border-white/15 bg-background/50 p-3 text-sm outline-none transition-colors focus:border-sky-400"
                  placeholder="Trage hier deine Antwort ein..."
                  disabled={submitting}
                />
              </label>

              <div className="flex flex-wrap items-center justify-between gap-2">
                <div className="text-xs text-muted-foreground">
                  {saving
                    ? "Speichere..."
                    : dirtyTaskIds.has(currentTask.task_id)
                      ? "Nicht gespeichert"
                      : "Gespeichert"}
                </div>
                <div className="flex items-center gap-2">
                  <Button
                    variant="outline"
                    onClick={() => void handleNavigateTo(Math.max(0, currentTaskIndex - 1))}
                    disabled={currentTaskIndex === 0 || saving || submitting}
                  >
                    Zurück
                  </Button>
                  <Button
                    variant="outline"
                    onClick={() =>
                      void handleNavigateTo(
                        Math.min(activeSession.task_count - 1, currentTaskIndex + 1),
                      )
                    }
                    disabled={currentTaskIndex >= activeSession.task_count - 1 || saving || submitting}
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
                      "Aufgabe abgeben"
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
                <Compass className="size-5" />
                Ergebnis Navigationsaufgabe {result.sheet_number}
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid gap-3 md:grid-cols-4">
                <ResultKpi
                  label="Punktzahl"
                  value={`${result.total_score} / ${result.max_score}`}
                />
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
                  Zeit war abgelaufen. Die Session wird unabhängig von der Punktzahl als nicht
                  bestanden gewertet.
                </div>
              ) : null}

              <div className="space-y-3">
                {result.questions.map((question) => (
                  <div
                    key={question.task_id}
                    className="rounded-lg border border-white/10 bg-background/40 p-4"
                  >
                    <div className="mb-3 flex items-start justify-between gap-3">
                      <p className="text-sm font-medium">Aufgabe {question.task_number}</p>
                      <span className="text-sm font-semibold">
                        {question.score} / {question.max_score}
                      </span>
                    </div>

                    <p className="text-sm leading-relaxed text-muted-foreground">
                      {question.context}
                    </p>

                    {question.sub_questions.length > 0 && (
                      <ul className="mt-2 space-y-1 text-sm text-muted-foreground">
                        {question.sub_questions.map((sq, i) => (
                          <li key={i} className="flex items-start gap-1.5">
                            <span>•</span>
                            <span>{sq}</span>
                          </li>
                        ))}
                      </ul>
                    )}

                    <div className="mt-3">
                      <p className="text-xs text-muted-foreground">Deine Antwort</p>
                      <p className="mt-1 whitespace-pre-wrap text-sm">
                        {question.student_answer || "(Keine Antwort)"}
                      </p>
                    </div>

                    <div className="mt-3 rounded-lg border border-emerald-500/30 bg-emerald-500/10 p-3">
                      <p className="text-xs font-medium text-emerald-200">Musterlösung</p>
                      <div className="mt-1.5 text-sm leading-relaxed text-emerald-100 [&_strong]:text-emerald-50 [&_ul]:mt-1 [&_ul]:list-disc [&_ul]:pl-4 [&_ol]:mt-1 [&_ol]:list-decimal [&_ol]:pl-4 [&_li]:mt-0.5 [&_p+p]:mt-2">
                        <Markdown>{question.solution_text}</Markdown>
                      </div>
                    </div>

                    <div className="mt-3 flex items-center gap-2 text-sm">
                      {question.is_correct ? (
                        <CheckCircle2 className="size-4 text-emerald-300" />
                      ) : (
                        <XCircle className="size-4 text-red-300" />
                      )}
                      <span>{question.feedback}</span>
                    </div>
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
