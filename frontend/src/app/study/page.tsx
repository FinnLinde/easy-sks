import { AuthGuard } from "@/components/auth/auth-guard";
import { StudySession } from "@/components/study/study-session";

export default function StudyPage() {
  return (
    <div className="min-h-screen flex flex-col items-center py-8">
      <AuthGuard
        description="Melde dich an, um deine fälligen Karten mit deinem persönlichen Lernstand zu lernen."
      >
        <StudySession />
      </AuthGuard>
    </div>
  );
}
