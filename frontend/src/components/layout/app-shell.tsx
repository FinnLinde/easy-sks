"use client";

import { usePathname } from "next/navigation";
import { AuthGuard } from "@/components/auth/auth-guard";
import { ProfileCompletionGate } from "@/components/auth/profile-completion-gate";
import { LegalFooter } from "@/components/legal/legal-footer";
import { MobileHeader } from "@/components/layout/mobile-header";
import { MobileBottomNav } from "@/components/layout/mobile-bottom-nav";
import { Sidenav } from "@/components/layout/sidenav";

export function AppShell({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const isAuthCallback = pathname.startsWith("/auth/callback");
  const isLegalPage = pathname.startsWith("/legal");
  const isProfileOnboarding = pathname.startsWith("/onboarding/profile");

  if (isAuthCallback) {
    return <main className="min-h-screen min-h-[100dvh]">{children}</main>;
  }

  if (isLegalPage) {
    return (
      <div className="flex min-h-screen min-h-[100dvh] flex-col">
        <main className="flex-1">{children}</main>
        <LegalFooter />
      </div>
    );
  }

  if (isProfileOnboarding) {
    return (
      <AuthGuard description="Melde dich an, um dein Profil zu vervollständigen.">
        <ProfileCompletionGate>
          <div className="flex min-h-screen min-h-[100dvh] flex-col">
            <main className="flex-1">{children}</main>
            <LegalFooter />
          </div>
        </ProfileCompletionGate>
      </AuthGuard>
    );
  }

  return (
    <AuthGuard description="Melde dich an, um mit deinem persönlichen Lernbereich zu starten.">
      <ProfileCompletionGate>
        <div className="flex min-h-screen min-h-[100dvh]">
          <Sidenav />
          <div className="flex flex-1 flex-col">
            <MobileHeader />
            <main className="flex-1 overflow-auto pb-[calc(5rem+env(safe-area-inset-bottom))] md:pb-0">
              {children}
            </main>
            <LegalFooter className="pb-[calc(5rem+env(safe-area-inset-bottom))] md:pb-4" />
            <MobileBottomNav />
          </div>
        </div>
      </ProfileCompletionGate>
    </AuthGuard>
  );
}
