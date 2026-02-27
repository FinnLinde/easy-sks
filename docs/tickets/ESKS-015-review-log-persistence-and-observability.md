# ESKS-015 - Review-Log Persistenz und Lern-Observability

- Status: `done`
- Prioritaet: `P2`
- Bereich: `backend`
- Owner: `unassigned`

## Ziel / Business Value

Review-Historie wird gespeichert und ist fuer Debugging, Analytics, Fortschrittsanzeigen und spaetere Produktfeatures nutzbar.

## Kontext / Ist-Stand

- `SchedulingService.review_card(...)` erzeugt ein `ReviewLog`.
- `StudyService.review_card(...)` verwirft dieses aktuell (`_review_log`).
- Tabelle `review_logs` existiert bereits in den Migrationen.

## Scope

- Persistenz des Review-Logs bei jeder Kartenbewertung.
- Repository-Port/-Implementierung fuer Review-Logs (falls noch nicht vorhanden) oder Erweiterung bestehender Scheduling-Persistenz.
- Fehlerbehandlung/Transaktionsverhalten dokumentieren.

## Out of Scope

- Dashboard-Analytics-UI
- Aggregationen/Reporting-Endpunkte (separates Ticket)

## Technische Spezifikation

- Review und Scheduling-Update werden in derselben DB-Transaktion gespeichert.
- Bei Fehlern kein partieller Zustand (z. B. Scheduling gespeichert, Log nicht gespeichert) ohne bewusste Entscheidung.
- Minimales Domain-/Repository-Design, das spaetere Queries auf Logs erlaubt.

## API-Aenderungen

- `none` (MVP; nur interne Persistenzverbesserung)

## DB-/Migrations-Aenderungen

- `none` (Tabelle existiert bereits)
- Optional spaeter: weitere Indizes je nach Analytics-Use-Cases

## Frontend-Aenderungen

- `none`

## Infra-Aenderungen

- `none`

## Akzeptanzkriterien

- [x] Jede erfolgreiche Review-Aktion erzeugt einen persistierten `review_logs`-Eintrag.
- [x] Scheduling-Update und Review-Log werden transaktional konsistent gespeichert.
- [x] Tests decken Persistenzpfad und Fehlerfaelle ab.

## Testplan

- Unit Tests:
  - Service-Orchestrierung (Scheduling + Log Persistenz)
- Integration Tests:
  - `POST /study/review` schreibt `review_logs`
- Manuelle Tests:
  - Review aus UI und DB-Pruefung

## Abhaengigkeiten

- `ESKS-001` (Multi-User-Scheduling Basis bereits vorhanden)

## Progress-Checklist

- [x] Review-Log-Repository-API festlegen
- [x] Persistenz in `StudyService.review_card` integrieren
- [x] Transaktionsverhalten verifizieren
- [x] Tests ergaenzen

## Offene Fragen

- Sollen wir zusaetzlich `review_duration_ms` schon jetzt erfassen?

## Implementierungsnotizen

- `SchedulingRepositoryPort` um `save_review_log(...)` erweitert.
- `SchedulingRepository` persistiert `ReviewLog` via `ReviewLogRow`.
- `StudyService.review_card(...)` persistiert nun sowohl aktualisiertes Scheduling als auch `ReviewLog`.
- Vor Persistenz wird die Karte validiert; bei `card not found` gibt es keine DB-Schreiboperation.
- Transaktionskonsistenz: Beide Writes laufen in derselben Session/Request-Unit; Commit/Rollback passiert zentral in `dependencies.get_db_session`.

## Test Evidence

- `/Users/finnlinde/Developer/projects/easy-sks/backend/.venv/bin/python -m pytest backend/tests/study/service/test_study_service.py`
  - Ergebnis: `19 passed in 0.03s`
- `/Users/finnlinde/Developer/projects/easy-sks/backend/.venv/bin/python -m pytest backend/tests/integration/test_repository.py backend/tests/integration/test_study_api.py`
  - Ergebnis: `26 passed, 2 warnings in 3.22s`
