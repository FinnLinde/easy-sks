import createClient from "openapi-fetch";
import { getRuntimeConfig } from "@/config/runtime-config";
import type { paths } from "./schema";

export const API_BASE_URL = getRuntimeConfig().apiUrl ?? "http://localhost:8000";

export const apiClient = createClient<paths>({
  baseUrl: API_BASE_URL,
});
