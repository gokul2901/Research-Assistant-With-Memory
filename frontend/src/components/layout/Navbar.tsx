"use client";

import React from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  Sparkles,
  Compass,
  Database,
  Layers,
  Settings as SettingsIcon,
  Moon,
  Sun,
  Plus,
  Activity,
  FileText,
} from "lucide-react";
import { cn } from "@/lib/utils";
import { useTheme } from "@/context/ThemeContext";
import { useResearch } from "@/context/ResearchContext";
import { useSourceStatistics } from "@/hooks/useSources";
import { useSystemHealth } from "@/hooks/useHealth";
import { Button } from "@/ui/Button";
import { Tooltip } from "@/ui/Tooltip";

export function Navbar() {
  const pathname = usePathname();
  const { theme, toggleTheme } = useTheme();
  const { setIsAddSourceOpen, currentSessionId } = useResearch();
  const { data: stats } = useSourceStatistics();
  const { data: health } = useSystemHealth();

  const navLinks = [
    { href: "/research", label: "Research", icon: Compass },
    { href: "/sources", label: "Sources", icon: Database },
    { href: "/sessions", label: "Sessions", icon: Layers },
  ];

  const isHealthy = health?.status === "healthy";

  return (
    <header className="sticky top-0 z-40 w-full border-b border-slate-800/80 bg-slate-950/70 backdrop-blur-xl">
      <div className="flex h-14 items-center justify-between px-4 sm:px-6">
        {/* Left: Brand Logo & Tagline */}
        <div className="flex items-center gap-6">
          <Link
            href="/"
            className="flex items-center gap-2.5 group transition-opacity hover:opacity-90"
          >
            <div className="w-8 h-8 rounded-xl bg-gradient-to-br from-indigo-500 via-indigo-600 to-violet-700 flex items-center justify-center shadow-lg shadow-indigo-950/50 border border-indigo-400/30 group-hover:scale-105 transition-transform duration-200">
              <Sparkles className="w-4 h-4 text-white" />
            </div>
            <div className="flex flex-col">
              <span className="text-sm font-bold tracking-tight text-slate-100 flex items-center gap-1.5">
                RESEARCH ASSISTANT
                <span className="text-[10px] uppercase font-mono px-1.5 py-0.2 rounded bg-indigo-500/20 text-indigo-300 border border-indigo-500/30">
                  RAG
                </span>
              </span>
              <span className="text-[10px] text-slate-400 font-medium hidden sm:inline-block">
                Persistent Knowledge Memory
              </span>
            </div>
          </Link>

          {/* Desktop Navigation Links */}
          <nav className="hidden md:flex items-center gap-1">
            {navLinks.map((link) => {
              const Icon = link.icon;
              const isActive =
                pathname === link.href ||
                (link.href !== "/" && pathname.startsWith(link.href));
              return (
                <Link
                  key={link.href}
                  href={link.href}
                  className={cn(
                    "flex items-center gap-2 px-3 py-1.5 rounded-lg text-xs font-medium transition-all duration-150",
                    isActive
                      ? "bg-slate-800/90 text-indigo-300 border border-slate-700/60 shadow-inner"
                      : "text-slate-400 hover:text-slate-200 hover:bg-slate-900/60"
                  )}
                >
                  <Icon className="w-3.5 h-3.5" />
                  {link.label}
                </Link>
              );
            })}
          </nav>
        </div>

        {/* Right Actions */}
        <div className="flex items-center gap-2.5 sm:gap-3">
          {/* Health & Knowledge Stat Indicator */}
          <div className="hidden lg:flex items-center gap-3 px-2.5 py-1 rounded-lg bg-slate-900/60 border border-slate-800 text-xs">
            <Tooltip
              content={
                isHealthy
                  ? `Backend connected (Chroma: ${health?.vectorstore_status}, Model: ${health?.active_primary_llm})`
                  : "Connecting to backend service..."
              }
            >
              <div className="flex items-center gap-1.5 cursor-help">
                <span
                  className={cn(
                    "w-2 h-2 rounded-full",
                    isHealthy
                      ? "bg-emerald-400 shadow-sm shadow-emerald-400/50 animate-pulse"
                      : "bg-amber-400"
                  )}
                />
                <span className="text-[11px] text-slate-400 font-mono">
                  {stats?.indexed_sources ?? 0} sources
                </span>
                <span className="text-slate-600 font-mono">/</span>
                <span className="text-[11px] text-slate-400 font-mono">
                  {stats?.total_chunks ?? 0} chunks
                </span>
              </div>
            </Tooltip>
          </div>


          {/* Theme Toggle */}
          <button
            onClick={toggleTheme}
            className="p-2 rounded-lg text-slate-400 hover:text-slate-200 hover:bg-slate-850 transition-colors cursor-pointer border border-transparent hover:border-slate-800"
            aria-label="Toggle dark/light theme"
          >
            {theme === "dark" ? (
              <Sun className="w-4 h-4" />
            ) : (
              <Moon className="w-4 h-4" />
            )}
          </button>

          {/* Settings Link */}
          <Link
            href="/settings"
            className={cn(
              "p-2 rounded-lg text-slate-400 hover:text-slate-200 hover:bg-slate-850 transition-colors border border-transparent hover:border-slate-800",
              pathname === "/settings" && "text-indigo-300 bg-slate-800/80 border-slate-700"
            )}
            aria-label="Settings"
          >
            <SettingsIcon className="w-4 h-4" />
          </Link>
        </div>
      </div>
    </header>
  );
}
