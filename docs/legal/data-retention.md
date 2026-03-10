# Datenaufbewahrung und Loeschung

Stand: 2026-03-10

Dies ist ein praktischer MVP-Ansatz fuer `ESKS-025`. Er beschreibt keine bereits vollautomatisierte Policy, sondern die aktuell ableitbare fachliche Zielrichtung.

## Grundsatz

- So lange ein Benutzerkonto aktiv ist, duerfen die fuer Betrieb, Vertragserfuellung und Nachvollziehbarkeit benoetigten Daten grundsaetzlich bestehen bleiben.
- Nach einer berechtigten Loeschanfrage oder einer internen Loeschentscheidung sollen Daten pro Tabelle nachvollziehbar entfernt oder, falls rechtlich noetig, eingeschraenkt aufbewahrt werden.
- Solange keine automatisierten Jobs existieren, ist der Prozess operativ ueber das Runbook in `/legal/dsar-runbook` abzuwickeln.

## Datensaetze und vorgeschlagene Behandlung

### `users`

- Inhalt: Basisprofil, Identitaetsbezug, Kontaktangaben
- Vorschlag: bis zur Kontoloeschung aufbewahren
- Bei Loeschung: Datensatz entfernen, sofern keine zwingenden Aufbewahrungspflichten entgegenstehen

### `card_scheduling_info`

- Inhalt: persoenlicher Lernzustand pro Karte
- Vorschlag: bis zur Kontoloeschung aufbewahren
- Bei Loeschung: komplett entfernen

### `review_logs`

- Inhalt: persoenliche Review-Historie
- Vorschlag: bis zur Kontoloeschung aufbewahren
- Bei Loeschung: komplett entfernen

### `exam_sessions` und `exam_answers`

- Inhalt: Session-Metadaten, Scores, Freitextantworten, Feedback
- Vorschlag: bis zur Kontoloeschung aufbewahren, solange keine separate kuerzere Retention beschlossen ist
- Bei Loeschung: komplett entfernen

### `navigation_sessions` und `navigation_answers`

- Inhalt: Session-Metadaten, Scores, Freitextantworten, Feedback
- Vorschlag: bis zur Kontoloeschung aufbewahren, solange keine separate kuerzere Retention beschlossen ist
- Bei Loeschung: komplett entfernen

### `billing_customers` und `subscriptions`

- Inhalt: Stripe-Referenzen und Subscription-Status
- Vorschlag: mindestens so lange aufbewahren, wie sie fuer Vertragsabwicklung, Nachvollziehbarkeit oder gesetzliche Pflichten benoetigt werden
- Offener Punkt: konkrete handels- und steuerrechtliche Aufbewahrungsfristen muessen vor Launch mit Business-/Rechtsinput festgelegt werden

## Nicht im Repo als separate Persistenz belegt

- Study-AI-Bewertungen haben laut Ticket `ESKS-024` keine eigene Persistenztabelle
- Vollstaendige Zahlungsinstrumentdaten werden nicht im EasySKS-Repo gespeichert

## Browser-Speicher

- Auth-Tokens in `localStorage` und PKCE-Daten in `sessionStorage` werden clientseitig gehalten
- Bei Logout oder `401` wird die Auth-Session clientseitig geloescht
- Diese Token-Strategie ist als Security-Follow-up markiert und sollte vor oder kurz nach Launch ersetzt werden

## Offene Punkte vor finaler Freigabe

TODO: Konkrete Fristen je Datenkategorie ergaenzen.

TODO: Vorgehen fuer Backups, Restore-Faelle und verzogerte endgueltige Loeschung dokumentieren.

TODO: Klare Entscheidung treffen, ob einzelne Lern- oder Freitextdaten kuerzer gespeichert werden sollen als Kontodaten.
