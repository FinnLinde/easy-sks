#!/usr/bin/env bash
set -euo pipefail

if [ "$(id -u)" -ne 0 ]; then
  echo "Run this script as root." >&2
  exit 1
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

DEPLOY_USER="${DEPLOY_USER:-deploy}"
EASY_SKS_ROOT="${EASY_SKS_ROOT:-/opt/easy-sks}"

DEV_APP_DOMAIN="${DEV_APP_DOMAIN:-dev.app.example.com}"
DEV_API_DOMAIN="${DEV_API_DOMAIN:-dev.api.example.com}"
PROD_APP_DOMAIN="${PROD_APP_DOMAIN:-app.example.com}"
PROD_API_DOMAIN="${PROD_API_DOMAIN:-api.example.com}"

DEV_FRONTEND_PORT="${DEV_FRONTEND_PORT:-13000}"
DEV_BACKEND_PORT="${DEV_BACKEND_PORT:-18000}"
PROD_FRONTEND_PORT="${PROD_FRONTEND_PORT:-23000}"
PROD_BACKEND_PORT="${PROD_BACKEND_PORT:-28000}"

WIREGUARD_PORT="${WIREGUARD_PORT:-51820}"
WIREGUARD_ALLOWED_CIDR="${WIREGUARD_ALLOWED_CIDR:-10.20.0.0/24}"
WIREGUARD_SERVER_IP="${WIREGUARD_SERVER_IP:-10.20.0.1}"
PUBLIC_INTERFACE="${PUBLIC_INTERFACE:-$(ip route list default | awk '/default/ {print $5; exit}')}"

render_template() {
  template_path="$1"
  destination_path="$2"

  sed \
    -e "s|__DEV_APP_DOMAIN__|$DEV_APP_DOMAIN|g" \
    -e "s|__DEV_API_DOMAIN__|$DEV_API_DOMAIN|g" \
    -e "s|__PROD_APP_DOMAIN__|$PROD_APP_DOMAIN|g" \
    -e "s|__PROD_API_DOMAIN__|$PROD_API_DOMAIN|g" \
    -e "s|__WIREGUARD_ALLOWED_CIDR__|$WIREGUARD_ALLOWED_CIDR|g" \
    -e "s|__DEV_FRONTEND_PORT__|$DEV_FRONTEND_PORT|g" \
    -e "s|__DEV_BACKEND_PORT__|$DEV_BACKEND_PORT|g" \
    -e "s|__PROD_FRONTEND_PORT__|$PROD_FRONTEND_PORT|g" \
    -e "s|__PROD_BACKEND_PORT__|$PROD_BACKEND_PORT|g" \
    -e "s|__WIREGUARD_SERVER_IP__|$WIREGUARD_SERVER_IP|g" \
    -e "s|__WIREGUARD_PORT__|$WIREGUARD_PORT|g" \
    -e "s|__PUBLIC_INTERFACE__|$PUBLIC_INTERFACE|g" \
    -e "s|__WIREGUARD_SERVER_PRIVATE_KEY__|$WIREGUARD_SERVER_PRIVATE_KEY|g" \
    "$template_path" > "$destination_path"
}

apt-get update
apt-get install -y \
  ca-certificates \
  caddy \
  curl \
  docker.io \
  docker-compose-plugin \
  git \
  gnupg \
  lsb-release \
  ufw \
  wireguard

systemctl enable --now docker
systemctl enable --now caddy

if ! id -u "$DEPLOY_USER" >/dev/null 2>&1; then
  useradd --create-home --shell /bin/bash "$DEPLOY_USER"
fi
usermod -aG docker "$DEPLOY_USER"

mkdir -p \
  "$EASY_SKS_ROOT/shared/compose" \
  "$EASY_SKS_ROOT/dev" \
  "$EASY_SKS_ROOT/prod"
chown -R "$DEPLOY_USER:$DEPLOY_USER" "$EASY_SKS_ROOT"

install -d -m 700 /etc/wireguard
install -d -m 700 /etc/wireguard/keys

if [ ! -f /etc/wireguard/keys/server.key ]; then
  wg genkey | tee /etc/wireguard/keys/server.key | wg pubkey > /etc/wireguard/keys/server.pub
  chmod 600 /etc/wireguard/keys/server.key
  chmod 644 /etc/wireguard/keys/server.pub
fi

WIREGUARD_SERVER_PRIVATE_KEY="$(tr -d '\n' < /etc/wireguard/keys/server.key)"

cat > /etc/sysctl.d/99-easy-sks-forwarding.conf <<'EOF'
net.ipv4.ip_forward = 1
net.ipv6.conf.all.forwarding = 1
EOF
sysctl --system

if grep -q '^DEFAULT_FORWARD_POLICY=' /etc/default/ufw; then
  sed -i 's/^DEFAULT_FORWARD_POLICY=.*/DEFAULT_FORWARD_POLICY="ACCEPT"/' /etc/default/ufw
fi

ufw allow 22/tcp
ufw allow 80/tcp
ufw allow 443/tcp
ufw allow "${WIREGUARD_PORT}/udp"
ufw --force enable

render_template "$REPO_ROOT/infra/wireguard/wg0.conf.template" /etc/wireguard/wg0.conf
chmod 600 /etc/wireguard/wg0.conf

render_template "$REPO_ROOT/infra/Caddyfile" /etc/caddy/Caddyfile

install -m 755 "$REPO_ROOT/infra/deploy-stack.sh" "$EASY_SKS_ROOT/shared/compose/deploy-stack.sh"
install -m 644 "$REPO_ROOT/docker-compose.base.yml" "$EASY_SKS_ROOT/shared/compose/docker-compose.base.yml"
install -m 644 "$REPO_ROOT/docker-compose.dev.yml" "$EASY_SKS_ROOT/shared/compose/docker-compose.dev.yml"
install -m 644 "$REPO_ROOT/docker-compose.prod.yml" "$EASY_SKS_ROOT/shared/compose/docker-compose.prod.yml"

systemctl enable wg-quick@wg0
systemctl restart wg-quick@wg0
systemctl reload caddy

echo "Bootstrap complete."
echo "WireGuard server public key:"
cat /etc/wireguard/keys/server.pub
