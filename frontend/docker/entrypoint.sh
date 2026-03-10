#!/bin/sh
set -eu

RUNTIME_CONFIG_PATH="/usr/share/nginx/html/runtime-config.js"

escape_js() {
  printf '%s' "$1" | sed 's/\\/\\\\/g; s/"/\\"/g'
}

write_optional_setting() {
  key="$1"
  value="$2"

  if [ -n "$value" ]; then
    printf '  %s: "%s",\n' "$key" "$(escape_js "$value")"
  fi
}

{
  echo "window.__EASY_SKS_RUNTIME_CONFIG__ = {"
  write_optional_setting "apiUrl" "${RUNTIME_API_URL:-}"
  write_optional_setting "cognitoDomain" "${RUNTIME_COGNITO_DOMAIN:-}"
  write_optional_setting "cognitoClientId" "${RUNTIME_COGNITO_CLIENT_ID:-}"
  write_optional_setting "cognitoRedirectUri" "${RUNTIME_COGNITO_REDIRECT_URI:-}"
  write_optional_setting "cognitoLogoutUri" "${RUNTIME_COGNITO_LOGOUT_URI:-}"
  write_optional_setting "cognitoScopes" "${RUNTIME_COGNITO_SCOPES:-}"
  echo "};"
} > "$RUNTIME_CONFIG_PATH"

exec "$@"
