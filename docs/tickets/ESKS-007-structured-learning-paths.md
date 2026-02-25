# ESKS-007 - Strukturierte Lernpfade und Kategorien

- Status: `todo`
- Prioritaet: `P1`
- Bereich: `cross-cutting`
- Owner: `unassigned`

## Ziel / Business Value

Nutzer lernen nicht unsortiert alle Karteikarten, sondern in einem didaktisch sinnvollen Ablauf nach Kategorien und Empfehlungen.

## Kontext / Ist-Stand

- Themenfilter existiert bereits im Study-UI.
- `SksTopic` und Topic-Endpoint sind vorhanden.
- Study-Flow zeigt Due-Cards, aber ohne Lernpfad-Logik ueber den Filter hinaus.

## Scope

- Lernmodi definieren (mindestens Kategorien + empfohlene Session).
- Priorisierungslogik fuer Kartenreihenfolge.
- API- und UI-Anpassungen fuer Modusauswahl.

## Out of Scope

- Vollstaendige adaptive Didaktik/ML-basierte Personalisierung
- Pruefungssimulation (separat)

## Technische Spezifikation

- Lernmodi MVP:
  - `topic`: Nutzer waehlt Kategorie
  - `recommended`: System waehlt naechsten Fokus
  - `weakest_topic` (optional MVP+)
- Priorisierung:
  - Due-Cards zuerst (bestehende FSRS-Logik)
  - Innerhalb Due-Cards sortieren nach:
    - Thema/Modus
    - Schwierigkeits-/Fehlerhistorie (spaeter)
    - `due` Zeit
- Optionale Modelle:
  - `learning_paths`
  - `user_learning_preferences`
  - Kann fuer MVP auch rein servicebasiert ohne neue Tabellen starten
- UX:
  - Lernmodus-Auswahl vor Start
  - Klarer Hinweis, warum ein Thema empfohlen wird

## API-Aenderungen

- Erweiterung bestehender Study-APIs oder neue Endpunkte:
  - `GET /study/due?mode=recommended`
  - oder `GET /study/session/recommendation`
- OpenAPI aktualisieren

## DB-/Migrations-Aenderungen

- Optional `none` fuer MVP

## Frontend-Aenderungen

- Lernmodus-Auswahl in Study-Page
- Anzeige "Empfohlenes Thema"
- Anpassung der Session-Initialisierung

## Infra-Aenderungen

- `none`

## Akzeptanzkriterien

- [ ] Nutzer kann mindestens nach Kategorie und im empfohlenen Modus lernen.
- [ ] Empfohlener Modus liefert reproduzierbar sinnvolle Kartenreihenfolge.
- [ ] Bestehender Topic-Filter-Flow bleibt funktionsfaehig.

## Testplan

- Unit Tests:
  - Priorisierungs-/Empfehlungslogik
- Integration Tests:
  - API-Verhalten fuer Lernmodi
- UI Tests:
  - Moduswechsel und Session-Start

## Abhaengigkeiten

- `ESKS-001`
- `ESKS-006` optional fuer Nutzung von Dashboard-Metriken

## Progress-Checklist

- [ ] Lernmodi und Priorisierungsregeln definieren
- [ ] API-Design festlegen
- [ ] Backend Service-Logik implementieren
- [ ] OpenAPI + Client-Typen aktualisieren
- [ ] Frontend Lernmodus-UI integrieren
- [ ] Tests ergaenzen

## Offene Fragen

- Soll "empfohlen" nur nach Due-Menge gehen oder auch Fehlerquote/Faelligkeit gewichten?

