"use client";

import React from "react";
import { AppShell } from "@/components/layout/AppShell";
import { SessionList } from "@/components/sessions/SessionList";
import { useResearch } from "@/context/ResearchContext";
import { Layers } from "lucide-react";

export default function SessionsPage() {
  const { sessions } = useResearch();

  return (
    <AppShell>
      <div className="p-4 sm:p-8 max-w-6xl mx-auto space-y-8">
        {/* Page Header */}
        <div className="space-y-1 pb-6 border-b border-slate-800/80">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-xl bg-indigo-500/10 border border-indigo-500/20 text-indigo-400 flex items-center justify-center">
              <Layers className="w-4 h-4" />
            </div>
            <h1 className="text-xl sm:text-2xl font-bold text-slate-100 tracking-tight">
              Research Sessions
            </h1>
          </div>
          <p className="text-xs sm:text-sm text-slate-400">
            Persistent multi-turn inquiry sessions. Switch between active investigations or export detailed intelligence PDF reports.
          </p>
        </div>

        {/* Session List */}
        <SessionList sessions={sessions} />
      </div>
    </AppShell>
  );
}
