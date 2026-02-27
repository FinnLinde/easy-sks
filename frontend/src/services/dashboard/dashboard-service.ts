import { apiClient } from "@/services/api/client";
import type { components } from "@/services/api/schema";

export type DashboardSummary = components["schemas"]["DashboardSummaryResponse"];

export async function getDashboardSummary(): Promise<DashboardSummary> {
  const { data, error } = await apiClient.GET("/dashboard/summary");
  if (error || !data) {
    throw new Error("Failed to fetch dashboard summary");
  }
  return data;
}
