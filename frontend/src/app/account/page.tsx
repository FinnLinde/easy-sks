"use client";

import { Calendar, Crown, Mail, ShieldCheck, User } from "lucide-react";
import { AuthGuard } from "@/components/auth/auth-guard";
import { useAuth } from "@/auth/auth-provider";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

export default function AccountPage() {
  const { claims, status } = useAuth();

  return (
    <div className="flex min-h-full w-full justify-center px-4 py-6 md:px-6 md:py-8">
      <AuthGuard description="Melde dich an, um deine Account-Daten und Rollen einzusehen.">
        <div className="w-full max-w-3xl space-y-6">
          <div>
            <h1 className="text-2xl font-semibold tracking-tight md:text-3xl">Account</h1>
            <p className="mt-1 text-sm text-muted-foreground">Kontoinformationen und Berechtigungen.</p>
          </div>

          <Card className="border-white/10 bg-card/70">
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-base">
                <User className="size-4" />
                Benutzer
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4 text-sm">
              <div className="flex items-center justify-between rounded-md border border-white/10 bg-background/30 px-3 py-2">
                <span className="flex items-center gap-2 text-muted-foreground"><Mail className="size-4" /> E-Mail</span>
                <span className="font-medium">{claims?.email ?? "-"}</span>
              </div>
              <div className="flex items-center justify-between rounded-md border border-white/10 bg-background/30 px-3 py-2">
                <span className="flex items-center gap-2 text-muted-foreground"><ShieldCheck className="size-4" /> Subject</span>
                <span className="font-mono text-xs md:text-sm">{claims?.subject ?? "-"}</span>
              </div>
              <div className="flex items-center justify-between rounded-md border border-white/10 bg-background/30 px-3 py-2">
                <span className="flex items-center gap-2 text-muted-foreground"><Calendar className="size-4" /> Auth Status</span>
                <Badge variant="secondary">{status}</Badge>
              </div>
            </CardContent>
          </Card>

          <Card className="border-white/10 bg-card/70">
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-base">
                <Crown className="size-4" />
                Rollen
              </CardTitle>
            </CardHeader>
            <CardContent className="flex flex-wrap gap-2">
              {claims?.roles?.length ? (
                claims.roles.map((role) => (
                  <Badge key={role} className="capitalize" variant={role === "premium" ? "default" : "outline"}>
                    {role}
                  </Badge>
                ))
              ) : (
                <p className="text-sm text-muted-foreground">Keine Rollen im Token gefunden.</p>
              )}
            </CardContent>
          </Card>
        </div>
      </AuthGuard>
    </div>
  );
}
