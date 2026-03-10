#!/usr/bin/env bash
set -euo pipefail

if [ "$#" -ne 1 ]; then
  echo "Usage: $0 <dev|prod>" >&2
  exit 1
fi

STACK="$1"
case "$STACK" in
  dev|prod) ;;
  *)
    echo "Unsupported stack: $STACK" >&2
    exit 1
    ;;
esac

EASY_SKS_ROOT="${EASY_SKS_ROOT:-/opt/easy-sks}"
COMPOSE_DIR="${COMPOSE_DIR:-$EASY_SKS_ROOT/shared/compose}"
STACK_DIR="$EASY_SKS_ROOT/$STACK"
ENV_FILE="$STACK_DIR/.env"

if [ ! -f "$ENV_FILE" ]; then
  echo "Missing env file: $ENV_FILE" >&2
  exit 1
fi

export COMPOSE_PROJECT_NAME="${COMPOSE_PROJECT_NAME:-easy-sks-$STACK}"

compose_args=(
  --env-file "$ENV_FILE"
  -f "$COMPOSE_DIR/docker-compose.base.yml"
  -f "$COMPOSE_DIR/docker-compose.$STACK.yml"
)

docker compose "${compose_args[@]}" pull
docker compose "${compose_args[@]}" run --rm backend alembic upgrade head
docker compose "${compose_args[@]}" up -d --remove-orphans
