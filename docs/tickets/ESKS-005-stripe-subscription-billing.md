# ESKS-005 - Abo-Zahlung (Stripe) und Premium-Freischaltung

- Status: `todo`
- Prioritaet: `P1`
- Bereich: `cross-cutting`
- Owner: `unassigned`

## Ziel / Business Value

Nutzer koennen ein Premium-Abo abschliessen, verwalten und verlieren/erhalten Premium-Zugriff automatisch entsprechend dem Subscription-Status.

## Kontext / Ist-Stand

- Freemium/Premium-Rollen sind im Auth-Setup vorbereitet.
- Es gibt noch keine Billing-Integration, keine Webhooks, keine Subscription-Daten.

## Scope

- Stripe Checkout fuer Premium-Abo.
- Stripe Customer Portal.
- Backend-Webhooks zur Status-Synchronisation.
- Entitlement-/Rollen-Sync auf Premium/Freemium.
- Frontend Pricing/Checkout-Trigger (MVP).

## Out of Scope

- Mehrere Tarifstufen (MVP: ein Premium-Plan)
- Rechnungsdownload-UI (Customer Portal deckt das ab)

## Technische Spezifikation

- Stripe-Objekte:
  - Product + Price (extern in Stripe)
  - `customer`, `subscription`, `checkout.session`
- Backend:
  - Endpoint `POST /billing/checkout-session`
  - Endpoint `POST /billing/customer-portal-session`
  - Webhook `POST /billing/webhook/stripe`
  - Webhook Signature Verification
- Lokales Datenmodell (MVP):
  - `billing_customers` (`user_id`, `stripe_customer_id`)
  - `subscriptions` (`user_id`, `provider`, `provider_subscription_id`, `status`, `current_period_end`, `price_id`)
- Entitlement Sync:
  - Subscription `active`/`trialing` => Premium
  - `past_due`/`canceled`/`unpaid` je nach Policy behandeln
  - Optional Sync zu Cognito-Gruppe `premium` oder lokale Entitlement-Quelle bevorzugen
- Sicherheit:
  - Webhook nur signiert akzeptieren
  - Checkout immer userbezogen serverseitig erstellen

## API-Aenderungen

- Neue Endpunkte:
  - `POST /billing/checkout-session`
  - `POST /billing/customer-portal-session`
  - `POST /billing/webhook/stripe`
- Optional:
  - `GET /billing/subscription`

## DB-/Migrations-Aenderungen

- `billing_customers`
- `subscriptions`
- Indizes auf Provider-IDs und `user_id`

## Frontend-Aenderungen

- Pricing-/Upgrade-CTA
- Checkout Start Button
- "Abo verwalten" Button (Customer Portal)
- Statusanzeige (Premium aktiv / ausstehend / gekuendigt)

## Infra-Aenderungen

- Secrets fuer Stripe API Key + Webhook Secret
- Oeffentlich erreichbarer Webhook-Endpoint (Staging/Prod)
- Konfiguration Redirect-URLs fuer Checkout/Portal

## Akzeptanzkriterien

- [ ] Nutzer kann aus der App eine Stripe Checkout Session starten.
- [ ] Erfolgreicher Abschluss aktiviert Premium im System.
- [ ] Webhooks aktualisieren Subscription-Status idempotent.
- [ ] Nutzer kann Customer Portal oeffnen.
- [ ] Premium-Zugriff wird nach Statusaenderung korrekt gewaehrt/entzogen.

## Testplan

- Unit Tests:
  - Mapping Stripe Status -> internes Entitlement
- Integration Tests:
  - Webhook Verarbeitung (mit Signatur-Mock)
- Manuell (Stripe Testmode):
  - Checkout Erfolg
  - Abo kuendigen / Statusupdate

## Abhaengigkeiten

- `ESKS-003` (lokaler User + Entitlement-Basis)
- `ESKS-004` (Plan-Policy Enforcement)
- Produktentscheidung: Stripe als Provider (MVP empfohlen)

## Progress-Checklist

- [ ] Billing-Datenmodell definieren
- [ ] Migrationen erstellen
- [ ] Stripe SDK integrieren
- [ ] Checkout-Endpoint implementieren
- [ ] Customer-Portal-Endpoint implementieren
- [ ] Webhook-Endpoint + Verifikation implementieren
- [ ] Entitlement-Sync anbinden
- [ ] Frontend Upgrade-/Manage-UI bauen
- [ ] Stripe Testmode E2E pruefen

## Offene Fragen

- Soll Premium-Status primaer aus lokaler Subscription-Tabelle oder aus Cognito-Gruppen gelesen werden?
- Wie wird mit `past_due` umgegangen (Grace Period ja/nein)?

