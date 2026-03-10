import { AuthGuard } from "@/components/auth/auth-guard";
import { NavigationSimulator } from "@/components/navigation/navigation-simulator";

export default function NavigationPage() {
  return (
    <div className="min-h-full w-full">
      <AuthGuard description="Melde dich an, um eine Navigationsprüfung zu starten.">
        <NavigationSimulator />
      </AuthGuard>
    </div>
  );
}
