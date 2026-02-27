"use client";

import { useEffect, useMemo, useState } from "react";
import { ArrowRight, BookOpen, Calendar, Target, TrendingUp } from "lucide-react";
import Link from "next/link";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { listTopics, type Topic } from "@/services/topic/topic-service";
import { getDueCards, getPracticeCards, type StudyCard, type TopicValue } from "@/services/study/study-service";

type DashboardState = {
  dueCards: StudyCard[];
  practiceCards: StudyCard[];
  topics: Topic[];
  dueByTopic: Record<string, number>;
};

function dayKey(date: Date) {
  return `${date.getUTCFullYear()}-${date.getUTCMonth()}-${date.getUTCDate()}`;
}

export function DashboardOverview() {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [state, setState] = useState<DashboardState>({
    dueCards: [],
    practiceCards: [],
    topics: [],
    dueByTopic: {},
  });

  useEffect(() => {
    let cancelled = false;

    async function load() {
      setLoading(true);
      setError(null);

      try {
        const [topics, dueCards, practiceCards] = await Promise.all([
          listTopics(),
          getDueCards(),
          getPracticeCards(),
        ]);

        const dueCounts = await Promise.all(
          topics.map(async (topic) => {
            const cards = await getDueCards(topic.value as TopicValue);
            return [topic.value, cards.length] as const;
          })
        );

        if (cancelled) return;

        setState({
          dueCards,
          practiceCards,
          topics,
          dueByTopic: Object.fromEntries(dueCounts),
        });
      } catch {
        if (!cancelled) {
          setError("Fehler beim Laden des Dashboards.");
        }
      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    }

    void load();

    return () => {
      cancelled = true;
    };
  }, []);

  const stats = useMemo(() => {
    const dueNow = state.dueCards.length;
    const reviewedToday = state.practiceCards.filter((entry) => {
      if (!entry.scheduling_info.last_review) return false;
      return dayKey(new Date(entry.scheduling_info.last_review)) === dayKey(new Date());
    }).length;

    const recommendedTopic = state.topics
      .map((topic) => ({ topic, count: state.dueByTopic[topic.value] ?? 0 }))
      .sort((a, b) => b.count - a.count)[0];

    return {
      dueNow,
      reviewedToday,
      availableCards: state.practiceCards.length,
      recommendedTopic: recommendedTopic?.count ? recommendedTopic : null,
    };
  }, [state]);

  if (loading) {
    return (
      <div className="w-full max-w-6xl space-y-6 px-4 py-6 md:px-6 md:py-8">
        <Skeleton className="h-8 w-52" />
        <div className="grid gap-4 md:grid-cols-3">
          <Skeleton className="h-32 w-full" />
          <Skeleton className="h-32 w-full" />
          <Skeleton className="h-32 w-full" />
        </div>
        <Skeleton className="h-64 w-full" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="w-full max-w-4xl px-4 py-10">
        <Card className="border-white/10 bg-card/70">
          <CardContent className="space-y-4 p-8 text-center">
            <p className="text-destructive">{error}</p>
            <Button onClick={() => window.location.reload()}>Neu laden</Button>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="w-full max-w-6xl space-y-6 px-4 py-6 md:px-6 md:py-8">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight md:text-3xl">Dashboard</h1>
        <p className="mt-1 text-sm text-muted-foreground">Dein Lernstatus im dunklen Fokus-Layout.</p>
      </div>

      <div className="grid gap-4 md:grid-cols-3">
        <Card className="border-sky-500/30 bg-gradient-to-br from-sky-500/15 via-card to-card">
          <CardHeader className="pb-3">
            <CardTitle className="text-sm text-muted-foreground">Fällig jetzt</CardTitle>
          </CardHeader>
          <CardContent className="flex items-end justify-between">
            <p className="text-3xl font-bold">{stats.dueNow}</p>
            <BookOpen className="size-5 text-sky-300" />
          </CardContent>
        </Card>

        <Card className="border-emerald-500/30 bg-gradient-to-br from-emerald-500/15 via-card to-card">
          <CardHeader className="pb-3">
            <CardTitle className="text-sm text-muted-foreground">Heute wiederholt</CardTitle>
          </CardHeader>
          <CardContent className="flex items-end justify-between">
            <p className="text-3xl font-bold">{stats.reviewedToday}</p>
            <TrendingUp className="size-5 text-emerald-300" />
          </CardContent>
        </Card>

        <Card className="border-amber-500/30 bg-gradient-to-br from-amber-500/15 via-card to-card">
          <CardHeader className="pb-3">
            <CardTitle className="text-sm text-muted-foreground">Karten gesamt</CardTitle>
          </CardHeader>
          <CardContent className="flex items-end justify-between">
            <p className="text-3xl font-bold">{stats.availableCards}</p>
            <Calendar className="size-5 text-amber-300" />
          </CardContent>
        </Card>
      </div>

      <Card className="border-white/10 bg-card/70">
        <CardHeader className="flex flex-row items-center justify-between gap-3">
          <CardTitle className="text-base">Themen mit fälligen Karten</CardTitle>
          <Link href="/study">
            <Button size="sm" className="gap-1">
              Lernen starten
              <ArrowRight className="size-4" />
            </Button>
          </Link>
        </CardHeader>
        <CardContent className="space-y-3">
          {state.topics.map((topic) => {
            const count = state.dueByTopic[topic.value] ?? 0;
            const recommended = stats.recommendedTopic?.topic.value === topic.value;
            return (
              <div key={topic.value} className="rounded-lg border border-white/10 bg-background/30 p-3">
                <div className="mb-2 flex items-center justify-between gap-2">
                  <span className="text-sm font-medium">{topic.label}</span>
                  <div className="flex items-center gap-2">
                    {recommended ? (
                      <span className="rounded-full bg-sky-500/20 px-2 py-0.5 text-xs text-sky-200">Empfohlen</span>
                    ) : null}
                    <span className="text-xs text-muted-foreground">{count} fällig</span>
                  </div>
                </div>
                <div className="h-2 overflow-hidden rounded-full bg-white/10">
                  <div
                    className="h-full rounded-full bg-sky-400"
                    style={{
                      width: `${stats.dueNow > 0 ? (count / stats.dueNow) * 100 : 0}%`,
                    }}
                  />
                </div>
              </div>
            );
          })}

          {stats.dueNow === 0 ? (
            <div className="rounded-lg border border-emerald-500/30 bg-emerald-500/10 p-4 text-sm text-emerald-200">
              Keine Karten sind aktuell fällig. Du kannst im Lernbereich den Practice-Modus nutzen.
            </div>
          ) : null}
        </CardContent>
      </Card>

      {stats.recommendedTopic ? (
        <Card className="border-sky-500/30 bg-sky-500/10">
          <CardContent className="flex flex-col items-start justify-between gap-3 p-6 md:flex-row md:items-center">
            <div>
              <p className="text-xs uppercase tracking-wide text-sky-200">Empfohlenes Thema</p>
              <p className="mt-1 text-lg font-semibold">{stats.recommendedTopic.topic.label}</p>
              <p className="text-sm text-muted-foreground">
                {stats.recommendedTopic.count} Karten warten auf Wiederholung.
              </p>
            </div>
            <Link href="/study">
              <Button className="gap-2">
                <Target className="size-4" />
                Direkt lernen
              </Button>
            </Link>
          </CardContent>
        </Card>
      ) : null}
    </div>
  );
}
