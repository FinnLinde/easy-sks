import { apiClient } from "@/services/api/client";
import type { components } from "@/services/api/schema";

export type NavigationTemplate = components["schemas"]["NavigationTemplateResponse"];
export type NavigationSession = components["schemas"]["NavigationSessionResponse"];
export type NavigationQuestion = components["schemas"]["NavigationQuestionResponse"];
export type NavigationSessionHistory = components["schemas"]["NavigationSessionHistoryResponse"];
export type NavigationResult = components["schemas"]["NavigationResultResponse"];
export type NavigationQuestionResult = components["schemas"]["NavigationQuestionResultResponse"];

export async function listNavigationTemplates(): Promise<NavigationTemplate[]> {
  const { data, error } = await apiClient.GET("/navigation-exams");
  if (error || !data) {
    throw new Error("Failed to fetch navigation templates");
  }
  return data;
}

export async function listNavigationHistory(): Promise<NavigationSessionHistory[]> {
  const { data, error } = await apiClient.GET("/navigation-sessions");
  if (error || !data) {
    throw new Error("Failed to fetch navigation history");
  }
  return data;
}

export async function startNavigationSession(
  sheetNumber: number,
  timeLimitMinutes?: number,
): Promise<NavigationSession> {
  const { data, error } = await apiClient.POST("/navigation-sessions", {
    body: {
      sheet_number: sheetNumber,
      ...(timeLimitMinutes ? { time_limit_minutes: timeLimitMinutes } : {}),
    },
  });
  if (error || !data) {
    throw new Error("Failed to start navigation session");
  }
  return data;
}

export async function getNavigationSession(sessionId: string): Promise<NavigationSession> {
  const { data, error } = await apiClient.GET("/navigation-sessions/{session_id}", {
    params: { path: { session_id: sessionId } },
  });
  if (error || !data) {
    throw new Error("Failed to fetch navigation session");
  }
  return data;
}

export async function saveNavigationAnswer(
  sessionId: string,
  taskId: string,
  studentAnswer: string,
): Promise<void> {
  const { error } = await apiClient.PUT("/navigation-sessions/{session_id}/answers/{task_id}", {
    params: { path: { session_id: sessionId, task_id: taskId } },
    body: { student_answer: studentAnswer },
  });
  if (error) {
    throw new Error("Failed to save navigation answer");
  }
}

export async function submitNavigationSession(sessionId: string): Promise<NavigationResult> {
  const { data, error } = await apiClient.POST("/navigation-sessions/{session_id}/submit", {
    params: { path: { session_id: sessionId } },
  });
  if (error || !data) {
    throw new Error("Failed to submit navigation session");
  }
  return data;
}

export async function getNavigationResult(sessionId: string): Promise<NavigationResult> {
  const { data, error } = await apiClient.GET("/navigation-sessions/{session_id}/result", {
    params: { path: { session_id: sessionId } },
  });
  if (error || !data) {
    throw new Error("Failed to fetch navigation result");
  }
  return data;
}
