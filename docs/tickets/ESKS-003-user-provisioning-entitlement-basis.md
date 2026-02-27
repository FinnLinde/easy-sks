# ESKS-003 - User-Provisioning und Entitlement-Basis

- Status: `done`
- Prioritaet: `P0`
- Bereich: `backend`
- Owner: `unassigned`

## Ziel / Business Value

Das Backend kennt lokale App-User und kann damit Fortschritt, Billing und Feature-Freischaltungen stabil verwalten.

## Kontext / Ist-Stand

- `AuthenticatedUser` wird aus Cognito JWT gebaut (enthaelt `user_id` = `sub` und Rollen).
- Es gibt noch keine lokale `users`-Tabelle und kein Provisioning.
- Freemium/Premium-Rollen existieren bereits in Cognito und im Backend-Rollenmodell.

## Scope

- Lokales User-Modell + Repository.
- Provisioning beim ersten authentifizierten Request (create-on-first-seen).
- Basis fuer Entitlements/Subscription-Zuordnung.
- Optional `GET /me` Endpoint fuer Frontend.

## Out of Scope

- Stripe-Integration
- Vollstaendige Subscription-Engine
- Admin-Userverwaltung

## Technische Spezifikation

- Datenmodell `users` (falls nicht bereits in `ESKS-001` eingefuehrt, dort konsolidieren):
  - `id`
  - `auth_provider` (z. B. `cognito`)
  - `auth_provider_user_id` (`sub`)
  - `email` (wenn im Token vorhanden)
  - `display_name` optional
  - `created_at`, `updated_at`
- Provisioning-Service:
  - Nimmt `AuthenticatedUser` + Claims-Metadaten
  - Legt lokalen User an, falls nicht vorhanden
  - Gibt `AppUser` zurueck
- Auth-Kontext fuer Anwendungsservices:
  - Trennung zwischen externem Auth-Principal und lokalem App-User
- Entitlement-Basis (MVP):
  - Tabelle `user_entitlements` oder `subscriptions` optional vorbereiten
  - Minimal kann auch Rolle aus JWT fuer Zugriff genutzt werden; lokaler Datensatz bleibt trotzdem Pflicht
- Optional `GET /me`:
  - liefert User-Basisdaten + Rollen + Entitlement-Status

## API-Aenderungen

- Optional neuer Endpoint `GET /me`
  - Response (MVP): `user_id`, `email`, `roles`, `plan`, `entitlements`

## DB-/Migrations-Aenderungen

- Tabelle `users` (falls nicht schon in `ESKS-001`)
- Optional `user_entitlements` oder `subscriptions` (nur Basisstruktur)

## Implementierungsstand (2026-02-25)

- Umgesetzt:
  - lokale `users`-Tabelle + Alembic-Migration
  - `UserRepository` inkl. idempotentem `get_or_create_cognito_user(...)`
  - `UserProvisioningService` fuer create-on-first-seen
  - Study-Endpoints verwenden lokalen `AppUser` (Provisioning bei `/study/due` und `/study/review`)
  - Email-Claim wird aus Cognito-Token in `AuthenticatedUser` uebernommen
  - `GET /me` Endpoint fuer Session-Grunddaten (`user_id`, `email`, `roles`, `plan`, `entitlements`)
  - Tests fuer User-Repository/Provisioning via API-Flow ergaenzt
- Noch offen:
  - Entitlement-/Subscription-Basistabelle (kommt mit Billing/Freemium-Tickets)

## Frontend-Aenderungen

- Optional Nutzung von `GET /me` fuer Session-UI
- Ansonsten `none`

## Infra-Aenderungen

- `none`

## Akzeptanzkriterien

- [x] Erster authentifizierter Request eines neuen Cognito-Users erzeugt lokalen User-Datensatz.
- [x] Wiederholte Requests erzeugen keine Duplikate.
- [x] Lokaler User ist fuer Services (z. B. Study) verfgbar.
- [x] Optionaler `GET /me` Endpoint liefert stabile Session-Grunddaten.

## Testplan

- Unit Tests:
  - Provisioning-Service (insert vs. load existing)
- Integration Tests:
  - Unique Constraint / Idempotenz
- API Tests:
  - `GET /me` (falls implementiert)

## Abhaengigkeiten

- `ESKS-001` (gemeinsames User-Datenmodell abstimmen)

## Progress-Checklist

- [x] Lokales User-Datenmodell finalisieren
- [x] Migration erstellen
- [x] User-Repository implementieren
- [x] Provisioning-Service implementieren
- [x] Auth-Dependency/Service-Wiring erweitern
- [x] Study/weitere Services auf lokalen User umstellen
- [x] Optional `GET /me` Endpoint implementieren
- [x] Tests ergaenzen

## Offene Fragen

- Welche Claims sollen persistent gespeichert werden (nur email vs. auch Name)?
- Soll `GET /me` direkt in diesem Ticket enthalten sein oder als eigenes Ticket folgen?
- MVP-Entscheidung getroffen: `users.id` entspricht vorerst dem Cognito `sub`, um bestehende Scheduling-Daten ohne Remapping weiterzuverwenden.
