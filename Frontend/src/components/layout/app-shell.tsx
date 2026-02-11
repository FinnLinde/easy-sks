import { MobileHeader } from "@/components/layout/mobile-header";
import { Sidenav } from "@/components/layout/sidenav";

export function AppShell({ children }: { children: React.ReactNode }) {
  return (
    <div className="flex min-h-screen min-h-[100dvh]">
      <Sidenav />
      <div className="flex flex-1 flex-col">
        <MobileHeader />
        <main className="flex-1 overflow-auto">{children}</main>
      </div>
    </div>
  );
}
