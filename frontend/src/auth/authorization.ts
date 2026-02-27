import type { AuthSession } from "@/auth/types";

export type AuthRole = "freemium" | "premium" | "admin";

export type AuthClaims = {
  subject: string | null;
  email: string | null;
  roles: AuthRole[];
};

const ROLE_IMPLICATIONS: Record<AuthRole, AuthRole[]> = {
  freemium: ["freemium"],
  premium: ["premium", "freemium"],
  admin: ["admin", "premium", "freemium"],
};

function decodeBase64Url(value: string): string {
  const normalized = value.replace(/-/g, "+").replace(/_/g, "/");
  const padded = normalized.padEnd(
    normalized.length + ((4 - (normalized.length % 4)) % 4),
    "="
  );
  return atob(padded);
}

function parseJwtPayload(token: string): Record<string, unknown> | null {
  const parts = token.split(".");
  if (parts.length !== 3) return null;

  try {
    const raw = decodeBase64Url(parts[1]);
    return JSON.parse(raw) as Record<string, unknown>;
  } catch {
    return null;
  }
}

function extractDirectRoles(payload: Record<string, unknown> | null): AuthRole[] {
  if (!payload) return [];
  const groups = payload["cognito:groups"];
  if (!Array.isArray(groups)) return [];

  const allowed = new Set<AuthRole>(["freemium", "premium", "admin"]);
  return groups.filter((g): g is AuthRole => typeof g === "string" && allowed.has(g as AuthRole));
}

function expandRoles(roles: AuthRole[]): AuthRole[] {
  const expanded = new Set<AuthRole>();
  for (const role of roles) {
    for (const implied of ROLE_IMPLICATIONS[role]) {
      expanded.add(implied);
    }
  }
  return Array.from(expanded);
}

export function getAuthClaimsFromSession(session: AuthSession): AuthClaims {
  const accessPayload = parseJwtPayload(session.accessToken);
  const idPayload = parseJwtPayload(session.idToken);
  const roles = expandRoles([
    ...extractDirectRoles(accessPayload),
    ...extractDirectRoles(idPayload),
  ]);

  const subjectFromAccess =
    typeof accessPayload?.sub === "string" ? accessPayload.sub : null;
  const subjectFromId = typeof idPayload?.sub === "string" ? idPayload.sub : null;
  const emailFromAccess =
    typeof accessPayload?.email === "string" ? accessPayload.email : null;
  const emailFromId = typeof idPayload?.email === "string" ? idPayload.email : null;

  return {
    subject: subjectFromAccess ?? subjectFromId,
    email: emailFromAccess ?? emailFromId,
    roles,
  };
}

export function claimsHasRole(claims: AuthClaims | null, role: AuthRole): boolean {
  if (!claims) return false;
  return claims.roles.includes(role);
}
