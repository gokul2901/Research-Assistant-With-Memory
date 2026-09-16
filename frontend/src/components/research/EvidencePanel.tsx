"use client";

import React, { useEffect, useRef } from "react";
import { useResearch } from "@/context/ResearchContext";
import {
  X,
  FileText,
  ExternalLink,
  BookOpen,
  Copy,
  Check,
  Globe,
  Sparkles,
  Layers,
  ChevronRight,
} from "lucide-react";
import { extractDomain } from "@/lib/utils";
import { toast } from "sonner";
import { Badge } from "@/ui/Badge";
import { ChatMessageHistoryItem } from "@/types";

export interface EvidencePanelProps {
  latestMessage?: ChatMessageHistoryItem;
}

export function EvidencePanel({ latestMessage }: EvidencePanelProps) {
  const {
    activeCitation,
    setActiveCitation,
    isEvidencePanelOpen,
    setIsEvidencePanelOpen,
  } = useResearch();

  const [copiedSnippetId, setCopiedSnippetId] = React.useState<number | null>(null);
  const activeSnippetRef = useRef<HTMLDivElement>(null);

  // Auto scroll to active citation when selected
  useEffect(() => {
    if (activeCitation && activeSnippetRef.current) {
      activeSnippetRef.current.scrollIntoView({ behavior: "smooth", block: "center" });
    }
  }, [activeCitation]);

  if (!isEvidencePanelOpen) return null;

  const citations = latestMessage?.citations || [];
  const sources = latestMessage?.sources || [];

  const handleCopySnippet = (snippetText: string, index: number) => {
    navigator.clipboard.writeText(snippetText);
    setCopiedSnippetId(index);
    toast.success(`Copied passage from [Source ${index}]`);
    setTimeout(() => setCopiedSnippetId(null), 2000);
  };

  return (
    <aside className="w-80 lg:w-96 shrink-0 flex flex-col h-[calc(100vh-3.5rem)] border-l border-slate-800/80 bg-slate-950/70 backdrop-blur-xl overflow-hidden select-none">
      {/* Header */}
      <div className="flex items-center justify-between p-3.5 border-b border-slate-800/80">
        <div className="flex items-center gap-2">
          <div className="w-6 h-6 rounded-lg bg-indigo-500/15 border border-indigo-500/25 text-indigo-400 flex items-center justify-center">
            <BookOpen className="w-3.5 h-3.5" />
          </div>
          <div>
            <h3 className="text-xs font-semibold text-slate-100 uppercase tracking-wider">
              Evidence & Sources
            </h3>
            <p className="text-[10px] text-slate-400">
              {citations.length > 0
                ? `${citations.length} grounded passage(s) referenced`
                : "Awaiting research query"}
            </p>
          </div>
        </div>

        <button
          onClick={() => setIsEvidencePanelOpen(false)}
          className="p-1 rounded-lg text-slate-400 hover:text-slate-200 hover:bg-slate-800 transition-colors"
          aria-label="Close evidence panel"
        >
          <X className="w-4 h-4" />
        </button>
      </div>

      {/* Content Body */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {citations.length === 0 ? (
          <div className="flex flex-col items-center justify-center text-center p-6 rounded-xl border border-dashed border-slate-800 bg-slate-900/30 text-xs text-slate-400">
            <FileText className="w-8 h-8 text-slate-600 mb-2" />
            <p className="font-medium text-slate-300">No Grounded Citations</p>
            <p className="text-[11px] text-slate-400 mt-1 max-w-xs leading-relaxed">
              Ask a research question in the chat to see referenced passages, similarity rankings, and source citations here.
            </p>
          </div>
        ) : (
          <div className="space-y-3.5">
            {citations.map((c) => {
              const isActive = activeCitation?.citation_index === c.citation_index;

              return (
                <div
                  key={c.citation_index}
                  ref={isActive ? activeSnippetRef : null}
                  onClick={() => setActiveCitation(c)}
                  className={`p-3.5 rounded-xl border transition-all duration-200 cursor-pointer ${
                    isActive
                      ? "bg-slate-900 border-indigo-500 ring-2 ring-indigo-500/30 shadow-lg shadow-indigo-950/50"
                      : "bg-slate-900/40 border-slate-800/80 hover:border-slate-700/80 hover:bg-slate-900/60"
                  }`}
                >
                  {/* Top Bar: Citation Index & Domain */}
                  <div className="flex items-start justify-between gap-2 mb-2">
                    <div className="flex items-center gap-2 min-w-0">
                      <span
                        className={`w-5 h-5 rounded-md flex items-center justify-center font-mono text-[11px] font-bold ${
                          isActive
                            ? "bg-indigo-500 text-white"
                            : "bg-slate-800 text-indigo-300 border border-indigo-500/20"
                        }`}
                      >
                        {c.citation_index}
                      </span>
                      <span className="text-[11px] font-mono text-slate-400 truncate">
                        {extractDomain(c.url)}
                      </span>
                    </div>

                    <a
                      href={c.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      onClick={(e) => e.stopPropagation()}
                      className="p-1 rounded text-slate-400 hover:text-indigo-400 hover:bg-slate-800 transition-colors"
                      title="Open full source webpage"
                    >
                      <ExternalLink className="w-3.5 h-3.5" />
                    </a>
                  </div>

                  {/* Title */}
                  <h4 className="text-xs font-semibold text-slate-200 line-clamp-1 mb-2">
                    {c.title || extractDomain(c.url)}
                  </h4>

                  {/* Grounded Snippet Passage */}
                  {c.snippet && (
                    <div className="p-2.5 rounded-lg bg-slate-950/80 border border-slate-800/80 text-[11px] text-slate-300 font-mono leading-relaxed space-y-1">
                      <p className="line-clamp-4">{c.snippet}</p>
                      <div className="flex justify-end pt-1">
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            handleCopySnippet(c.snippet || "", c.citation_index);
                          }}
                          className="text-[10px] text-slate-400 hover:text-slate-200 flex items-center gap-1 font-sans"
                        >
                          {copiedSnippetId === c.citation_index ? (
                            <>
                              <Check className="w-3 h-3 text-emerald-400" />
                              <span className="text-emerald-400">Copied</span>
                            </>
                          ) : (
                            <>
                              <Copy className="w-3 h-3" />
                              <span>Copy Passage</span>
                            </>
                          )}
                        </button>
                      </div>
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        )}
      </div>

      {/* Footer Info */}
      <div className="p-3 border-t border-slate-800/80 bg-slate-950/80 text-[11px] text-slate-400 flex items-center justify-between">
        <span className="flex items-center gap-1">
          <Sparkles className="w-3 h-3 text-indigo-400" />
          Indexed Dense Retrieval
        </span>
        <span className="font-mono text-[10px]">ChromaDB Cosine</span>
      </div>
    </aside>
  );
}
