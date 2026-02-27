"use client";

import { Menu, Sailboat, X } from "lucide-react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { useEffect, useState } from "react";
import { useAuth } from "@/auth/auth-provider";
import { cn } from "@/lib/utils";
import { AuthStatusActions } from "@/components/auth/auth-status-actions";
import { navItems } from "./nav-config";

export function MobileHeader() {
  const [open, setOpen] = useState(false);
  const pathname = usePathname();
  const { status, hasRole } = useAuth();

  const close = () => setOpen(false);

  useEffect(() => {
    document.body.style.overflow = open ? "hidden" : "";
    return () => {
      document.body.style.overflow = "";
    };
  }, [open]);

  return (
    <>
      <header className="sticky top-0 z-40 flex h-14 items-center justify-between gap-2 border-b border-sidebar-border bg-sidebar px-4 pt-[env(safe-area-inset-top)] md:hidden">
        <button
          type="button"
          onClick={() => setOpen(true)}
          className="-ml-2 flex size-10 items-center justify-center rounded-md text-sidebar-foreground hover:bg-sidebar-accent/50"
          aria-label="Menü öffnen"
        >
          <Menu className="size-5" />
        </button>
        <div className="flex flex-1 items-center justify-center gap-2">
          <Sailboat className="size-5 shrink-0" />
          <h1 className="text-lg font-bold text-sidebar-foreground">
            Easy SKS
          </h1>
        </div>
        <AuthStatusActions compact />
      </header>

      {/* Overlay */}
      <div
        role="button"
        tabIndex={0}
        onClick={close}
        onKeyDown={(e) => e.key === "Escape" && close()}
        className={cn(
          "fixed inset-0 z-50 bg-black/50 md:hidden",
          "transition-opacity duration-200",
          open ? "opacity-100" : "pointer-events-none opacity-0"
        )}
        aria-hidden={!open}
      />

      {/* Drawer */}
      <aside
        className={cn(
          "fixed inset-y-0 left-0 z-50 w-72 border-r border-sidebar-border bg-sidebar pt-[env(safe-area-inset-top)] md:hidden",
          "transition-transform duration-200 ease-out",
          open ? "translate-x-0" : "-translate-x-full"
        )}
        aria-label="Navigation"
        aria-hidden={!open}
      >
        <div className="flex h-14 items-center justify-between border-b border-sidebar-border px-4">
          <span className="text-lg font-bold text-sidebar-foreground">
            Menü
          </span>
          <button
            type="button"
            onClick={close}
            className="-mr-2 flex size-10 items-center justify-center rounded-md text-sidebar-foreground hover:bg-sidebar-accent/50"
            aria-label="Menü schließen"
          >
            <X className="size-5" />
          </button>
        </div>
        <nav className="flex flex-col gap-1 p-4">
          {navItems.map(({ href, label, icon: Icon, requiredRole }) => {
            const isActive =
              href === "/" ? pathname === "/" : pathname.startsWith(href);
            const isAllowed =
              status === "authenticated" &&
              (!requiredRole || hasRole(requiredRole));
            return (
              <div key={href}>
                {isAllowed ? (
                  <Link
                    href={href}
                    onClick={close}
                    className={cn(
                      "flex items-center gap-3 rounded-md px-3 py-2 text-sm font-medium transition-colors",
                      isActive
                        ? "bg-sidebar-accent text-sidebar-accent-foreground"
                        : "text-sidebar-foreground hover:bg-sidebar-accent/50"
                    )}
                  >
                    <Icon className="size-4 shrink-0" />
                    {label}
                  </Link>
                ) : (
                  <span
                    aria-disabled="true"
                    className="flex cursor-not-allowed items-center gap-3 rounded-md px-3 py-2 text-sm font-medium text-sidebar-foreground opacity-50"
                    title="Kein Zugriff mit aktueller Rolle"
                  >
                    <Icon className="size-4 shrink-0" />
                    {label}
                  </span>
                )}
              </div>
            );
          })}
        </nav>
        <div className="border-t border-sidebar-border p-4">
          <AuthStatusActions />
        </div>
      </aside>
    </>
  );
}
