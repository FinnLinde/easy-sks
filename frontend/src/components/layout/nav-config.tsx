import type { LucideIcon } from "lucide-react";
import { BookOpen, LayoutDashboard, User } from "lucide-react";
import type { AuthRole } from "@/auth/authorization";

export const navItems = [
  { href: "/", label: "Dashboard", icon: LayoutDashboard, requiredRole: "freemium" },
  { href: "/study", label: "Lernen", icon: BookOpen, requiredRole: "freemium" },
  { href: "/account", label: "Account", icon: User, requiredRole: "freemium" },
] as const satisfies readonly {
  href: string;
  label: string;
  icon: LucideIcon;
  requiredRole?: AuthRole;
}[];
