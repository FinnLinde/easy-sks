"use client";

import { useEffect, useState } from "react";
import { AlertTriangle, Loader2, Sailboat } from "lucide-react";
import { useRouter, useSearchParams } from "next/navigation";
import { useAuth } from "@/auth/auth-provider";

export default function AuthCallbackPage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const { completeLogin } = useAuth();
  const [error, setError] = useState<string | null>(null);
  const code = searchParams.get("code");
  const state = searchParams.get("state");
  const providerError = searchParams.get("error");

  const immediateError =
    providerError
      ? `Login fehlgeschlagen: ${providerError}`
      : !code
        ? "Kein Authorization Code in der Callback-URL gefunden."
        : null;

  useEffect(() => {
    if (!code || immediateError) {
      return;
    }

    void (async () => {
      try {
        const result = await completeLogin(code, state);
        router.replace(result.returnTo || "/study");
      } catch (err) {
        setError(
          err instanceof Error
            ? err.message
            : "Login konnte nicht abgeschlossen werden."
        );
      }
    })();
  }, [code, completeLogin, immediateError, router, state]);

  return (
    <div className="relative flex min-h-screen min-h-[100dvh] w-full items-center justify-center overflow-hidden bg-background px-6 py-10">
      <div className="absolute inset-0 bg-[radial-gradient(circle_at_15%_15%,rgba(14,165,233,0.2),transparent_40%),radial-gradient(circle_at_85%_20%,rgba(34,197,94,0.12),transparent_38%),radial-gradient(circle_at_50%_115%,rgba(251,191,36,0.12),transparent_45%)]" />

      <div className="relative w-full max-w-xl rounded-3xl border border-white/10 bg-card/80 p-8 text-center shadow-2xl backdrop-blur-xl">
        <div className="mx-auto mb-4 flex size-12 items-center justify-center rounded-2xl border border-white/10 bg-white/5">
          {immediateError || error ? (
            <AlertTriangle className="size-6 text-amber-300" />
          ) : (
            <Sailboat className="size-6 text-sky-300" />
          )}
        </div>

        {immediateError || error ? (
          <>
            <h1 className="text-xl font-semibold">Login fehlgeschlagen</h1>
            <p className="mt-2 text-sm text-muted-foreground">
              {immediateError ?? error}
            </p>
            <p className="mt-6 text-xs text-muted-foreground">
              Prüfe Cognito-Domain, Client-ID und Callback-URL-Konfiguration.
            </p>
          </>
        ) : (
          <>
            <h1 className="text-xl font-semibold">Login wird abgeschlossen...</h1>
            <p className="mt-2 text-sm text-muted-foreground">
              Bitte einen Moment warten.
            </p>
            <div className="mt-6 flex items-center justify-center gap-2 text-sm text-muted-foreground">
              <Loader2 className="size-4 animate-spin" />
              Cognito-Session wird übernommen
            </div>
          </>
        )}
      </div>
    </div>
  );
}
