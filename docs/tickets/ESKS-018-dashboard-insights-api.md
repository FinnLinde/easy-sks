# ESKS-018 - Dashboard Insights API (streak, reviewedToday, topic breakdown)

- Status: `todo`
- Prioritaet: `P1`
- Bereich: `cross-cutting`
- Owner: `unassigned`

## Ziel / Business Value

Das Dashboard soll belastbare Kennzahlen aus dem Backend erhalten, statt mehrere Listenendpunkte clientseitig zusammenzurechnen.

## Kontext / Ist-Stand

- Frontend kann aktuell `due`, `practice`, `review` und `topics` abrufen.
- KPI-Felder wie `reviewedToday`, `streakDays`, `dueByTopic`, `recommendedTopic` fehlen als dedizierte API.
- Clientseitige Approximation erzeugt zusaetzliche Requests und inkonsistente Zahlen.

## Scope

- Neuer Dashboard-Endpoint fuer aggregierte Nutzermetriken.
- Serverseitige Berechnung von Tageswerten, Streak, Topic-Verteilung und Empfehlung.
- Frontend nutzt ausschliesslich den neuen Endpoint fuer Dashboard-KPIs.

## Out of Scope

- Historische Charts > 30 Tage.
- Premium-Analytics und Team-Vergleiche.

## Technische Spezifikation

- Endpoint-Vorschlag: `GET /dashboard/summary`.
- Response:
  - `due_now: number`
  - `reviewed_today: number`
  - `streak_days: number`
  - `due_by_topic: Record<Topic, number>`
  - `recommended_topic: Topic | null`
  - `available_cards: number`
- Berechnung basiert auf User-spezifischem Scheduling + Review-Log.
- Timezone klar definieren (UTC intern, User-Tag sauber gemappt).

## API-Aenderungen

- Neu: `GET /dashboard/summary` + OpenAPI-Schema.

## DB-/Migrations-Aenderungen

- `none` sofern vorhandene Review-/Scheduling-Daten ausreichen.
- Sonst: kleine Erweiterung fuer effiziente Tagesaggregation.

## Frontend-Aenderungen

- `frontend/src/app/page.tsx` und Dashboard-Komponenten auf neuen Endpoint umstellen.
- Fallback/Error-States fuer fehlende Summary-Daten.

## Infra-Aenderungen

- `none`

## Akzeptanzkriterien

- [ ] Ein API-Call liefert alle Dashboard-KPIs fuer den aktuellen Nutzer.
- [ ] Werte sind konsistent zu Scheduling- und Review-Daten.
- [ ] Frontend benoetigt keine Topic-N+1-Requests mehr.
- [ ] OpenAPI + Client-Typen sind aktualisiert.

## Testplan

- Backend Unit Tests fuer KPI-Berechnung (inkl. Tagesgrenzen/Streak).
- Integration Test fuer Endpoint mit realistischen Daten.
- Frontend Integration Test fuer Rendering + Error-State.

## Abhaengigkeiten

- ESKS-015 (Review-Log Persistenz) als Datenbasis.

## Progress-Checklist

- [ ] Endpoint + Service bauen.
- [ ] OpenAPI aktualisieren.
- [ ] Frontend umstellen.
- [ ] Tests + Doku finalisieren.

## Offene Fragen

- Welche User-Zeitzone soll fuer `reviewed_today` massgeblich sein?
