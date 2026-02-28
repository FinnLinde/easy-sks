# ESKS-021 - Pruefungsaufgaben-Import und Antwort-Linking (gleich/aehnlich)

- Status: `todo`
- Prioritaet: `P1`
- Bereich: `backend`
- Owner: `unassigned`

## Ziel / Business Value

Pruefungsaufgaben und zugehoerige Antworten sollen per Skript importiert und zu bestehenden Fragen im System zuverlaessig verknuepft werden, auch bei kleinen Textabweichungen.

## Kontext / Ist-Stand

- Karten/Fragen liegen bereits im System.
- Es gibt Scripts fuer Datenverarbeitung im Backend-Ordner.
- Ein dediziertes Matching fuer externe Pruefungsantworten existiert noch nicht.
- Externe Quelle fuer Aufgaben/Antworten inkl. Zuordnung zu Pruefungen:
  - `http://www.tim.sf-ub.de/www2/trainer_online/sks/shared/katalog.html`

## Scope

- Importskript fuer Aufgaben + Antworten aus definierter Quelldatei.
- Matching-Logik fuer Antwort-zu-Frage-Linking mit zwei Modi:
  - exakter Match
  - Aehnlichkeitsmatch mit Schwellwert
- Deterministische Konfliktbehandlung und Report-Ausgabe.

## Out of Scope

- Vollautomatische KI-Korrektur unsicherer Zuordnungen ohne Review.
- Laufende, automatisierte Delta-Synchronisation.

## Technische Spezifikation

- Script-Ort: `backend/scripts/`.
- Eingaben:
  - Source-Datei(en) mit Aufgaben + Antworten.
  - Metadaten, in welchen Pruefungen/Boegen eine Frage vorkommt.
  - Optionale Mapping-Datei/Override fuer manuelle Zuordnungen.
- Normalisierung vor Match:
  - lowercasing
  - trim/whitespace-collapse
  - optionale Satzzeichen-Normalisierung
  - optionale Umlaut-/ASCII-Strategie konsistent dokumentieren
- Matching-Pipeline:
  1. exact normalized equality
  2. similarity score (z. B. rapidfuzz ratio/token_set_ratio)
  3. threshold-based assignment
  4. unresolved/ambiguous in review report
- Safety:
  - Dry-run Modus (default)
  - Apply Modus nur mit explizitem Flag
  - Idempotente Upserts
- Output:
  - Maschinenlesbarer Report (JSON/CSV) mit `matched`, `ambiguous`, `unmatched`.

## API-Aenderungen

- `none` (batch script).

## DB-/Migrations-Aenderungen

- Optional: Mapping-Tabelle fuer externe IDs falls notwendig.
- Andernfalls: vorhandene Card/Question-Struktur verwenden.

## Frontend-Aenderungen

- `none` fuer MVP.

## Infra-Aenderungen

- `none`.

## Akzeptanzkriterien

- [ ] Skript kann im Dry-Run alle Kandidaten inkl. Match-Status reporten.
- [ ] Apply-Modus verlinkt Antworten idempotent zu Fragen.
- [ ] Kleine Textabweichungen werden ueber Similarity-Match robust behandelt.
- [ ] Ambigue Treffer werden nicht blind geschrieben, sondern als Review-Faelle ausgegeben.

## Testplan

- Unit Tests fuer Normalisierung und Match-Pipeline.
- Fixture-basierte Integrationstests fuer exact/similar/ambiguous/unmatched.
- Manuelle Stichprobe mit echten Pruefungsdaten.

## Abhaengigkeiten

- Verfuegbarkeit der Quelldaten fuer Pruefungsaufgaben + Antworten.
- Zugriff auf Quelle: `http://www.tim.sf-ub.de/www2/trainer_online/sks/shared/katalog.html`

## Progress-Checklist

- [ ] Input-/Output-Format finalisieren.
- [ ] Matching-Pipeline implementieren.
- [ ] Dry-run + apply + report bauen.
- [ ] Tests und Beispielaufruf dokumentieren.

## Offene Fragen

- Welche Similarity-Metrik und welcher Schwellwert werden fuer MVP als Default gesetzt?
