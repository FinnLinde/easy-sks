# ESKS-008 - Pruefungssimulation MVP

- Status: `todo`
- Prioritaet: `P1`
- Bereich: `cross-cutting`
- Owner: `unassigned`

## Ziel / Business Value

Nutzer koennen realistische SKS-Pruefungssimulationen absolvieren — mit Zeitlimit, freier Textantwort und KI-gestuetzter Auswertung inkl. Fehleranalyse und Gesamtpunktzahl.

## Kontext / Ist-Stand

- 15 offizielle Pruefungsboegen (Bogen 1–15) mit je 30 Fragen sind im System hinterlegt.
- Jede Karte hat ein `exam_sheets`-Feld (Array von Bogen-Nummern), importiert via `ESKS-021`.
- Referenzantworten liegen als Volltext (`answer_text`) und strukturierte Stichpunkte (`short_answer`) vor.
- KI-Antwortauswertung fuer Freitext ist in `ESKS-009` spezifiziert und kann hier integriert werden.
- Es gibt noch kein Exam-Datenmodell, keine Session-Verwaltung und keine Exam-UI.

## Scope

- Neues `exam`-Domain-Paket mit Datenmodell, Service und API.
- Exam-Session-Lifecycle: Starten → Beantworten → Abgeben/Timeout → KI-Auswertung → Ergebnis.
- Zeitlimit pro Pruefung (konfigurierbar, Default 90 Minuten).
- KI-Bewertung jeder Antwort gegen Referenz-Stichpunkte mit Punktvergabe und Fehlerbeschreibung.
- Ergebnisseite mit Einzelbewertungen und Gesamtpunktzahl.

## Out of Scope

- Offizielle Zertifizierung oder Proctoring.
- Eigene Pruefungsboegen erstellen (nur die 15 offiziellen).
- Mehrsprachigkeit der Auswertung (nur Deutsch im MVP).

## Technische Spezifikation

### Datenmodell

Neues Domain-Paket `exam/` nach bestehender DDD-Struktur:

```
exam/
  model/
    exam_template.py       # Bogen-Metadaten
    exam_session.py        # Laufende/abgeschlossene Sitzung
    exam_answer.py         # Einzelne Antwort des Nutzers
    exam_result.py         # KI-Bewertung einer Antwort
  service/
    exam_service.py        # Session-Lifecycle und Auswertung
  controller/
    exam_controller.py     # API-Endpunkte
  db/
    exam_tables.py         # SQLAlchemy-Tabellen
    exam_repository.py     # Persistenz-Adapter
    exam_db_mapper.py      # Row <-> Domain Mapping
```

#### ExamTemplate (abgeleitet, keine eigene Tabelle noetig)

Die 15 Boegen werden aus den `exam_sheets`-Zuordnungen der Karten aggregiert. Optional kann eine leichtgewichtige Konfiguration (z.B. JSON oder Konstanten) Metadaten bereitstellen:

| Feld                | Typ     | Beschreibung                     |
|---------------------|---------|----------------------------------|
| `sheet_number`      | int     | 1–15                             |
| `display_name`      | str     | z.B. "Pruefungsbogen 3"         |
| `question_count`    | int     | 30 (alle Boegen)                 |
| `time_limit_minutes`| int     | Default 90                       |

#### exam_sessions (Tabelle)

| Feld                | Typ              | Beschreibung                           |
|---------------------|------------------|----------------------------------------|
| `id`                | UUID / String    | Primary Key                            |
| `user_id`           | String(255)      | FK → users.id                          |
| `sheet_number`      | Integer          | Pruefungsbogen 1–15                    |
| `status`            | String           | `in_progress`, `submitted`, `evaluated`|
| `started_at`        | DateTime (tz)    | Startzeitpunkt                         |
| `submitted_at`      | DateTime (tz)    | Abgabezeitpunkt (nullable)             |
| `time_limit_minutes`| Integer          | Zeitlimit fuer diese Session           |
| `total_score`       | Float            | Gesamtpunktzahl (nullable, nach Eval)  |
| `max_score`         | Float            | Maximale Punktzahl (nullable)          |
| `passed`            | Boolean          | Bestanden ja/nein (nullable)           |

#### exam_answers (Tabelle)

| Feld                | Typ              | Beschreibung                           |
|---------------------|------------------|----------------------------------------|
| `id`                | UUID / String    | Primary Key                            |
| `session_id`        | String           | FK → exam_sessions.id                  |
| `card_id`           | String(36)       | FK → cards.card_id                     |
| `student_answer`    | Text             | Freitext-Antwort des Nutzers           |
| `answered_at`       | DateTime (tz)    | Zeitpunkt der Antwort                  |
| `score`             | Float            | 0.0 / 0.5 / 1.0 (nullable, nach Eval) |
| `is_correct`        | Boolean          | Korrekt ja/nein (nullable)             |
| `feedback`          | Text             | KI-Feedback (nullable)                 |
| `errors`            | JSON             | Liste der Fehler/fehlenden Punkte      |

### Exam-Session-Lifecycle

