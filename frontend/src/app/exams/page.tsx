import { AuthGuard } from "@/components/auth/auth-guard";
import { ExamSimulator } from "@/components/exams/exam-simulator";

export default function ExamsPage() {
  return (
    <div className="min-h-full w-full">
      <AuthGuard description="Melde dich an, um eine Prüfungssimulation zu starten.">
        <ExamSimulator />
      </AuthGuard>
    </div>
  );
}
