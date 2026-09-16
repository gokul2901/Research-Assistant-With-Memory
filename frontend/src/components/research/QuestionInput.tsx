"use client";

import React, { useState, useRef, useEffect } from "react";
import { Button } from "@/ui/Button";
import {
  Send,
  SlidersHorizontal,
  Sparkles,
  ChevronDown,
  Layers,
  Percent,
} from "lucide-react";
import { useResearch } from "@/context/ResearchContext";

export interface QuestionInputProps {
  onSend: (
    question: string,
    options?: {
      topK?: number;
      similarityThreshold?: number;
      modelOverride?: string;
    }
  ) => void;
  isLoading: boolean;
  placeholder?: string;
}

export function QuestionInput({
  onSend,
  isLoading,
  placeholder = "Ask anything across your indexed sources... (e.g. 'How does authentication work?')",
}: QuestionInputProps) {
  const [question, setQuestion] = useState("");
  const [showOptions, setShowOptions] = useState(false);
  const [topK, setTopK] = useState(5);
  const [similarityThreshold, setSimilarityThreshold] = useState(0.35);
  const [modelOverride, setModelOverride] = useState<string>("");
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  // Auto-resize textarea
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = "auto";
      textareaRef.current.style.height = `${Math.min(
        textareaRef.current.scrollHeight,
        180
      )}px`;
    }
  }, [question]);

  const handleSubmit = (e?: React.FormEvent) => {
    e?.preventDefault();
    if (!question.trim() || isLoading) return;

    onSend(question, {
      topK,
      similarityThreshold,
      modelOverride: modelOverride || undefined,
    });

    setQuestion("");
    if (textareaRef.current) {
      textareaRef.current.style.height = "auto";
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  return (
    <div className="relative w-full max-w-4xl mx-auto space-y-2">
      {/* Optional RAG Retrieval Tuning Drawer */}
      {showOptions && (
        <div className="p-3.5 rounded-xl bg-slate-900/90 border border-slate-700/80 shadow-xl space-y-3 text-xs animate-in fade-in slide-in-from-bottom-2 duration-200">
          <div className="flex items-center justify-between text-slate-300 font-medium">
            <span className="flex items-center gap-1.5">
              <SlidersHorizontal className="w-3.5 h-3.5 text-indigo-400" />
              Retrieval & Model Parameters
            </span>
            <button
              onClick={() => setShowOptions(false)}
              className="text-slate-400 hover:text-slate-200 text-[11px]"
            >
              Close
            </button>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
            {/* Model Override */}
            <div>
              <label className="text-[11px] text-slate-400 block mb-1">
                LLM Routing Mode
              </label>
              <select
                value={modelOverride}
                onChange={(e) => setModelOverride(e.target.value)}
                className="w-full px-2.5 py-1.5 rounded-lg bg-slate-950 border border-slate-750 text-xs text-slate-200 focus:outline-none focus:border-indigo-500"
              >
                <option value="">Auto Router (Gemini → Fallbacks)</option>
                <option value="gemini/gemini-1.5-flash">Gemini 1.5 Flash</option>
                <option value="glm/glm-4-flash">GLM-4 Flash</option>
                <option value="groq/llama3-70b-8192">Groq Llama 3 70B</option>
              </select>
            </div>

            {/* Top-K Chunks */}
            <div>
              <div className="flex justify-between text-[11px] text-slate-400 mb-1">
                <span>Top-K Chunks</span>
                <span className="font-mono text-indigo-300">{topK}</span>
              </div>
              <input
                type="range"
                min={1}
                max={15}
                value={topK}
                onChange={(e) => setTopK(parseInt(e.target.value, 10))}
                className="w-full accent-indigo-500 cursor-pointer"
              />
            </div>

            {/* Similarity Threshold */}
            <div>
              <div className="flex justify-between text-[11px] text-slate-400 mb-1">
                <span>Cosine Threshold</span>
                <span className="font-mono text-indigo-300">
                  {similarityThreshold.toFixed(2)}
                </span>
              </div>
              <input
                type="range"
                min={0.1}
                max={0.8}
                step={0.05}
                value={similarityThreshold}
                onChange={(e) => setSimilarityThreshold(parseFloat(e.target.value))}
                className="w-full accent-indigo-500 cursor-pointer"
              />
            </div>
          </div>
        </div>
      )}

      {/* Main Input Box */}
      <div className="relative rounded-2xl bg-slate-900/90 border border-slate-700/80 shadow-2xl shadow-black/60 focus-within:border-indigo-500/80 focus-within:ring-2 focus-within:ring-indigo-500/30 transition-all">
        <textarea
          ref={textareaRef}
          rows={1}
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder={placeholder}
          disabled={isLoading}
          className="w-full pl-4 pr-24 py-3.5 bg-transparent text-sm text-slate-100 placeholder:text-slate-400 resize-none focus:outline-none max-h-44"
        />

        {/* Action Controls in Right corner */}
        <div className="absolute right-2.5 bottom-2.5 flex items-center gap-1.5">
          <button
            type="button"
            onClick={() => setShowOptions(!showOptions)}
            className={`p-1.5 rounded-lg text-slate-400 hover:text-slate-200 hover:bg-slate-800 transition-colors ${
              showOptions ? "text-indigo-400 bg-slate-800" : ""
            }`}
            title="Tuning settings"
          >
            <SlidersHorizontal className="w-4 h-4" />
          </button>

          <Button
            type="button"
            size="sm"
            variant="primary"
            onClick={() => handleSubmit()}
            disabled={!question.trim() || isLoading}
            isLoading={isLoading}
            className="px-3 py-1.5 rounded-lg"
          >
            <Send className="w-3.5 h-3.5" />
          </Button>
        </div>
      </div>

      <div className="flex items-center justify-between px-2 text-[11px] text-slate-400">
        <span>Press <strong>Enter</strong> to ask, <strong>Shift+Enter</strong> for new line</span>
        <span className="font-mono">Strict Hallucination Protection Active</span>
      </div>
    </div>
  );
}
