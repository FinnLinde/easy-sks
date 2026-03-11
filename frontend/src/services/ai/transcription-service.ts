import type { components } from "@/services/api/schema";
import { API_BASE_URL, apiFetch } from "@/services/api/client";

export type AudioTranscriptionResponse =
  components["schemas"]["AudioTranscriptionResponse"];

export async function transcribeAudio(
  audio: Blob,
  language = "de"
): Promise<AudioTranscriptionResponse> {
  const formData = new FormData();
  formData.append("audio", audio, buildAudioFilename(audio.type));
  formData.append("language", language);

  const response = await apiFetch(new URL("/ai/transcribe-audio", API_BASE_URL), {
    method: "POST",
    body: formData,
  });

  const payload = (await response.json().catch(() => null)) as
    | AudioTranscriptionResponse
    | { detail?: string }
    | null;

  if (!response.ok || !payload || !("transcript" in payload)) {
    throw new Error(
      (payload && "detail" in payload && payload.detail) ||
        "Audio transcription failed."
    );
  }

  return payload;
}

function buildAudioFilename(contentType: string): string {
  if (contentType.includes("mp4")) return "answer-recording.mp4";
  if (contentType.includes("mpeg")) return "answer-recording.mp3";
  if (contentType.includes("ogg")) return "answer-recording.ogg";
  if (contentType.includes("wav")) return "answer-recording.wav";
  return "answer-recording.webm";
}
