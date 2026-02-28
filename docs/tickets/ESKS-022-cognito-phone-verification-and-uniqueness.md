# ESKS-022 - Cognito-first Mobilnummer-Verifikation und Eindeutigkeit

- Status: `todo`
- Prioritaet: `P1`
- Bereich: `cross-cutting`
- Owner: `unassigned`

## Ziel / Business Value

Mobilnummer und Verifikationsstatus sollen aus Cognito als Single Source of Truth kommen, damit Identitaetsdaten nicht zwischen lokalem DB-Status und IdP divergieren.

## Kontext / Ist-Stand

- ESKS-020 fuehrt lokale Profilfelder `full_name`, `mobile_number`, `mobile_verified_at` ein.
- Aktuell ist die Mobilnummer-Eindeutigkeit lokal ueber DB-Constraint abgesichert.
- Cognito-Login ist bereits in Betrieb.
- Fuer Cognito-only Verifikation muessen Token/Claims, User-Pool-Konfiguration und ggf. Terraform angepasst werden.

## Scope

- Zielarchitektur fuer Cognito als Source of Truth fuer `phone_number` und `phone_number_verified`.
- Implementierung eines Verifikationsflows auf Cognito-Basis (Update + OTP verify).
- Backend liest Verifikationsstatus aus Cognito-Claims oder Cognito UserInfo/GetUser.
- Eindeutigkeitsstrategie fuer Mobilnummer auf Cognito-Ebene definieren und umsetzen.
- Terraform-Anpassungen fuer User Pool / App Client / SMS-Setup.

## Out of Scope

- Komplette Migration historischer Nutzer auf einen neuen User Pool ohne abgestimmtes Migrationskonzept.
- Multi-Provider-Strategie (Twilio Verify etc.) im gleichen Ticket.

## Technische Spezifikation

- Cognito Claim-Quelle:
  - bevorzugt `phone_number_verified` aus Token-Claims oder UserInfo/GetUser.
  - Backend darf keinen separaten lokalen "verified" Wahrheitswert fuehren.
- Verifikationsflow:
  1. Nutzer setzt/aktualisiert `phone_number` via Cognito API.
  2. Cognito sendet OTP.
  3. Nutzer bestaetigt OTP via Cognito Verify-API.
  4. Backend/UI lesen nur noch Cognito-Status.
- Eindeutigkeit:
  - Pruefen, ob aktueller Pool strikte Eindeutigkeit fuer `phone_number` ermoeglicht.
  - Falls nicht moeglich: Migrationspfad fuer neuen Pool (oder klar dokumentierte Zwischenstrategie).
- Lokale Felder:
  - lokale Persistenz fuer Mobilnummer nur als Cache/Read-Model oder auslaufend.
  - kein divergierender Business-Status gegenueber Cognito.

## API-Aenderungen

- Wahrscheinlich Erweiterung von `/me`:
  - `phone_number` (aus Cognito)
  - `phone_number_verified` (aus Cognito)
- Neue Endpunkte (oder Backend-Proxies) fuer:
  - Start Verifikation
  - OTP bestaetigen

## DB-/Migrations-Aenderungen

- Optional: lokale Felder fuer Mobilnummer-Verifikation deprecaten oder auf Read-Model reduzieren.
- Kein neuer lokaler "verified" Business-Status als Source of Truth.

## Frontend-Aenderungen

- Profil-/Onboarding-Flow um OTP-Eingabe fuer Mobilnummer erweitern.
- Gateing nicht nur auf "Nummer vorhanden", sondern auf "Nummer verifiziert".
- Fehlermeldungen fuer OTP, Timeout, Retry und Konfliktfaelle.

## Infra-Aenderungen

- Terraform wahrscheinlich notwendig:
  - User Pool Attribute / Sign-in-Konfiguration pruefen (Eindeutigkeit/aliases).
  - App Client Scopes (`phone`) und Token-Claim-Strategie.
  - SMS-Konfiguration (IAM role, external id, region constraints).
  - Ggf. Pre Token Generation Trigger fuer Claim-Anreicherung.
- Hinweis:
  - Teile der User-Pool-Sign-in-Konfiguration sind nach Erstellung nicht in-place aenderbar.
  - ggf. neuer Pool + Migrationsplan notwendig.

## Akzeptanzkriterien

- [ ] `/me` zeigt `phone_number` + verifizierten Status aus Cognito.
- [ ] Nutzer kann Mobilnummer per OTP ueber Cognito verifizieren.
- [ ] Verifikationsstatus wird nach erfolgreicher OTP-Bestaetigung korrekt reflektiert.
- [ ] Eindeutigkeitsstrategie fuer Mobilnummer ist umgesetzt und dokumentiert (inkl. Pool-Limitierungen).
- [ ] Terraform und Betriebsdokumentation sind konsistent mit der gewaehlten Strategie.

## Testplan

- Backend Integration:
  - Claims/UserInfo Mapping in `/me`.
  - Fehlerfaelle bei Verify-Flow (ungultiger Code, abgelaufen, zu viele Versuche).
- Frontend:
  - OTP-UX + Fehlerzustaende.
  - Gateing fuer unverifizierte Nummern.
- Manuell:
  - End-to-end mit realem Cognito Test-Client in Dev.

## Abhaengigkeiten

- ESKS-020 (Profil-Hardening Basis).
- Entscheidung, ob bestehender User Pool die gewuenschte Eindeutigkeit leisten kann.

## Progress-Checklist

- [ ] Cognito-Konfigurationsanalyse (aktueller Pool vs. Zielanforderung).
- [ ] Terraform-Aenderungsplan inkl. evtl. Migrationspfad.
- [ ] Backend Claim/Verify-Flow implementieren.
- [ ] Frontend OTP-Flow und Gateing umsetzen.
- [ ] Tests und Betriebsdoku ergaenzen.

## Offene Fragen

- Ist ein neuer User Pool akzeptabel, falls der aktuelle Pool strikte Mobilnummer-Eindeutigkeit nicht in-place unterstuetzt?
