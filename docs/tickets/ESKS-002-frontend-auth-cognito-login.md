# ESKS-002 - Frontend Cognito Login und Token-Injektion

- Status: `done`
- Prioritaet: `P0`
- Bereich: `frontend`
- Owner: `unassigned`

## Ziel / Business Value

Nutzer koennen sich anmelden und die bereits geschuetzten Study-Endpunkte im Frontend nutzen.

## Kontext / Ist-Stand

- Backend verlangt Bearer-Token fuer Study/Card-Routen.
- Frontend-API-Client sendet aktuell keine `Authorization`-Header (`frontend/src/services/api/client.ts`).
- Study-UI existiert bereits (`frontend/src/components/study/study-session.tsx`).
- Cognito User Pool und App Clients sind per Terraform vorhanden (`infrastructure/cognito.tf`).

## Scope

- Login/Logout-Flow im Frontend (Cognito).
- Token-Verwaltung (ID/Access/Refresh je nach gewaehltem Flow).
- API-Client erweitert um Bearer-Token.
- Route-/Page-Handling fuer nicht eingeloggte Nutzer.
- Basis-Session-Status im UI (eingeloggt / ausgeloggt / loading).

## Out of Scope

- Billing/Checkout
- Premium-Upsell-UX
- Komplette Account-Verwaltung

## Technische Spezifikation

- Empfohlener MVP: Cognito Hosted UI mit Authorization Code Flow (PKCE).
- Frontend-Komponenten:
  - `AuthProvider` / Session-Store
  - `useAuth()` Hook
  - Login/Logout Buttons
- Token-Speicher:
  - Bevorzugt sichere Session-Loesung (Server-side Session oder httpOnly Cookie)
  - Falls MVP rein Client-seitig: Risiko dokumentieren und begrenzen
- API-Client:
  - Bearer-Token pro Request injizieren
  - 401-Behandlung (Session invalid -> Logout/Retry/Login Prompt)
- UX:
  - `/study` zeigt Login-Aufforderung statt generischer Fehlermeldung
  - `/` (Dashboard) kann zunaechst Auth-gated Placeholder sein

## API-Aenderungen

- Keine Backend-Endpunkt-Aenderung zwingend erforderlich.
- Optional spaeter `GET /me` fuer Session-Anzeige (`ESKS-003`/Folgeticket).

## DB-/Migrations-Aenderungen

- `none`

## Frontend-Aenderungen

- Auth-Konfiguration (Cognito Domain, Client ID, Redirect URLs)
- API-Client Interceptor/Wrapper fuer `Authorization`
- Login-/Logout-UI
- Session Guard fuer geschuetzte Bereiche
- Fehler- und Ladezustands-UX fuer Auth

## Implementierungsstand (2026-02-25)

- Umgesetzt (MVP):
  - Cognito Hosted UI Login via Authorization Code + PKCE (clientseitig)
  - Callback-Route `/auth/callback` mit Token-Austausch
  - `AuthProvider` + `useAuth()` + LocalStorage Session (MVP Tradeoff)
  - API-Client injiziert Bearer-Token automatisch
  - 401 fuehrt zu lokalem Logout + Re-Login-Zustand
  - Login/Logout UI in Sidebar + Mobile Header
  - `/study` ist auth-guarded mit Login-Aufforderung
- Noch offen / bewusst verschoben:
  - Refresh-Token-Renewal (aktuell Ablauf => Re-Login)
  - Serverseitige Session/httpOnly Cookie (haertere Security-Variante)

## Infra-Aenderungen

- Sicherstellen, dass Cognito Callback-/Logout-URLs fuer lokale und produktive Frontend-URLs korrekt gesetzt sind.
- Ggf. Cognito Hosted UI Domain konfigurieren (falls noch nicht vorhanden).

## Akzeptanzkriterien

- [x] Nicht eingeloggte Nutzer erhalten auf `/study` eine klare Login-Aufforderung.
- [x] Nach erfolgreichem Login kann der Nutzer Due-Cards laden.
- [x] API-Requests an geschuetzte Endpunkte enthalten Bearer-Token.
- [x] Ungueltige/abgelaufene Session fuehrt zu sauberem Re-Login-Flow.

## Testplan

- Unit Tests:
  - Session-Store / Auth-Utility
- Integration/UI Tests:
  - Guard-Verhalten bei nicht eingeloggtem Nutzer
  - API-Client Header-Injektion
- Manuell:
  - Login, Page Refresh, Logout

## Abhaengigkeiten

- Terraform Cognito App Client (`infrastructure/cognito.tf`)
- Umgebungsvariablen fuer Frontend-Auth-Konfiguration

## Progress-Checklist

- [x] Auth-Flow-Variante festlegen (Hosted UI + PKCE empfohlen)
- [x] Frontend Auth-Konfiguration anlegen
- [x] Session-Provider / Hook implementieren
- [x] API-Client um Bearer-Token erweitern
- [x] `/study` Auth-Guard integrieren
- [x] Login/Logout UI ergaenzen
- [x] 401-Handling implementieren
- [x] Manuelle E2E-Pruefung lokal dokumentieren

## Offene Fragen

- Hosted UI vs. SDK-basierter Login?
- Sollen Tokens clientseitig gespeichert werden oder via serverseitiger Session abstrahiert werden?
- MVP-Entscheidung getroffen: clientseitige Speicherung in `localStorage` fuer schnelle Integration; spaeter auf serverseitige Session umstellen.

## Manuelle E2E-Validierung

- Datum: `2026-02-27`
- Ergebnis: Login via Cognito erfolgreich, danach koennen Due-Cards in `/study` geladen werden.
