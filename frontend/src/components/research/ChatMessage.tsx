"use client";

import React, { useState } from "react";
import { ChatMessageHistoryItem, CitationItem } from "@/types";
import { CitationMarker } from "./CitationMarker";
import { NotFoundCoverage } from "./NotFoundCoverage";
import { Badge } from "@/ui/Badge";
import {
  Copy,
  Check,
  Sparkles,
  User,
  Clock,
  ShieldCheck,
  Cpu,
  Layers,
  ExternalLink,
  Zap,
} from "lucide-react";
import { toast } from "sonner";
import { formatDate, extractDomain } from "@/lib/utils";
import { useResearch } from "@/context/ResearchContext";

export interface ChatMessageProps {
  message: ChatMessageHistoryItem;
}

export function ChatMessage({ message }: ChatMessageProps) {
  const [copied, setCopied] = useState(false);
  const { setActiveCitation, setIsEvidencePanelOpen } = useResearch();

  const isAssistant = message.role === "assistant";
  // Only show the hard-gate card for the literal sentinel string
  const isNotFound = message.content.trim() === "Not found in sources.";
  // General-knowledge fallback: real LLM answer but no grounded sources
  const isGeneralKnowledge =
    !isNotFound &&
    message.is_grounded === false &&
    (!message.citations || message.citations.length === 0);

  const handleCopy = () => {
    navigator.clipboard.writeText(message.content);
    setCopied(true);
    toast.success("Research answer copied to clipboard.");
    setTimeout(() => setCopied(false), 2000);
  };

  /**
   * Render answer paragraph cleanly without inline [1] or [Source 1] markers
   */
  const renderFormattedAnswer = (content: string, _citations?: CitationItem[]) => {
    // Clean out inline citation markers like [1] or [Source 1]
    const cleanContent = content
      .replace(/\s*\[(?:Source\s*)?\d+\]/gi, "")
      .replace(/\s{2,}/g, " ")
      .trim();

    return <p className="whitespace-pre-wrap leading-relaxed">{cleanContent}</p>;
  };

  if (!isAssistant) {
    return (
      <div className="flex justify-end my-4">
        <div className="max-w-2xl flex items-start gap-3 flex-row-reverse">
          <div className="w-8 h-8 rounded-full bg-slate-800 border border-slate-700 flex items-center justify-center shrink-0">
            <User className="w-4 h-4 text-slate-300" />
          </div>
          <div className="rounded-2xl rounded-tr-sm bg-gradient-to-br from-indigo-600 to-violet-700 p-4 text-white shadow-md shadow-indigo-950/30 text-sm font-normal leading-relaxed">
            <p className="whitespace-pre-wrap">{message.content}</p>
            <div className="text-[10px] text-indigo-200/70 text-right mt-1.5 font-mono">
              {formatDate(message.timestamp)}
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="flex justify-start my-5 group">
      <div className="w-full max-w-3xl flex items-start gap-3.5">
        {/* Assistant Avatar */}
        <div className="w-8 h-8 rounded-xl bg-gradient-to-br from-indigo-500 to-violet-600 border border-indigo-400/30 flex items-center justify-center shrink-0 shadow-md shadow-indigo-950/40 mt-1">
          <Sparkles className="w-4 h-4 text-white" />
        </div>

        {/* Message Bubble & Metadata */}
        <div className="flex-1 min-w-0 space-y-2.5">
          {/* Header Metadata Bar */}
          <div className="flex flex-wrap items-center justify-between gap-2 text-xs">
            <div className="flex items-center gap-2">
              <span className="font-semibold text-slate-200">Research Assistant</span>

              {message.model_used && (
                <Badge variant="indigo" size="sm">
                  <Cpu className="w-3 h-3" />
                  {message.model_used.replace(/^(models\/|gemini\/)/, "")}
                </Badge>
              )}

              {message.is_grounded && (
                <Badge variant="success" size="sm">
                  <ShieldCheck className="w-3 h-3" />
                  Grounded
                </Badge>
              )}

              {isGeneralKnowledge && (
                <Badge variant="warning" size="sm">
                  <Zap className="w-3 h-3" />
                  General Knowledge
                </Badge>
              )}
            </div>

            <div className="flex items-center gap-2 text-slate-400 text-[11px]">
              {message.execution_time_ms && (
                <span className="flex items-center gap-1 font-mono">
                  <Clock className="w-3 h-3" />
                  {message.execution_time_ms}ms
                </span>
              )}
              <button
                onClick={handleCopy}
                className="p-1 rounded hover:bg-slate-800 text-slate-400 hover:text-slate-200 transition-colors"
                title="Copy Answer"
              >
                {copied ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5" />}
              </button>
            </div>
          </div>

          {/* Answer Body */}
          <div className="p-5 rounded-2xl rounded-tl-sm bg-slate-900/70 border border-slate-800/90 text-slate-100 text-sm shadow-md">
            {isNotFound ? (
              <NotFoundCoverage />
            ) : (
              renderFormattedAnswer(message.content, message.citations)
            )}
          </div>

          {/* General Knowledge Notice Banner */}
          {isGeneralKnowledge && (
            <div className="flex items-start gap-2.5 px-4 py-2.5 rounded-xl bg-amber-500/5 border border-amber-500/20 text-[11px] text-amber-300/80">
              <Zap className="w-3.5 h-3.5 mt-0.5 shrink-0 text-amber-400" />
              <span>
                <span className="font-semibold text-amber-300">General knowledge response</span> — no indexed sources matched this query.
                {" "}Index relevant URLs via <span className="font-semibold">+ Add Source</span> for grounded, cited answers.
              </span>
            </div>
          )}

          {/* Referenced Source Chips */}
          {message.sources && message.sources.length > 0 && !isNotFound && (
            <div className="space-y-1.5 pt-1">
              <div className="flex items-center gap-1.5 text-[11px] font-medium text-slate-400">
                <Layers className="w-3 h-3 text-indigo-400" />
                <span>Referenced Sources ({message.sources.length}):</span>
              </div>
              <div className="flex flex-wrap gap-2">
                {message.sources.map((src, i) => (
                  <button
                    key={i}
                    onClick={() => {
                      if (message.citations && message.citations[i]) {
                        setActiveCitation(message.citations[i]);
                      }
                      setIsEvidencePanelOpen(true);
                    }}
                    className="flex items-center gap-1.5 px-2.5 py-1 rounded-lg bg-slate-900/90 hover:bg-slate-800 border border-slate-800 hover:border-indigo-500/40 text-[11px] text-slate-300 hover:text-indigo-300 transition-colors truncate max-w-xs cursor-pointer"
                  >
                    <span className="w-1.5 h-1.5 rounded-full bg-indigo-400 shrink-0" />
                    <span className="font-semibold text-slate-200">[{i + 1}]</span>
                    <span className="truncate">{src.title || src.domain}</span>
                  </button>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
