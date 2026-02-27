import { AuthGuard } from "@/components/auth/auth-guard";
import { StudySession } from "@/components/study/study-session";

export default function StudyPage() {
  return (
    <div className="min-h-screen w-full bg-[radial-gradient(circle_at_12%_10%,rgba(14,165,233,0.12),transparent_40%),radial-gradient(circle_at_88%_12%,rgba(34,197,94,0.08),transparent_38%),radial-gradient(circle_at_50%_115%,rgba(245,158,11,0.08),transparent_40%)] py-6 md:py-8">
      <AuthGuard
        description="Melde dich an, um deine fälligen Karten mit deinem persönlichen Lernstand zu lernen."
      >
        <StudySession />
      </AuthGuard>
    </div>
  );
}
