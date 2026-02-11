import createClient from "openapi-fetch";
import type { paths } from "./schema";

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export const apiClient = createClient<paths>({
  baseUrl: API_BASE_URL,
});
