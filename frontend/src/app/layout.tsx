import type { Metadata } from "next";
import { Geist } from "next/font/google";
import Script from "next/script";
import { AuthProvider } from "@/auth/auth-provider";
import { AppShell } from "@/components/layout/app-shell";
import "./globals.css";

const geistSans = Geist({
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "Easy SKS",
  description: "Flashcard study app for the Sportküstenschifferschein",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="de" className="dark">
      <body className={`${geistSans.className} antialiased`}>
        <Script src="/runtime-config.js" strategy="beforeInteractive" />
        <AuthProvider>
          <AppShell>{children}</AppShell>
        </AuthProvider>
      </body>
    </html>
  );
}
