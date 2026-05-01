import type { LucideIcon } from "lucide-react";
import { BookOpen, ClipboardCheck, Compass, LayoutDashboard, Settings } from "lucide-react";

export const navItems = [
  { href: "/", label: "Dashboard", icon: LayoutDashboard },
  { href: "/study", label: "Lernen", icon: BookOpen },
  { href: "/exams", label: "Prüfung", icon: ClipboardCheck },
  { href: "/navigation", label: "Navigation", icon: Compass },
  { href: "/settings", label: "Settings", icon: Settings },
] as const satisfies readonly {
  href: string;
  label: string;
  icon: LucideIcon;
}[];
