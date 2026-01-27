import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import { ThemeProvider } from "@/components/theme-provider";

const inter = Inter({ subsets: ["latin"], display: "swap" });

export const metadata: Metadata = {
  title: {
    default: "AI Prompt Refinement - Transform Your Prompts with AI",
    template: "%s | AI Prompt Refinement",
  },
  description:
    "Transform your prompts with AI-powered refinement and custom filters. Upload files, generate domain-specific filters, and chat with GPT-4o-mini.",
  keywords: [
    "AI",
    "prompt refinement",
    "GPT",
    "Gemini",
    "prompt engineering",
    "AI chat",
    "file processing",
    "OCR",
  ],
  authors: [{ name: "AI Prompt Refinement" }],
  creator: "AI Prompt Refinement",
  openGraph: {
    type: "website",
    locale: "en_US",
    url: "https://your-domain.vercel.app",
    title: "AI Prompt Refinement - Transform Your Prompts with AI",
    description:
      "Transform your prompts with AI-powered refinement and custom filters. Upload files, generate domain-specific filters, and chat with GPT-4o-mini.",
    siteName: "AI Prompt Refinement",
  },
  twitter: {
    card: "summary_large_image",
    title: "AI Prompt Refinement - Transform Your Prompts with AI",
    description:
      "Transform your prompts with AI-powered refinement and custom filters.",
    creator: "@yourusername",
  },
  robots: {
    index: true,
    follow: true,
    googleBot: {
      index: true,
      follow: true,
      "max-video-preview": -1,
      "max-image-preview": "large",
      "max-snippet": -1,
    },
  },
  viewport: {
    width: "device-width",
    initialScale: 1,
    maximumScale: 5,
  },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className={inter.className}>
        <ThemeProvider
          attribute="class"
          defaultTheme="dark"
          enableSystem
          disableTransitionOnChange
        >
          {children}
        </ThemeProvider>
      </body>
    </html>
  );
}
