# ESKS-018 - Dashboard Insights API (streak, reviewedToday, topic breakdown)

- Status: `review`
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

- [x] Ein API-Call liefert alle Dashboard-KPIs fuer den aktuellen Nutzer.
- [x] Werte sind konsistent zu Scheduling- und Review-Daten.
- [x] Frontend benoetigt keine Topic-N+1-Requests mehr.
- [x] OpenAPI + Client-Typen sind aktualisiert.

## Testplan

- Backend Unit Tests fuer KPI-Berechnung (inkl. Tagesgrenzen/Streak).
- Integration Test fuer Endpoint mit realistischen Daten.
- Frontend Integration Test fuer Rendering + Error-State.

## Abhaengigkeiten

- ESKS-015 (Review-Log Persistenz) als Datenbasis.

## Progress-Checklist

- [x] Endpoint + Service bauen.
- [x] OpenAPI aktualisieren.
- [x] Frontend umstellen.
- [x] Tests + Doku finalisieren.

## Implementierungsnotizen

- Umgesetzt ueber `GET /dashboard/summary` mit Backend-Aggregation fuer:
  - `due_now`
  - `reviewed_today`
  - `streak_days`
  - `due_by_topic`
  - `recommended_topic`
  - `available_cards`
- Frontend-Dashboard nutzt den Summary-Endpoint und berechnet KPIs nicht mehr ueber Topic-N+1-Requests.
- Summary-Berechnung ist side-effect-free (keine Persistenz neuer Scheduling-Eintraege beim Lesen).

## Offene Fragen

- Welche User-Zeitzone soll fuer `reviewed_today` massgeblich sein?
