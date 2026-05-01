import { API_BASE_URL } from "@/services/api/client";

export type AppSettings = {
  ai_enabled: boolean;
  openai_api_key_set: boolean;
  openai_chat_model: string;
  openai_transcription_model: string;
};

export type AppSettingsUpdate = {
  ai_enabled?: boolean;
  openai_api_key?: string | null;
  openai_chat_model?: string;
  openai_transcription_model?: string;
};

export async function getSettings(): Promise<AppSettings> {
  const response = await fetch(`${API_BASE_URL}/settings`);
  if (!response.ok) throw new Error("Failed to load settings");
  return (await response.json()) as AppSettings;
}

export async function updateSettings(body: AppSettingsUpdate): Promise<AppSettings> {
  const response = await fetch(`${API_BASE_URL}/settings`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!response.ok) throw new Error("Failed to save settings");
  return (await response.json()) as AppSettings;
}
