"use client";

import type { ReactNode } from "react";
import { usePathname } from "next/navigation";
import { useAuth } from "@/auth/auth-provider";
import { Button } from "@/components/ui/button";

export function AuthGuard({
  children,
  title = "Login erforderlich",
  description = "Bitte melde dich an, um diesen Bereich zu nutzen.",
}: {
  children: ReactNode;
  title?: string;
  description?: string;
}) {
  const { status, login } = useAuth();
  const pathname = usePathname();

  if (status === "loading") {
    return (
      <div className="w-full max-w-2xl py-16 text-center text-sm text-muted-foreground">
        Sitzung wird geladen...
      </div>
    );
  }

  if (status !== "authenticated") {
    return (
      <div className="w-full max-w-2xl rounded-xl border p-8 text-center">
        <h2 className="text-xl font-semibold">{title}</h2>
        <p className="mt-2 text-sm text-muted-foreground">{description}</p>
        <Button className="mt-6" onClick={() => void login(pathname || "/study")}>
          Login mit Cognito
        </Button>
      </div>
    );
  }

  return <>{children}</>;
}

