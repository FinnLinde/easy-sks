# Subprozessoren und Drittempfaenger

Stand: 2026-03-10

Diese Liste dokumentiert nur Dienste, die im aktuellen Repo klar belegt sind. Fehlende Anbieterinformationen werden absichtlich nicht geraten.

## Aktuell klar belegbare Dienste

### AWS Cognito

- Zweck: Login, Token-Ausgabe, Benutzerverwaltung
- Datenkategorien: Identitaets- und Kontodaten, insbesondere `email`; Telefonnummer ist im aktuellen Cognito-Setup noch nicht als Scope oder verifizierter Produktfluss belegt
- Quelle im Repo: Frontend-Cognito-Login, Backend-Token-Verifikation, Terraform fuer User Pool
- Hinweis: aktueller Terraform-Stand zeigt `openid`, `email`, `profile` als Scopes, nicht `phone`

### Stripe

- Zweck: Checkout, Customer Portal, Subscription-Verwaltung, Webhook-Synchronisierung
- Datenkategorien: `email`, interner `user_id`-Bezug in `metadata` bzw. `client_reference_id`, Billing- und Subscription-Referenzen
- Quelle im Repo: Billing-Service und Stripe-SDK-Adapter
- Hinweis: Zahlungsinstrumente werden nach aktuellem Repo-Stand nicht vollstaendig im EasySKS-System gespeichert

### OpenAI

- Zweck: Bewertung von Freitextantworten in Exam-, Navigation- und Study-Flows, wenn konfiguriert
- Datenkategorien: Nutzerantworten, Aufgabenkontext, Referenzantworten, Bewertungs-Feedback
- Quelle im Repo: OpenAI-basierte Evaluatoren fuer Exam und Navigation sowie Study-Adapter
- Hinweis: ohne API-Konfiguration faellt das System laut Code auf heuristische Bewertungen zurueck

### Hosting / Infrastruktur / Datenbankbetrieb

- Zweck: Bereitstellung von Frontend, Backend und Datenbank
- Datenkategorien: saemtliche im Produkt verarbeiteten Daten koennen auf der eingesetzten Infrastruktur gespeichert oder verarbeitet werden
- Quelle im Repo: VPS-Deploy-Runbook und Caddy/VPS-Setup
- Offener Punkt: konkreter Providername, Rechenzentrumsstandort, Auftragsverarbeitervertrag und Transfermechanismus sind im Repo derzeit nicht benannt

## Noch nicht ausreichend belegt

Folgende Aussagen sollten vorerst nicht als feste Tatsache kommuniziert werden, solange sie nicht im Repo oder in Betriebsunterlagen verifiziert sind:

- konkreter Cloud- oder VPS-Anbietername
- konkreter Datenbankanbieter ausserhalb des selbst betriebenen Stacks
- konkrete Support-, Analytics- oder Error-Tracking-Dienste
- konkrete Transfermechanismen ausserhalb des EWR

## Vor Launch zu vervollstaendigen

TODO: Verbindliche Anbieterbezeichnungen, Adressen, Rechtsgrundlagen fuer Transfers und vertragliche Schutzmassnahmen ergaenzen.
