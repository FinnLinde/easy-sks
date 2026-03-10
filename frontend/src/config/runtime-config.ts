type RuntimeConfig = {
  apiUrl?: string;
  cognitoDomain?: string;
  cognitoClientId?: string;
  cognitoRedirectUri?: string;
  cognitoLogoutUri?: string;
  cognitoScopes?: string;
};

function readBrowserRuntimeConfig(): RuntimeConfig {
  if (typeof window === "undefined") {
    return {};
  }

  return window.__EASY_SKS_RUNTIME_CONFIG__ ?? {};
}

export function getRuntimeConfig(): RuntimeConfig {
  const runtime = readBrowserRuntimeConfig();

  return {
    apiUrl: runtime.apiUrl ?? process.env.NEXT_PUBLIC_API_URL,
    cognitoDomain:
      runtime.cognitoDomain ?? process.env.NEXT_PUBLIC_COGNITO_DOMAIN,
    cognitoClientId:
      runtime.cognitoClientId ?? process.env.NEXT_PUBLIC_COGNITO_CLIENT_ID,
    cognitoRedirectUri:
      runtime.cognitoRedirectUri ??
      process.env.NEXT_PUBLIC_COGNITO_REDIRECT_URI,
    cognitoLogoutUri:
      runtime.cognitoLogoutUri ?? process.env.NEXT_PUBLIC_COGNITO_LOGOUT_URI,
    cognitoScopes:
      runtime.cognitoScopes ?? process.env.NEXT_PUBLIC_COGNITO_SCOPES,
  };
}
