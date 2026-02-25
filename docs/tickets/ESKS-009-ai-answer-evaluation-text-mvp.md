# ESKS-009 - KI-Antwortbewertung (Text) MVP

- Status: `todo`
- Prioritaet: `P1`
- Bereich: `cross-cutting`
- Owner: `unassigned`

## Ziel / Business Value

Freitextantworten werden gegen Musterantworten bewertet; Nutzer erhalten Punkte und verstaendliches Feedback zu Fehlern.

## Kontext / Ist-Stand

- `openai` Dependency ist im Backend vorhanden.
- Es gibt noch keine AI-Endpoints, keine Bewertungslogik und keine UI fuer Freitextbewertung.

## Scope

- Textbasierte Antwortbewertung (kein Audio in diesem Ticket).
- Strukturierte Bewertungsantwort mit Punkten und Fehlererklaerungen.
- MVP-UI zum Eingeben und Anzeigen der Auswertung.

## Out of Scope

- Spracheingabe / Transkription (`ESKS-010`)
- Langfristiges Modell-Tuning / Offline-Evaluation-Pipeline

## Technische Spezifikation

- Endpoint `POST /ai/evaluate-answer` (Name final abstimmen)
- Request (MVP):
  - `question_text`
  - `reference_answer`
  - `user_answer`
  - `max_points`
  - optional `grading_rubric`
- Response (JSON, strikt validiert):
  - `awarded_points`
  - `max_points`
  - `verdict` (`full`, `partial`, `incorrect`)
  - `reasoning_summary`
  - `mistakes[]`
  - `missing_points[]`
  - `improved_answer_suggestion`
- Prompting:
  - deterministisches System-Prompt
  - klare Bewertungsrubrik
  - JSON-only Ausgabe erzwingen
- Guardrails:
  - Input-Validierung
  - Timeouts/Retry-Strategie
  - Fallback-Fehlerantwort ohne Stacktrace
- Optional Speicherung:
  - `ai_evaluations` Tabelle fuer Nachvollziehbarkeit (MVP optional)

## API-Aenderungen

- Neuer Endpoint `POST /ai/evaluate-answer`
- OpenAPI-Schema fuer Request/Response + Fehlerfaelle

## DB-/Migrations-Aenderungen

- Optional `ai_evaluations` (nur wenn Speicherung im MVP enthalten)

## Frontend-Aenderungen

- Eingabemaske fuer Freitextantwort
- Ergebnisansicht mit Punktevergabe und Fehlerliste
- Ladezustand / Fehlerzustand

## Infra-Aenderungen

- API Key / Secret fuer AI-Provider
- Rate-Limits / Kostenkontrolle (mindestens Konfig-Flags)

## Akzeptanzkriterien

- [ ] Nutzer kann eine Freitextantwort absenden und strukturierte Bewertung erhalten.
- [ ] Antwort enthaelt Punktevergabe und erklaerte Fehler.
- [ ] Backend validiert AI-Ausgabe gegen erwartetes JSON-Schema.
- [ ] Fehlerszenarien (Timeout/Providerfehler) werden sauber behandelt.

## Testplan

- Unit Tests:
  - Response-Schema-Validation
  - Mapping von Provider-Output auf API-Response
- Integration Tests:
  - Endpoint mit gemocktem AI-Provider
- Manuell:
  - Beispielantworten mit voller/teilweiser/keiner Punktzahl

## Abhaengigkeiten

- Produktentscheidung fuer Bewertungsrubrik pro Aufgabentyp
- Optional `ESKS-004`, falls KI-Nutzung planlimitiert sein soll

## Progress-Checklist

- [ ] API-Request/Response Schema finalisieren
- [ ] Prompt-Template und Rubrik definieren
- [ ] AI-Provider Adapter implementieren
- [ ] Endpoint + Validierung implementieren
- [ ] Frontend MVP-UI bauen
- [ ] Kosten-/Rate-Limit-Schutz ergaenzen
- [ ] Tests ergaenzen

## Offene Fragen

- Soll die KI-Bewertung deterministisch reproduzierbar sein (niedrige Temperatur) oder eher erklaerend/variabel?
- Welche Aufgabenformate werden im MVP zuerst unterstuetzt?

