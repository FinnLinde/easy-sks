# ESKS-020 - Registrierung und Profil-Hardening (Name + Mobilnummer)

- Status: `todo`
- Prioritaet: `P1`
- Bereich: `cross-cutting`
- Owner: `unassigned`

## Ziel / Business Value

Nutzer sollen nach dem Login ein vollstaendiges Profil hinterlegen (voller Name, Mobilnummer), damit Accounts nicht unkontrolliert ueber verschiedene E-Mails entstehen und Nutzer sauber identifizierbar bleiben.

## Kontext / Ist-Stand

- Auth basiert auf Cognito Login.
- Lokaler User wird ueber Cognito-Sub provisioniert.
- Es gibt noch keinen verpflichtenden Registrierungs-/Onboarding-Schritt fuer Profilfelder.

## Scope

- Profilfelder einfuehren: `full_name`, `mobile_number`.
- Onboarding-Flow nach erstem Login, wenn Pflichtfelder fehlen.
- Backend-Validierung und Persistenz der Profilfelder.
- UI fuer Profilpflege im Account-Bereich.
- Grundlegende Strategie gegen Mehrfachaccounts ueber unterschiedliche E-Mails.

## Out of Scope

- Vollstaendige KYC/Ident-Verifikation.
- Externe CRM-/SMS-Integrationen.

## Technische Spezifikation

- User-Datenmodell erweitern um:
  - `full_name` (required nach Onboarding)
  - `mobile_number` (required nach Onboarding)
  - optional `mobile_verified_at` fuer spaetere Verifikation
- API:
  - `GET /me` liefert neue Felder + Profilvollstaendigkeit.
  - `PATCH /me/profile` zum Setzen/Aktualisieren von Name/Mobilnummer.
- Validation:
  - Name: Mindestlaenge, keine reinen Leerzeichen.
  - Mobilnummer: E.164-nahes Format fuer MVP (z. B. `+49...`).
- Mehrfachaccount-Schutz (MVP):
  - Mobilnummer eindeutig pro lokaler User (Unique Constraint).
  - Konfliktfall liefert klaren Fehlercode (z. B. `409 mobile_number_in_use`).
- Frontend:
  - Nach Login Redirect in Profil-Onboarding, wenn unvollstaendig.
  - Account-Seite zeigt und bearbeitet Profilfelder.

## API-Aenderungen

- Erweiterung `GET /me`.
- Neuer Endpoint `PATCH /me/profile`.

## DB-/Migrations-Aenderungen

- `users` Tabelle erweitern um `full_name`, `mobile_number`, optional `mobile_verified_at`.
- Unique Index auf `mobile_number` (nullable-handling beachten).

## Frontend-Aenderungen

- Onboarding-Seite/Modal fuer Erstprofil.
- Account-Form fuer Profilpflege.
- Fehlerbehandlung fuer Mobilnummer-Konflikte.

## Infra-Aenderungen

- `none` fuer MVP.

## Akzeptanzkriterien

- [ ] Nutzer mit unvollstaendigem Profil werden nach Login in den Profil-Onboarding-Flow geleitet.
- [ ] Name und Mobilnummer koennen gespeichert und ueber `/me` gelesen werden.
- [ ] Doppelte Mobilnummern werden serverseitig verhindert.
- [ ] UI zeigt valide Fehlermeldungen bei ungultigen/konfligierenden Eingaben.

## Testplan

- Backend Unit/Integration: Validierung, Update, Konfliktfall `409`.
- Frontend: Form-Validation, Error-Handling, Redirect-Flow.
- Manuell: neuer User, bestehender User, Konfliktfall.

## Abhaengigkeiten

- ESKS-003 (User-Provisioning)
- ESKS-019 (`/me` Account Surface)

## Progress-Checklist

- [ ] Datenmodell + Migration umsetzen.
- [ ] API fuer Profil-Update implementieren.
- [ ] Login-Onboarding-Gate im Frontend integrieren.
- [ ] Account-Profilform bauen.
- [ ] Tests + Doku ergaenzen.

## Offene Fragen

- Soll Mobilnummer bereits im MVP verifiziert werden (SMS-OTP) oder zunaechst nur erfasst werden?
