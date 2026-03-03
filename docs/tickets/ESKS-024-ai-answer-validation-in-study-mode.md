# ESKS-024 - KI-Antwortvalidierung im Lern-/Practice-Modus

- Status: `review`
- Prioritaet: `P1`
- Bereich: `cross-cutting`
- Owner: `unassigned`

## Ziel / Business Value

Nutzer sollen im Lern- und Practice-Modus eine eigene Freitextantwort eingeben und diese direkt durch KI bewerten lassen, bevor sie die Karte manuell raten.

## Kontext / Ist-Stand

- Study-Flow hat aktuell Frontseite -> Reveal -> manuelles Rating (`Nochmal/Schwer/Gut/Leicht`).
- Es gibt keine Antwort-Eingabe und keine automatische Rueckmeldung zur Qualitaet der eigenen Antwort.
- Exam-Flow hat bereits KI-Bewertungskomponenten, die wiederverwendet werden koennen.

## Scope

- Neuer Study-Endpoint `POST /study/evaluate-answer`.
- KI-gestuetzte Bewertung gegen `short_answer`/Referenzantwort.
- Antwortschema mit Punkten, Verdict, Feedback, fehlenden Punkten und vorgeschlagenem Rating.
- Frontend-Integration in `/study`:
  - Eingabefeld fuer Freitextantwort
  - Button "Mit KI pruefen"
  - Anzeige der KI-Bewertung inkl. Rating-Vorschlag
- Fallback ohne API-Key (deterministisch/heuristisch), damit Feature lokal nutzbar bleibt.

## Out of Scope

- Vollautomatisches Uebernehmen des Ratings ohne Nutzeraktion.
- Persistenz der KI-Bewertungen in eigener DB-Tabelle.
- Audio/Sprach-Eingabe (`ESKS-010`).

## Technische Spezifikation

### API

`POST /study/evaluate-answer`

Request:
- `card_id: string`
- `user_answer: string`

Response:
- `card_id: string`
- `awarded_points: float`
- `max_points: float` (MVP: `1.0`)
- `verdict: full | partial | incorrect`
- `reasoning_summary: string`
- `mistakes: string[]`
- `missing_points: string[]`
- `improved_answer_suggestion: string`
- `suggested_rating: 1 | 2 | 3 | 4`

### Service-Design (SOLID)

- `StudyService` erhaelt einen zusaetzlichen `answer_evaluator` Port.
- Evaluator-Adapter kapselt LLM-/Fallback-Details und liefert ein stabiles Domain-Ergebnis.
- Controller bleibt thin; Business-Logik liegt im Service.

## Akzeptanzkriterien

- [x] Nutzer kann im Study-/Practice-Flow eine Antwort eingeben.
- [x] Nutzer kann eine KI-Bewertung triggern und strukturiertes Feedback sehen.
- [x] API liefert deterministisches Fallback bei fehlender AI-Config.
- [x] Nutzer kann weiterhin manuell raten; KI-Vorschlag ist optional.
- [x] Unit-/Integration-Tests decken Endpoint und Service-Logik ab.

## Testplan

- Unit: StudyService `evaluate_answer` inklusive Mapping auf Rating-Vorschlag.
- Integration: `POST /study/evaluate-answer` fuer gueltige/ungueltige Requests.
- Frontend manuell: `/study` in due/practice, KI-Bewertung sichtbar, danach Rating weiterhin moeglich.

## Abhaengigkeiten

- AI-Konfiguration (`EXAM_AI_OPENAI_API_KEY` oder `OPENAI_API_KEY`) optional.
- Bestehende Card-/Study-Daten vorhanden.

## Progress-Checklist

- [x] Ticket angelegt
- [x] Backend Endpoint + Service-Integration
- [x] OpenAPI + Frontend API Types aktualisiert
- [x] Study-UI mit Antwortfeld + KI-Ergebnis
- [x] Tests aktualisiert

## Offene Fragen

- Sollen KI-Bewertungen spaeter historisiert werden (Audit/Verlauf)?
- Soll ein Mindest-Confidence fuer Rating-Vorschlaege eingefuehrt werden?
