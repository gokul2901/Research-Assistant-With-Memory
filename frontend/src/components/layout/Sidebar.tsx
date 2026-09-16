"use client";

import React from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  Compass,
  Database,
  Layers,
  Plus,
  Globe,
  CheckCircle2,
  AlertCircle,
  Clock,
  ExternalLink,
  Search,
} from "lucide-react";
import { cn, extractDomain } from "@/lib/utils";
import { useResearch } from "@/context/ResearchContext";
import { useSourcesList, useSourceStatistics } from "@/hooks/useSources";
import { Button } from "@/ui/Button";
import { Skeleton } from "@/ui/Skeleton";

export function Sidebar() {
  const pathname = usePathname();
  const {
    setIsAddSourceOpen,
    createSession,
    setActiveEvidenceSourceId,
  } = useResearch();
  const { data: stats, isLoading: isStatsLoading } = useSourceStatistics();
  const { data: sourcesData, isLoading: isSourcesLoading } = useSourcesList(15, 0);

  const navItems = [
    { href: "/research", label: "Research Workspace", icon: Compass },
    { href: "/sources", label: "Knowledge Sources", icon: Database },
    { href: "/sessions", label: "Research Sessions", icon: Layers },
  ];

  return (
    <aside className="w-64 shrink-0 flex flex-col h-[calc(100vh-3.5rem)] border-r border-slate-800/80 bg-slate-950/40 backdrop-blur-md overflow-hidden select-none">
      {/* Knowledge Base Metrics Header */}
      <div className="p-4 border-b border-slate-800/60">
        <div className="flex items-center justify-between mb-3">
          <span className="text-[11px] font-semibold uppercase tracking-wider text-slate-400">
            Knowledge Memory
          </span>
          <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
            ChromaDB
          </span>
        </div>

        <div className="grid grid-cols-2 gap-2">
          <div className="p-2.5 rounded-xl bg-slate-900/60 border border-slate-800/80">
            <span className="text-[10px] text-slate-400 block">Total Sources</span>
            {isStatsLoading ? (
              <Skeleton className="h-5 w-10 mt-1" />
            ) : (
              <span className="text-base font-bold text-slate-100 font-mono">
                {stats?.indexed_sources ?? 0}
              </span>
            )}
          </div>
          <div className="p-2.5 rounded-xl bg-slate-900/60 border border-slate-800/80">
            <span className="text-[10px] text-slate-400 block">Vector Chunks</span>
            {isStatsLoading ? (
              <Skeleton className="h-5 w-10 mt-1" />
            ) : (
              <span className="text-base font-bold text-slate-100 font-mono">
                {stats?.total_chunks ?? 0}
              </span>
            )}
          </div>
        </div>

        {/* Quick Action Buttons */}
        <div className="mt-3 flex gap-2">
          <Button
            size="xs"
            variant="primary"
            onClick={() => setIsAddSourceOpen(true)}
            leftIcon={<Plus className="w-3 h-3" />}
            className="flex-1 text-xs"
          >
            Add Source
          </Button>
          <Button
            size="xs"
            variant="secondary"
            onClick={() => createSession()}
            className="text-xs px-2.5"
            title="New Research Session"
          >
            + Session
          </Button>
        </div>
      </div>

      {/* Main Navigation Links */}
      <div className="p-3 border-b border-slate-800/60 space-y-1">
        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive =
            pathname === item.href ||
            (item.href !== "/" && pathname.startsWith(item.href));
          return (
            <Link
              key={item.href}
              href={item.href}
              className={cn(
                "flex items-center gap-2.5 px-3 py-2 rounded-lg text-xs font-medium transition-colors",
                isActive
                  ? "bg-slate-800 text-indigo-300 font-semibold shadow-sm border border-slate-700/60"
                  : "text-slate-400 hover:text-slate-200 hover:bg-slate-900/60"
              )}
            >
              <Icon className="w-4 h-4 shrink-0" />
              <span>{item.label}</span>
            </Link>
          );
        })}
      </div>

      {/* Recent Ingested Sources Section */}
      <div className="flex-1 overflow-y-auto p-3 space-y-2">
        <div className="flex items-center justify-between px-1 mb-1">
          <span className="text-[10px] font-semibold uppercase tracking-wider text-slate-400">
            Recent Sources
          </span>
          <Link
            href="/sources"
            className="text-[10px] text-indigo-400 hover:text-indigo-300 transition-colors"
          >
            View all
          </Link>
        </div>

        {isSourcesLoading ? (
          <div className="space-y-2">
            <Skeleton className="h-10 w-full" />
            <Skeleton className="h-10 w-full" />
            <Skeleton className="h-10 w-full" />
          </div>
        ) : !sourcesData?.sources || sourcesData.sources.length === 0 ? (
          <div className="p-4 text-center rounded-xl bg-slate-900/30 border border-slate-800/50">
            <Globe className="w-6 h-6 text-slate-600 mx-auto mb-1.5" />
            <p className="text-[11px] text-slate-400 font-medium">No sources indexed</p>
            <p className="text-[10px] text-slate-400 mt-0.5">Drop URLs to start querying</p>
          </div>
        ) : (
          <div className="space-y-1">
            {sourcesData.sources.slice(0, 10).map((source) => {
              const isSuccess = source.status === "indexed" || source.status === "updated";
              return (
                <div
                  key={source.source_id}
                  onClick={() => setActiveEvidenceSourceId(source.source_id)}
                  className="group flex items-start gap-2 p-2 rounded-lg hover:bg-slate-900/80 border border-transparent hover:border-slate-800/80 cursor-pointer transition-colors"
                  title={source.title || source.url}
                >
                  <div className="mt-0.5">
                    {isSuccess ? (
                      <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400/80" />
                    ) : source.status === "processing" ? (
                      <Clock className="w-3.5 h-3.5 text-amber-400 animate-spin" />
                    ) : (
                      <AlertCircle className="w-3.5 h-3.5 text-red-400/80" />
                    )}
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-xs font-medium text-slate-300 truncate group-hover:text-indigo-300">
                      {source.title || extractDomain(source.url)}
                    </p>
                    <div className="flex items-center gap-1.5 mt-0.5">
                      <span className="text-[10px] text-slate-400 truncate">
                        {extractDomain(source.url)}
                      </span>
                      <span className="text-slate-400 text-[10px]">•</span>
                      <span className="text-[10px] text-slate-400 font-mono">
                        {source.chunk_count} chunks
                      </span>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>

      {/* Footer Tagline */}
      <div className="p-3 border-t border-slate-800/60 text-center">
        <p className="text-[10px] text-slate-400 font-mono">
          &quot;Drop URLs. Build knowledge. Ask anything.&quot;
        </p>
      </div>
    </aside>
  );
}
