import createClient from "openapi-fetch";
import type { paths } from "./schema";
import { clearAuthSession, loadAccessToken } from "@/auth/storage";

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export const apiClient = createClient<paths>({
  baseUrl: API_BASE_URL,
  fetch: async (input, init) => {
    const headers = new Headers(init?.headers);
    const token = loadAccessToken();

    if (token) {
      headers.set("Authorization", `Bearer ${token}`);
    }

    const response = await fetch(input, {
      ...init,
      headers,
    });

    if (typeof window !== "undefined" && response.status === 401) {
      clearAuthSession();
      window.dispatchEvent(new Event("easy-sks-auth-unauthorized"));
    }

    return response;
  },
});
