# AGB und Subscription Terms

Stand: 2026-03-10

Dieser Text ist ein Produkt- und UX-naher Entwurf fuer `ESKS-025`. Fehlende Anbieter-, Preis- und Verbraucherangaben muessen vor dem Live-Gang vervollstaendigt und rechtlich geprueft werden.

## 1. Vertragspartner

TODO: Vollstaendigen Anbieter eintragen.

TODO: Anschrift, Kontakt, Rechtsform und ggf. Registerdaten aus dem Impressum uebernehmen.

## 2. Produkt

EasySKS ist nach aktuellem Repo-Stand eine digitale Lernanwendung fuer den Sportkuestenschifferschein.

Der Leistungsumfang umfasst im MVP insbesondere:

- Zugang zu einem persoenlichen Benutzerkonto
- Lernkarten, Wiederholungsplanung und Fortschrittsspeicherung
- Exam- und Navigation-Simulationen
- optional KI-gestuetzte Bewertung bestimmter Freitextantworten
- Premium-Funktionen ueber ein Stripe-basiertes Abo

## 3. Konto und Zugang

- Der Zugang setzt aktuell ein Cognito-basiertes Benutzerkonto voraus.
- Im aktuellen Produktstand muss das Profil fuer den Vollzugang mindestens `full_name` und `mobile_number` enthalten.
- Die Mobilnummer bleibt ein offener Punkt fuer Datenminimierung und bedarf vor Launch einer finalen Produktentscheidung.

## 4. Premium-Abo

Nach dem aktuellen Produktstand gilt fuer das Premium-Abo:

- Der Abschluss erfolgt ueber Stripe Checkout.
- Das Abo ist wiederkehrend und verlaengert sich automatisch, bis es beendet wird.
- Die Verwaltung und Kuendigung erfolgen ueber das Stripe Customer Portal.
- Der lokale Billing-Status in EasySKS wird ueber Stripe-Webhooks synchronisiert.

## 5. Preis und Abrechnungsintervall

TODO: Verbindlichen Premium-Preis eintragen.

TODO: Verbindliches Abrechnungsintervall eintragen, zum Beispiel monatlich oder jaehrlich.

Bis diese Angaben final feststehen, darf EasySKS keine abschliessenden Preiszusagen ausserhalb des Stripe-Checkouts machen.

## 6. Laufzeit und Kuendigung

Nach dem derzeitigen Implementierungsstand soll gelten:

- Kuendigungen werden ueber Stripe verwaltet.
- Eine Beendigung soll zum Ende des laufenden Abrechnungszeitraums wirksam werden.
- Der in EasySKS sichtbare Plan- und Billing-Status folgt der Synchronisation aus Stripe.

TODO: Finalen Wortlaut zur Laufzeit, eventuellen Testphasen und Kuendigungsfristen rechtlich freigeben.

## 7. Digitale Leistungen und Verfuegbarkeit

- EasySKS wird als Online-Dienst bereitgestellt.
- Einzelne Funktionen, insbesondere KI-Auswertung und Billing, koennen von externen Diensten abhaengen.
- Es werden derzeit keine verbindlichen Verfuegbarkeits-, SLA- oder Support-Zusagen aus dem Repo abgeleitet.

## 8. KI-Hinweis

Wenn KI-Auswertung aktiv ist, koennen Freitextantworten an einen externen KI-Dienst uebermittelt werden. Die Funktion dient als Lernhilfe und ersetzt keine amtliche Bewertung oder rechtliche Beratung.

## 9. Haftung und Gewaehrleistung

TODO: Rechtlich gepruefte Haftungs- und Gewaehrleistungsklauseln einfuegen.

## 10. Verbraucherinformationen

Verbraucherrelevante Hinweise zu digitalen Leistungen, Widerruf und etwaigen Refund-Regeln sind separat in `/legal/withdrawal-and-refund` zu pflegen.

## 11. Schlussbestimmungen

TODO: Anwendbares Recht, Gerichtsstand und eventuelle B2B/B2C-Differenzierung erst nach rechtlicher Klaerung ergaenzen.
