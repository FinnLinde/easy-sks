# ESKS-008 - Pruefungssimulation MVP

- Status: `blocked`
- Prioritaet: `P1`
- Bereich: `cross-cutting`
- Owner: `unassigned`

## Ziel / Business Value

Nutzer koennen realistische Pruefungssimulationen absolvieren und ihre Punkte/Fehler auswerten.

## Kontext / Ist-Stand

- Karteikarten-Lernsystem ist vorhanden.
- Pruefungsboegen werden vom Product Owner noch bereitgestellt.
- Es gibt noch kein Exam-Datenmodell und keine Exam-UI.

## Scope

- Importformat fuer Pruefungsboegen definieren.
- Datenmodell fuer Simulationssessions und Antworten.
- MVP-Flow: Starten -> Bearbeiten -> Abgeben -> Auswertung.

## Out of Scope

- KI-Auswertung freier Antworten (separat `ESKS-009`)
- Offizielle Zertifizierung/Proctoring

## Technische Spezifikation

- Datenmodell (MVP):
  - `exam_templates`
  - `exam_questions`
  - `exam_sessions`
  - `exam_answers`
  - `exam_results` (optional aggregiert)
- Exam Session:
  - start timestamp
  - optional timer
  - status (`started`, `submitted`, `graded`)
- Bewertung:
  - automatische Auswertung fuer geschlossene Fragen
  - Ergebnis mit Punktzahl, Fehlerliste, Themenzuordnung
- UX:
  - Simulationsauswahl
  - Fortschrittsanzeige in der Simulation
  - Ergebnisseite mit Fehleranalyse

## API-Aenderungen

- Neue Endpunkte (voraussichtlich):
  - `GET /exams`
  - `POST /exam-sessions`
  - `GET /exam-sessions/{id}`
  - `POST /exam-sessions/{id}/answers`
  - `POST /exam-sessions/{id}/submit`
  - `GET /exam-sessions/{id}/result`

## DB-/Migrations-Aenderungen

- Neue Exam-Tabellen laut finalem Datenmodell

## Frontend-Aenderungen

- Exam-Simulation UI
- Ergebnisansicht
- Fehler-/Ladezustande

## Infra-Aenderungen

- `none`

## Akzeptanzkriterien

- [ ] Nutzer kann eine Simulation starten und abschliessen.
- [ ] Ergebnis zeigt Punktzahl und fehlerhafte Antworten.
- [ ] Simulationsdaten sind nutzerbezogen gespeichert.

## Testplan

- Unit Tests:
  - Bewertung geschlossener Fragen
- Integration Tests:
  - Session-Lifecycle
- UI Tests:
  - Start/Antworten/Submit/Result

## Abhaengigkeiten

- `ESKS-001` (userbezogene Daten)
- Externer Input: Pruefungsboegen / Datenformat vom Product Owner

## Progress-Checklist

- [ ] Importformat fuer Pruefungsboegen definieren
- [ ] Beispiel-Datensatz erhalten
- [ ] Datenmodell finalisieren
- [ ] API und Backend implementieren
- [ ] Frontend Simulation und Ergebnis bauen
- [ ] Tests ergaenzen

## Offene Fragen

- Welches Quellformat haben die Pruefungsboegen (JSON, PDF, CSV, manuell)?
- Gibt es unterschiedliche Bogen-Typen/Versionen?

