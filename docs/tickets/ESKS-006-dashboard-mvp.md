# ESKS-006 - Dashboard MVP (Fortschritt und Tagesuebersicht)

- Status: `todo`
- Prioritaet: `P1`
- Bereich: `cross-cutting`
- Owner: `unassigned`

## Ziel / Business Value

Das Dashboard zeigt dem Nutzer auf einen Blick seinen Lernstand und die naechsten sinnvollen Schritte.

## Kontext / Ist-Stand

- Navigation hat bereits einen Dashboard-Eintrag.
- Startseite `/` rendert aktuell leeres `<main />`.
- Study- und Scheduling-Daten sind vorhanden, aber es gibt kein Dashboard-Aggregat.

## Scope

- Backend Summary-Endpoint fuer Dashboard-Metriken.
- Frontend Dashboard-MVP UI auf `/`.
- Personalisierte Kennzahlen im eingeloggten Zustand.

## Out of Scope

- Aufwendige Analytics/Charts mit historischen Drilldowns
- Gamification (Badges, Rankings)

## Technische Spezifikation

- Metriken MVP:
  - faellige Karten gesamt
  - faellige Karten pro Kategorie
  - heute beantwortete Karten
  - aktuelle Lernserie (Streak) (MVP-Definition klar festlegen)
  - naechste empfohlene Session (z. B. Kategorie mit meisten Due-Cards)
- Backend:
  - `DashboardService` aggregiert aus Scheduling + ReviewLogs
  - Userbezogene Berechnung
- Frontend:
  - Dashboard Cards (KPIs)
  - Kategorie-Uebersicht
  - CTA "Jetzt lernen" / Deep Link zu `/study`
  - Loading / Error / Empty States

## API-Aenderungen

- Neuer Endpoint `GET /dashboard/summary`
  - Response:
    - `due_total`
    - `due_by_topic[]`
    - `reviewed_today`
    - `streak_days`
    - `recommended_topic`

## DB-/Migrations-Aenderungen

- `none` (setzt userbezogene `review_logs` aus `ESKS-001` voraus)

## Frontend-Aenderungen

- Implementierung Dashboard-Page `/`
- API-Service fuer Dashboard Summary
- Auth-gated Rendering / Login-Hinweis

## Infra-Aenderungen

- `none`

## Akzeptanzkriterien

- [ ] Eingeloggter Nutzer sieht personalisierte Dashboard-Kennzahlen.
- [ ] Kennzahlen passen zu den Review-/Scheduling-Daten des Nutzers.
- [ ] Dashboard zeigt sinnvolle Empty States bei neuem Nutzer.
- [ ] CTA fuehrt in den Study-Flow.

## Testplan

- Unit Tests:
  - Streak-Berechnung
  - Aggregation pro Thema
- Integration Tests:
  - `GET /dashboard/summary`
- UI Tests:
  - Loading/Error/Empty/Data States

## Abhaengigkeiten

- `ESKS-001` (userbezogene Fortschrittsdaten)
- `ESKS-002` (Frontend Auth)

## Progress-Checklist

- [ ] Dashboard-Metriken final definieren
- [ ] Backend Aggregationsservice implementieren
- [ ] Endpoint in API + OpenAPI aufnehmen
- [ ] Frontend Dashboard-Services und Typen anlegen
- [ ] Dashboard-UI auf `/` bauen
- [ ] Tests ergaenzen

## Offene Fragen

- Wie wird die Streak definiert (Kalendertage mit >=1 Review, lokale Zeitzone vs UTC)?

