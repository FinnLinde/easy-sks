import createClient from "openapi-fetch";
import { getRuntimeConfig } from "@/config/runtime-config";
import type { paths } from "./schema";
import { clearAuthSession, loadAccessToken } from "@/auth/storage";

export const API_BASE_URL = getRuntimeConfig().apiUrl ?? "http://localhost:8000";

export async function apiFetch(input: Request | URL | string, init?: RequestInit) {
  const request =
    input instanceof Request
      ? input
      : new Request(input instanceof URL ? input.toString() : input, init);

  const headers = new Headers(request.headers);
  const token = loadAccessToken();

  if (token) {
    headers.set("Authorization", `Bearer ${token}`);
  }

  const authorizedRequest = new Request(request, { headers });
  const response = await fetch(authorizedRequest);

  if (typeof window !== "undefined" && response.status === 401) {
    clearAuthSession();
    window.dispatchEvent(new Event("easy-sks-auth-unauthorized"));
  }

  return response;
}

export const apiClient = createClient<paths>({
  baseUrl: API_BASE_URL,
  fetch: apiFetch,
});
