import type { LucideIcon } from "lucide-react";
import { BookOpen, LayoutDashboard } from "lucide-react";
import type { AuthRole } from "@/auth/authorization";

export const navItems = [
  { href: "/", label: "Dashboard", icon: LayoutDashboard, requiredRole: "freemium" },
  { href: "/study", label: "Lernen", icon: BookOpen, requiredRole: "freemium" },
] as const satisfies readonly {
  href: string;
  label: string;
  icon: LucideIcon;
  requiredRole?: AuthRole;
}[];
