"use client";

import { useEffect, useState, type FormEvent } from "react";
import { Loader2, Save } from "lucide-react";
import { Button } from "@/components/ui/button";
import {
  UpdateProfileError,
  updateMyProfile,
  type MeSummary,
} from "@/services/user/user-service";

const MOBILE_NUMBER_PATTERN = /^\+[1-9]\d{7,14}$/;

type FieldErrors = {
  fullName?: string;
  mobileNumber?: string;
};

function normalizeFullName(value: string): string {
  return value.trim().split(/\s+/).filter(Boolean).join(" ");
}

function validateProfileInput(
  fullName: string,
  mobileNumber: string
): { normalizedFullName: string; normalizedMobileNumber: string; errors: FieldErrors } {
  const normalizedFullName = normalizeFullName(fullName);
  const normalizedMobileNumber = mobileNumber.trim();
  const errors: FieldErrors = {};

  if (normalizedFullName.length < 2) {
    errors.fullName = "Bitte gib deinen vollen Namen ein (mindestens 2 Zeichen).";
  }

  if (!MOBILE_NUMBER_PATTERN.test(normalizedMobileNumber)) {
    errors.mobileNumber = "Bitte nutze das internationale Format, z. B. +491701234567.";
  }

  return { normalizedFullName, normalizedMobileNumber, errors };
}

export function ProfileForm({
  initialFullName,
  initialMobileNumber,
  submitLabel = "Profil speichern",
  onSaved,
}: {
  initialFullName?: string | null;
  initialMobileNumber?: string | null;
  submitLabel?: string;
  onSaved?: (summary: MeSummary) => void;
}) {
  const [fullName, setFullName] = useState(initialFullName ?? "");
  const [mobileNumber, setMobileNumber] = useState(initialMobileNumber ?? "");
  const [fieldErrors, setFieldErrors] = useState<FieldErrors>({});
  const [formError, setFormError] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    setFullName(initialFullName ?? "");
  }, [initialFullName]);

  useEffect(() => {
    setMobileNumber(initialMobileNumber ?? "");
  }, [initialMobileNumber]);

  async function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setFormError(null);
    setSuccessMessage(null);

    const {
      normalizedFullName,
      normalizedMobileNumber,
      errors,
    } = validateProfileInput(fullName, mobileNumber);
    setFieldErrors(errors);
    if (Object.keys(errors).length > 0) {
      return;
    }

    setSaving(true);
    try {
      const summary = await updateMyProfile({
        full_name: normalizedFullName,
        mobile_number: normalizedMobileNumber,
      });
      setFullName(summary.full_name ?? normalizedFullName);
      setMobileNumber(summary.mobile_number ?? normalizedMobileNumber);
      setSuccessMessage("Profil gespeichert.");
      setFieldErrors({});
      onSaved?.(summary);
    } catch (error) {
      if (error instanceof UpdateProfileError) {
        if (error.code === "mobile_number_in_use") {
          setFieldErrors({
            mobileNumber:
              "Diese Mobilnummer wird bereits von einem anderen Account verwendet.",
          });
        } else if (error.code === "invalid_mobile_number") {
          setFieldErrors({
            mobileNumber:
              "Bitte nutze das internationale Format, z. B. +491701234567.",
          });
        } else if (error.code === "invalid_full_name") {
          setFieldErrors({
            fullName:
              "Bitte gib deinen vollen Namen ein (mindestens 2 Zeichen).",
          });
        } else {
          setFormError("Profil konnte nicht gespeichert werden.");
        }
      } else {
        setFormError("Profil konnte nicht gespeichert werden.");
      }
    } finally {
      setSaving(false);
    }
  }

  return (
    <form className="space-y-4" onSubmit={onSubmit}>
      <div className="space-y-1.5">
        <label htmlFor="full-name" className="text-sm font-medium">
          Voller Name
        </label>
        <input
          id="full-name"
          value={fullName}
          onChange={(event) => setFullName(event.target.value)}
          className="h-10 w-full rounded-md border border-white/10 bg-background/40 px-3 text-sm outline-none transition focus:border-sky-300/70 focus:ring-2 focus:ring-sky-400/20"
          autoComplete="name"
          placeholder="Max Mustermann"
        />
        {fieldErrors.fullName ? (
          <p className="text-xs text-destructive">{fieldErrors.fullName}</p>
        ) : null}
      </div>

      <div className="space-y-1.5">
        <label htmlFor="mobile-number" className="text-sm font-medium">
          Mobilnummer
        </label>
        <input
          id="mobile-number"
          value={mobileNumber}
          onChange={(event) => setMobileNumber(event.target.value)}
          className="h-10 w-full rounded-md border border-white/10 bg-background/40 px-3 text-sm outline-none transition focus:border-sky-300/70 focus:ring-2 focus:ring-sky-400/20"
          autoComplete="tel"
          inputMode="tel"
          placeholder="+491701234567"
        />
        {fieldErrors.mobileNumber ? (
          <p className="text-xs text-destructive">{fieldErrors.mobileNumber}</p>
        ) : (
          <p className="text-xs text-muted-foreground">
            Format: international mit `+` und Landesvorwahl.
          </p>
        )}
      </div>

      {formError ? <p className="text-sm text-destructive">{formError}</p> : null}
      {successMessage ? (
        <p className="text-sm text-emerald-400">{successMessage}</p>
      ) : null}

      <Button type="submit" disabled={saving} className="gap-2">
        {saving ? <Loader2 className="size-4 animate-spin" /> : <Save className="size-4" />}
        {saving ? "Speichert..." : submitLabel}
      </Button>
    </form>
  );
}
