import type { Metadata } from "next";
import { Geist } from "next/font/google";
import { AppShell } from "@/components/layout/app-shell";
import { AppSettingsProvider } from "@/services/settings/app-settings-context";
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
        <AppSettingsProvider>
          <AppShell>{children}</AppShell>
        </AppSettingsProvider>
      </body>
    </html>
  );
}