1. **Start**: Nutzer waehlt einen Bogen (1–15) oder "zufaellig". System erstellt `exam_session`, laedt die 30 zugehoerigen Karten (`WHERE sheet_number = ANY(exam_sheets)`), startet Timer.
2. **Beantworten**: Nutzer tippt Freitext-Antworten. Jede Antwort wird als `exam_answer` gespeichert. Navigation zwischen Fragen ist frei moeglich. Antworten koennen bis zur Abgabe geaendert werden.
3. **Abgabe / Timeout**: Nutzer gibt explizit ab, oder Timer laeuft ab → Status wechselt zu `submitted`.
4. **KI-Auswertung**: Fuer jede Antwort wird ein LLM-Call ausgefuehrt mit Frage, Referenz-Stichpunkten (`short_answer`) und Nutzer-Antwort. Ergebnis: `score`, `is_correct`, `feedback`, `errors`. Status wechselt zu `evaluated`.
5. **Ergebnis**: Nutzer sieht Gesamtpunktzahl, Bestanden/Nicht-bestanden, und pro Frage: Bewertung, Feedback, fehlende Punkte.

### KI-Bewertungs-Prompt (Entwurf)

```
Du bewertest eine SKS-Pruefungsantwort.

Frage: {question}
Referenzantwort (Kernpunkte): {short_answer_bullets}
Vollstaendige Referenz: {answer_text}
Antwort des Prueflings: {student_answer}

Bewerte: Welche Kernpunkte hat der Pruefling abgedeckt? Welche fehlen oder sind falsch?
Antworte als JSON: { "score": 0|0.5|1, "is_correct": bool, "errors": [...], "feedback": "..." }
```

Die `short_answer`-Stichpunkte dienen als klare Bewertungskriterien und verhindern zu nachsichtige oder zu strenge LLM-Bewertungen.

## API-Aenderungen

Neue Endpunkte:

| Methode | Pfad                              | Beschreibung                        |
|---------|-----------------------------------|-------------------------------------|
| GET     | `/exams`                          | Verfuegbare Boegen auflisten        |
| POST    | `/exam-sessions`                  | Neue Pruefungssession starten       |
| GET     | `/exam-sessions/{id}`             | Session-Status und Fragen abrufen   |
| PUT     | `/exam-sessions/{id}/answers/{card_id}` | Antwort speichern/aktualisieren |
| POST    | `/exam-sessions/{id}/submit`      | Pruefung abgeben                    |
| GET     | `/exam-sessions/{id}/result`      | Auswertung abrufen                  |

## DB-/Migrations-Aenderungen

- Neue Tabellen: `exam_sessions`, `exam_answers`.
- Indizes auf `exam_sessions.user_id` und `exam_answers.session_id`.

## Frontend-Aenderungen

- Pruefungsauswahl-Screen (Bogen 1–15).
- Pruefungs-UI mit Timer, Fragennavigation, Freitext-Eingabe.
- Abgabe-Bestaetigung.
- Ergebnis-Screen mit Gesamtpunktzahl, Bestanden-Status, Fehleranalyse pro Frage.

## Infra-Aenderungen

- `none` (LLM-Anbindung besteht bereits via ESKS-009).

## Akzeptanzkriterien

- [ ] Nutzer kann einen der 15 Pruefungsboegen auswaehlen und eine Session starten.
- [ ] Timer laeuft sichtbar herunter und erzwingt Abgabe bei Ablauf.
- [ ] Nutzer kann Freitext-Antworten eingeben und zwischen Fragen navigieren.
- [ ] Nach Abgabe werden alle Antworten per KI bewertet.
- [ ] Ergebnis zeigt Gesamtpunktzahl, Bestanden/Nicht-bestanden und pro Frage: Score, Feedback, Fehler.
- [ ] Sessiondaten sind nutzerbezogen gespeichert und wiederabrufbar.

## Testplan

- Unit Tests:
  - Session-Lifecycle (Statusuebergaenge, Timer-Logik).
  - Score-Aggregation und Bestanden-Logik.
- Integration Tests:
  - Vollstaendiger Flow: Start → Antworten → Submit → Evaluate → Result.
  - Timeout-Szenario.
- Manueller Test:
  - Einen Bogen komplett durchspielen und Auswertungsqualitaet pruefen.

## Abhaengigkeiten

- `ESKS-021` (Pruefungsbogen-Zuordnungen importiert) — erledigt.
- `ESKS-009` (KI-Antwortauswertung) — kann parallel oder vorab implementiert werden.
- `ESKS-001` (nutzerbezogene Daten) — erledigt.

## Progress-Checklist

- [ ] Datenmodell finalisieren und Migration erstellen.
- [ ] Exam-Service mit Session-Lifecycle implementieren.
- [ ] API-Endpunkte bauen.
- [ ] KI-Bewertungs-Integration umsetzen.
- [ ] Frontend: Pruefungsauswahl und Simulations-UI.
- [ ] Frontend: Ergebnis-Screen.
- [ ] Tests ergaenzen.

## Offene Fragen

- Soll der Nutzer seine Pruefungshistorie einsehen koennen (Liste vergangener Sessions)?
- Bestanden-Schwellwert: Welcher Prozentsatz gilt als bestanden (z.B. 70%)?
- Soll es einen "Uebungsmodus" ohne Timer geben, oder ist das separat?
