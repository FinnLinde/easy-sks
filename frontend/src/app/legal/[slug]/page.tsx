import { promises as fs } from "node:fs";
import path from "node:path";
import Link from "next/link";
import { notFound } from "next/navigation";
import { LegalMarkdown } from "@/components/legal/legal-markdown";
import {
  getLegalDocumentBySlug,
  legalDocuments,
} from "@/lib/legal-documents";

type LegalDocumentPageProps = {
  params: Promise<{ slug: string }>;
};

async function loadLegalDocument(slug: string) {
  const document = getLegalDocumentBySlug(slug);
  if (!document) {
    return null;
  }

  const filePath = path.join(process.cwd(), "..", "docs", "legal", document.fileName);
  const content = await fs.readFile(filePath, "utf8");
  return { document, content };
}

export function generateStaticParams() {
  return legalDocuments.map((document) => ({ slug: document.slug }));
}

export default async function LegalDocumentPage({ params }: LegalDocumentPageProps) {
  const { slug } = await params;
  const loadedDocument = await loadLegalDocument(slug);

  if (!loadedDocument) {
    notFound();
  }

  return (
    <div className="mx-auto flex min-h-screen w-full max-w-4xl flex-col gap-6 px-4 py-10 md:px-6">
      <div className="space-y-3">
        <Link href="/legal" className="text-sm text-sky-300 underline underline-offset-4">
          Alle Rechtstexte
        </Link>
        <p className="text-sm text-muted-foreground md:text-base">
          {loadedDocument.document.description}
        </p>
      </div>

      <article className="rounded-2xl border border-white/10 bg-card/70 p-6 md:p-8">
        <LegalMarkdown content={loadedDocument.content} />
      </article>
    </div>
  );
}
