export {};

declare global {
  interface Window {
    __EASY_SKS_RUNTIME_CONFIG__?: {
      apiUrl?: string;
      cognitoDomain?: string;
      cognitoClientId?: string;
      cognitoRedirectUri?: string;
      cognitoLogoutUri?: string;
      cognitoScopes?: string;
    };
  }
}
