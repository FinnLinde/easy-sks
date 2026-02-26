# ESKS-014 - Due-Queue Ordering und konsistente Lernreihenfolge

- Status: `todo`
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

- [ ] Due-Queue ist bei gleichen Daten deterministisch sortiert.
- [ ] Sortierregel ist im Code dokumentiert.
- [ ] Tests decken Tie-Breaker-Faelle ab.

## Testplan

- Unit/Repository-Tests:
  - mehrere due-Eintraege mit gleichem Timestamp
- Integration Tests:
  - `GET /study/due` liefert erwartete Reihenfolge

## Abhaengigkeiten

- `none`

## Progress-Checklist

- [ ] Sortierregel definieren
- [ ] Repository-Query mit `order_by(...)` erweitern
- [ ] Tests fuer Reihenfolge ergaenzen
- [ ] Verhalten dokumentieren

## Offene Fragen

- Sollen neue Karten innerhalb der Due-Queue separat gruppiert werden (spaeter `ESKS-012`)?

