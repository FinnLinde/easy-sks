import { apiClient } from "@/services/api/client";
import type { components } from "@/services/api/schema";

export type MeSummary = components["schemas"]["MeResponse"];
export type ProfileUpdateRequest = components["schemas"]["ProfileUpdateRequest"];

export class UpdateProfileError extends Error {
  code: string;
  status: number;

  constructor(code: string, status: number) {
    super(code);
    this.code = code;
    this.status = status;
  }
}

export async function getMe(): Promise<MeSummary> {
  const { data, error } = await apiClient.GET("/me");
  if (error || !data) {
    throw new Error("Failed to fetch account summary");
  }
  return data;
}

export async function updateMyProfile(
  payload: ProfileUpdateRequest
): Promise<MeSummary> {
  const { data, error, response } = await apiClient.PATCH("/me/profile", {
    body: payload,
  });

  if (!data) {
    const detail =
      error &&
      typeof error === "object" &&
      "detail" in error &&
      typeof error.detail === "string"
        ? error.detail
        : "profile_update_failed";
    throw new UpdateProfileError(detail, response.status);
  }

  return data;
}
