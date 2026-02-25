# ESKS-011 - Produktions-Infrastruktur-Basis (Staging/Prod)

- Status: `todo`
- Prioritaet: `P1`
- Bereich: `infrastructure`
- Owner: `unassigned`

## Ziel / Business Value

EasySKS wird deploybar und betreibbar in einer stabilen Staging-/Produktionsumgebung, inklusive Auth, API, Frontend, DB, Secrets und Observability-Grundlagen.

## Kontext / Ist-Stand

- Terraform konfiguriert aktuell primar Cognito.
- Lokale Entwicklung nutzt Docker-Postgres.
- Backend-DB-URL ist aktuell im Code hardcoded.
- Noch keine sichtbare Deploy-Targets fuer Frontend/Backend/Webhooks.

## Scope

- Zielarchitektur fuer Staging/Prod festlegen.
- Infrastruktur fuer Backend, Frontend, Datenbank, Secrets.
- Konfigurationsmanagement (Env Vars/Secrets) statt Hardcodes.
- Basis Monitoring/Logging.

## Out of Scope

- Vollstaendige SRE-Reife (Alerting on-call, chaos tests)
- Kostenoptimierung in Tiefe

## Technische Spezifikation

- Zielarchitektur (MVP Beispiel, final festlegen):
  - Frontend Hosting (z. B. Vercel oder AWS)
  - Backend Hosting (z. B. ECS/Fargate/App Runner)
  - Managed Postgres (RDS)
  - Cognito (bereits vorhanden)
  - Object Storage/CDN fuer Bilder (falls noetig)
- Konfiguration:
  - `DATABASE_URL` aus Env/Secret
  - Auth Config aus Env/Secret
  - Stripe/AI Secrets (wenn Features aktiv)
- Deployability:
  - Staging und Production getrennt
  - DNS/HTTPS
  - Webhook-Endpunkte oeffentlich erreichbar
- Observability (MVP):
  - strukturierte Logs
  - Error Tracking oder Cloud Logs
  - Healthchecks

## API-Aenderungen

- `none` (indirekt nur Konfig/Deploy)

## DB-/Migrations-Aenderungen

- `none` (aber Migrationsausfuehrung in Deploy-Prozess einplanen)

## Frontend-Aenderungen

- Env-Konfiguration fuer API/Auth/Billing URLs

## Infra-Aenderungen

- Terraform-Module erweitern:
  - Compute fuer Backend
  - Datenbank
  - Networking/Security Groups (falls AWS Compute)
  - Secret Management
  - Outputs fuer App-Konfiguration

## Akzeptanzkriterien

- [ ] Staging-Umgebung ist deploybar und erreichbar.
- [ ] Backend nutzt konfigurierbare DB/Auth-Settings statt Hardcodes.
- [ ] Migrationsprozess ist fuer Deploy dokumentiert/automatisiert.
- [ ] Basis-Logging und Healthchecks funktionieren.

## Testplan

- Manuell:
  - Staging Deploy
  - Login-Flow
  - API Healthcheck
- Smoke Tests:
  - `/health`
  - Kern-Userflow (Login -> Study)

## Abhaengigkeiten

- Entscheidungen zu Hosting-Stack
- `ESKS-005` fuer produktive Webhook-Erreichbarkeit (wenn Billing live geht)

## Progress-Checklist

- [ ] Zielarchitektur festlegen (Frontend/Backend/DB Hosting)
- [ ] Konfig-Hardcodes identifizieren und auf Env umstellen
- [ ] Terraform-Module fuer Runtime/DB/Secrets erstellen
- [ ] Staging Deployment aufsetzen
- [ ] Deploy-/Migration-Runbook dokumentieren
- [ ] Smoke Tests definieren/automatisieren

## Offene Fragen

- Soll das Frontend auf Vercel bleiben und nur Backend/DB auf AWS laufen?
- Welche Mindestanforderungen gelten fuer Datenschutz/Logging-Aufbewahrung?

