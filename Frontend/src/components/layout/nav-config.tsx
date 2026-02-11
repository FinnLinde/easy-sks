import type { LucideIcon } from "lucide-react";
import { BookOpen, LayoutDashboard } from "lucide-react";

export const navItems = [
  { href: "/", label: "Dashboard", icon: LayoutDashboard },
  { href: "/study", label: "Lernen", icon: BookOpen },
] as const satisfies readonly { href: string; label: string; icon: LucideIcon }[];
