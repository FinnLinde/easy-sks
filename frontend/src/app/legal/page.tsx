import Link from "next/link";
import { legalDocuments } from "@/lib/legal-documents";

export default function LegalOverviewPage() {
  return (
    <div className="mx-auto flex min-h-screen w-full max-w-5xl flex-col gap-8 px-4 py-10 md:px-6">
      <div className="space-y-3">
        <p className="text-sm font-medium uppercase tracking-[0.2em] text-sky-300">
          Rechtliches
        </p>
        <h1 className="text-3xl font-semibold tracking-tight md:text-4xl">
          Rechtliche und Compliance-Dokumente
        </h1>
        <p className="max-w-3xl text-sm text-muted-foreground md:text-base">
          Diese MVP-Seiten spiegeln den aktuell im Repo belegbaren Produktstand wider.
          Fehlende Unternehmens-, Steuer- oder Jurisdiktionsangaben bleiben bewusst als
          TODO markiert, bis sie rechtlich und operativ verifiziert sind.
        </p>
      </div>

      <div className="grid gap-4 md:grid-cols-2">
        {legalDocuments.map((document) => (
          <Link
            key={document.slug}
            href={`/legal/${document.slug}`}
            className="rounded-2xl border border-white/10 bg-card/70 p-5 transition-colors hover:border-sky-300/40 hover:bg-card"
          >
            <h2 className="text-lg font-semibold">{document.title}</h2>
            <p className="mt-2 text-sm text-muted-foreground">{document.description}</p>
          </Link>
        ))}
      </div>
    </div>
  );
}
