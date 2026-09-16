"use client";

import React, { useState } from "react";
import { Modal } from "@/ui/Modal";
import { Button } from "@/ui/Button";
import { useResearch } from "@/context/ResearchContext";
import { useIngestUrls } from "@/hooks/useSources";
import {
  Globe,
  Plus,
  Trash2,
  Sparkles,
  CheckCircle2,
  AlertCircle,
  RefreshCw,
  Layers,
  Cpu,
  Database,
  ArrowRight,
} from "lucide-react";
import { IngestionStage, IngestionSummaryResponse } from "@/types";
import { motion, AnimatePresence } from "framer-motion";
import { extractDomain } from "@/lib/utils";

const PIPELINE_STAGES: { stage: IngestionStage; label: string; icon: React.ComponentType<{ className?: string }> }[] = [
  { stage: "QUEUED", label: "Request Queued", icon: ClockIcon },
  { stage: "FETCHING", label: "Scraping & Cleansing Content", icon: Globe },
  { stage: "CHUNKING", label: "Hierarchical Chunking", icon: Layers },
  { stage: "EMBEDDING", label: "Generating Vector Embeddings", icon: Cpu },
  { stage: "INDEXING", label: "ChromaDB Semantic Indexing", icon: Database },
];

function ClockIcon(props: { className?: string }) {
  return <RefreshCw className={props.className} />;
}

