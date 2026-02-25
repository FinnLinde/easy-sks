# ESKS-010 - Spracheingabe und Transkription fuer KI-Bewertung

- Status: `todo`
- Prioritaet: `P2`
- Bereich: `cross-cutting`
- Owner: `unassigned`

## Ziel / Business Value

Nutzer koennen Antworten einsprechen statt tippen und diese anschliessend von der KI bewerten lassen.

## Kontext / Ist-Stand

- KI-Textbewertung ist als separates MVP geplant (`ESKS-009`).
- Es gibt noch keine Audioaufnahme oder Speech-to-Text-Integration im Frontend/Backend.

## Scope

- Audioaufnahme im Frontend.
- Upload/Transkription (STT).
- Uebergabe des Transkripts an die bestehende Text-Bewertung.

## Out of Scope

- Live-Konversationsmodus
- Aussprachebewertung (Pronunciation Scoring)

## Technische Spezifikation

- Frontend:
  - Mikrofonberechtigung
  - Aufnahme starten/stoppen
  - Playback optional
  - Transkript vor Bewertung editierbar
- Backend:
  - Endpoint fuer Audio-Upload oder STT-Proxy
  - Dateiformat/Laengenlimits
  - Provider-Adapter fuer STT
- Integrationsflow:
  - Audio -> Transkript -> Nutzer bestaetigt/editiert -> `ESKS-009` Bewertung
- Fehlerfaelle:
  - Mikrofon verweigert
  - Upload fehlgeschlagen
  - STT nicht verstaendlich / leeres Transkript

## API-Aenderungen

- Neuer Endpoint z. B. `POST /ai/transcribe-audio`
- Optional kombinierter Endpoint fuer Transcribe+Evaluate (MVP eher getrennt)

## DB-/Migrations-Aenderungen

- `none` (optional spaeter Speicherung von Audio/Transkript)

## Frontend-Aenderungen

- Audioaufnahme-Komponente
- Transkript-Review UI
- Integration in KI-Bewertungs-UI

## Infra-Aenderungen

- STT-Provider-Secrets
- Dateigroessenlimits / Reverse Proxy Konfiguration (spaeter)

## Akzeptanzkriterien

- [ ] Nutzer kann Sprache aufnehmen und transkribieren lassen.
- [ ] Transkript ist vor Bewertung editierbar.
- [ ] Transkript kann in den bestehenden KI-Bewertungsflow uebergeben werden.
- [ ] Fehlerfaelle werden dem Nutzer klar angezeigt.

## Testplan

- Unit Tests:
  - Upload-/Statuslogik
- Integration Tests:
  - STT Endpoint mit Provider-Mock
- Manuell:
  - Browser-Mikrofonflow

## Abhaengigkeiten

- `ESKS-009` (Textbewertung)
- Providerentscheidung fuer STT

## Progress-Checklist

- [ ] STT-Provider und Audioformat festlegen
- [ ] Backend Transkriptions-Endpoint implementieren
- [ ] Frontend Audioaufnahme bauen
- [ ] Transkript-Review integrieren
- [ ] Verbindung zur Textbewertung herstellen
- [ ] Tests ergaenzen

## Offene Fragen

- Soll Audio auf dem Server gespeichert werden oder nur transient verarbeitet werden?
- Gibt es maximale Antwortdauer pro Versuch?

