import { apiClient } from "@/services/api/client";
import type { components } from "@/services/api/schema";

export type StudyCard = components["schemas"]["StudyCardResponse"];
export type TopicValue =
  | "navigation"
  | "schifffahrtsrecht"
  | "wetterkunde"
  | "seemannschaft_i"
  | "seemannschaft_ii";
export type Rating = 1 | 2 | 3 | 4;

export async function getDueCards(
  topic?: TopicValue
): Promise<StudyCard[]> {
  const { data, error } = await apiClient.GET("/study/due", {
    params: { query: topic ? { topic } : {} },
  });
  if (error || !data) throw new Error("Failed to fetch due cards");
  return data;
}

export async function reviewCard(
  cardId: string,
  rating: Rating
): Promise<StudyCard> {
  const { data, error } = await apiClient.POST("/study/review", {
    body: { card_id: cardId, rating },
  });
  if (error || !data) throw new Error("Failed to review card");
  return data;
}
