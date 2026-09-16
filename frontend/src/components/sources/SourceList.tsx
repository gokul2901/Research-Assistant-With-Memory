"use client";

import React, { useState, useMemo } from "react";
import { Source } from "@/types";
import { SourceCard } from "./SourceCard";
import { SourceCardSkeleton } from "@/ui/Skeleton";
import { EmptyState } from "@/ui/EmptyState";
import { Button } from "@/ui/Button";
import { useResearch } from "@/context/ResearchContext";
import {
  Search,
  Filter,
  ArrowUpDown,
  Plus,
  Database,
  Globe,
  Sparkles,
} from "lucide-react";

export interface SourceListProps {
  sources: Source[];
  isLoading: boolean;
  onSelectSource?: (source: Source) => void;
  selectedSourceId?: string | null;
}

export function SourceList({
  sources,
  isLoading,
  onSelectSource,
  selectedSourceId,
}: SourceListProps) {
  const { setIsAddSourceOpen } = useResearch();
  const [searchQuery, setSearchQuery] = useState("");
  const [statusFilter, setStatusFilter] = useState<string>("all");
  const [sortBy, setSortBy] = useState<"newest" | "oldest" | "chunks" | "title">("newest");

  // Filter & Sort sources in memory
  const filteredSources = useMemo(() => {
    return sources
      .filter((s) => {
        // Query match
        if (searchQuery.trim()) {
          const q = searchQuery.toLowerCase();
          const matchTitle = s.title?.toLowerCase().includes(q);
          const matchUrl = s.url?.toLowerCase().includes(q);
          const matchDomain = s.domain?.toLowerCase().includes(q);
          if (!matchTitle && !matchUrl && !matchDomain) return false;
        }

        // Status match
        if (statusFilter !== "all") {
          if (statusFilter === "indexed") {
            return s.status === "indexed" || s.status === "updated";
          }
          return s.status === statusFilter;
        }

        return true;
      })
      .sort((a, b) => {
        if (sortBy === "newest") {
          return new Date(b.date_added || 0).getTime() - new Date(a.date_added || 0).getTime();
        }
        if (sortBy === "oldest") {
          return new Date(a.date_added || 0).getTime() - new Date(b.date_added || 0).getTime();
        }
        if (sortBy === "chunks") {
          return (b.chunk_count || 0) - (a.chunk_count || 0);
        }
        if (sortBy === "title") {
          return (a.title || a.url).localeCompare(b.title || b.url);
        }
        return 0;
      });
  }, [sources, searchQuery, statusFilter, sortBy]);

  return (
    <div className="space-y-4">
      {/* Search & Filter Controls */}
      <div className="flex flex-col sm:flex-row items-stretch sm:items-center justify-between gap-3">
        {/* Search Input */}
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
          <input
            type="text"
            placeholder="Search by title, domain, or URL..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full pl-9 pr-4 py-2 rounded-xl bg-slate-900/60 border border-slate-800 text-xs text-slate-100 placeholder:text-slate-400 focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 transition-colors"
          />
        </div>

        {/* Filter and Sort options */}
        <div className="flex items-center gap-2">
          {/* Status Filter */}
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="px-3 py-2 rounded-xl bg-slate-900/60 border border-slate-800 text-xs text-slate-300 focus:outline-none focus:border-indigo-500 transition-colors cursor-pointer"
          >
            <option value="all">All Statuses</option>
            <option value="indexed">Indexed</option>
            <option value="processing">Processing</option>
            <option value="failed">Failed</option>
          </select>

          {/* Sort Select */}
          <select
            value={sortBy}
            onChange={(e) => setSortBy(e.target.value as any)}
            className="px-3 py-2 rounded-xl bg-slate-900/60 border border-slate-800 text-xs text-slate-300 focus:outline-none focus:border-indigo-500 transition-colors cursor-pointer"
          >
            <option value="newest">Newest First</option>
            <option value="oldest">Oldest First</option>
            <option value="chunks">Most Chunks</option>
            <option value="title">Alphabetical (A-Z)</option>
          </select>

          {/* Quick Add CTA */}
          <Button
            size="sm"
            variant="primary"
            onClick={() => setIsAddSourceOpen(true)}
            leftIcon={<Plus className="w-3.5 h-3.5" />}
            className="shrink-0"
          >
            Add Source
          </Button>
        </div>
      </div>

      {/* Grid of Sources */}
      {isLoading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          <SourceCardSkeleton />
          <SourceCardSkeleton />
          <SourceCardSkeleton />
          <SourceCardSkeleton />
          <SourceCardSkeleton />
          <SourceCardSkeleton />
        </div>
      ) : filteredSources.length === 0 ? (
        sources.length === 0 ? (
          <EmptyState
            icon={<Database className="w-6 h-6" />}
            title="No knowledge sources yet"
            description="Add your first website or documentation URLs to start building your persistent research memory."
            actionLabel="Add your first source"
            onAction={() => setIsAddSourceOpen(true)}
          />
        ) : (
          <EmptyState
            icon={<Search className="w-6 h-6" />}
            title="No matching sources found"
            description="Try changing your search keywords or resetting the status filters."
            actionLabel="Clear Filters"
            onAction={() => {
              setSearchQuery("");
              setStatusFilter("all");
            }}
          />
        )
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {filteredSources.map((source) => (
            <SourceCard
              key={source.source_id}
              source={source}
              isSelected={selectedSourceId === source.source_id}
              onSelect={onSelectSource}
            />
          ))}
        </div>
      )}
    </div>
  );
}
