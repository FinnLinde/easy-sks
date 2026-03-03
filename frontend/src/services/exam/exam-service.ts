import { apiClient } from "@/services/api/client";
import type { components } from "@/services/api/schema";

export type ExamTemplate = components["schemas"]["ExamTemplateResponse"];
export type ExamSession = components["schemas"]["ExamSessionResponse"];
export type ExamSessionHistory = components["schemas"]["ExamSessionHistoryResponse"];
export type ExamResult = components["schemas"]["ExamResultResponse"];

export async function listExamTemplates(): Promise<ExamTemplate[]> {
  const { data, error } = await apiClient.GET("/exams");
  if (error || !data) {
    throw new Error("Failed to fetch exam templates");
  }
  return data;
}

export async function listExamHistory(): Promise<ExamSessionHistory[]> {
  const { data, error } = await apiClient.GET("/exam-sessions");
  if (error || !data) {
    throw new Error("Failed to fetch exam history");
  }
  return data;
}

export async function startExamSession(
  sheetNumber: number,
  timeLimitMinutes?: number
): Promise<ExamSession> {
  const { data, error } = await apiClient.POST("/exam-sessions", {
    body: {
      sheet_number: sheetNumber,
      ...(timeLimitMinutes ? { time_limit_minutes: timeLimitMinutes } : {}),
    },
  });
  if (error || !data) {
    throw new Error("Failed to start exam session");
  }
  return data;
}

export async function getExamSession(sessionId: string): Promise<ExamSession> {
  const { data, error } = await apiClient.GET("/exam-sessions/{session_id}", {
    params: { path: { session_id: sessionId } },
  });
  if (error || !data) {
    throw new Error("Failed to fetch exam session");
  }
  return data;
}

export async function saveExamAnswer(
  sessionId: string,
  cardId: string,
  studentAnswer: string
): Promise<void> {
  const { error } = await apiClient.PUT("/exam-sessions/{session_id}/answers/{card_id}", {
    params: { path: { session_id: sessionId, card_id: cardId } },
    body: { student_answer: studentAnswer },
  });
  if (error) {
    throw new Error("Failed to save exam answer");
  }
}

export async function submitExamSession(sessionId: string): Promise<ExamResult> {
  const { data, error } = await apiClient.POST("/exam-sessions/{session_id}/submit", {
    params: { path: { session_id: sessionId } },
  });
  if (error || !data) {
    throw new Error("Failed to submit exam session");
  }
  return data;
}

export async function getExamResult(sessionId: string): Promise<ExamResult> {
  const { data, error } = await apiClient.GET("/exam-sessions/{session_id}/result", {
    params: { path: { session_id: sessionId } },
  });
  if (error || !data) {
    throw new Error("Failed to fetch exam result");
  }
  return data;
}
