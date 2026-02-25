"use client";

import { LogIn, LogOut, Loader2 } from "lucide-react";
import { useAuth } from "@/auth/auth-provider";
import { Button } from "@/components/ui/button";

type Props = {
  compact?: boolean;
};

export function AuthStatusActions({ compact = false }: Props) {
  const { status, login, logout } = useAuth();

  if (status === "loading") {
    return (
      <Button variant="ghost" size={compact ? "sm" : "default"} disabled>
        <Loader2 className="animate-spin" />
        {!compact ? "Lade..." : null}
      </Button>
    );
  }

  if (status === "authenticated") {
    return (
      <Button
        type="button"
        variant="outline"
        size={compact ? "sm" : "default"}
        onClick={logout}
      >
        <LogOut />
        {!compact ? "Logout" : null}
      </Button>
    );
  }

  return (
    <Button
      type="button"
      size={compact ? "sm" : "default"}
      onClick={() => void login()}
    >
      <LogIn />
      {!compact ? "Login" : null}
    </Button>
  );
}