export function AddSourceModal() {
  const { isAddSourceOpen, setIsAddSourceOpen } = useResearch();
  const [urlInputs, setUrlInputs] = useState<string[]>([""]);
  const [forceRefresh, setForceRefresh] = useState(false);
  const [currentStage, setCurrentStage] = useState<IngestionStage | null>(null);
  const [ingestionResult, setIngestionResult] = useState<IngestionSummaryResponse | null>(null);

  const ingestMutation = useIngestUrls();

  const handleAddUrlField = () => {
    setUrlInputs([...urlInputs, ""]);
  };

  const handleUrlChange = (index: number, val: string) => {
    const updated = [...urlInputs];
    updated[index] = val;
    setUrlInputs(updated);
  };

  const handleRemoveField = (index: number) => {
    if (urlInputs.length <= 1) {
      setUrlInputs([""]);
      return;
    }
    setUrlInputs(urlInputs.filter((_, i) => i !== index));
  };

  const handlePasteBatch = (e: React.ClipboardEvent<HTMLTextAreaElement>) => {
    const paste = e.clipboardData.getData("text");
    if (paste.includes("\n") || paste.includes(",")) {
      e.preventDefault();
      const lines = paste
        .split(/[\n,]+/)
        .map((l) => l.trim())
        .filter((l) => l.startsWith("http://") || l.startsWith("https://") || l.length > 3);
      if (lines.length > 0) {
        setUrlInputs(lines);
      }
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const validUrls = urlInputs
      .map((u) => u.trim())
      .filter((u) => u.length > 0);

    if (validUrls.length === 0) return;

    // Simulate progressive pipeline states during backend execution
    setCurrentStage("FETCHING");
    const timer1 = setTimeout(() => setCurrentStage("CHUNKING"), 800);
    const timer2 = setTimeout(() => setCurrentStage("EMBEDDING"), 1800);
    const timer3 = setTimeout(() => setCurrentStage("INDEXING"), 2800);

    try {
      const summary = await ingestMutation.mutateAsync({
        urls: validUrls,
        forceRefresh,
      });

      clearTimeout(timer1);
      clearTimeout(timer2);
      clearTimeout(timer3);

      setCurrentStage("COMPLETED");
      setIngestionResult(summary);
    } catch {
      clearTimeout(timer1);
      clearTimeout(timer2);
      clearTimeout(timer3);
      setCurrentStage("FAILED");
    }
  };

  const handleResetAndClose = () => {
    setIsAddSourceOpen(false);
    setTimeout(() => {
      setUrlInputs([""]);
      setCurrentStage(null);
      setIngestionResult(null);
      setForceRefresh(false);
    }, 300);
  };

  return (
    <Modal
      isOpen={isAddSourceOpen}
      onClose={handleResetAndClose}
      title="Add Knowledge Sources"
      description="Ingest websites or documentation URLs into persistent ChromaDB memory."
      maxWidth="lg"
    >
      <AnimatePresence mode="wait">
        {currentStage === null ? (
          <motion.form
            key="form"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onSubmit={handleSubmit}
            className="space-y-4"
          >
            <div className="space-y-2.5 max-h-72 overflow-y-auto pr-1">
              <label className="text-xs font-medium text-slate-300 flex items-center justify-between">
                <span>Documentation / Website URLs</span>
                <span className="text-[11px] text-slate-400">
                  Multiple URLs or batch paste supported
                </span>
              </label>

              {urlInputs.map((url, idx) => (
                <div key={idx} className="flex items-center gap-2">
                  <div className="relative flex-1">
                    <Globe className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
                    <input
                      type="url"
                      required={idx === 0}
                      placeholder="https://docs.example.com/api"
                      value={url}
                      onChange={(e) => handleUrlChange(idx, e.target.value)}
                      className="w-full pl-9 pr-3 py-2 rounded-xl bg-slate-950/80 border border-slate-700/80 text-xs text-slate-100 placeholder:text-slate-400 focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 transition-colors"
                    />
                  </div>
                  {urlInputs.length > 1 && (
                    <button
                      type="button"
                      onClick={() => handleRemoveField(idx)}
                      className="p-2 rounded-lg text-slate-400 hover:text-red-400 hover:bg-slate-800 transition-colors"
                      title="Remove URL"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  )}
                </div>
              ))}
            </div>

            <div className="flex items-center justify-between pt-1">
              <button
                type="button"
                onClick={handleAddUrlField}
                className="text-xs font-medium text-indigo-400 hover:text-indigo-300 flex items-center gap-1.5 transition-colors cursor-pointer"
              >
                <Plus className="w-3.5 h-3.5" />
                Add another URL
              </button>

              <label className="flex items-center gap-2 text-xs text-slate-400 cursor-pointer">
                <input
                  type="checkbox"
                  checked={forceRefresh}
                  onChange={(e) => setForceRefresh(e.target.checked)}
                  className="rounded bg-slate-950 border-slate-700 text-indigo-600 focus:ring-indigo-500 focus:ring-offset-slate-900"
                />
                Force refresh if already indexed
              </label>
            </div>

            {/* Quick paste helper */}
            <div className="p-3 rounded-xl bg-slate-950/50 border border-slate-800/80">
              <span className="text-[11px] text-slate-400 block mb-1">
                Tip: Paste multiple URLs separated by newlines:
              </span>
              <textarea
                rows={2}
                onPaste={handlePasteBatch}
                placeholder="Paste multi-line URLs directly here..."
                className="w-full bg-transparent text-[11px] text-slate-300 placeholder:text-slate-400 resize-none focus:outline-none"
              />
            </div>

            {/* Actions */}
            <div className="flex items-center justify-end gap-3 pt-3 border-t border-slate-800/80">
              <Button
                type="button"
                variant="ghost"
                size="sm"
                onClick={handleResetAndClose}
              >
                Cancel
              </Button>
              <Button
                type="submit"
                variant="primary"
                size="sm"
                isLoading={ingestMutation.isPending}
                leftIcon={<Sparkles className="w-4 h-4" />}
              >
                Ingest & Index
              </Button>
            </div>
          </motion.form>
        ) : (
          <motion.div
            key="pipeline"
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0 }}
            className="space-y-5 py-2"
          >
            {/* Real Pipeline Stage Tracker */}
            <div className="space-y-3">
              <p className="text-xs font-medium text-slate-300">
                Knowledge Processing Pipeline
              </p>

              <div className="space-y-2 rounded-xl bg-slate-950/70 border border-slate-800/80 p-3.5">
                {PIPELINE_STAGES.map((s, idx) => {
                  const Icon = s.icon;
                  const isCurrent = currentStage === s.stage;
                  const isFinished =
                    currentStage === "COMPLETED" ||
                    (idx < PIPELINE_STAGES.findIndex((x) => x.stage === currentStage));

                  return (
                    <div
                      key={s.stage}
                      className="flex items-center justify-between py-1 px-2 rounded-lg text-xs"
                    >
                      <div className="flex items-center gap-2.5">
                        <div
                          className={`w-5 h-5 rounded-full flex items-center justify-center text-[10px] ${
                            isFinished
                              ? "bg-emerald-500/20 text-emerald-400 border border-emerald-500/30"
                              : isCurrent
                              ? "bg-indigo-500/20 text-indigo-300 border border-indigo-500/40 animate-pulse"
                              : "bg-slate-800/60 text-slate-400 border border-slate-700/40"
                          }`}
                        >
                          {isFinished ? (
                            <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
                          ) : (
                            <Icon className={`w-3 h-3 ${isCurrent ? "animate-spin" : ""}`} />
                          )}
                        </div>
                        <span
                          className={`font-medium ${
                            isFinished
                              ? "text-slate-200"
                              : isCurrent
                              ? "text-indigo-300 font-semibold"
                              : "text-slate-400"
                          }`}
                        >
                          {s.label}
                        </span>
                      </div>
                      <span className="text-[10px] font-mono text-slate-400">
                        {isFinished ? "DONE" : isCurrent ? "PROCESSING" : "WAITING"}
                      </span>
                    </div>
                  );
                })}
              </div>
            </div>

            {/* Ingestion Results Summary */}
            {ingestionResult && (
              <div className="p-3.5 rounded-xl bg-emerald-950/20 border border-emerald-500/30 space-y-2">
                <div className="flex items-center gap-2 text-emerald-400 text-xs font-semibold">
                  <CheckCircle2 className="w-4 h-4" />
                  <span>
                    Indexed {ingestionResult.successful_count} source(s) successfully!
                  </span>
                </div>
                <div className="space-y-1.5 max-h-36 overflow-y-auto">
                  {ingestionResult.results.map((res, i) => (
                    <div
                      key={i}
                      className="flex items-center justify-between text-[11px] text-slate-300 bg-slate-900/60 p-2 rounded-lg border border-slate-800"
                    >
                      <div className="truncate mr-2">
                        <span className="font-semibold text-slate-200 block truncate">
                          {res.title || extractDomain(res.url)}
                        </span>
                        <span className="text-slate-400 text-[10px] block truncate">
                          {res.url}
                        </span>
                      </div>
                      <span className="font-mono text-indigo-300 shrink-0">
                        {res.chunk_count} chunks
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {currentStage === "FAILED" && (
              <div className="p-3.5 rounded-xl bg-red-950/20 border border-red-500/30 flex items-start gap-2 text-red-400 text-xs">
                <AlertCircle className="w-4 h-4 shrink-0 mt-0.5" />
                <div>
                  <p className="font-semibold">Ingestion Interrupted</p>
                  <p className="text-red-300/80 text-[11px] mt-0.5">
                    {ingestMutation.error?.message || "Could not retrieve URL content."}
                  </p>
                </div>
              </div>
            )}

            {/* Finish Actions */}
            {(currentStage === "COMPLETED" || currentStage === "FAILED") && (
              <div className="flex items-center justify-end gap-2 pt-2">
                <Button
                  size="sm"
                  variant="primary"
                  onClick={handleResetAndClose}
                  rightIcon={<ArrowRight className="w-3.5 h-3.5" />}
                >
                  Done
                </Button>
              </div>
            )}
          </motion.div>
        )}
      </AnimatePresence>
    </Modal>
  );
}
