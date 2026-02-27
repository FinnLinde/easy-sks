# ESKS-014 - Due-Queue Ordering und konsistente Lernreihenfolge

- Status: `done`
- Prioritaet: `P1`
- Bereich: `backend`
- Owner: `unassigned`

## Ziel / Business Value

Nutzer erhalten eine stabile, nachvollziehbare Reihenfolge der faelligen Karten. Das verbessert UX, Debugging und Wiederholbarkeit.

## Kontext / Ist-Stand

- Due-Karten werden ohne explizites `ORDER BY` aus der DB geladen.
- Reihenfolge kann dadurch je nach DB-Ausfuehrung/Index variieren.
- Frontend zeigt Karte `X von N`; instabile Reihenfolge kann verwirrend wirken.

## Scope

- Explizite Sortierung der Due-Queue im Backend.
- Dokumentation der Sortierregel (z. B. `due ASC`, dann `last_review ASC NULLS FIRST`, dann `card_id`).
- Tests fuer deterministische Reihenfolge.

## Out of Scope

- Komplexe Priorisierungsheuristiken (Difficulty, Topic Weighting, etc.)
- UI-Queue-Management

## Technische Spezifikation

- `SchedulingRepository.get_due_for_user(...)` liefert deterministische Reihenfolge.
- Sortierregel:
  - primaer: `due` aufsteigend
  - sekundaer: `last_review` aufsteigend / `NULLS FIRST`
  - tertiaer: `card_id` aufsteigend (stabiler Tie-Breaker)
- Tests decken gleiche Due-Zeitpunkte ab.

## API-Aenderungen

- `none` (Vertragsaenderung nur semantisch/verhaltensseitig)

## DB-/Migrations-Aenderungen

- `none` (bestehender Index reicht fuer MVP wahrscheinlich aus)

## Frontend-Aenderungen

- `none`

## Infra-Aenderungen

- `none`

## Akzeptanzkriterien

- [x] Due-Queue ist bei gleichen Daten deterministisch sortiert.
- [x] Sortierregel ist im Code dokumentiert.
- [x] Tests decken Tie-Breaker-Faelle ab.

## Testplan

- Unit/Repository-Tests:
  - mehrere due-Eintraege mit gleichem Timestamp
- Integration Tests:
  - `GET /study/due` liefert erwartete Reihenfolge

## Abhaengigkeiten

- `none`

## Progress-Checklist

- [x] Sortierregel definieren
- [x] Repository-Query mit `order_by(...)` erweitern
- [x] Tests fuer Reihenfolge ergaenzen
- [x] Verhalten dokumentieren

## Offene Fragen

- Sollen neue Karten innerhalb der Due-Queue separat gruppiert werden (spaeter `ESKS-012`)?

## Implementierungsnotizen

- Deterministische Sortierung in `SchedulingRepository.get_due_for_user(...)` umgesetzt:
  - `due ASC`
  - `last_review ASC NULLS FIRST`
  - `card_id ASC`
- `StudyService.get_due_cards(...)` dokumentiert explizit, dass die Repository-Reihenfolge fuer stabile `/study/due`-Ausgabe erhalten bleibt.
- Testabdeckung erweitert:
  - Repository: Tie-Breaker-Ordering bei identischem `due`
  - Integration: `/study/due` liefert erwartete deterministische Reihenfolge
  - Service-Unit-Test: Reihenfolge aus Repository bleibt unveraendert

## Test Evidence

- `/Users/finnlinde/Developer/projects/easy-sks/backend/.venv/bin/python -m pytest backend/tests/study/service/test_study_service.py`
  - Ergebnis: `17 passed in 0.03s`
- `/Users/finnlinde/Developer/projects/easy-sks/backend/.venv/bin/python -m pytest backend/tests/integration/test_repository.py backend/tests/integration/test_study_api.py`
  - Ergebnis: `25 passed, 2 warnings in 3.18s`
