"use client";

import { useCallback, useEffect, useState } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import {
  getSettings,
  updateSettings,
  type AppSettings,
} from "@/services/settings/settings-service";
import { notifySettingsUpdated } from "@/services/settings/app-settings-context";

const DEFAULT_CHAT_MODEL = "gpt-4o-mini";
const DEFAULT_TRANSCRIPTION_MODEL = "gpt-4o-mini-transcribe";

export function SettingsForm() {
  const [settings, setSettings] = useState<AppSettings | null>(null);
  const [aiEnabled, setAiEnabled] = useState(false);
  const [chatModel, setChatModel] = useState("");
  const [transcriptionModel, setTranscriptionModel] = useState("");
  const [keyDraft, setKeyDraft] = useState("");
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [statusMessage, setStatusMessage] = useState<string | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const loadSettings = useCallback(async () => {
    setLoading(true);
    setErrorMessage(null);
    try {
      const current = await getSettings();
      applySettings(current);
    } catch {
      setErrorMessage("Settings konnten nicht geladen werden.");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void loadSettings();
  }, [loadSettings]);

  function applySettings(next: AppSettings) {
    setSettings(next);
    setAiEnabled(next.ai_enabled);
    setChatModel(next.openai_chat_model);
    setTranscriptionModel(next.openai_transcription_model);
    setKeyDraft("");
  }

  async function save() {
    setSaving(true);
    setStatusMessage(null);
    setErrorMessage(null);
    try {
      const body: Parameters<typeof updateSettings>[0] = {
        ai_enabled: aiEnabled,
        openai_chat_model: chatModel || DEFAULT_CHAT_MODEL,
        openai_transcription_model:
          transcriptionModel || DEFAULT_TRANSCRIPTION_MODEL,
      };
      if (keyDraft.trim().length > 0) {
        body.openai_api_key = keyDraft.trim();
      }
      const updated = await updateSettings(body);
      applySettings(updated);
      notifySettingsUpdated();
      setStatusMessage("Einstellungen gespeichert.");
    } catch {
      setErrorMessage("Einstellungen konnten nicht gespeichert werden.");
    } finally {
      setSaving(false);
    }
  }

  async function clearKey() {
    setSaving(true);
    setStatusMessage(null);
    setErrorMessage(null);
    try {
      const updated = await updateSettings({ openai_api_key: null });
      applySettings(updated);
      notifySettingsUpdated();
      setStatusMessage("OpenAI-Key entfernt.");
    } catch {
      setErrorMessage("Key konnte nicht entfernt werden.");
    } finally {
      setSaving(false);
    }
  }

  if (loading) {
    return (
      <div className="space-y-3">
        <Skeleton className="h-8 w-40" />
        <Skeleton className="h-48 w-full" />
      </div>
    );
  }

  if (!settings) {
    return (
      <div className="rounded-2xl border border-red-500/30 bg-red-500/10 p-6 text-sm">
        <p>{errorMessage ?? "Settings sind nicht verfügbar."}</p>
        <Button variant="outline" className="mt-3" onClick={loadSettings}>
          Erneut versuchen
        </Button>
      </div>
    );
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>KI-Einstellungen</CardTitle>
        <CardDescription>
          Aktiviere KI-gestützte Antwortbewertung und Audio-Transkription
          mit deinem eigenen OpenAI-API-Key. Die App funktioniert auch ohne
          KI – heuristische Bewertung bleibt aktiv.
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-5">
        <label className="flex items-center justify-between gap-4 rounded-lg border border-white/10 bg-background/40 p-3">
          <span className="text-sm font-medium">KI-Funktionen aktivieren</span>
          <input
            type="checkbox"
            checked={aiEnabled}
            onChange={(event) => setAiEnabled(event.target.checked)}
            className="size-5 cursor-pointer accent-sky-400"
          />
        </label>

        <div className="space-y-2">
          <label className="text-xs font-medium uppercase tracking-wide text-muted-foreground">
            OpenAI API Key
          </label>
          <div className="flex flex-wrap items-center gap-3">
            <input
              type="password"
              autoComplete="off"
              spellCheck={false}
              value={keyDraft}
              onChange={(event) => setKeyDraft(event.target.value)}
              placeholder={
                settings.openai_api_key_set
                  ? "Gespeichert – neuen Key eingeben um zu ersetzen"
                  : "sk-..."
              }
              className="flex-1 min-w-0 rounded-md border border-white/10 bg-background/40 px-3 py-2 text-sm focus:border-sky-400/50 focus:outline-none"
            />
            {settings.openai_api_key_set ? (
              <Button variant="outline" onClick={clearKey} disabled={saving}>
                Key entfernen
              </Button>
            ) : null}
          </div>
          <p className="text-xs text-muted-foreground">
            {settings.openai_api_key_set
              ? "Ein Key ist gespeichert. Wird nicht erneut angezeigt."
              : "Kein Key gespeichert. Hol dir einen auf platform.openai.com."}
          </p>
        </div>

        <div className="grid gap-3 md:grid-cols-2">
          <div className="space-y-2">
            <label className="text-xs font-medium uppercase tracking-wide text-muted-foreground">
              Chat-Modell
            </label>
            <input
              type="text"
              value={chatModel}
              onChange={(event) => setChatModel(event.target.value)}
              placeholder={DEFAULT_CHAT_MODEL}
              className="w-full rounded-md border border-white/10 bg-background/40 px-3 py-2 text-sm focus:border-sky-400/50 focus:outline-none"
            />
          </div>
          <div className="space-y-2">
            <label className="text-xs font-medium uppercase tracking-wide text-muted-foreground">
              Transkriptions-Modell
            </label>
            <input
              type="text"
              value={transcriptionModel}
              onChange={(event) => setTranscriptionModel(event.target.value)}
              placeholder={DEFAULT_TRANSCRIPTION_MODEL}
              className="w-full rounded-md border border-white/10 bg-background/40 px-3 py-2 text-sm focus:border-sky-400/50 focus:outline-none"
            />
          </div>
        </div>

        <div className="flex flex-wrap items-center justify-between gap-3">
          <div className="text-xs text-muted-foreground" aria-live="polite">
            {errorMessage ? (
              <span className="text-destructive">{errorMessage}</span>
            ) : statusMessage ? (
              <span>{statusMessage}</span>
            ) : null}
          </div>
          <Button onClick={save} disabled={saving}>
            {saving ? "Speichere..." : "Speichern"}
          </Button>
        </div>
      </CardContent>
    </Card>
  );
}
