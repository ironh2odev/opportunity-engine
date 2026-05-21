import type { Metadata } from "next";
import { Manrope, Sora } from "next/font/google";
import "./globals.css";

const manrope = Manrope({
  subsets: ["latin"],
  variable: "--font-manrope",
});

const sora = Sora({
  subsets: ["latin"],
  variable: "--font-sora",
});

export const metadata: Metadata = {
  title: "Opportunity Engine",
  description:
    "A premium, AI-assisted, human-in-the-loop opportunity and application operations platform.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className="dark">
      <body
        className={`${manrope.variable} ${sora.variable} bg-mesh-gradient [font-family:var(--font-manrope)] antialiased`}
      >
        {children}
      </body>
    </html>
  );
}
