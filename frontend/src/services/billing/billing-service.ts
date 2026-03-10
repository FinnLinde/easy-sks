import { apiClient } from "@/services/api/client";
import type { components } from "@/services/api/schema";

export type BillingSubscription = components["schemas"]["BillingSubscriptionResponse"];

function extractDetail(error: unknown, fallback: string): string {
  if (
    error &&
    typeof error === "object" &&
    "detail" in error &&
    typeof (error as { detail?: unknown }).detail === "string"
  ) {
    return (error as { detail: string }).detail;
  }
  return fallback;
}

export async function createCheckoutSession(): Promise<string> {
  const { data, error } = await apiClient.POST("/billing/checkout-session");
  if (!data?.checkout_url) {
    throw new Error(extractDetail(error, "checkout_session_failed"));
  }
  return data.checkout_url;
}

export async function createCustomerPortalSession(): Promise<string> {
  const { data, error } = await apiClient.POST("/billing/customer-portal-session");
  if (!data?.portal_url) {
    throw new Error(extractDetail(error, "customer_portal_session_failed"));
  }
  return data.portal_url;
}

export async function getBillingSubscription(): Promise<BillingSubscription> {
  const { data, error } = await apiClient.GET("/billing/subscription");
  if (!data) {
    throw new Error(extractDetail(error, "billing_subscription_fetch_failed"));
  }
  return data;
}
