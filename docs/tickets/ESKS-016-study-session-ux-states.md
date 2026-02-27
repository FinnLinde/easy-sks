# ESKS-016 - Study Session UX States (Setup, Completion, Welcome)

- Status: `todo`
- Prioritaet: `P1`
- Bereich: `frontend`
- Owner: `unassigned`

## Ziel / Business Value

Die Lernsession fuehrt Nutzer klar durch Start, aktive Bearbeitung und Abschluss. Das reduziert Abbrueche und verbessert wahrgenommenen Fortschritt.

## Kontext / Ist-Stand

- Aktuell zeigt `StudySession` direkt Karten inkl. Reveal + Rating.
- Figma-Inspiration enthaelt separate States: Setup-Screen, Session-Complete-Screen, optionales Welcome-Overlay.
- Practice/Due Mode existiert bereits technisch.

## Scope

- Setup-Screen vor Session-Start mit Moduswahl + Themenfilter.
- Completion-Screen nach letzter Karte (zusammenfassende Metriken + CTA).
- Optionales Welcome-Overlay (einmal pro Nutzer/Browser) fuer Erststart.
- Konsistente Error/Loading/Empty-States im Dark Theme.

## Out of Scope

- Aenderung des FSRS/Scheduling-Algorithmus.
- Neue Backend-Endpunkte fuer Session-Analytics.

## Technische Spezifikation

- Refactor in explizite Session-States (`setup|active|complete|error|loading`).
- `setup` startet Session mit Snapshot der Kartenliste.
- `complete` zeigt Anzahl bearbeiteter Karten und Modus.
- Welcome-Overlay persistiert lokal (`localStorage` Flag pro Nutzer).
- Accessibility: Fokusmanagement bei State-Wechsel, Tastatursteuerung fuer zentrale CTAs.

## API-Aenderungen

- `none`

## DB-/Migrations-Aenderungen

- `none`

## Frontend-Aenderungen

- `frontend/src/components/study/study-session.tsx`
- Neue Komponenten fuer Setup/Completion/Welcome im Study-Ordner.
- Anpassung von `flashcard.tsx` und `rating-buttons.tsx` fuer konsistente States.

## Infra-Aenderungen

- `none`

## Akzeptanzkriterien

- [ ] Session startet erst nach explizitem Klick auf "Session starten".
- [ ] Nach letzter Karte erscheint Completion-Screen mit klaren CTAs.
- [ ] Erstnutzer sehen einmalig das Welcome-Overlay.
- [ ] Loading/Error/Empty bleiben fuer Due und Practice robust.

## Testplan

- Unit Tests fuer State-Transition-Helfer.
- Component Tests fuer Setup/Active/Complete Rendermodi.
- Manuell: Due/Practice, Topic-Wechsel, Session-Ende, Reload.

## Abhaengigkeiten

- Keine harten Abhaengigkeiten.

## Progress-Checklist

- [ ] State-Machine/Flow im Code modellieren.
- [ ] Setup- und Completion-UI bauen.
- [ ] Welcome-Overlay + Persistenz bauen.
- [ ] Tests + QA dokumentieren.

## Offene Fragen

- Soll das Welcome-Overlay pro Account (serverseitig) statt lokal gespeichert werden?
