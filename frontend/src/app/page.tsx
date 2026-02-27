import { AuthGuard } from "@/components/auth/auth-guard";
import { DashboardOverview } from "@/components/dashboard/dashboard-overview";

export default function Home() {
  return (
    <div className="flex min-h-full w-full justify-center">
      <AuthGuard description="Melde dich an, um deinen Lernstand und fällige Karten im Dashboard zu sehen.">
        <DashboardOverview />
      </AuthGuard>
    </div>
  );
}
