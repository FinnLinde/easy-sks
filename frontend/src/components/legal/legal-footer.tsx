import Link from "next/link";
import { cn } from "@/lib/utils";

const legalLinks = [
  { href: "/legal", label: "Rechtliches" },
  { href: "/legal/impressum", label: "Impressum" },
  { href: "/legal/privacy-policy", label: "Datenschutz" },
  { href: "/legal/terms-and-subscription", label: "Abo-AGB" },
  { href: "/legal/withdrawal-and-refund", label: "Widerruf & Refund" },
];

export function LegalFooter({ className }: { className?: string }) {
  return (
    <footer
      className={cn(
        "border-t border-white/10 bg-background/70 px-4 py-4 text-xs text-muted-foreground md:px-6",
        className
      )}
    >
      <div className="mx-auto flex w-full max-w-6xl flex-col gap-2 md:flex-row md:items-center md:justify-between">
        <p>
          EasySKS rechtliche Informationen in Bearbeitung. Fehlende Unternehmens- und
          Steuerangaben sind vor einem Live-Gang zu ergaenzen.
        </p>
        <nav className="flex flex-wrap gap-x-4 gap-y-2">
          {legalLinks.map((link) => (
            <Link
              key={link.href}
              href={link.href}
              className="transition-colors hover:text-foreground"
            >
              {link.label}
            </Link>
          ))}
        </nav>
      </div>
    </footer>
  );
}
