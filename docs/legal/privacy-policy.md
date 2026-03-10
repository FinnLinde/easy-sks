# Datenschutzerklaerung

Stand: 2026-03-10

Dieser Entwurf beschreibt nur Verarbeitungen, die im aktuellen EasySKS-Repo nachvollziehbar sind. Fehlende Unternehmens- und Kontaktangaben bleiben bewusst als TODO markiert.

## 1. Verantwortlicher

TODO: Vollstaendigen Namen, Anschrift und Kontakt des Verantwortlichen eintragen.

TODO: Falls vorhanden, Datenschutz-Kontakt oder Datenschutzbeauftragten ergaenzen.

## 2. Produkt und Leistungsumfang

EasySKS ist aktuell eine Lernanwendung mit:

- Benutzerkonto und Login ueber AWS Cognito
- Lernfortschritt und Wiederholungsplanung
- Pruefungssimulationen und Navigation-Simulationen
- Stripe-basiertem Premium-Abo
- optionaler KI-Auswertung von Freitextantworten

## 3. Welche Daten aktuell verarbeitet werden

Nach dem aktuellen Code- und Datenmodell verarbeitet EasySKS insbesondere folgende Kategorien:

### Kontodaten

- `user_id` bzw. lokaler Nutzerbezug auf Basis des Cognito-`sub`
- `email`
- `full_name`
- `mobile_number`
- `mobile_verified_at`
- `created_at`, `updated_at`

### Lern- und Nutzungsdaten

- FSRS-Scheduling-Zustand pro Karte
- Review-Historie mit `card_id`, Rating, Zeitstempel und optionaler Dauer
- Dashboard-Aggregate aus Lernaktivitaet

### Pruefungs- und Navigationsdaten

- Exam- und Navigation-Sessions mit Start-/Abgabezeit, Status, Score und Bestanden-Status
- Freitextantworten in `student_answer`
- KI- oder heuristikbasierte Feedbacktexte, Fehlerlisten und Bewertungsdaten

### Billing-Daten

- Stripe-Referenzen wie `stripe_customer_id`, `provider_subscription_id`, `status`, `current_period_end`, `price_id`
- keine vollstaendige Speicherung von Karten- oder Kontodaten von Zahlungsinstrumenten im EasySKS-Repo

### Browser-Speicher

Im Frontend werden aktuell lokal gespeichert:

- Auth-Session in `localStorage` mit `accessToken`, `idToken`, optional `refreshToken` und `expiresAt`
- PKCE-Login-Status in `sessionStorage`
- ein lokaler Welcome-Overlay-Status pro Benutzer in `localStorage`

## 4. Zwecke der Verarbeitung

Die aktuell belegbaren Zwecke sind:

- Bereitstellung des Benutzerkontos und Authentifizierung
- Synchronisierung des lokalen EasySKS-Nutzers mit Cognito
- Speicherung und Anzeige von Profilangaben
- Durchfuehrung von Lern-, Exam- und Navigation-Sessions
- Speicherung von Lernfortschritt, Review-Verlauf und Session-Ergebnissen
- Verwaltung von Premium-Berechtigungen und Stripe-Abos
- Bewertung von Freitextantworten, inklusive optionaler KI-Auswertung
- Fehlerbehandlung, Sicherheit und Betriebsfaehigkeit des Systems

## 5. Empfaenger und externe Dienste

Die nach aktuellem Repo-Stand klar erkennbaren externen Empfaenger sind in `/legal/subprocessors` dokumentiert. Dazu gehoeren insbesondere:

- AWS Cognito fuer Login und Identitaetsdaten
- Stripe fuer Checkout, Subscription-Verwaltung und Webhooks
- OpenAI fuer KI-Auswertung von Freitextantworten, wenn eine API-Konfiguration aktiv ist
- externer Hosting-/Infrastruktur-Betrieb fuer App und Datenbank; konkreter Anbieter im Repo derzeit nicht benannt

## 6. KI-Auswertung von Freitextantworten

Wenn die KI-Auswertung aktiviert ist, koennen Freitextantworten zusammen mit Aufgabenkontext und Referenzantworten an OpenAI uebermittelt werden. Laut aktuellem Produktstand betrifft das:

- Exam-Freitextantworten
- Navigation-Freitextantworten
- Study-/Practice-Freitextantworten

Ist keine passende OpenAI-Konfiguration gesetzt, faellt das System laut Code auf heuristische Bewertungen zurueck.

## 7. Mobilnummer

Die Mobilnummer ist im aktuellen Produktstand Teil des Pflichtprofils. Der Code belegt derzeit folgende direkte Zwecke:

- Profilvollstaendigkeit fuer den Zugang zum Lernbereich
- Vermeidung doppelter Accounts ueber einen Unique Constraint

Der aktuelle Repo-Stand belegt noch keinen produktiven SMS-, OTP- oder telefonbasierten Login-Flow. Ob `mobile_number` fuer den Produktzweck wirklich erforderlich ist, ist daher noch als Produkt- und Rechtsfrage offen.

## 8. Aufbewahrung und Loeschung

Der aktuelle MVP-Ansatz ist in `/legal/data-retention` dokumentiert. Stand heute gilt:

- Es gibt noch keine vollstaendig automatisierte Self-Service-Loeschung
- Retention-, Export- und Loeschschritte sind aktuell als Runbook zu behandeln
- einzelne Produktdaten bleiben bestehen, bis ein manueller oder spaeter automatisierter Loeschprozess umgesetzt ist

## 9. Betroffenenrechte

Je nach anwendbarem Recht koennen insbesondere Rechte auf Auskunft, Berichtigung, Loeschung, Einschraenkung, Datenuebertragbarkeit und Widerspruch bestehen.

TODO: Verbindlichen Kontaktweg fuer solche Anfragen eintragen.

Bis ein Self-Service-Prozess vorhanden ist, sollten Anfragen intern nach dem Runbook in `/legal/dsar-runbook` bearbeitet werden.

## 10. Sicherheitshinweis

Das Repo dokumentiert selbst, dass Auth-Tokens im Frontend aktuell noch in `localStorage` gespeichert werden. Das ist als MVP-Zwischenstand zu behandeln und sollte vor oder kurz nach Launch durch eine haertere Session-Strategie ersetzt werden, zum Beispiel serverseitige Sessions oder `httpOnly`-Cookies.

## 11. Internationale Datenuebermittlungen

Da AWS, Stripe und OpenAI eingesetzt werden und der Hosting-Anbieter im Repo nicht abschliessend beschrieben ist, koennen Datenuebermittlungen ausserhalb des EWR nicht ausgeschlossen werden.

TODO: Vor Live-Gang die tatsaechlichen Anbieterstandorte, Transfermechanismen und vertraglichen Schutzmassnahmen ergaenzen.
