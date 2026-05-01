"use client";

import Link from "next/link";
import { CheckCircle2, Target, TrendingUp } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";

type StudyMode = "due" | "practice";

export function SessionComplete({
  mode,
  cardsCompleted,
  onStartNew,
}: {
  mode: StudyMode;
  cardsCompleted: number;
  onStartNew: () => void;
}) {
  return (
    <Card className="w-full max-w-3xl border-white/10 bg-card/80 shadow-xl">
      <CardContent className="space-y-6 p-8 text-center">
        <div className="mx-auto inline-flex rounded-full bg-emerald-500/20 p-4 text-emerald-300">
          <CheckCircle2 className="size-10" />
        </div>

        <div>
          <h2 className="text-2xl font-semibold tracking-tight">Session abgeschlossen</h2>
          <p className="mt-2 text-sm text-muted-foreground">
            Du hast {cardsCompleted} {cardsCompleted === 1 ? "Karte" : "Karten"} bearbeitet.
          </p>
        </div>

        <div className="grid gap-3 md:grid-cols-2">
          <div className="rounded-xl border border-sky-500/20 bg-sky-500/10 p-4">
            <div className="mb-2 inline-flex items-center gap-2 text-xs text-sky-200">
              <Target className="size-4" />
              Modus
            </div>
            <p className="font-medium">{mode === "due" ? "Wiederholung" : "Practice"}</p>
          </div>
          <div className="rounded-xl border border-emerald-500/20 bg-emerald-500/10 p-4">
            <div className="mb-2 inline-flex items-center gap-2 text-xs text-emerald-200">
              <TrendingUp className="size-4" />
              Fortschritt
            </div>
            <p className="font-medium">{cardsCompleted} abgeschlossen</p>
          </div>
        </div>

        <div className="flex flex-col gap-3 sm:flex-row">
          <Button variant="outline" className="flex-1" onClick={onStartNew}>
            Neue Session
          </Button>
          <Button asChild className="flex-1">
            <Link href="/">Zum Dashboard</Link>
          </Button>
        </div>
      </CardContent>
    </Card>
  );
}
