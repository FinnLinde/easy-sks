"use client";

import { Sailboat } from "lucide-react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { useAuth } from "@/auth/auth-provider";
import { cn } from "@/lib/utils";
import { AuthStatusActions } from "@/components/auth/auth-status-actions";
import { navItems } from "./nav-config";

export function Sidenav() {
  const pathname = usePathname();
  const { status, hasRole } = useAuth();

  return (
    <aside className="hidden w-60 shrink-0 border-r border-sidebar-border bg-sidebar text-sidebar-foreground md:block">
      <div className="flex h-full flex-col p-4">
        <div className="mb-6 flex items-center gap-2">
          <Sailboat className="size-5 shrink-0" />
          <h1 className="text-lg font-bold">Easy SKS</h1>
        </div>
        <nav className="flex flex-col gap-1">
          {navItems.map(({ href, label, icon: Icon, requiredRole }) => {
            const isActive =
              href === "/"
                ? pathname === "/"
                : pathname.startsWith(href);
            const isAllowed =
              status === "authenticated" &&
              (!requiredRole || hasRole(requiredRole));

            return (
              <div key={href}>
                {isAllowed ? (
                  <Link
                    href={href}
                    className={cn(
                      "flex items-center gap-3 rounded-md px-3 py-2 text-sm font-medium transition-colors",
                      isActive
                        ? "bg-sidebar-accent text-sidebar-accent-foreground"
                        : "hover:bg-sidebar-accent/50 hover:text-sidebar-accent-foreground"
                    )}
                  >
                    <Icon className="size-4 shrink-0" />
                    {label}
                  </Link>
                ) : (
                  <span
                    aria-disabled="true"
                    className="flex cursor-not-allowed items-center gap-3 rounded-md px-3 py-2 text-sm font-medium opacity-50"
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
        <div className="mt-auto pt-4">
          <AuthStatusActions />
        </div>
      </div>
    </aside>
  );
}
