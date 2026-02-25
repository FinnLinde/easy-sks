# ESKS-004 - Freemium-Regeln definieren und durchsetzen

- Status: `todo`
- Prioritaet: `P1`
- Bereich: `cross-cutting`
- Owner: `unassigned`

## Ziel / Business Value

Gratis- und Premium-Nutzer erhalten klar unterschiedliche Leistungsumfaenge. Limits werden technisch erzwungen und nicht nur im UI versteckt.

## Kontext / Ist-Stand

- Cognito-Gruppen `freemium` und `premium` existieren bereits.
- Backend-Rollenpruefung existiert (`require_role`).
- Es gibt noch keine Produkt-/Entitlement-Policies (z. B. Lernlimits, Feature-Sperren).

## Scope

- Freemium/Premium-Regeln definieren (Produktentscheidung als Konfiguration).
- Backend-Policy-Layer fuer Featurezugriff und Limits.
- Frontend-UX fuer gesperrte Features/Upsell-Hinweise.

## Out of Scope

- Zahlungsabwicklung selbst (`ESKS-005`)
- Marketing-Landingpage

## Technische Spezifikation

- Policy-Modell (z. B. `PlanPolicy`):
  - erlaubte Themen
  - Reviews pro Tag
  - Dashboard-Features
  - Pruefungssimulation erlaubt/nicht erlaubt
  - KI-Bewertungen pro Tag/Monat
- Enforcement im Backend:
  - Policy-Checks in Endpunkten/Services
  - Einheitliche Fehlercodes (z. B. `403` oder `402`-aehnlicher Domain-Fehler via `403`)
  - Maschinenlesbare Fehlerantwort fuer UI (`code`, `message`, `upgrade_hint`)
- Usage Tracking (falls limits-basiert):
  - Tageszaehler / Ereignislogs
  - Nutzerzeitzone fuer Tagesgrenzen spaeter beruecksichtigen (MVP: UTC)
- Frontend:
  - Feature-Hinweise / gesperrte CTA
  - Upgrade-Call-to-Action

## API-Aenderungen

- Bestehende Endpunkte koennen neue Fehlerresponses liefern:
  - `403 plan_limit_reached`
  - `403 feature_not_in_plan`
- Optional `GET /entitlements` oder Bestandteil von `GET /me`

## DB-/Migrations-Aenderungen

- Optional Tabellen fuer Usage Tracking / Entitlements, falls nicht bereits in `ESKS-003`

## Frontend-Aenderungen

- Upsell-Hinweise an betroffenen Stellen
- Fehlerbehandlung fuer planbezogene API-Errors

## Infra-Aenderungen

- `none`

## Akzeptanzkriterien

- [ ] Freemium-Regeln sind dokumentiert und als Konfiguration implementiert.
- [ ] Backend erzwingt Limits/Feature-Sperren serverseitig.
- [ ] Frontend zeigt klare Upgrade-Hinweise statt generischer Fehler.
- [ ] Premium-Nutzer sind von den definierten Freemium-Limits ausgenommen.

## Testplan

- Unit Tests:
  - Policy-Matrix (Freemium vs Premium)
- Integration Tests:
  - Endpunkte mit planbezogenen Limits
- UI Tests:
  - Rendering von Upgrade-Hinweisen

## Abhaengigkeiten

- `ESKS-003` (User/Entitlement-Basis)
- Produktentscheidung: konkrete Freemium-Regeln

## Progress-Checklist

- [ ] Freemium/Premium-Leistungsumfang final definieren
- [ ] Policy-Modell implementieren
- [ ] Serverseitige Enforcement-Punkte festlegen
- [ ] Fehlerformat fuer Plan-Limits standardisieren
- [ ] Usage Tracking (falls noetig) implementieren
- [ ] Frontend Upsell-/Error-UX integrieren
- [ ] Tests ergaenzen

## Offene Fragen

- Welche Features sind im Freemium enthalten (Themen, KI, Simulation)?
- Werden Limits pro Tag, Woche oder Monat gesetzt?

