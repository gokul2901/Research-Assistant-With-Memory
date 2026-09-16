import type { Metadata } from "next";
import { Inter, JetBrains_Mono } from "next/font/google";
import "./globals.css";
import { QueryProvider } from "@/components/providers/QueryProvider";
import { ThemeProvider } from "@/context/ThemeContext";
import { ResearchProvider } from "@/context/ResearchContext";

const inter = Inter({
  variable: "--font-sans",
  subsets: ["latin"],
  display: "swap",
});

const mono = JetBrains_Mono({
  variable: "--font-mono",
  subsets: ["latin"],
  display: "swap",
});

export const metadata: Metadata = {
  title: "Research Assistant with Persistent Memory | RAG Platform",
  description:
    "Drop URLs. Build knowledge. Ask anything. Enterprise AI research assistant with persistent vector memory, multi-LLM routing, and grounded citation attribution.",
  keywords: [
    "RAG",
    "Research Assistant",
    "Persistent Memory",
    "ChromaDB",
    "FastAPI",
    "LiteLLM",
    "Citation Attribution",
    "Next.js",
  ],
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className={`${inter.variable} ${mono.variable} dark h-full antialiased`}>
      <body className="min-h-full flex flex-col font-sans bg-slate-950 text-slate-100 selection:bg-indigo-500/30 selection:text-indigo-100">
        <QueryProvider>
          <ThemeProvider>
            <ResearchProvider>
              {children}
            </ResearchProvider>
          </ThemeProvider>
        </QueryProvider>
      </body>
    </html>
  );
}
