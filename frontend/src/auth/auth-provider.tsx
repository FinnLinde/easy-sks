"use client";

import {
  createContext,
  useContext,
  useEffect,
  useReducer,
  type ReactNode,
} from "react";
import {
  exchangeCodeForSession,
  redirectToCognitoLogin,
  redirectToCognitoLogout,
} from "@/auth/cognito";
import {
  claimsHasRole,
  getAuthClaimsFromSession,
  type AuthClaims,
  type AuthRole,
} from "@/auth/authorization";
import {
  clearAuthSession,
  loadAuthSession,
  saveAuthSession,
} from "@/auth/storage";
import type { AuthSession, AuthStatus } from "@/auth/types";

type AuthContextValue = {
  status: AuthStatus;
  session: AuthSession | null;
  claims: AuthClaims | null;
  hasRole: (role: AuthRole) => boolean;
  login: (returnTo?: string) => Promise<void>;
  logout: () => void;
  completeLogin: (
    code: string,
    state: string | null
  ) => Promise<{ returnTo: string }>;
};

type AuthState = {
  session: AuthSession | null;
  status: AuthStatus;
};

type AuthAction =
  | { type: "hydrated"; session: AuthSession | null }
  | { type: "unauthorized" }
  | { type: "login-complete"; session: AuthSession }
  | { type: "logout" };

const AuthContext = createContext<AuthContextValue | null>(null);

function authReducer(state: AuthState, action: AuthAction): AuthState {
  switch (action.type) {
    case "hydrated":
      return {
        session: action.session,
        status: action.session ? "authenticated" : "unauthenticated",
      };
    case "unauthorized":
    case "logout":
      return { session: null, status: "unauthenticated" };
    case "login-complete":
      return { session: action.session, status: "authenticated" };
    default:
      return state;
  }
}

export function AuthProvider({ children }: { children: ReactNode }) {
  // Start in a deterministic state for SSR + hydration, then load localStorage
  // on the client after mount.
  const [authState, dispatch] = useReducer(authReducer, {
    session: null,
    status: "loading",
  });

  useEffect(() => {
    const existing = loadAuthSession();
    if (!existing) {
      dispatch({ type: "hydrated", session: null });
      return;
    }

    if (existing.expiresAt <= Date.now()) {
      clearAuthSession();
      dispatch({ type: "hydrated", session: null });
      return;
    }

    dispatch({ type: "hydrated", session: existing });
  }, []);

  useEffect(() => {
    const onUnauthorized = () => {
      clearAuthSession();
      dispatch({ type: "unauthorized" });
    };

    window.addEventListener("easy-sks-auth-unauthorized", onUnauthorized);
    return () => {
      window.removeEventListener("easy-sks-auth-unauthorized", onUnauthorized);
    };
  }, []);

  async function login(returnTo?: string) {
    await redirectToCognitoLogin(returnTo);
  }

  function logout() {
    clearAuthSession();
    dispatch({ type: "logout" });
    try {
      redirectToCognitoLogout();
    } catch {
      // Missing config in local dev should still allow local logout.
    }
  }

  async function completeLogin(code: string, state: string | null) {
    const result = await exchangeCodeForSession(code, state);
    saveAuthSession(result.session);
    dispatch({ type: "login-complete", session: result.session });
    return { returnTo: result.returnTo };
  }

  const { session, status } = authState;
  const claims = session ? getAuthClaimsFromSession(session) : null;
  const hasRole = (role: AuthRole) => claimsHasRole(claims, role);

  return (
    <AuthContext.Provider
      value={{
        status,
        session,
        claims,
        hasRole,
        login,
        logout,
        completeLogin,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) {
    throw new Error("useAuth must be used within <AuthProvider>");
  }
  return ctx;
}
