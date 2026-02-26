# ESKS-012 - New Card Limit und Einfuehrungs-Queue

- Status: `review`
- Prioritaet: `P0`
- Bereich: `cross-cutting`
- Owner: `unassigned`

## Ziel / Business Value

Neue Nutzer erhalten sofort einen sinnvollen Start ins Lernen, ohne mit dem gesamten Kartenbestand auf einmal ueberfordert zu werden.

## Kontext / Ist-Stand

- `GET /study/due` erstellt fuer unbekannte Karten Scheduling-Eintraege on-demand.
- MVP-Implementierung begrenzt neu eingefuehrte Karten pro Queue (`new_card_limit_per_queue`) und liefert due-first.
- Frontend zeigt aktuell noch keine explizite Queue-Zusammensetzung (due/new) an.

## Scope

- Einfuehrung eines konfigurierbaren Limits fuer neue Karten pro Tag / pro Session (MVP: pro Tag oder einfaches hartes Queue-Limit).
- Trennung im Backend zwischen "due reviews" und "new introductions" (internes Verhalten, API kann fuer MVP gleich bleiben oder erweitert werden).
- UI-Anzeige fuer "neue Karten" vs "Wiederholungen" (mindestens Basis-Transparenz).

## Out of Scope

- Komplette Lernpfad-/Curriculum-Steuerung
- Adaptive Priorisierung nach Schwierigkeit/Thema

## Technische Spezifikation

- Backend:
  - Beim Queue-Aufbau zuerst faellige Reviews liefern.
  - Falls Kapazitaet vorhanden, neue Karten bis zum Limit hinzufuegen.
  - Neue Karten duerfen nicht unlimitiert auf einmal freigeschaltet werden.
  - Limit zentral konfigurierbar (z. B. Konstanten/Settings).
- Datenmodell:
  - MVP moeglich ohne neue Tabellen, wenn Limit nur auf aktueller Queue basiert.
  - Falls Tageslimit strikt erzwungen werden soll: Tracking fuer "new cards introduced today".
- UX:
  - Sichtbar machen, warum nicht alle Karten sofort erscheinen.

## API-Aenderungen

- Optional:
  - Erweiterung von `GET /study/due` Response um Metadaten (`queue_summary`)
  - oder neuer Endpunkt `GET /study/queue`
- MVP-Alternative ohne API-Aenderung moeglich

## DB-/Migrations-Aenderungen

- `none` fuer einfaches Queue-Limit (MVP)
- Optional spaeter: Tracking fuer taegliches New-Card-Limit

## Frontend-Aenderungen

- Hinweistext / Badge fuer "Neue Karten"
- Optional Queue-Summary (Due/New)

## Infra-Aenderungen

- `none`

## Akzeptanzkriterien

- [x] Ein brandneuer Nutzer sieht nicht mehr den gesamten Kartenbestand auf einmal.
- [x] Faellige Wiederholungen werden gegenueber neuen Karten priorisiert.
- [x] Die Anzahl neu eingefuehrter Karten ist konfigurierbar.
- [x] Verhalten ist durch Tests abgedeckt.

## Testplan

- Unit Tests:
  - Queue-Aufbau mit Mix aus due/new
  - Limit-Grenzfaelle (0, 1, N)
- Integration Tests:
  - Neuer Nutzer bekommt initiale Queue in begrenzter Groesse
- Manuelle Tests:
  - Login als neuer Nutzer und Lernstart auf `/study`

## Abhaengigkeiten

- Baut auf bestehender Multi-User-/Scheduling-Basis auf (`ESKS-001`)
- Sollte mit Freemium-Regeln (`ESKS-004`) abgestimmt werden, falls Limits planabhaengig werden

## Progress-Checklist

- [x] Zielmodell festlegen (MVP: hartes Queue-Limit pro Request)
- [x] Queue-Aufbau im Backend um Due-vor-New erweitern
- [x] Konfigurierbares New-Card-Limit einfuehren
- [ ] UI-Hinweis fuer Queue-Zusammensetzung ergaenzen
- [x] Tests ergaenzen

## Offene Fragen

- Soll das MVP-Limit pro Session oder pro Kalendertag gelten?
- Wie viele neue Karten sind ein guter Startwert (z. B. 10, 20)?
