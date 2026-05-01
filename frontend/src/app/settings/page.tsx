import { SettingsForm } from "@/components/settings/settings-form";

export default function SettingsPage() {
  return (
    <div className="mx-auto w-full max-w-3xl space-y-6 px-4 py-6 md:py-8">
      <header className="space-y-1">
        <h1 className="text-2xl font-semibold">Settings</h1>
        <p className="text-sm text-muted-foreground">
          Konfiguriere optionale KI-Features für Easy SKS.
        </p>
      </header>
      <SettingsForm />
    </div>
  );
}
