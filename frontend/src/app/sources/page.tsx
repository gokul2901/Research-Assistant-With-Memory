"use client";

import React, { useState } from "react";
import { AppShell } from "@/components/layout/AppShell";
import { SourceList } from "@/components/sources/SourceList";
import { useSourcesList, useSourceStatistics } from "@/hooks/useSources";
import { useResearch } from "@/context/ResearchContext";
import { Button } from "@/ui/Button";
import {
  Database,
  Plus,
  CheckCircle2,
  AlertCircle,
  Clock,
  Layers,
  Sparkles,
} from "lucide-react";
import { Source } from "@/types";

export default function SourcesPage() {
  const { setIsAddSourceOpen, setActiveEvidenceSourceId } = useResearch();
  const { data: stats, isLoading: isStatsLoading } = useSourceStatistics();
  const { data: sourcesData, isLoading: isSourcesLoading } = useSourcesList(200, 0);
  const [selectedSource, setSelectedSource] = useState<Source | null>(null);

  const sources = sourcesData?.sources || [];

  const handleSelectSource = (source: Source) => {
    setSelectedSource(source);
    setActiveEvidenceSourceId(source.source_id);
  };

  return (
    <AppShell>
      <div className="p-4 sm:p-8 max-w-7xl mx-auto space-y-8">
        {/* Page Header */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-6 border-b border-slate-800/80">
          <div className="space-y-1">
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 rounded-xl bg-indigo-500/10 border border-indigo-500/20 text-indigo-400 flex items-center justify-center">
                <Database className="w-4 h-4" />
              </div>
              <h1 className="text-xl sm:text-2xl font-bold text-slate-100 tracking-tight">
                Knowledge Sources
              </h1>
            </div>
            <p className="text-xs sm:text-sm text-slate-400">
              Manage indexed websites, documentation URLs, and persistent ChromaDB vector chunks.
            </p>
          </div>

          <Button
            size="md"
            variant="primary"
            onClick={() => setIsAddSourceOpen(true)}
            leftIcon={<Plus className="w-4 h-4" />}
          >
            Add Knowledge URL
          </Button>
        </div>

        {/* Aggregated Statistics Cards */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
          <div className="p-4 rounded-2xl bg-slate-900/40 border border-slate-800/80 shadow-sm space-y-1">
            <span className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider block">
              Total Sources
            </span>
            <span className="text-2xl font-bold font-mono text-slate-100">
              {stats?.total_sources ?? 0}
            </span>
          </div>

          <div className="p-4 rounded-2xl bg-slate-900/40 border border-slate-800/80 shadow-sm space-y-1">
            <div className="flex items-center justify-between">
              <span className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider block">
                Indexed Chunks
              </span>
              <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
            </div>
            <span className="text-2xl font-bold font-mono text-emerald-400">
              {stats?.total_chunks ?? 0}
            </span>
          </div>

          <div className="p-4 rounded-2xl bg-slate-900/40 border border-slate-800/80 shadow-sm space-y-1">
            <span className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider block">
              Active Domains
            </span>
            <span className="text-2xl font-bold font-mono text-indigo-300">
              {stats?.domain_breakdown?.length ?? 0}
            </span>
          </div>

          <div className="p-4 rounded-2xl bg-slate-900/40 border border-slate-800/80 shadow-sm space-y-1">
            <div className="flex items-center justify-between">
              <span className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider block">
                Failed Ingestions
              </span>
              <AlertCircle className="w-3.5 h-3.5 text-red-400" />
            </div>
            <span className="text-2xl font-bold font-mono text-red-400">
              {stats?.failed_sources ?? 0}
            </span>
          </div>
        </div>

        {/* Source List Component */}
        <div className="space-y-4">
          <h2 className="text-sm font-semibold text-slate-200">
            All Knowledge Base Sources ({sources.length})
          </h2>
          <SourceList
            sources={sources}
            isLoading={isSourcesLoading}
            selectedSourceId={selectedSource?.source_id}
            onSelectSource={handleSelectSource}
          />
        </div>
      </div>
    </AppShell>
  );
}
