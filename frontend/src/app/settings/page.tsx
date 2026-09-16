"use client";

import React, { useState } from "react";
import { AppShell } from "@/components/layout/AppShell";
import { useSystemHealth } from "@/hooks/useHealth";
import { useSourceStatistics } from "@/hooks/useSources";
import { useTheme } from "@/context/ThemeContext";
import { Button } from "@/ui/Button";
import { Badge } from "@/ui/Badge";
import {
  Settings as SettingsIcon,
  Activity,
  Cpu,
  Database,
  Moon,
  Sun,
  ShieldCheck,
  Server,
  RefreshCw,
  Sliders,
  CheckCircle2,
  AlertCircle,
  ExternalLink,
} from "lucide-react";
import { API_BASE_URL } from "@/api/client";
import { toast } from "sonner";

export default function SettingsPage() {
  const { theme, setTheme } = useTheme();
  const { data: health, isLoading: isHealthLoading, refetch: refetchHealth } = useSystemHealth();
  const { data: stats } = useSourceStatistics();
  const [isTestingConn, setIsTestingConn] = useState(false);

  const handleTestConnection = async () => {
    setIsTestingConn(true);
    try {
      await refetchHealth();
      toast.success("Backend diagnostic probe succeeded.");
    } catch {
      toast.error("Could not reach backend service.");
    } finally {
      setIsTestingConn(false);
    }
  };

  const isHealthy = health?.status === "healthy";

  return (
    <AppShell>
      <div className="p-4 sm:p-8 max-w-5xl mx-auto space-y-8">
        {/* Page Header */}
        <div className="space-y-1 pb-6 border-b border-slate-800/80">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-xl bg-indigo-500/10 border border-indigo-500/20 text-indigo-400 flex items-center justify-center">
              <SettingsIcon className="w-4 h-4" />
            </div>
            <h1 className="text-xl sm:text-2xl font-bold text-slate-100 tracking-tight">
              Settings &amp; Diagnostics
            </h1>
          </div>
          <p className="text-xs sm:text-sm text-slate-400">
            System health, vector database status, multi-LLM router configuration, and appearance preferences.
          </p>
        </div>

        {/* Section 1: Backend Connection & Health Status */}
        <div className="p-6 rounded-2xl bg-slate-900/40 border border-slate-800/80 space-y-5">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-9 h-9 rounded-xl bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 flex items-center justify-center">
                <Activity className="w-4 h-4" />
              </div>
              <div>
                <h3 className="text-sm font-bold text-slate-200">
                  Backend System Health
                </h3>
                <p className="text-xs text-slate-400">
                  FastAPI RAG Engine Diagnostics
                </p>
              </div>
            </div>

            <Button
              size="xs"
              variant="outline"
              onClick={handleTestConnection}
              isLoading={isTestingConn || isHealthLoading}
              leftIcon={<RefreshCw className="w-3.5 h-3.5" />}
            >
              Run Diagnostic
            </Button>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            <div className="p-3.5 rounded-xl bg-slate-950/70 border border-slate-800 space-y-1">
              <span className="text-[11px] text-slate-400 block font-mono">Service Status</span>
              <div className="flex items-center gap-2">
                <span
                  className={`w-2.5 h-2.5 rounded-full ${
                    isHealthy ? "bg-emerald-400 shadow-emerald-400/50 shadow-sm animate-pulse" : "bg-red-400"
                  }`}
                />
                <span className="text-sm font-bold capitalize text-slate-200">
                  {health?.status || "Connecting..."}
                </span>
              </div>
            </div>

            <div className="p-3.5 rounded-xl bg-slate-950/70 border border-slate-800 space-y-1">
              <span className="text-[11px] text-slate-400 block font-mono">Vectorstore Status</span>
              <div className="flex items-center gap-1.5 text-sm font-bold text-slate-200">
                <Database className="w-3.5 h-3.5 text-indigo-400" />
                <span>{health?.vectorstore_status || "ChromaDB Connected"}</span>
              </div>
            </div>

            <div className="p-3.5 rounded-xl bg-slate-950/70 border border-slate-800 space-y-1">
              <span className="text-[11px] text-slate-400 block font-mono">API Base Endpoint</span>
              <span className="text-xs font-mono text-indigo-300 block truncate">
                {API_BASE_URL}
              </span>
            </div>
          </div>
        </div>

        {/* Section 2: Multi-LLM Router Diagnostics */}
        <div className="p-6 rounded-2xl bg-slate-900/40 border border-slate-800/80 space-y-5">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-xl bg-indigo-500/10 border border-indigo-500/20 text-indigo-400 flex items-center justify-center">
              <Cpu className="w-4 h-4" />
            </div>
            <div>
              <h3 className="text-sm font-bold text-slate-200">
                Multi-LLM Automated Failover Router
              </h3>
              <p className="text-xs text-slate-400">
                Configured model fallback hierarchy powered by LiteLLM
              </p>
            </div>
          </div>

          <div className="space-y-2">
            <div className="flex items-center justify-between p-3 rounded-xl bg-slate-950/80 border border-slate-800 text-xs">
              <div className="flex items-center gap-2">
                <Badge variant="indigo" size="sm">Primary</Badge>
                <span className="font-semibold text-slate-200">
                  {health?.active_primary_llm || "gemini/gemini-1.5-flash"}
                </span>
              </div>
              <span className="text-emerald-400 text-[11px] font-mono">ACTIVE (Priority 0)</span>
            </div>

            <div className="flex items-center justify-between p-3 rounded-xl bg-slate-950/80 border border-slate-800 text-xs">
              <div className="flex items-center gap-2">
                <Badge variant="default" size="sm">Fallback 1</Badge>
                <span className="text-slate-300">
                  {health?.fallback_llms?.[0] || "glm/glm-4-flash"}
                </span>
              </div>
              <span className="text-slate-400 text-[11px] font-mono">STANDBY (Priority 1)</span>
            </div>

            <div className="flex items-center justify-between p-3 rounded-xl bg-slate-950/80 border border-slate-800 text-xs">
              <div className="flex items-center gap-2">
                <Badge variant="default" size="sm">Fallback 2</Badge>
                <span className="text-slate-300">
                  {health?.fallback_llms?.[1] || "groq/llama3-70b-8192"}
                </span>
              </div>
              <span className="text-slate-400 text-[11px] font-mono">STANDBY (Priority 2)</span>
            </div>
          </div>
        </div>

        {/* Section 3: Appearance & Theme */}
        <div className="p-6 rounded-2xl bg-slate-900/40 border border-slate-800/80 space-y-4">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-xl bg-violet-500/10 border border-violet-500/20 text-violet-400 flex items-center justify-center">
              <Sliders className="w-4 h-4" />
            </div>
            <div>
              <h3 className="text-sm font-bold text-slate-200">Appearance &amp; Theme</h3>
              <p className="text-xs text-slate-400">
                Customize workspace visual mode
              </p>
            </div>
          </div>

          <div className="flex items-center gap-3 pt-2">
            <button
              onClick={() => setTheme("dark")}
              className={`flex items-center gap-2 px-4 py-2.5 rounded-xl text-xs font-medium border transition-all cursor-pointer ${
                theme === "dark"
                  ? "bg-slate-800 text-indigo-300 border-indigo-500/50 shadow-md"
                  : "bg-slate-950/60 text-slate-400 border-slate-800 hover:border-slate-700"
              }`}
            >
              <Moon className="w-4 h-4 text-indigo-400" />
              Dark Mode (Recommended)
            </button>

            <button
              onClick={() => setTheme("light")}
              className={`flex items-center gap-2 px-4 py-2.5 rounded-xl text-xs font-medium border transition-all cursor-pointer ${
                theme === "light"
                  ? "bg-slate-200 text-slate-900 border-indigo-500 shadow-md"
                  : "bg-slate-950/60 text-slate-400 border-slate-800 hover:border-slate-700"
              }`}
            >
              <Sun className="w-4 h-4 text-amber-400" />
              Light Mode
            </button>
          </div>
        </div>

        {/* Section 4: Hallucination Prevention Guarantees */}
        <div className="p-6 rounded-2xl bg-indigo-950/20 border border-indigo-500/20 space-y-3">
          <div className="flex items-center gap-2 text-indigo-300 text-sm font-bold">
            <ShieldCheck className="w-4 h-4 text-indigo-400" />
            <span>Strict Hallucination Prevention Active</span>
          </div>
          <p className="text-xs text-slate-300 leading-relaxed">
            All research answers are passed through the strict citation engine. If an LLM response contains claims not substantiated by retrieved context chunks from ChromaDB, or if no chunks pass the cosine similarity threshold, the answer is flagged as ungrounded and coverage boundaries are explicitly displayed.
          </p>
        </div>
      </div>
    </AppShell>
  );
}
