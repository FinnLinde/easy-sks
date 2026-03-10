export type LegalDocument = {
  slug: string;
  title: string;
  description: string;
  fileName: string;
};

export const legalDocuments: LegalDocument[] = [
  {
    slug: "impressum",
    title: "Impressum",
    description: "Anbieterkennzeichnung mit Platzhaltern fuer fehlende Pflichtangaben.",
    fileName: "impressum.md",
  },
  {
    slug: "privacy-policy",
    title: "Datenschutzerklaerung",
    description: "MVP-Datenschutztext auf Basis der aktuell im Repo sichtbaren Datenfluesse.",
    fileName: "privacy-policy.md",
  },
  {
    slug: "terms-and-subscription",
    title: "AGB und Subscription Terms",
    description: "Vertrags- und Abo-Rahmen fuer den Premium-Zugang mit offenen TODOs.",
    fileName: "terms-and-subscription.md",
  },
  {
    slug: "withdrawal-and-refund",
    title: "Widerruf und Refund",
    description: "Verbraucherhinweise fuer digitale Leistungen ohne unbestaetigte Zusagen.",
    fileName: "withdrawal-and-refund.md",
  },
  {
    slug: "subprocessors",
    title: "Subprozessoren und Drittempfaenger",
    description: "Dokumentation der heute klar erkennbaren externen Dienste.",
    fileName: "subprocessors.md",
  },
  {
    slug: "data-retention",
    title: "Datenaufbewahrung und Loeschung",
    description: "Praktischer MVP-Ansatz fuer Retention, Loeschung und offene Punkte.",
    fileName: "data-retention.md",
  },
  {
    slug: "dsar-runbook",
    title: "DSAR- und Export-Runbook",
    description: "Interner Ablauf fuer Auskunft, Export und Loeschanfragen.",
    fileName: "dsar-runbook.md",
  },
];

export function getLegalDocumentBySlug(slug: string): LegalDocument | undefined {
  return legalDocuments.find((document) => document.slug === slug);
}
