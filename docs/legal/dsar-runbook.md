# DSAR- und Export-Runbook

Stand: 2026-03-10

Dieses Dokument ist ein internes MVP-Runbook fuer Auskunfts-, Export- und Loeschanfragen. Es beschreibt den aktuellen manuellen Zielprozess, nicht bereits fertig implementierte Self-Service-Funktionen.

## 1. Eingang einer Anfrage

- Anfrage dokumentieren mit Datum, Kanal und angefragter Massnahme
- Identitaet des anfragenden Nutzers pruefen
- TODO: verbindliche Support- oder Datenschutz-Kontaktadresse festlegen

## 2. Relevante Datenquellen

Nach aktuellem Repo-Stand sind insbesondere folgende Datenquellen zu pruefen:

- `users`
- `card_scheduling_info`
- `review_logs`
- `exam_sessions`
- `exam_answers`
- `navigation_sessions`
- `navigation_answers`
- `billing_customers`
- `subscriptions`

Zusaetzlich sind externe Systeme zu beruecksichtigen:

- AWS Cognito fuer Identitaets- und Login-Daten
- Stripe fuer Customer- und Subscription-Daten
- OpenAI nicht als dauerhafte Nutzerakte, aber als externer Empfaenger bei aktiver KI-Auswertung

## 3. Export

### Mindestumfang

- Kontodaten: `user_id`, `email`, `full_name`, `mobile_number`, Zeitstempel
- Lernzustand und Review-Historie
- Exam- und Navigation-Sessions samt Antworten und Feedback
- Billing-Referenzen und aktueller Subscription-Status

### Vorgehen

- Daten pro Tabelle fuer den betroffenen `user_id` extrahieren
- Exporte in einem strukturierten Format bereitstellen, zum Beispiel JSON oder CSV plus begleitende Erklaerung
- Externe Datenpunkte aus Cognito und Stripe separat dazulegen oder manuell dokumentieren

TODO: Technischen Standard fuer Exportformat und sicheren Uebermittlungsweg festlegen.

## 4. Berichtigung

- Profilkorrekturen koennen fuer `full_name` und `mobile_number` aktuell ueber das Produkt vorgenommen werden
- Falls Daten in Cognito oder Stripe abweichen, muss die Korrektur zusaetzlich im jeweiligen Fremdsystem geprueft werden

## 5. Loeschung

### Vor der Loeschung pruefen

- Ist die Anfrage authentifiziert?
- Gibt es offene vertragliche, abrechnungsbezogene oder gesetzliche Gruende gegen eine sofortige Voll-Loeschung?
- Muss das Stripe-Abo zuerst beendet oder dokumentiert werden?

### Operatives Zielbild

- Cognito-Benutzer deaktivieren oder loeschen
- Lokale Nutzerdaten und abhaengige Lern-, Exam- und Navigationstabellen entfernen
- Billing-Referenzen nur so lange behalten, wie rechtlich oder operativ noetig
- Abschluss der Anfrage intern dokumentieren

TODO: Konkrete SQL-/Admin-Schritte fuer Dev und Prod ergaenzen, sobald der operative Zugriffspfad final definiert ist.

## 6. Fristen und Nachweis

TODO: Verbindliche Service-Level und interne Freigabeschritte festlegen.

TODO: Dokumentieren, wo Nachweise ueber Bearbeitung und Abschluss gespeichert werden.
