# ESKS-023 - Pruefungs-Uebungsmodus mit Sofort-Feedback

- Status: `todo`
- Prioritaet: `P2`
- Bereich: `cross-cutting`
- Owner: `unassigned`

## Ziel / Business Value

Nutzer koennen einzelne Pruefungsfragen beantworten und erhalten sofort eine KI-gestuetzte Bewertung — ohne Zeitdruck und ohne Pruefungs-Kontext. Dies foerdert gezieltes Lernen und schnellere Wissenskorrektur.

## Kontext / Ist-Stand

- Die Pruefungssimulation (`ESKS-008`) bietet Auswertung nur nach Abgabe der gesamten Pruefung.
- Die KI-Bewertungsinfrastruktur (`OpenAiExamEvaluator`, `ExamEvaluatorPort`) ist bereits vorhanden und kann wiederverwendet werden.
- Nutzer wuenschen sich einen Lernmodus, in dem Feedback direkt nach jeder Antwort sichtbar ist.

## Scope

- Neuer Uebungsmodus neben der bestehenden Pruefungssimulation.
- Nutzer beantwortet eine Frage und erhaelt sofort KI-Feedback (Score, Fehler, Erklaerung).
- Kein Timer, kein Bestanden/Nicht-bestanden, keine Session-Gesamtwertung.
- Wiederverwendung der bestehenden `ExamEvaluatorPort`-Infrastruktur.

## Out of Scope

- Aenderungen an der bestehenden Pruefungssimulation (bleibt wie gehabt).
- Fortschritts-Tracking oder Statistiken fuer den Uebungsmodus (Folge-Ticket).
- Spracheingabe (`ESKS-010`).

## Technische Spezifikation

### API

- Neuer Endpoint `POST /exam-practice/evaluate` (oder aehnlich).
- Request: `card_id` + `student_answer`.
- Response: `score`, `is_correct`, `feedback`, `errors[]`, `reference_short_answer`.
- Nutzt intern `ExamEvaluatorPort.evaluate()` mit den gleichen Prompt- und Scoring-Regeln.

### Frontend

- Moduswahl auf dem Pruefungs-Screen: "Pruefungssimulation" vs. "Uebungsmodus".
- Im Uebungsmodus: Eine Frage pro Ansicht, Antwortfeld, Absenden-Button.
- Nach Absenden: Inline-Anzeige von Score, Feedback und Fehlern unterhalb der Antwort.
- Navigation zur naechsten Frage nach Durchsicht des Feedbacks.

## Akzeptanzkriterien

- [ ] Nutzer kann den Uebungsmodus separat von der Pruefungssimulation starten.
- [ ] Nach Absenden einer Antwort wird sofort KI-Feedback angezeigt.
- [ ] Kein Timer und keine Bestanden-Logik im Uebungsmodus.
- [ ] Bestehende Pruefungssimulation bleibt unveraendert.

## Abhaengigkeiten

- `ESKS-008` (Pruefungssimulation MVP) — Basis-Infrastruktur.

## Progress-Checklist

- [ ] API-Endpoint fuer Einzel-Bewertung implementieren.
- [ ] Frontend: Moduswahl und Uebungs-UI bauen.
- [ ] Frontend: Inline-Feedback-Anzeige.
- [ ] Tests ergaenzen.

## Offene Fragen

- Soll der Uebungsmodus nur Fragen aus einem bestimmten Bogen zeigen oder aus allen?
- Soll es eine zufaellige Reihenfolge oder die Bogen-Reihenfolge geben?
