import { API_BASE_URL, apiFetch } from "@/services/api/client";

export type NavigationTemplate = {
  sheet_number: number;
  display_name: string;
  task_count: number;
  total_points: number;
  time_limit_minutes: number;
};

export type NavigationSubQuestion = {
  text: string;
  points: number;
};

export type NavigationQuestion = {
  task_number: number;
  task_id: string;
  points: number;
  context: string;
  sub_questions: NavigationSubQuestion[];
  student_answer: string;
  answered_at?: string | null;
};

export type NavigationSession = {
  session_id: string;
  sheet_number: number;
  status: string;
  started_at: string;
  submitted_at?: string | null;
  deadline_at: string;
  time_limit_minutes: number;
  time_remaining_seconds: number;
  time_over: boolean;
  task_count: number;
  questions: NavigationQuestion[];
};

export type NavigationSessionHistory = {
  session_id: string;
  sheet_number: number;
  status: string;
  started_at: string;
  submitted_at?: string | null;
  total_score?: number | null;
  max_score?: number | null;
  passed?: boolean | null;
  time_over: boolean;
};

export type NavigationQuestionResult = {
  task_number: number;
  task_id: string;
  context: string;
  sub_questions: string[];
  key_answers: string[];
  solution_text: string;
  student_answer: string;
  score: number;
  max_score: number;
  is_correct: boolean;
  feedback: string;
};

export type NavigationResult = {
  session_id: string;
  sheet_number: number;
  status: string;
  started_at: string;
  submitted_at?: string | null;
  time_limit_minutes: number;
  time_over: boolean;
  total_score: number;
  max_score: number;
  passed: boolean;
  pass_score_threshold: number;
  questions: NavigationQuestionResult[];
};

export async function listNavigationTemplates(): Promise<NavigationTemplate[]> {
  return fetchJson<NavigationTemplate[]>("/navigation-exams", {
    errorMessage: "Failed to fetch navigation templates",
  });
}

export async function listNavigationHistory(): Promise<NavigationSessionHistory[]> {
  return fetchJson<NavigationSessionHistory[]>("/navigation-sessions", {
    errorMessage: "Failed to fetch navigation history",
  });
}

export async function startNavigationSession(
  sheetNumber: number,
  timeLimitMinutes?: number,
): Promise<NavigationSession> {
  return fetchJson<NavigationSession>("/navigation-sessions", {
    method: "POST",
    body: {
      sheet_number: sheetNumber,
      ...(timeLimitMinutes ? { time_limit_minutes: timeLimitMinutes } : {}),
    },
    errorMessage: "Failed to start navigation session",
  });
}

export async function getNavigationSession(sessionId: string): Promise<NavigationSession> {
  return fetchJson<NavigationSession>(`/navigation-sessions/${sessionId}`, {
    errorMessage: "Failed to fetch navigation session",
  });
}

export async function saveNavigationAnswer(
  sessionId: string,
  taskId: string,
  studentAnswer: string,
): Promise<void> {
  await fetchJson(`/navigation-sessions/${sessionId}/answers/${taskId}`, {
    method: "PUT",
    body: { student_answer: studentAnswer },
    errorMessage: "Failed to save navigation answer",
  });
}

export async function submitNavigationSession(sessionId: string): Promise<NavigationResult> {
  return fetchJson<NavigationResult>(`/navigation-sessions/${sessionId}/submit`, {
    method: "POST",
    errorMessage: "Failed to submit navigation session",
  });
}

export async function getNavigationResult(sessionId: string): Promise<NavigationResult> {
  return fetchJson<NavigationResult>(`/navigation-sessions/${sessionId}/result`, {
    errorMessage: "Failed to fetch navigation result",
  });
}

async function fetchJson<T>(
  path: string,
  options: {
    method?: string;
    body?: unknown;
    errorMessage: string;
  },
): Promise<T> {
  const response = await apiFetch(new URL(path, API_BASE_URL), {
    method: options.method ?? "GET",
    headers: options.body ? { "Content-Type": "application/json" } : undefined,
    body: options.body ? JSON.stringify(options.body) : undefined,
  });

  const payload = (await response.json().catch(() => null)) as
    | T
    | { detail?: string }
    | null;

  if (!response.ok || payload == null) {
    throw new Error(
      (payload && typeof payload === "object" && "detail" in payload && payload.detail) ||
        options.errorMessage,
    );
  }

  return payload as T;
}
