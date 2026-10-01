import type { ReactNode } from "react";
import "./globals.css";

export const metadata = {
  title: "GreenBusiness",
  description: "GreenBusiness production foundation",
  manifest: "/manifest.webmanifest",
  appleWebApp: {
    capable: true,
    title: "GreenBusiness",
    statusBarStyle: "black-translucent",
  },
};

export const viewport = {
  themeColor: "#102016",
};

export default function RootLayout({ children }: { children: ReactNode }) {
  return <html lang="en"><body>{children}</body></html>;
}
