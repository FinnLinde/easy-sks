# Stripe Sandbox Setup

## Test-mode resources

1. Open Stripe in test mode.
2. Create one `Product` for the premium plan.
3. Create one recurring `Price` and copy the resulting `price_*` value.
4. Create a webhook endpoint for `https://dev.api.example.com/billing/webhook/stripe`.
5. Subscribe the endpoint to:
   - `checkout.session.completed`
   - `customer.subscription.updated`
   - `customer.subscription.deleted`

## Environment values to capture

- `STRIPE_SECRET_KEY`
- `STRIPE_WEBHOOK_SECRET`
- `STRIPE_PRICE_ID_PREMIUM`
- `STRIPE_CHECKOUT_SUCCESS_URL`
- `STRIPE_CHECKOUT_CANCEL_URL`
- `STRIPE_PORTAL_RETURN_URL`

These values map directly to the backend settings in `backend/billing/service/stripe_config.py`.

## Where to store them

- Put the full dev environment file into the GitHub environment secret `DEV_ENV_FILE`.
- Put the full prod environment file into the GitHub environment secret `PROD_ENV_FILE`.
- Use `.env.dev.example` and `.env.prod.example` as the starting template.

## Dev webhook caveat

The dev UI and most dev API routes are intended to stay VPN-only. Stripe cannot reach a private WireGuard address, so the reverse proxy allows only `POST /billing/webhook/stripe` on the dev API host from the public internet. All other dev routes remain restricted to the WireGuard subnet.

## Verification checklist

1. Start checkout from the app and confirm Stripe creates a checkout session.
2. Complete a test purchase with Stripe's test card.
3. Confirm the webhook updates `subscriptions` and `billing_customers`.
4. Open the customer portal from the account screen.
5. Cancel the subscription in test mode and confirm the local premium entitlement is removed.
