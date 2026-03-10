# ESKS-025 - Legal und Compliance Launch Readiness (DE/EU)

- Status: `todo`
- Prioritaet: `P1`
- Bereich: `cross-cutting`
- Owner: `unassigned`

## Ziel / Business Value

EasySKS soll vor einem bezahlten Launch in Deutschland/EU ueber die notwendigen rechtlichen, datenschutzbezogenen und verbraucherrechtlichen Grundlagen verfuegen, damit Billing, Identitaetsdaten und Lern-/Pruefungsdaten belastbar und nachvollziehbar verarbeitet werden.

## Kontext / Ist-Stand

- Die App bietet Login via Cognito, Lernfortschritt, Pruefungssimulationen, Navigation-Simulationen und Stripe-basiertes Premium-Billing.
- Es werden personenbezogene und nutzerbezogene Leistungsdaten verarbeitet:
  - `email`, `full_name`, `mobile_number`
  - Lern-/Review-Historie, Scheduling-Zustand
  - Freitext-Antworten in Exam-/Navigation-Sessions
  - Billing-Referenzen zu Stripe (`customer`, `subscription`, `price`)
- KI-Auswertung kann Freitext-Antworten an OpenAI uebermitteln.
- Im Repo sind aktuell keine sichtbaren rechtlichen Produktflaechen vorhanden:
  - kein `Impressum`
  - keine Datenschutzerklaerung
  - keine AGB/Subscription Terms
  - keine dokumentierte Loesch-/Export-/Retention-Strategie
- Der aktuelle Frontend-Auth-MVP speichert Tokens clientseitig in `localStorage`, was aus Security-/Datenschutzsicht nur eine Zwischenloesung sein sollte.

## Scope

- Rechtliche Produktflaechen fuer DE/EU definieren und im Produkt verlinkbar machen:
  - `Impressum`
  - Datenschutzerklaerung
  - AGB / Subscription Terms
  - Widerrufs-/Refund-Information fuer digitale Leistungen, falls B2C relevant
- Datenverarbeitung fuer EasySKS dokumentieren:
  - Kategorien personenbezogener Daten
  - Zwecke und Rechtsgrundlagen
  - Empfaenger / Subprozessoren
  - Aufbewahrung / Loeschung
  - Betroffenenrechte / Kontaktweg
- Billing- und Upgrade-Flows auf verpflichtende Vorabinformationen pruefen und ergaenzen:
  - Preis
  - Abrechnungsintervall
  - Auto-Renewal
  - Kuendigungslogik
  - Widerruf / Erloeschen des Widerrufsrechts
- Entscheidung und Dokumentation zur Datensparsamkeit:
  - Ist `mobile_number` fuer den Produktzweck wirklich erforderlich?
  - Falls ja: begruendete Zweckbeschreibung und konsistente Verifikationsstrategie
  - Falls nein: Feld optional machen oder entfernen
- Operative Compliance-Grundlagen schaffen:
  - Retention-/Deletion-Policy
  - DSAR-/Export-/Loesch-Runbook
  - Subprocessor-Liste
  - Security-/Incident-Minimum fuer personenbezogene Daten

## Out of Scope

- Verbindliche anwaltliche Pruefung oder finale juristische Freigabe.
- Vollstaendige Zertifizierungen / ISO / SOC2.
- Kompletter Umbau des Auth-Stacks in diesem Ticket.
- Steuer-/VAT-Engine-Implementierung im Produkt.

## Technische Spezifikation

- Rechtliche Artefakte im Repo vorbereiten, z. B. unter `docs/legal/`:
  - `privacy-policy.md`
  - `impressum.md`
  - `terms-and-subscription.md`
  - `withdrawal-and-refund.md`
  - `subprocessors.md`
  - `data-retention.md`
  - `dsar-runbook.md`
- Frontend:
  - Sichtbare Links zu Impressum / Datenschutz / Terms im App-Shell/Footer und in billing-nahen Screens.
  - Vor Upgrade klare Billing-Disclosure mit Preis, Intervall, Auto-Renewal, Kuendigung.
  - Optional Hinweis auf KI-Auswertung / externe Verarbeitung fuer Freitext-Antworten.
- Backend / Operations:
  - Loesch- und Exportprozess fuer `users`, `review_logs`, `card_scheduling_info`, `exam_sessions`, `exam_answers`, `navigation_sessions`, `navigation_answers`, `billing_customers`, `subscriptions` fachlich definieren.
  - Logging-Policy pruefen: keine unnoetige Persistenz sensibler Freitext-Inhalte in Logs.
  - Security-Follow-up als explizite Massnahme dokumentieren:
    - Migration weg von `localStorage` Bearer Tokens hin zu serverseitiger Session oder `httpOnly` Cookie-Strategie.
