type RuntimeConfig = {
  apiUrl?: string;
};

export function getRuntimeConfig(): RuntimeConfig {
  return {
    apiUrl: process.env.NEXT_PUBLIC_API_URL,
  };
}
