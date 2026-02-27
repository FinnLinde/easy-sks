# ESKS-019 - Account Plan Status und Billing Surface

- Status: `todo`
- Prioritaet: `P2`
- Bereich: `cross-cutting`
- Owner: `unassigned`

## Ziel / Business Value

Nutzer sollen im Account-Bereich klar sehen, welchen Plan sie haben, welche Entitlements aktiv sind und welchen Billing-Status das Abo hat.

## Kontext / Ist-Stand

- Account-UI zeigt aktuell nur Token-basierte Rollen.
- Stripe/Billing-Flows sind als Ticket ESKS-005 vorgesehen.
- Ein stabiler API-Surface fuer Plan-/Billing-Status fehlt im Frontend.

## Scope

- API fuer Account Summary (Plan, Entitlements, Billing-Status, Renewal/Cancel Dates).
- Frontend Account-Seite zeigt diese Felder mit passenden States.
- Status-Badges fuer `active`, `past_due`, `canceled`, `trialing`.

## Out of Scope

- Vollstaendige Checkout-/Portal-Implementierung.
- Historische Rechnungslisten.

## Technische Spezifikation

- Erweiterung des User-Account Endpoints oder eigener Endpoint `GET /account/summary`.
- Response enthaelt:
  - `plan: freemium|premium`
  - `entitlements: string[]`
  - `billing_status: string | null`
  - `renews_at: datetime | null`
  - `cancels_at: datetime | null`
- Wenn Billing nicht konfiguriert ist, liefert API konsistente `null`-Werte statt Fehler.

## API-Aenderungen

- Neu oder erweitert: Account Summary Endpoint + OpenAPI.

## DB-/Migrations-Aenderungen

- Abhaengig von ESKS-005 (Subscription-Persistenz).

## Frontend-Aenderungen

- `frontend/src/app/account/page.tsx` auf Account Summary API umstellen.
- Neue Plan/Billing Panels inkl. Loading/Error/Empty States.

## Infra-Aenderungen

- `none` fuer UI-Scope; Stripe-Infra siehe ESKS-005.

## Akzeptanzkriterien

- [ ] Account zeigt Plan + Entitlements aus API.
- [ ] Billing-Status wird mit klaren Badges dargestellt.
- [ ] Fehlen von Billing-Daten fuehrt nicht zu UI-Absturz.

## Testplan

- Backend Unit/Integration fuer Summary Mapping.
- Frontend Component Tests fuer Statusvarianten.
- Manuell: freemium vs premium vs canceled/past_due.

## Abhaengigkeiten

- ESKS-005 Stripe Subscription Billing.

## Progress-Checklist

- [ ] API-Vertrag definieren und implementieren.
- [ ] Frontend-Integration bauen.
- [ ] Status-Badges und Fallbacks testen.

## Offene Fragen

- Kommt die Wahrheit fuer `plan` primaer aus Entitlements oder aus Billing-Status?
