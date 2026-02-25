export type AuthStatus =
  | "loading"
  | "authenticated"
  | "unauthenticated";

export type AuthSession = {
  accessToken: string;
  idToken: string;
  refreshToken: string | null;
  expiresAt: number; // epoch ms
};

export type StoredPkceRequest = {
  codeVerifier: string;
  state: string;
  returnTo: string;
};

