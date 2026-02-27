import { apiClient } from "@/services/api/client";
import type { components } from "@/services/api/schema";

export type MeSummary = components["schemas"]["MeResponse"];

export async function getMe(): Promise<MeSummary> {
  const { data, error } = await apiClient.GET("/me");
  if (error || !data) {
    throw new Error("Failed to fetch account summary");
  }
  return data;
}
