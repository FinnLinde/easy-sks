import { consumePkceRequest, savePkceRequest } from "@/auth/storage";
import type { AuthSession } from "@/auth/types";

type CognitoConfig = {
  domain: string;
  clientId: string;
  redirectUri: string;
  logoutUri: string;
  scopes: string;
};

type TokenResponse = {
  access_token: string;
  id_token: string;
  refresh_token?: string;
  expires_in: number;
  token_type: string;
};

function requireBrowserOrigin() {
  if (typeof window === "undefined") {
    throw new Error("Browser context required");
  }
  return window.location.origin;
}

function normalizeDomain(domain: string): string {
  return domain.replace(/\/+$/, "");
}

function getConfig(): CognitoConfig {
  const origin = requireBrowserOrigin();
  const domain = process.env.NEXT_PUBLIC_COGNITO_DOMAIN;
  const clientId = process.env.NEXT_PUBLIC_COGNITO_CLIENT_ID;

  if (!domain || !clientId) {
    throw new Error(
      "Missing Cognito config. Set NEXT_PUBLIC_COGNITO_DOMAIN and NEXT_PUBLIC_COGNITO_CLIENT_ID."
    );
  }

  return {
    domain: normalizeDomain(domain),
    clientId,
    redirectUri:
      process.env.NEXT_PUBLIC_COGNITO_REDIRECT_URI ?? `${origin}/auth/callback`,
    logoutUri: process.env.NEXT_PUBLIC_COGNITO_LOGOUT_URI ?? origin,
    scopes: process.env.NEXT_PUBLIC_COGNITO_SCOPES ?? "openid email profile",
  };
}

function randomString(length = 64): string {
  const bytes = new Uint8Array(length);
  crypto.getRandomValues(bytes);
  return Array.from(bytes, (b) => (b % 36).toString(36)).join("");
}

function toBase64Url(bytes: ArrayBuffer): string {
  const chars = Array.from(new Uint8Array(bytes), (b) =>
    String.fromCharCode(b)
  ).join("");
  return btoa(chars).replace(/\+/g, "-").replace(/\//g, "_").replace(/=+$/g, "");
}

async function sha256(value: string): Promise<ArrayBuffer> {
  const data = new TextEncoder().encode(value);
  return crypto.subtle.digest("SHA-256", data);
}

async function createPkceChallenge(codeVerifier: string): Promise<string> {
  const digest = await sha256(codeVerifier);
  return toBase64Url(digest);
}

export async function redirectToCognitoLogin(returnTo?: string) {
  const config = getConfig();
  const codeVerifier = randomString(64);
  const state = randomString(32);
  const codeChallenge = await createPkceChallenge(codeVerifier);

  savePkceRequest({
    codeVerifier,
    state,
    returnTo: returnTo ?? window.location.pathname ?? "/study",
  });

  const url = new URL(`${config.domain}/oauth2/authorize`);
  url.searchParams.set("response_type", "code");
  url.searchParams.set("client_id", config.clientId);
  url.searchParams.set("redirect_uri", config.redirectUri);
  url.searchParams.set("scope", config.scopes);
  url.searchParams.set("state", state);
  url.searchParams.set("code_challenge_method", "S256");
  url.searchParams.set("code_challenge", codeChallenge);

  window.location.assign(url.toString());
}

export function redirectToCognitoLogout() {
  const config = getConfig();
  const url = new URL(`${config.domain}/logout`);
  url.searchParams.set("client_id", config.clientId);
  url.searchParams.set("logout_uri", config.logoutUri);
  window.location.assign(url.toString());
}

export async function exchangeCodeForSession(
  code: string,
  stateFromUrl: string | null
): Promise<{ session: AuthSession; returnTo: string }> {
  const config = getConfig();
  const pkce = consumePkceRequest();

  if (!pkce) {
    throw new Error("Login-Status fehlt. Bitte Login erneut starten.");
  }
  if (!stateFromUrl || pkce.state !== stateFromUrl) {
    throw new Error("Ungültiger Login-Status (State stimmt nicht überein).");
  }

  const body = new URLSearchParams();
  body.set("grant_type", "authorization_code");
  body.set("client_id", config.clientId);
  body.set("code", code);
  body.set("redirect_uri", config.redirectUri);
  body.set("code_verifier", pkce.codeVerifier);

  const response = await fetch(`${config.domain}/oauth2/token`, {
    method: "POST",
    headers: {
      "Content-Type": "application/x-www-form-urlencoded",
    },
    body: body.toString(),
  });

  if (!response.ok) {
    throw new Error("Token-Austausch mit Cognito fehlgeschlagen.");
  }

  const tokenData = (await response.json()) as TokenResponse;
  const now = Date.now();

  return {
    session: {
      accessToken: tokenData.access_token,
      idToken: tokenData.id_token,
      refreshToken: tokenData.refresh_token ?? null,
      expiresAt: now + tokenData.expires_in * 1000,
    },
    returnTo: pkce.returnTo || "/study",
  };
}
