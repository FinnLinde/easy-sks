# ESKS-001 - Multi-User-Fortschritt einfuehren

- Status: `done`
- Prioritaet: `P0`
- Bereich: `backend`
- Owner: `unassigned`

## Ziel / Business Value

Jeder Nutzer hat seinen eigenen Lernfortschritt. Reviews und Due-Cards duerfen nicht global pro Karte geteilt werden.

## Kontext / Ist-Stand

- Auth ist bereits im Backend vorhanden (JWT/Cognito + Rollen).
- Study-Endpunkte sind bereits geschuetzt und funktionsfaehig.
- Scheduling-Daten sind aktuell global pro `card_id` gespeichert.
- Aktuelle Migration legt `card_scheduling_info` mit PK `card_id` an (`backend/alembic/versions/6ef04772ae3b_initial_schema.py`).
- `review_logs` enthalten derzeit kein `user_id`.

## Scope

- Nutzerbezogenes Scheduling- und Review-Datenmodell einfuehren.
- Repository- und Service-Schnittstellen auf `user_id` erweitern.
- Study-Controller/Service so erweitern, dass Requests im User-Kontext laufen.
- Tests fuer Multi-User-Verhalten ergaenzen.

## Out of Scope

- Billing/Subscriptions
- Frontend-Login-UX
- Dashboard-Metriken (separates Ticket)

## Technische Spezifikation

- Einfuehrung eines lokalen App-Users (MVP minimal):
  - Tabelle `users`
  - Primarschluessel `id` (UUID/String)
  - Eindeutiges Feld `auth_provider_user_id` (Cognito `sub`)
  - Optional `email`, `created_at`, `updated_at`
- `card_scheduling_info` wird user-bezogen:
  - Composite Key `(user_id, card_id)` oder eigener PK + Unique Index auf `(user_id, card_id)`
  - Fremdschluessel auf `users.id`
- `review_logs` wird user-bezogen:
  - Feld `user_id` (FK)
  - Index auf `(user_id, reviewed_at)`
- Repository-Ports:
  - `get_by_card_id(card_id)` -> `get_by_user_and_card_id(user_id, card_id)`
  - `get_due(before)` -> `get_due_for_user(user_id, before)`
  - `save(info)` muss `user_id` persistieren
- `StudyService`:
  - `get_due_cards(user_id, topic)`
  - `review_card(user_id, card_id, rating)`
- User-Kontext:
  - Controller liest `AuthenticatedUser` und reicht `user_id` weiter.
  - Falls lokaler User noch nicht existiert: Provisioning via `ESKS-003` oder temporarer Adapter.
- Datenmigration:
  - Falls bestehende Daten vorhanden sind, klar dokumentieren:
    - Entweder Reset (dev-only)
    - Oder Migration globaler Daten auf einen Seed-/Legacy-User

## API-Aenderungen

- Keine aenderung der externen Study-Endpoints notwendig (`GET /study/due`, `POST /study/review`).
- Optional spaeter `GET /me` (separates Ticket).

## DB-/Migrations-Aenderungen

- Neue Tabelle `users` (deferred an `ESKS-003`, noch offen)
- Anpassung `card_scheduling_info` fuer `user_id`
- Anpassung `review_logs` fuer `user_id`
- Neue Indizes fuer User-Queries
- Alembic-Migration inkl. Downgrade

## Implementierungsstand (2026-02-25)

- Umgesetzt:
  - user-scoped Scheduling via Composite Key `(user_id, card_id)`
  - `review_logs.user_id` + User-Indizes
  - FK-Verknuepfung `card_scheduling_info.user_id -> users.id`
  - FK-Verknuepfung `review_logs.user_id -> users.id`
  - Repository-/Service-/Controller-Refactor auf `user_id`
  - Tests fuer User-Isolation in Service/API/Repository ergaenzt
  - Alembic-Migration mit Backfill auf `legacy-user`
- Noch offen:
  - `none` fuer den Scope dieses Tickets

## Frontend-Aenderungen

- `none` (keine UI-Aenderung erforderlich)

## Infra-Aenderungen

- `none`

## Akzeptanzkriterien

- [x] Zwei Nutzer koennen dieselbe Karte unterschiedlich weit gelernt haben.
- [x] Review eines Nutzers veraendert nicht den Fortschritt eines anderen Nutzers.
- [x] `GET /study/due` liefert nur Karten des angemeldeten Nutzers.
- [x] Bestehende Tests werden angepasst und laufen weiterhin.

## Testplan

- Unit Tests:
  - `StudyService` mit zwei Nutzerkontexten
- Repository-Integrationstests:
  - Scheduling laden/speichern pro User
  - Due-Query filtert pro User
- API-Integrationstests:
  - Authenticated Requests mit unterschiedlichen Test-Usern

## Abhaengigkeiten

- Nutzt bestehende Auth-Struktur (`AuthenticatedUser`) als Eingangspunkt.
- Eng gekoppelt mit `ESKS-003` (lokales User-Provisioning), kann aber mit einfachem Test-Mapping vorbereitet werden.

## Progress-Checklist

- [x] Ziel-Datenmodell finalisieren (Key-Strategie fuer `card_scheduling_info`)
- [x] Alembic-Migration erstellen
- [x] ORM-Tabellen anpassen
- [x] Scheduling-Repository und Mapper anpassen
- [x] StudyService-Signaturen und Aufrufer anpassen
- [x] Controller mit User-Kontext verbinden
- [x] Tests anpassen/erweitern
- [x] Migrations-/Backfill-Strategie dokumentieren

## Offene Fragen

- Soll `users.id` intern UUID sein und `cognito_sub` separat gespeichert werden, oder reicht zunaechst `cognito_sub` als PK?
- Gibt es bestehende Produktionsdaten oder ist ein dev-reset akzeptabel?
