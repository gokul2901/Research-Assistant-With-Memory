"use client";

import React from "react";
import { ShieldAlert, Plus, BookOpen } from "lucide-react";
import { Button } from "@/ui/Button";
import { useResearch } from "@/context/ResearchContext";

export function NotFoundCoverage() {
  const { setIsAddSourceOpen } = useResearch();

  return (
    <div className="p-4 sm:p-5 rounded-2xl bg-slate-900/50 border border-slate-700/60 shadow-lg space-y-3">
      <div className="flex items-center gap-2.5 text-slate-300">
        <div className="w-7 h-7 rounded-lg bg-amber-500/10 border border-amber-500/25 text-amber-400 flex items-center justify-center">
          <BookOpen className="w-4 h-4" />
        </div>
        <div className="flex flex-col">
          <span className="text-xs font-semibold text-slate-200">
            Source Coverage Check
          </span>
          <span className="text-[10px] text-slate-400">
            Zero-Hallucination Grounding Gate
          </span>
        </div>
      </div>

      <div className="p-3.5 rounded-xl bg-slate-950/70 border border-slate-800 text-xs text-slate-300 space-y-2">
        <p className="leading-relaxed">
          This query does not match any indexed passages with sufficient similarity in your persistent knowledge base.
        </p>
        <p className="text-[11px] text-slate-400">
          The research engine refuses to hallucinate facts without direct source verification.
        </p>
      </div>

      <div className="flex items-center justify-between pt-1">
        <span className="text-[11px] text-slate-400">
          Expand knowledge coverage by indexing relevant URLs.
        </span>
        <Button
          size="xs"
          variant="subtle"
          onClick={() => setIsAddSourceOpen(true)}
          leftIcon={<Plus className="w-3.5 h-3.5" />}
        >
          Add Source
        </Button>
      </div>
    </div>
  );
}
