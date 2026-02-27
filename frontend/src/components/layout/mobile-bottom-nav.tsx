"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useAuth } from "@/auth/auth-provider";
import { cn } from "@/lib/utils";
import { navItems } from "./nav-config";

export function MobileBottomNav() {
  const pathname = usePathname();
  const { status, hasRole } = useAuth();

  if (status !== "authenticated") {
    return null;
  }

  return (
    <nav
      className="fixed inset-x-0 bottom-0 z-40 border-t border-sidebar-border/80 bg-sidebar/95 backdrop-blur md:hidden"
      aria-label="Mobile Navigation"
    >
      <div className="flex h-16 px-1 pb-[env(safe-area-inset-bottom)]">
        {navItems.map(({ href, label, icon: Icon, requiredRole }) => {
          const isActive = href === "/" ? pathname === "/" : pathname.startsWith(href);
          const isAllowed = !requiredRole || hasRole(requiredRole);

          if (!isAllowed) {
            return (
              <span
                key={href}
                className="flex flex-1 flex-col items-center justify-center gap-1 text-xs text-sidebar-foreground/40"
                aria-disabled="true"
              >
                <Icon className="size-4" />
                <span>{label}</span>
              </span>
            );
          }

          return (
            <Link
              key={href}
              href={href}
              className={cn(
                "flex flex-1 flex-col items-center justify-center gap-1 rounded-md text-xs transition-colors",
                isActive
                  ? "bg-sidebar-accent text-sidebar-accent-foreground"
                  : "text-sidebar-foreground/80 hover:bg-sidebar-accent/50"
              )}
            >
              <Icon className="size-4" />
              <span>{label}</span>
            </Link>
          );
        })}
      </div>
    </nav>
  );
}
