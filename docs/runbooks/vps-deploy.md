# VPS Deploy Runbook

## One-time bootstrap

1. Provision a fresh Ubuntu VPS.
2. Clone this repository onto the server or copy the `infra` and compose files over.
3. Run `sudo ./infra/bootstrap-vps.sh` with environment variables for your domains if they differ from the defaults.
4. Create one WireGuard client config from `infra/wireguard/dev-client.conf.template`.
5. Connect a client to the VPN and confirm `dev.app` and `dev.api` are reachable only through the tunnel.

## Required GitHub environment secrets

### `dev`

- `VPS_HOST`
- `VPS_PORT`
- `VPS_USER`
- `VPS_SSH_KEY`
- `GHCR_READ_TOKEN`
- `DEV_ENV_FILE`

### `prod`

- `VPS_HOST`
- `VPS_PORT`
- `VPS_USER`
- `VPS_SSH_KEY`
- `GHCR_READ_TOKEN`
- `PROD_ENV_FILE`

## Deployment flow

1. Push to `main`.
2. `Build and Push Images` publishes immutable backend and frontend images tagged with the commit SHA.
3. `Deploy Dev` copies the compose files to the VPS, writes `/opt/easy-sks/dev/.env`, runs migrations, and updates the dev stack.
4. `Deploy Prod` is triggered manually, checks out the selected git ref, builds fresh production images, pushes them to GHCR, and deploys the resulting tag to prod.

## Remote layout

- `/opt/easy-sks/shared/compose`
- `/opt/easy-sks/dev/.env`
- `/opt/easy-sks/prod/.env`

## Operational notes

- Both stacks bind only to `127.0.0.1`; Caddy is the only public entry point.
- `dev.app` and most of `dev.api` are limited to the WireGuard subnet.
- `dev.api/billing/webhook/stripe` stays public so Stripe test webhooks can reach it.
- The frontend image is environment-agnostic because runtime config is generated at container start, but prod no longer depends on reusing the exact dev image tag.