- Datenminimierung:
  - Bewertung, ob `mobile_number` fuer Vertragserfuellung / Sicherheit erforderlich ist.
  - Ergebnis als Produktentscheidung dokumentieren und in ESKS-020 / ESKS-022 rueckkoppeln.

## API-Aenderungen

- Optional:
  - Self-service Endpunkte fuer Datenexport / Account-Loeschung nur, wenn bewusst in Scope gezogen.
- Fuer dieses Ticket primaer `none`, solange zunaechst Dokumentation, Policy und UI-Disclosure umgesetzt werden.

## DB-/Migrations-Aenderungen

- `none` im Basisscope.
- Folgeaenderungen moeglich, falls `mobile_number` optional/entfernt wird oder Retention-Loeschpfade technische Anpassungen benoetigen.

## Frontend-Aenderungen

- Footer / Navigation um rechtliche Links ergaenzen.
- Billing-/Upgrade-Surface um Pflichtinformationen und Terms-/Datenschutz-Verweise ergaenzen.
- Falls `mobile_number` bleibt: klare Zweckerklaerung im Onboarding/Profil.
- Falls KI-Auswertung aktiv ist: transparenter Nutzerhinweis in betroffenen Flows.

## Infra-Aenderungen

- Konfig-/Betriebsdokumentation fuer Subprozessoren und Datenfluesse ergaenzen.
- Security-Folgearbeit fuer sichere Session-Strategie als konkrete Abhaengigkeit oder Folge-Ticket verankern.

## Akzeptanzkriterien

- [ ] Es gibt einen abgestimmten Satz rechtlicher Basisdokumente fuer DE/EU (`Impressum`, Datenschutz, Terms/Subscription, Widerruf/Refund sofern erforderlich).
- [ ] Die tatsaechlich verarbeiteten Datenkategorien und externen Empfaenger (Cognito/AWS, Stripe, OpenAI, Hosting) sind dokumentiert.
- [ ] Das Produkt zeigt vor dem Premium-Upgrade die wesentlichen Billing-/Abo-Informationen transparent an.
- [ ] Es gibt eine dokumentierte Retention-/Deletion-/Export-Strategie fuer Nutzer-, Lern-, Pruefungs- und Billing-Daten.
- [ ] Es gibt eine dokumentierte Entscheidung, ob `mobile_number` notwendig ist, inklusive Begruendung und Folgewirkung auf Produkt/Backend.
- [ ] Es gibt einen benannten Security-Follow-up fuer den Ersatz der `localStorage`-Tokenstrategie.

## Testplan

- Review:
  - Dokumente und Produkttexte gegen tatsaechliche Datenfluesse im Code abgleichen.
- Manuell:
  - Sichtbarkeit aller rechtlichen Links im Frontend pruefen.
  - Upgrade-Flow auf Vollstaendigkeit der Billing-Disclosure pruefen.
  - Account-/Profil-Flaechen auf Zweckerklaerungen und Datenschutz-Hinweise pruefen.
- Operativ:
  - DSAR-/Loesch-Runbook einmal testweise an einem Dev-User durchspielen.

## Abhaengigkeiten

- ESKS-005 (Stripe Billing Surface und Subscription Flow)
- ESKS-019 (Account Surface)
- ESKS-020 (Profil-Hardening)
- ESKS-022 (Cognito-first Mobilnummer-Verifikation)
- ESKS-024 (KI-Antwortvalidierung / OpenAI-Nutzung)
- Produktentscheidung: B2C vs. B2B vs. gemischt
- Externe juristische Pruefung vor Live-Gang empfohlen

## Progress-Checklist

- [ ] Dateninventar und Datenfluesse final konsolidieren
- [ ] Rechtliche Basisdokumente als Entwurf erstellen
- [ ] Subprozessoren / Drittanbieter und Transfers dokumentieren
- [ ] Billing-Disclosure im Produkt definieren
- [ ] Entscheidung zu `mobile_number` treffen und Folgeumfang festlegen
- [ ] Retention-/Deletion-/Export-Runbook erstellen
- [ ] Security-Follow-up fuer Session-/Token-Haertung als konkretes Folge-Ticket oder Teilplan erfassen
- [ ] Juristischen Review organisieren

## Offene Fragen

- Wird EasySKS an Verbraucher (`B2C`) verkauft, an Unternehmen (`B2B`) oder an beide?
- Ist `mobile_number` fachlich wirklich erforderlich oder nur ein MVP-Platzhalter?
- Soll OpenAI fuer produktive Freitext-Antworten standardmaessig aktiviert sein?
- Soll Datenexport / Account-Loeschung nur intern als Runbook oder direkt als Self-Service-Funktion angeboten werden?
