"use client";

import {
  createContext,
  useContext,
  useEffect,
  useState,
  type ReactNode,
} from "react";
import {
  exchangeCodeForSession,
  redirectToCognitoLogin,
  redirectToCognitoLogout,
} from "@/auth/cognito";
import {
  clearAuthSession,
  loadAuthSession,
  saveAuthSession,
} from "@/auth/storage";
import type { AuthSession, AuthStatus } from "@/auth/types";

type AuthContextValue = {
  status: AuthStatus;
  session: AuthSession | null;
  login: (returnTo?: string) => Promise<void>;
  logout: () => void;
  completeLogin: (
    code: string,
    state: string | null
  ) => Promise<{ returnTo: string }>;
};

const AuthContext = createContext<AuthContextValue | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [session, setSession] = useState<AuthSession | null>(() => {
    const existing = loadAuthSession();
    if (!existing) return null;
    if (existing.expiresAt <= Date.now()) {
      clearAuthSession();
      return null;
    }
    return existing;
  });
  const [status, setStatus] = useState<AuthStatus>(() =>
    session ? "authenticated" : "unauthenticated"
  );

  useEffect(() => {
    const onUnauthorized = () => {
      clearAuthSession();
      setSession(null);
      setStatus("unauthenticated");
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
    setSession(null);
    setStatus("unauthenticated");
    try {
      redirectToCognitoLogout();
    } catch {
      // Missing config in local dev should still allow local logout.
    }
  }

  async function completeLogin(code: string, state: string | null) {
    const result = await exchangeCodeForSession(code, state);
    saveAuthSession(result.session);
    setSession(result.session);
    setStatus("authenticated");
    return { returnTo: result.returnTo };
  }

  return (
    <AuthContext.Provider
      value={{ status, session, login, logout, completeLogin }}
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
