"use client";

import type { ReactNode } from "react";
import { Lock, Sailboat, Sparkles, Trophy } from "lucide-react";
import { usePathname } from "next/navigation";
import { useAuth } from "@/auth/auth-provider";
import { Button } from "@/components/ui/button";

export function AuthGuard({
  children,
  description = "Bitte melde dich an, um diesen Bereich zu nutzen.",
}: {
  children: ReactNode;
  description?: string;
}) {
  const { status, login } = useAuth();
  const pathname = usePathname();

  if (status === "loading") {
    return (
      <div className="relative flex min-h-screen min-h-[100dvh] w-full items-center justify-center overflow-hidden bg-background px-6 py-10">
        <div className="absolute inset-0 bg-[radial-gradient(circle_at_20%_20%,rgba(56,189,248,0.18),transparent_45%),radial-gradient(circle_at_80%_15%,rgba(34,197,94,0.14),transparent_40%),radial-gradient(circle_at_50%_100%,rgba(245,158,11,0.12),transparent_45%)]" />
        <div className="relative w-full max-w-lg rounded-3xl border border-white/10 bg-card/80 p-8 text-center backdrop-blur">
          <div className="mx-auto mb-4 flex size-12 items-center justify-center rounded-2xl border border-white/10 bg-white/5">
            <Sailboat className="size-6" />
          </div>
          <p className="text-sm text-muted-foreground">Sitzung wird geladen...</p>
        </div>
      </div>
    );
  }

  if (status !== "authenticated") {
    return (
      <div className="relative min-h-screen min-h-[100dvh] w-full overflow-hidden bg-background">
        <div className="absolute inset-0 bg-[radial-gradient(circle_at_10%_10%,rgba(14,165,233,0.18),transparent_40%),radial-gradient(circle_at_85%_15%,rgba(34,197,94,0.12),transparent_38%),radial-gradient(circle_at_50%_120%,rgba(251,191,36,0.12),transparent_42%)]" />
        <div className="absolute inset-0 opacity-20 [background-image:linear-gradient(to_right,rgba(255,255,255,0.06)_1px,transparent_1px),linear-gradient(to_bottom,rgba(255,255,255,0.06)_1px,transparent_1px)] [background-size:32px_32px]" />

        <div className="relative mx-auto flex min-h-screen min-h-[100dvh] w-full max-w-5xl items-center px-6 py-10">
          <div className="w-full">
            <section className="rounded-3xl border border-white/10 bg-card/70 p-7 shadow-2xl backdrop-blur-xl sm:p-10">
              <div className="inline-flex items-center gap-2 rounded-full border border-white/10 bg-white/5 px-3 py-1 text-xs font-medium text-muted-foreground">
                <Sailboat className="size-3.5" />
                Easy SKS Lernplattform
              </div>

              <h1 className="mt-5 text-3xl font-semibold tracking-tight sm:text-4xl">
                SKS-Prüfung vorbereiten
                <span className="mt-1 block text-sky-300">strukturiert statt chaotisch</span>
              </h1>

              <p className="mt-4 max-w-xl text-sm leading-6 text-muted-foreground sm:text-base">
                {description}
              </p>

              <div className="mt-7 flex flex-col gap-3 sm:flex-row">
                <Button
                  className="h-11 rounded-xl px-5 text-sm font-semibold"
                  onClick={() => void login(pathname || "/study")}
                >
                  <Lock className="size-4" />
                  Login
                </Button>
              </div>

              <div className="mt-8 grid gap-3 sm:grid-cols-3">
                <div className="rounded-2xl border border-white/10 bg-white/5 p-4">
                  <Sparkles className="mb-2 size-4 text-sky-300" />
                  <p className="text-sm font-medium">Adaptive Wiederholung</p>
                  <p className="mt-1 text-xs leading-5 text-muted-foreground">
                    Intelligente Wiederholungen im richtigen Moment.
                  </p>
                </div>
                <div className="rounded-2xl border border-white/10 bg-white/5 p-4">
                  <Trophy className="mb-2 size-4 text-amber-300" />
                  <p className="text-sm font-medium">Prüfungsfokus</p>
                  <p className="mt-1 text-xs leading-5 text-muted-foreground">
                    Lernen nach Themen und Prioritäten.
                  </p>
                </div>
                <div className="rounded-2xl border border-white/10 bg-white/5 p-4">
                  <Lock className="mb-2 size-4 text-emerald-300" />
                  <p className="text-sm font-medium">Dein Lernstand</p>
                  <p className="mt-1 text-xs leading-5 text-muted-foreground">
                    Dein Fortschritt wird automatisch gespeichert.
                  </p>
                </div>
              </div>
            </section>
          </div>
        </div>
      </div>
    );
  }

  return <>{children}</>;
}
