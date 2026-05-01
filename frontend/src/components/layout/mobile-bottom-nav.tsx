"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { cn } from "@/lib/utils";
import { navItems } from "./nav-config";

const MOBILE_CORE_ROUTES = new Set(["/", "/study", "/exams", "/settings"]);

export function MobileBottomNav() {
  const pathname = usePathname();
  const mobileNavItems = navItems.filter((item) => MOBILE_CORE_ROUTES.has(item.href));

  return (
    <nav
      className="fixed inset-x-0 bottom-0 z-40 border-t border-sidebar-border/80 bg-sidebar/95 backdrop-blur md:hidden"
      aria-label="Mobile Navigation"
    >
      <div className="flex h-16 px-1 pb-[env(safe-area-inset-bottom)]">
        {mobileNavItems.map(({ href, label, icon: Icon }) => {
          const isActive = href === "/" ? pathname === "/" : pathname.startsWith(href);

          return (
            <Link
              key={href}
              href={href}
              aria-current={isActive ? "page" : undefined}
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
