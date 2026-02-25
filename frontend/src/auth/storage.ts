import type { AuthSession, StoredPkceRequest } from "@/auth/types";

const SESSION_KEY = "easy-sks.auth.session";
const PKCE_KEY = "easy-sks.auth.pkce";

function hasWindow() {
  return typeof window !== "undefined";
}

export function loadAuthSession(): AuthSession | null {
  if (!hasWindow()) return null;
  const raw = window.localStorage.getItem(SESSION_KEY);
  if (!raw) return null;

  try {
    const parsed = JSON.parse(raw) as AuthSession;
    if (
      typeof parsed.accessToken !== "string" ||
      typeof parsed.idToken !== "string" ||
      typeof parsed.expiresAt !== "number"
    ) {
      return null;
    }
    return parsed;
  } catch {
    return null;
  }
}

export function saveAuthSession(session: AuthSession) {
  if (!hasWindow()) return;
  window.localStorage.setItem(SESSION_KEY, JSON.stringify(session));
}

export function clearAuthSession() {
  if (!hasWindow()) return;
  window.localStorage.removeItem(SESSION_KEY);
}

export function loadAccessToken(): string | null {
  const session = loadAuthSession();
  if (!session) return null;
  if (Date.now() >= session.expiresAt) {
    clearAuthSession();
    return null;
  }
  return session.accessToken;
}

export function savePkceRequest(request: StoredPkceRequest) {
  if (!hasWindow()) return;
  window.sessionStorage.setItem(PKCE_KEY, JSON.stringify(request));
}

export function consumePkceRequest(): StoredPkceRequest | null {
  if (!hasWindow()) return null;
  const raw = window.sessionStorage.getItem(PKCE_KEY);
  window.sessionStorage.removeItem(PKCE_KEY);
  if (!raw) return null;
  try {
    return JSON.parse(raw) as StoredPkceRequest;
  } catch {
    return null;
  }
}

