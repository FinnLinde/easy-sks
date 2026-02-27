# ESKS-013 - Practice Mode / Lernen jederzeit (ohne Faelligkeit)

- Status: `review`
- Prioritaet: `P1`
- Bereich: `cross-cutting`
- Owner: `unassigned`

## Ziel / Business Value

Nutzer koennen jederzeit lernen, auch wenn keine Karten faellig sind. Das verbessert Motivation und reduziert "Dead End"-Momente im Produkt.

## Kontext / Ist-Stand

- MVP implementiert:
  - separater Endpunkt `GET /study/practice`
  - CTA im leeren Due-State (`Practice starten`)
  - Practice-Modus-Hinweis in der Lernansicht
- Produktentscheidung getroffen: Practice-Reviews nutzen denselben `POST /study/review`-Pfad wie normale Reviews und beeinflussen damit FSRS-Scheduling.

## Scope

- Ein "Practice"-Modus, der Karten auch ohne Faelligkeit anbietet.
- UI-CTA bei leerer Due-Queue ("Trotzdem lernen"/"Practice starten").
- Klare Definition, ob Practice-Reviews den FSRS-Zeitplan beeinflussen (MVP-Empfehlung: konfigurierbar, initial eher separater Modus ohne Einfluss oder explizit gekennzeichnet).

## Out of Scope

- Vollstaendige Lernpfad-Engine
- Personalisierte Empfehlungssysteme

## Technische Spezifikation

- Backend:
  - Neuer Queue-Modus (`due`, `practice`) oder separater Endpunkt.
  - Practice-Auswahl z. B. nach Thema, zufaellig oder "zuletzt faellig / bald faellig".
  - Schutz gegen endlose Wiederholung derselben 1-2 Karten innerhalb einer Session.
- Frontend:
  - UX fuer leere Due-Queue mit klaren Aktionen.
  - Kennzeichnung des Modus in der Lernansicht.
- Produktregel:
  - Verhalten von Ratings im Practice-Modus explizit definieren (persistieren vs nicht persistieren).

## API-Aenderungen

- Implementiert (MVP): `GET /study/practice` (gleiche Query-Filter wie `/study/due`, inkl. `topic`)
- Fehlercodes fuer invalides `topic` analog zu `/study/due` (`400`)

## DB-/Migrations-Aenderungen

- `none` (MVP)
- Optional spaeter: Session-/Practice-Tracking

## Frontend-Aenderungen

- CTA im leeren State auf `/study`
- Modus-Umschalter oder separater Button
- Angepasste Texte/Hinweise bei Practice-Ratings

## Infra-Aenderungen

- `none`

## Akzeptanzkriterien

- [x] Wenn keine due-Karten vorhanden sind, kann der Nutzer trotzdem eine Lernsession starten.
- [x] Practice-Modus ist in UI und Backend eindeutig definiert.
- [x] Ratings verhalten sich gem. Produktentscheidung konsistent.
- [x] Tests decken leere Due-Queue + Practice-Fallback ab.

## Testplan

- Unit Tests:
  - Queue-Selektion im Practice-Modus
- Integration Tests:
  - API liefert Practice-Karten bei leerer Due-Queue
- Manuelle Tests:
  - Leere Due-Queue -> Practice-Start aus UI

## Abhaengigkeiten

- Sinnvoll nach `ESKS-012` (damit New-/Due-Queue sauber definiert ist)
- Abstimmung mit `ESKS-004` (Freemium moegliche Limits fuer Practice)

## Progress-Checklist

- [x] Produktentscheidung fuer Rating-Verhalten im Practice-Modus treffen (Practice-Reviews aktualisieren FSRS)
- [x] API-Design festlegen (`mode` vs separater Endpunkt) (MVP: separater Endpunkt)
- [x] Backend-Queue fuer Practice implementieren
- [x] Leere-State-CTA im Frontend implementieren
- [x] Tests ergaenzen

## Offene Fragen

- Welche Karten sollen im Practice-Modus bevorzugt werden?
