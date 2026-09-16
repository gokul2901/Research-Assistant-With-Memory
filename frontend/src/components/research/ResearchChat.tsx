"use client";

import React, { useRef, useEffect } from "react";
import { useResearch } from "@/context/ResearchContext";
import { useResearchChat } from "@/hooks/useChat";
import { usePDFExport } from "@/hooks/useExport";
import { ChatMessage } from "./ChatMessage";
import { QuestionInput } from "./QuestionInput";
import { ChatMessageSkeleton } from "@/ui/Skeleton";
import { Button } from "@/ui/Button";
import {
  Download,
  Sparkles,
  HelpCircle,
  FileText,
  Layers,
  BookOpen,
  Compass,
  ArrowRight,
} from "lucide-react";
import { toast } from "sonner";

export interface ResearchChatProps {
  sessionId: string;
}

export function ResearchChat({ sessionId }: ResearchChatProps) {
  const { sessions, updateSessionActivity, setIsAddSourceOpen, setIsEvidencePanelOpen } = useResearch();
  const { messages, isHistoryLoading, isSubmitting, sendQuestion } = useResearchChat(sessionId);
  const { exportPDF, isExporting } = usePDFExport();
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const activeSessionMeta = sessions.find((s) => s.id === sessionId);

  // Auto-scroll on new message
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isSubmitting]);

  const handleSend = async (
    q: string,
    options?: { topK?: number; similarityThreshold?: number; modelOverride?: string }
  ) => {
    updateSessionActivity(sessionId, q);
    await sendQuestion(q, options);
  };

  const handleExportPDF = async () => {
    try {
      await exportPDF({
        session_id: sessionId,
        report_title: activeSessionMeta?.title || "Enterprise Research Report",
        include_sources_summary: true,
        include_full_citations: true,
      });
    } catch {
      // Handled in mutation hook
    }
  };

  const samplePrompts = [
    "How does FastAPI handle asynchronous request processing?",
    "What are the best practices for vector embeddings in ChromaDB?",
    "Summarize the key architectural principles mentioned in the sources.",
  ];

  return (
    <div className="flex-1 flex flex-col h-[calc(100vh-3.5rem)] bg-slate-950/20 overflow-hidden relative">
      {/* Top Session Action Bar */}
      <div className="h-13 px-4 sm:px-6 border-b border-slate-800/60 bg-slate-950/40 backdrop-blur-md flex items-center justify-between shrink-0">
        <div className="flex items-center gap-2.5 min-w-0">
          <span className="w-2 h-2 rounded-full bg-indigo-500 shadow-sm shadow-indigo-500/50" />
          <h2 className="text-xs sm:text-sm font-bold text-slate-100 truncate">
            {activeSessionMeta?.title || "Research Conversation"}
          </h2>
          <span className="text-[10px] font-mono text-slate-400 hidden sm:inline-block">
            ID: {sessionId.slice(0, 16)}...
          </span>
        </div>

        <div className="flex items-center gap-2">
          <Button
            size="xs"
            variant="outline"
            onClick={() => setIsEvidencePanelOpen(true)}
            leftIcon={<BookOpen className="w-3.5 h-3.5 text-indigo-400" />}
            className="hidden md:inline-flex text-xs"
          >
            Evidence
          </Button>

          <Button
            size="xs"
            variant="secondary"
            isLoading={isExporting}
            onClick={handleExportPDF}
            leftIcon={<Download className="w-3.5 h-3.5" />}
            className="text-xs font-semibold"
          >
            Export PDF
          </Button>
        </div>
      </div>

      {/* Messages Scroll Area */}
      <div className="flex-1 overflow-y-auto px-4 sm:px-8 py-6 space-y-6">
        {isHistoryLoading ? (
          <div className="max-w-3xl mx-auto space-y-4">
            <ChatMessageSkeleton />
            <ChatMessageSkeleton />
          </div>
        ) : messages.length === 0 ? (
          /* Empty Workspace Welcome State */
          <div className="max-w-2xl mx-auto my-auto text-center py-12 space-y-6 animate-in fade-in zoom-in-95 duration-300">
            <div className="w-14 h-14 rounded-2xl bg-gradient-to-br from-indigo-500/20 to-violet-600/20 border border-indigo-500/30 text-indigo-400 flex items-center justify-center mx-auto shadow-xl shadow-indigo-950/40">
              <Sparkles className="w-7 h-7" />
            </div>

            <div className="space-y-2">
              <h3 className="text-lg sm:text-xl font-bold text-slate-100 tracking-tight">
                Ask anything across your knowledge memory
              </h3>
              <p className="text-xs sm:text-sm text-slate-400 max-w-md mx-auto leading-relaxed">
                Query documentation and websites with automatic citation attribution, semantic re-ranking, and zero hallucinations.
              </p>
            </div>

            {/* Prompt Starter Pills */}
            <div className="space-y-2 max-w-lg mx-auto text-left">
              <span className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider block px-1">
                Suggested questions:
              </span>
              <div className="grid gap-2">
                {samplePrompts.map((prompt, i) => (
                  <button
                    key={i}
                    onClick={() => handleSend(prompt)}
                    className="flex items-center justify-between p-3 rounded-xl bg-slate-900/60 hover:bg-slate-900 border border-slate-800 hover:border-indigo-500/50 text-xs text-slate-300 hover:text-white transition-all text-left group cursor-pointer shadow-sm"
                  >
                    <span>&quot;{prompt}&quot;</span>
                    <ArrowRight className="w-3.5 h-3.5 text-slate-400 group-hover:text-indigo-400 group-hover:translate-x-0.5 transition-all shrink-0 ml-2" />
                  </button>
                ))}
              </div>
            </div>
          </div>
        ) : (
          <div className="max-w-3xl mx-auto space-y-4">
            {messages.map((msg, index) => (
              <ChatMessage key={msg.message_id || index} message={msg} />
            ))}

            {isSubmitting && <ChatMessageSkeleton />}
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Bottom Question Input Bar */}
      <div className="p-4 sm:p-6 border-t border-slate-800/80 bg-slate-950/60 backdrop-blur-lg shrink-0">
        <QuestionInput onSend={handleSend} isLoading={isSubmitting} />
      </div>
    </div>
  );
}
