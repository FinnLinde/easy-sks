import { apiClient } from "@/services/api/client";
import type { components } from "@/services/api/schema";

export type Card = components["schemas"]["CardResponse"];

export async function getCard(cardId: string): Promise<Card> {
  const { data, error } = await apiClient.GET("/cards/{card_id}", {
    params: { path: { card_id: cardId } },
  });
  if (error || !data) throw new Error(`Failed to fetch card ${cardId}`);
  return data;
}
