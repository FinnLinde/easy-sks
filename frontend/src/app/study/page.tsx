import { AuthGuard } from "@/components/auth/auth-guard";
import { StudySession } from "@/components/study/study-session";

export default function StudyPage() {
  return (
    <div className="min-h-screen flex flex-col items-center py-8">
      <AuthGuard
        title="Lernbereich nur mit Login"
        description="Melde dich an, um deine faelligen Karten mit deinem persoenlichen Fortschritt zu lernen."
      >
        <StudySession />
      </AuthGuard>
    </div>
  );
}
