"use client";

import React, { useState } from "react";
import { Source } from "@/types";
import { Badge } from "@/ui/Badge";
import { Button } from "@/ui/Button";
import {
  Globe,
  RefreshCw,
  Trash2,
  ExternalLink,
  Layers,
  FileCode,
  Calendar,
  CheckCircle2,
  AlertCircle,
  Clock,
} from "lucide-react";
import { formatRelativeTime, extractDomain, cn } from "@/lib/utils";
import { useRefreshSource } from "@/hooks/useSources";
import { DeleteSourceDialog } from "./DeleteSourceDialog";

export interface SourceCardProps {
  source: Source;
  onSelect?: (source: Source) => void;
  isSelected?: boolean;
}

export function SourceCard({
  source,
  onSelect,
  isSelected = false,
}: SourceCardProps) {
  const [isDeleteDialogOpen, setIsDeleteDialogOpen] = useState(false);
  const refreshMutation = useRefreshSource();

  const handleRefresh = (e: React.MouseEvent) => {
    e.stopPropagation();
    refreshMutation.mutate(source.source_id);
  };

  const handleDeleteClick = (e: React.MouseEvent) => {
    e.stopPropagation();
    setIsDeleteDialogOpen(true);
  };

  const getStatusBadge = () => {
    switch (source.status) {
      case "indexed":
      case "updated":
        return (
          <Badge variant="success" size="sm">
            <CheckCircle2 className="w-3 h-3" />
            Indexed
          </Badge>
        );
      case "processing":
        return (
          <Badge variant="warning" size="sm">
            <Clock className="w-3 h-3 animate-spin" />
            Processing
          </Badge>
        );
      case "failed":
        return (
          <Badge variant="error" size="sm">
            <AlertCircle className="w-3 h-3" />
            Failed
          </Badge>
        );
      default:
        return (
          <Badge variant="default" size="sm">
            {source.status}
          </Badge>
        );
    }
  };

  return (
    <>
      <div
        onClick={() => onSelect?.(source)}
        className={cn(
          "group relative flex flex-col justify-between p-4 rounded-xl border bg-slate-900/40 backdrop-blur-sm transition-all duration-200 cursor-pointer",
          isSelected
            ? "border-indigo-500/80 bg-slate-900/80 shadow-lg shadow-indigo-950/40 ring-1 ring-indigo-500/30"
            : "border-slate-800/80 hover:border-slate-700/80 hover:bg-slate-900/60 shadow-sm"
        )}
      >
        {/* Top bar: Domain & Status */}
        <div className="flex items-start justify-between gap-3 mb-2.5">
          <div className="flex items-center gap-2 min-w-0">
            <div className="w-7 h-7 rounded-lg bg-indigo-500/10 border border-indigo-500/20 text-indigo-400 flex items-center justify-center shrink-0">
              <Globe className="w-3.5 h-3.5" />
            </div>
            <div className="min-w-0">
              <span className="text-[11px] font-mono text-slate-400 block truncate">
                {source.domain || extractDomain(source.url)}
              </span>
            </div>
          </div>
          <div className="shrink-0">{getStatusBadge()}</div>
        </div>

        {/* Title & URL */}
        <div className="space-y-1.5 mb-4">
          <h4 className="text-sm font-semibold text-slate-100 group-hover:text-indigo-300 transition-colors line-clamp-2">
            {source.title || extractDomain(source.url)}
          </h4>
          <a
            href={source.url}
            target="_blank"
            rel="noopener noreferrer"
            onClick={(e) => e.stopPropagation()}
            className="text-[11px] text-slate-400 hover:text-indigo-400 flex items-center gap-1 truncate transition-colors"
          >
            <span className="truncate">{source.url}</span>
            <ExternalLink className="w-3 h-3 shrink-0" />
          </a>
        </div>

        {/* Bottom Metadata & Actions */}
        <div className="flex items-center justify-between pt-3 border-t border-slate-800/60 text-xs text-slate-400">
          <div className="flex items-center gap-3">
            <span className="flex items-center gap-1 font-mono text-[11px] text-indigo-300">
              <Layers className="w-3.5 h-3.5 text-indigo-400" />
              {source.chunk_count} chunks
            </span>
            <span className="hidden sm:inline-block text-[11px] text-slate-400">
              {formatRelativeTime(source.last_updated || source.date_added)}
            </span>
          </div>

          {/* Quick Action buttons */}
          <div className="flex items-center gap-1 opacity-80 group-hover:opacity-100 transition-opacity">
            <button
              onClick={handleRefresh}
              disabled={refreshMutation.isPending}
              className="p-1.5 rounded-lg text-slate-400 hover:text-slate-200 hover:bg-slate-800 transition-colors"
              title="Refresh / Re-scrape source"
            >
              <RefreshCw
                className={`w-3.5 h-3.5 ${refreshMutation.isPending ? "animate-spin text-indigo-400" : ""}`}
              />
            </button>
            <button
              onClick={handleDeleteClick}
              className="p-1.5 rounded-lg text-slate-400 hover:text-red-400 hover:bg-slate-800 transition-colors"
              title="Delete source and vectors"
            >
              <Trash2 className="w-3.5 h-3.5" />
            </button>
          </div>
        </div>
      </div>

      <DeleteSourceDialog
        source={source}
        isOpen={isDeleteDialogOpen}
        onClose={() => setIsDeleteDialogOpen(false)}
      />
    </>
  );
}
