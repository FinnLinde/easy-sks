"use client";

import { useEffect, useMemo, useRef, useState } from "react";
import { Loader2, Mic, Square } from "lucide-react";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";
import { transcribeAudio } from "@/services/ai/transcription-service";

type SpeechAnswerInputProps = {
  value: string;
  onChange: (value: string) => void;
  label: string;
  placeholder: string;
  disabled?: boolean;
  rows?: number;
  textareaClassName?: string;
  labelClassName?: string;
  language?: string;
};

export function SpeechAnswerInput({
  value,
  onChange,
  label,
  placeholder,
  disabled = false,
  rows = 5,
  textareaClassName,
  labelClassName,
  language = "de",
}: SpeechAnswerInputProps) {
  const [isRecording, setIsRecording] = useState(false);
  const [isTranscribing, setIsTranscribing] = useState(false);
  const [recordingSeconds, setRecordingSeconds] = useState(0);
  const [error, setError] = useState<string | null>(null);
  const recorderRef = useRef<MediaRecorder | null>(null);
  const streamRef = useRef<MediaStream | null>(null);
  const chunksRef = useRef<BlobPart[]>([]);
  const currentValueRef = useRef(value);

  useEffect(() => {
    currentValueRef.current = value;
  }, [value]);

  useEffect(() => {
    if (!isRecording) return;

    const intervalId = window.setInterval(() => {
      setRecordingSeconds((current) => current + 1);
    }, 1000);

    return () => window.clearInterval(intervalId);
  }, [isRecording]);

  useEffect(() => {
    return () => {
      const recorder = recorderRef.current;
      if (recorder && recorder.state !== "inactive") {
        recorder.stop();
      }
      stopStream(streamRef.current);
    };
  }, []);

  const speechSupported = useMemo(() => {
    return (
      typeof window !== "undefined" &&
      typeof navigator !== "undefined" &&
      Boolean(navigator.mediaDevices?.getUserMedia) &&
      typeof MediaRecorder !== "undefined"
    );
  }, []);

  const handleToggleRecording = async () => {
    if (isRecording) {
      recorderRef.current?.stop();
      return;
    }

    if (!speechSupported) {
      setError("Sprachaufnahme wird in diesem Browser nicht unterstützt.");
      return;
    }

    try {
      setError(null);
      setRecordingSeconds(0);
      chunksRef.current = [];

      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const mimeType = getPreferredMimeType();
      const recorder = mimeType
        ? new MediaRecorder(stream, { mimeType })
        : new MediaRecorder(stream);

      streamRef.current = stream;
      recorderRef.current = recorder;

      recorder.addEventListener("dataavailable", (event) => {
        if (event.data.size > 0) {
          chunksRef.current.push(event.data);
        }
      });

      recorder.addEventListener("stop", () => {
        const audioType = recorder.mimeType || mimeType || "audio/webm";
        const blob = new Blob(chunksRef.current, { type: audioType });
        recorderRef.current = null;
        stopStream(streamRef.current);
        streamRef.current = null;
        setIsRecording(false);
        setRecordingSeconds(0);
        chunksRef.current = [];

        if (!blob.size) {
          setError("Keine Aufnahme erkannt. Bitte erneut versuchen.");
          return;
        }

        void handleTranscription(blob);
      });

      recorder.addEventListener("error", () => {
        stopStream(streamRef.current);
        streamRef.current = null;
        recorderRef.current = null;
        setIsRecording(false);
        setRecordingSeconds(0);
        setError("Die Aufnahme konnte nicht gestartet werden.");
      });

      recorder.start();
      setIsRecording(true);
    } catch {
      stopStream(streamRef.current);
      streamRef.current = null;
      recorderRef.current = null;
      setIsRecording(false);
      setRecordingSeconds(0);
      setError("Mikrofonzugriff wurde verweigert oder ist nicht verfügbar.");
    }
  };

  const statusText = isRecording
    ? `Aufnahme läuft ${formatDuration(recordingSeconds)}`
    : isTranscribing
      ? "Transkribiere Aufnahme..."
      : "Spracheingabe fügt Text in das Antwortfeld ein.";

  async function handleTranscription(blob: Blob) {
    setIsTranscribing(true);
    setError(null);
    try {
      const response = await transcribeAudio(blob, language);
      onChange(appendTranscript(currentValueRef.current, response.transcript));
    } catch (transcriptionError) {
      setError(
        transcriptionError instanceof Error
          ? transcriptionError.message
          : "Die Aufnahme konnte nicht transkribiert werden."
      );
    } finally {
      setIsTranscribing(false);
    }
  }

  return (
    <div className="space-y-2">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <span className={cn("text-sm text-muted-foreground", labelClassName)}>{label}</span>
        <Button
          type="button"
          variant={isRecording ? "destructive" : "outline"}
          size="sm"
          onClick={() => void handleToggleRecording()}
          disabled={disabled || isTranscribing}
        >
          {isRecording ? (
            <>
              <Square />
              Aufnahme stoppen
            </>
          ) : isTranscribing ? (
            <>
              <Loader2 className="animate-spin" />
              Transkribiere...
            </>
          ) : (
            <>
              <Mic />
              Antwort sprechen
            </>
          )}
        </Button>
      </div>

      <textarea
        value={value}
        onChange={(event) => onChange(event.target.value)}
        rows={rows}
        className={cn(
          "w-full resize-y rounded-lg border border-white/15 bg-background/50 p-3 text-sm outline-none transition-colors focus:border-sky-400",
          textareaClassName
        )}
        placeholder={placeholder}
        disabled={disabled}
      />

      <div className="flex flex-wrap items-center gap-2 text-xs text-muted-foreground">
        {isTranscribing ? <Loader2 className="size-3 animate-spin" /> : null}
        <span>{statusText}</span>
      </div>

      {error ? <p className="text-xs text-destructive">{error}</p> : null}
    </div>
  );
}

function appendTranscript(existingText: string, transcript: string): string {
  const normalizedTranscript = transcript.trim();
  if (!normalizedTranscript) {
    return existingText;
  }
  if (!existingText.trim()) {
    return normalizedTranscript;
  }
  return `${existingText.trimEnd()}\n${normalizedTranscript}`;
}

function formatDuration(totalSeconds: number): string {
  const minutes = Math.floor(totalSeconds / 60);
  const seconds = totalSeconds % 60;
  return `${minutes}:${seconds.toString().padStart(2, "0")}`;
}

function getPreferredMimeType(): string | undefined {
  const candidates = [
    "audio/webm;codecs=opus",
    "audio/webm",
    "audio/mp4",
    "video/mp4",
  ];

  return candidates.find((candidate) => MediaRecorder.isTypeSupported(candidate));
}

function stopStream(stream: MediaStream | null) {
  stream?.getTracks().forEach((track) => track.stop());
}
