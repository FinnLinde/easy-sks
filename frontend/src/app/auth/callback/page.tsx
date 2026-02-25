"use client";

import { useEffect, useState } from "react";
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
    <div className="mx-auto flex min-h-[60vh] w-full max-w-xl items-center justify-center px-6">
      <div className="w-full rounded-xl border p-8 text-center">
        {immediateError || error ? (
          <>
            <h1 className="text-xl font-semibold">Login fehlgeschlagen</h1>
            <p className="mt-2 text-sm text-muted-foreground">
              {immediateError ?? error}
            </p>
          </>
        ) : (
          <>
            <h1 className="text-xl font-semibold">Login wird abgeschlossen...</h1>
            <p className="mt-2 text-sm text-muted-foreground">
              Bitte einen Moment warten.
            </p>
          </>
        )}
      </div>
    </div>
  );
}
