import { apiClient } from "@/services/api/client";
import type { components } from "@/services/api/schema";

export type Topic = components["schemas"]["Topic"];

export async function listTopics(): Promise<Topic[]> {
  const { data, error } = await apiClient.GET("/topics");
  if (error || !data) throw new Error("Failed to fetch topics");
  return data;
}
