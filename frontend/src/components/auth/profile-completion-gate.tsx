"use client";

import { useEffect, useState, type ReactNode } from "react";
import { Loader2, UserRoundPen } from "lucide-react";
import { usePathname, useRouter, useSearchParams } from "next/navigation";
import { useAuth } from "@/auth/auth-provider";
import { getMe } from "@/services/user/user-service";

const PROFILE_ONBOARDING_PATH = "/onboarding/profile";

function resolveReturnTo(path: string | null): string {
  if (!path || !path.startsWith("/")) {
    return "/study";
  }
  if (path.startsWith(PROFILE_ONBOARDING_PATH)) {
    return "/study";
  }
  return path;
}

export function ProfileCompletionGate({ children }: { children: ReactNode }) {
  const { status } = useAuth();
  const router = useRouter();
  const pathname = usePathname();
  const searchParams = useSearchParams();
  const [checking, setChecking] = useState(true);

  useEffect(() => {
    if (status !== "authenticated") {
      setChecking(false);
      return;
    }

    const isOnboardingRoute = pathname.startsWith(PROFILE_ONBOARDING_PATH);
    let isCancelled = false;

    async function runGateCheck() {
      setChecking(true);
      try {
        const summary = await getMe();
        if (isCancelled) {
          return;
        }

        if (!summary.profile_complete && !isOnboardingRoute) {
          const currentSearch = searchParams.toString();
          const returnTo = currentSearch
            ? `${pathname}?${currentSearch}`
            : pathname;
          router.replace(
            `${PROFILE_ONBOARDING_PATH}?returnTo=${encodeURIComponent(returnTo)}`
          );
          return;
        }

        if (summary.profile_complete && isOnboardingRoute) {
          const returnTo = resolveReturnTo(searchParams.get("returnTo"));
          router.replace(returnTo);
        }
      } catch {
        // Allow app usage when profile status cannot be fetched.
      } finally {
        if (!isCancelled) {
          setChecking(false);
        }
      }
    }

    void runGateCheck();

    return () => {
      isCancelled = true;
    };
  }, [pathname, router, searchParams, status]);

  if (status === "authenticated" && checking) {
    return (
      <div className="flex min-h-screen min-h-[100dvh] w-full items-center justify-center px-6 py-10">
        <div className="rounded-2xl border border-white/10 bg-card/80 px-6 py-5 text-center shadow-xl">
          <div className="mb-2 flex items-center justify-center gap-2 text-sm text-muted-foreground">
            <UserRoundPen className="size-4 text-sky-300" />
            Profil wird geprüft
          </div>
          <div className="flex items-center justify-center gap-2 text-sm text-muted-foreground">
            <Loader2 className="size-4 animate-spin" />
            Bitte einen Moment warten...
          </div>
        </div>
      </div>
    );
  }

  return <>{children}</>;
}
