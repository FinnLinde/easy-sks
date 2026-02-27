"use client";

import { useEffect, useState } from "react";
import { Calendar, Crown, Mail, RefreshCw, ShieldCheck, User, Wallet } from "lucide-react";
import { AuthGuard } from "@/components/auth/auth-guard";
import { useAuth } from "@/auth/auth-provider";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { getMe, type MeSummary } from "@/services/user/user-service";

function BillingStatusBadge({ status }: { status: string | null | undefined }) {
  if (!status) {
    return <Badge variant="outline">Nicht konfiguriert</Badge>;
  }

  const normalized = status.toLowerCase();
  if (normalized === "active" || normalized === "trialing") {
    return <Badge className="bg-emerald-600">{status}</Badge>;
  }

  if (normalized === "past_due") {
    return <Badge className="bg-amber-600">{status}</Badge>;
  }

  if (normalized === "canceled") {
    return <Badge variant="secondary">{status}</Badge>;
  }

  return <Badge variant="outline">{status}</Badge>;
}

export default function AccountPage() {
  const { status: authStatus } = useAuth();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [summary, setSummary] = useState<MeSummary | null>(null);

  async function loadSummary() {
    setLoading(true);
    setError(null);
    try {
      const data = await getMe();
      setSummary(data);
    } catch {
      setError("Kontodaten konnten nicht geladen werden.");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    void loadSummary();
  }, []);

  return (
    <div className="flex min-h-full w-full justify-center px-4 py-6 md:px-6 md:py-8">
      <AuthGuard description="Melde dich an, um deine Account-Daten und Rollen einzusehen.">
        <div className="w-full max-w-3xl space-y-6">
          <div>
            <h1 className="text-2xl font-semibold tracking-tight md:text-3xl">Account</h1>
            <p className="mt-1 text-sm text-muted-foreground">Kontoinformationen, Plan und Billing-Status.</p>
          </div>

          {loading ? (
            <div className="space-y-4">
              <Skeleton className="h-36 w-full" />
              <Skeleton className="h-28 w-full" />
              <Skeleton className="h-28 w-full" />
            </div>
          ) : error ? (
            <Card className="border-red-500/30 bg-red-500/10">
              <CardContent className="space-y-4 p-6 text-center">
                <p className="text-sm text-destructive">{error}</p>
                <Button variant="outline" onClick={() => void loadSummary()} className="gap-2">
                  <RefreshCw className="size-4" />
                  Erneut versuchen
                </Button>
              </CardContent>
            </Card>
          ) : summary ? (
            <>
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
                    <span className="font-medium">{summary.email ?? "-"}</span>
                  </div>
                  <div className="flex items-center justify-between rounded-md border border-white/10 bg-background/30 px-3 py-2">
                    <span className="flex items-center gap-2 text-muted-foreground"><ShieldCheck className="size-4" /> User ID</span>
                    <span className="font-mono text-xs md:text-sm">{summary.user_id}</span>
                  </div>
                  <div className="flex items-center justify-between rounded-md border border-white/10 bg-background/30 px-3 py-2">
                    <span className="flex items-center gap-2 text-muted-foreground"><Calendar className="size-4" /> Auth Status</span>
                    <Badge variant="secondary">{authStatus}</Badge>
                  </div>
                </CardContent>
              </Card>

              <Card className="border-white/10 bg-card/70">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2 text-base">
                    <Crown className="size-4" />
                    Plan & Entitlements
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-3">
                  <div className="flex items-center justify-between rounded-md border border-white/10 bg-background/30 px-3 py-2 text-sm">
                    <span className="text-muted-foreground">Plan</span>
                    <Badge className="capitalize" variant={summary.plan === "premium" ? "default" : "outline"}>
                      {summary.plan}
                    </Badge>
                  </div>
                  <div className="flex flex-wrap gap-2">
                    {summary.entitlements.length ? (
                      summary.entitlements.map((entitlement) => (
                        <Badge key={entitlement} variant="outline">{entitlement}</Badge>
                      ))
                    ) : (
                      <p className="text-sm text-muted-foreground">Keine Entitlements vorhanden.</p>
                    )}
                  </div>
                </CardContent>
              </Card>

              <Card className="border-white/10 bg-card/70">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2 text-base">
                    <Wallet className="size-4" />
                    Billing
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-4 text-sm">
                  <div className="flex items-center justify-between rounded-md border border-white/10 bg-background/30 px-3 py-2">
                    <span className="text-muted-foreground">Status</span>
                    <BillingStatusBadge status={summary.billing_status} />
                  </div>
                  <div className="flex items-center justify-between rounded-md border border-white/10 bg-background/30 px-3 py-2">
                    <span className="text-muted-foreground">Verlaengert am</span>
                    <span>{summary.renews_at ?? "-"}</span>
                  </div>
                  <div className="flex items-center justify-between rounded-md border border-white/10 bg-background/30 px-3 py-2">
                    <span className="text-muted-foreground">Gekuendigt am</span>
                    <span>{summary.cancels_at ?? "-"}</span>
                  </div>
                </CardContent>
              </Card>
            </>
          ) : (
            <Card className="border-white/10 bg-card/70">
              <CardContent className="p-6 text-sm text-muted-foreground">
                Keine Kontodaten verfuegbar.
              </CardContent>
            </Card>
          )}
        </div>
      </AuthGuard>
    </div>
  );
}
