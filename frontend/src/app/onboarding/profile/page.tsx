"use client";

import { useEffect, useMemo, useState } from "react";
import { AlertTriangle, RefreshCw, UserRoundPen } from "lucide-react";
import { useRouter, useSearchParams } from "next/navigation";
import { ProfileForm } from "@/components/profile/profile-form";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { getMe, type MeSummary } from "@/services/user/user-service";

function resolveReturnTo(path: string | null): string {
  if (!path || !path.startsWith("/") || path.startsWith("/onboarding/profile")) {
    return "/study";
  }
  return path;
}

export default function ProfileOnboardingPage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const returnTo = useMemo(
    () => resolveReturnTo(searchParams.get("returnTo")),
    [searchParams]
  );

  const [summary, setSummary] = useState<MeSummary | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  async function loadSummary() {
    setLoading(true);
    setError(null);
    try {
      const data = await getMe();
      setSummary(data);
    } catch {
      setError("Profilstatus konnte nicht geladen werden.");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    void loadSummary();
  }, []);

  return (
    <div className="relative flex min-h-screen min-h-[100dvh] w-full items-center justify-center overflow-hidden bg-background px-4 py-8 md:px-6">
      <div className="absolute inset-0 bg-[radial-gradient(circle_at_18%_12%,rgba(14,165,233,0.2),transparent_40%),radial-gradient(circle_at_83%_18%,rgba(34,197,94,0.12),transparent_40%),radial-gradient(circle_at_50%_115%,rgba(251,191,36,0.12),transparent_45%)]" />
      <div className="relative w-full max-w-lg">
        <Card className="border-white/10 bg-card/80 shadow-2xl backdrop-blur-xl">
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-xl">
              <UserRoundPen className="size-5 text-sky-300" />
              Profil vervollständigen
            </CardTitle>
            <p className="text-sm text-muted-foreground">
              Bitte ergänze deinen vollen Namen und deine Mobilnummer, bevor du
              den Lernbereich nutzt.
            </p>
          </CardHeader>
          <CardContent>
            {loading ? (
              <div className="space-y-3">
                <Skeleton className="h-10 w-full" />
                <Skeleton className="h-10 w-full" />
                <Skeleton className="h-10 w-40" />
              </div>
            ) : error ? (
              <div className="space-y-4 rounded-lg border border-red-500/30 bg-red-500/10 p-4">
                <p className="flex items-center gap-2 text-sm text-destructive">
                  <AlertTriangle className="size-4" />
                  {error}
                </p>
                <Button
                  type="button"
                  variant="outline"
                  className="gap-2"
                  onClick={() => void loadSummary()}
                >
                  <RefreshCw className="size-4" />
                  Erneut versuchen
                </Button>
              </div>
            ) : (
              <ProfileForm
                initialFullName={summary?.full_name}
                initialMobileNumber={summary?.mobile_number}
                submitLabel="Profil abschließen"
                onSaved={(updated) => {
                  setSummary(updated);
                  if (updated.profile_complete) {
                    router.replace(returnTo);
                  }
                }}
              />
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
