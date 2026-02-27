"use client";

import { BookOpen, Calendar, Target, X } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";

export function WelcomeOverlay({
  onDismiss,
}: {
  onDismiss: () => void;
}) {
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 p-4 backdrop-blur-sm">
      <Card className="w-full max-w-2xl border-white/10 bg-card/95 shadow-2xl">
        <CardContent className="space-y-6 p-6 md:p-8">
          <div className="flex items-start justify-between gap-4">
            <div>
              <h2 className="text-2xl font-semibold tracking-tight">Willkommen im Lernbereich</h2>
              <p className="mt-2 text-sm text-muted-foreground">
                Kurze Sessions, klare Priorisierung und regelmaessige Wiederholung.
              </p>
            </div>
            <Button variant="ghost" size="icon" onClick={onDismiss} aria-label="Overlay schliessen">
              <X className="size-4" />
            </Button>
          </div>

          <div className="grid gap-3 md:grid-cols-3">
            <div className="rounded-xl border border-sky-500/20 bg-sky-500/10 p-4">
              <BookOpen className="mb-2 size-4 text-sky-300" />
              <p className="text-sm font-medium">Setup first</p>
              <p className="mt-1 text-xs text-muted-foreground">Waehle Modus und Thema vor Sessionstart.</p>
            </div>
            <div className="rounded-xl border border-emerald-500/20 bg-emerald-500/10 p-4">
              <Target className="mb-2 size-4 text-emerald-300" />
              <p className="text-sm font-medium">Priorisiert lernen</p>
              <p className="mt-1 text-xs text-muted-foreground">Wiederholung zeigt zuerst faellige Karten.</p>
            </div>
            <div className="rounded-xl border border-amber-500/20 bg-amber-500/10 p-4">
              <Calendar className="mb-2 size-4 text-amber-300" />
              <p className="text-sm font-medium">Konstanz</p>
              <p className="mt-1 text-xs text-muted-foreground">Taegliche Sessions halten den Lernfluss stabil.</p>
            </div>
          </div>

          <div className="flex justify-end">
            <Button onClick={onDismiss}>Verstanden</Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
