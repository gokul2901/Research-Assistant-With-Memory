"use client";

import React from "react";
import Link from "next/link";
import { AppShell } from "@/components/layout/AppShell";
import { Button } from "@/ui/Button";
import { useResearch } from "@/context/ResearchContext";
import { useSourceStatistics } from "@/hooks/useSources";
import { useSystemHealth } from "@/hooks/useHealth";
import {
  Sparkles,
  ArrowRight,
  Globe,
  Database,
  Cpu,
  ShieldCheck,
  FileDown,
  Layers,
  Search,
  CheckCircle2,
  Zap,
} from "lucide-react";
import { motion } from "framer-motion";

export default function LandingPage() {
  const { setIsAddSourceOpen } = useResearch();
  const { data: stats } = useSourceStatistics();
  const { data: health } = useSystemHealth();

  const pipelineSteps = [
    {
      icon: Globe,
      step: "01",
      title: "URL Ingestion",
      desc: "Paste single or batch URLs. Content is extracted, sanitized, and hierarchy-preserved.",
      badge: "n8n / FastAPI",
    },
    {
      icon: Database,
      step: "02",
      title: "Persistent Memory",
      desc: "Recursive token chunking and dense vector embedding storage in ChromaDB.",
      badge: "Cosine Index",
    },
    {
      icon: Cpu,
      step: "03",
      title: "AI Retrieval & Routing",
      desc: "Multi-stage semantic search with fallback routing across Gemini, GLM, and Mistral.",
      badge: "LiteLLM Router",
    },
    {
      icon: ShieldCheck,
      step: "04",
      title: "Grounded Answer",
      desc: "Precise claim-to-source attribution with inline clickable citations & anti-hallucination gates.",
      badge: "Citation Engine",
    },
  ];

  return (
    <AppShell>
      {/* Background Ambient Glow & Grid */}
      <div className="relative min-h-[calc(100vh-3.5rem)] flex flex-col justify-between overflow-hidden bg-grid-pattern">
        {/* Glow Spheres */}
        <div className="ambient-glow bg-indigo-600 w-[600px] h-[600px] -top-40 left-1/2 -translate-x-1/2 opacity-20" />
        <div className="ambient-glow bg-violet-600 w-[400px] h-[400px] top-96 -left-40 opacity-15" />
        <div className="ambient-glow bg-emerald-600 w-[350px] h-[350px] bottom-10 -right-20 opacity-10" />

        {/* Hero Section */}
        <section className="relative z-10 pt-16 sm:pt-24 pb-12 px-4 sm:px-6 max-w-5xl mx-auto text-center space-y-8">
          {/* Top Pill */}
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.4 }}
            className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-indigo-500/10 border border-indigo-500/25 text-indigo-300 text-xs font-medium shadow-inner"
          >
            <Sparkles className="w-3.5 h-3.5 text-indigo-400" />
            <span>Autonomous Grounded RAG &amp; Persistent Memory</span>
          </motion.div>

          {/* Hero Headlines */}
          <motion.div
            initial={{ opacity: 0, y: 15 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.1 }}
            className="space-y-4"
          >
            <h1 className="text-4xl sm:text-6xl lg:text-7xl font-extrabold tracking-tight text-white font-sans">
              Drop URLs. Build knowledge.{" "}
              <span className="bg-clip-text text-transparent bg-gradient-to-r from-indigo-400 via-indigo-200 to-violet-400">
                Ask anything.
              </span>
            </h1>
            <p className="text-base sm:text-xl text-slate-400 max-w-2xl mx-auto font-normal leading-relaxed">
              Turn scattered documentation and web sources into a persistent, searchable research memory with verified citation attribution.
            </p>
          </motion.div>

          {/* CTAs */}
          <motion.div
            initial={{ opacity: 0, y: 15 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.2 }}
            className="flex flex-wrap items-center justify-center gap-4 pt-2"
          >
            <Link href="/research">
              <Button
                size="lg"
                variant="primary"
                rightIcon={<ArrowRight className="w-4 h-4" />}
                className="shadow-xl shadow-indigo-950/60 text-sm font-semibold px-6 py-3"
              >
                Start Researching
              </Button>
            </Link>

            <Link href="/sources">
              <Button
                size="lg"
                variant="secondary"
                leftIcon={<Database className="w-4 h-4 text-indigo-400" />}
                className="text-sm font-medium px-5 py-3"
              >
                Explore Knowledge Base
              </Button>
            </Link>
          </motion.div>

          {/* Real-time Knowledge Stats Bar */}
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.5, delay: 0.3 }}
            className="pt-8"
          >
            <div className="inline-grid grid-cols-2 sm:grid-cols-4 gap-4 p-4 rounded-2xl bg-slate-900/60 border border-slate-800/80 backdrop-blur-xl shadow-2xl text-left">
              <div className="px-3">
                <span className="text-[11px] text-slate-400 uppercase font-mono block">
                  Indexed Sources
                </span>
                <span className="text-xl font-bold font-mono text-slate-100">
                  {stats?.indexed_sources ?? 0}
                </span>
              </div>
              <div className="px-3 border-l border-slate-800">
                <span className="text-[11px] text-slate-400 uppercase font-mono block">
                  Vector Chunks
                </span>
                <span className="text-xl font-bold font-mono text-indigo-300">
                  {stats?.total_chunks ?? 0}
                </span>
              </div>
              <div className="px-3 border-l border-slate-800">
                <span className="text-[11px] text-slate-400 uppercase font-mono block">
                  Primary Engine
                </span>
                <span className="text-sm font-bold font-mono text-slate-200 truncate block">
                  {health?.active_primary_llm ? health.active_primary_llm.replace(/^(models\/|gemini\/)/, "") : "Gemini Flash"}
                </span>
              </div>
              <div className="px-3 border-l border-slate-800">
                <span className="text-[11px] text-slate-400 uppercase font-mono block">
                  Vectorstore
                </span>
                <span className="text-sm font-bold font-mono text-emerald-400 flex items-center gap-1">
                  <span className="w-2 h-2 rounded-full bg-emerald-400 animate-ping inline-block" />
                  ChromaDB
                </span>
              </div>
            </div>
          </motion.div>
        </section>

        {/* Visual Architecture & Research Pipeline */}
        <section className="relative z-10 py-16 px-4 sm:px-6 max-w-6xl mx-auto w-full">
          <div className="text-center mb-10 space-y-2">
            <span className="text-xs font-semibold font-mono uppercase tracking-widest text-indigo-400">
              End-to-End Pipeline
            </span>
            <h2 className="text-2xl sm:text-3xl font-bold text-slate-100">
              How Persistent RAG Intelligence Works
            </h2>
          </div>

          {/* 4-Step Animated Pipeline Visual */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4 relative">
            {pipelineSteps.map((step, idx) => {
              const Icon = step.icon;
              return (
                <div
                  key={idx}
                  className="group relative p-5 rounded-2xl bg-slate-900/40 border border-slate-800/80 hover:border-indigo-500/40 hover:bg-slate-900/80 transition-all duration-300 shadow-lg flex flex-col justify-between"
                >
                  <div className="space-y-3">
                    <div className="flex items-center justify-between">
                      <div className="w-10 h-10 rounded-xl bg-indigo-500/10 border border-indigo-500/20 text-indigo-400 flex items-center justify-center group-hover:scale-110 transition-transform">
                        <Icon className="w-5 h-5" />
                      </div>
                      <span className="font-mono text-xs font-bold text-slate-400">
                        {step.step}
                      </span>
                    </div>
                    <div className="space-y-1">
                      <h3 className="text-sm font-bold text-slate-200">
                        {step.title}
                      </h3>
                      <p className="text-xs text-slate-400 leading-relaxed">
                        {step.desc}
                      </p>
                    </div>
                  </div>

                  <div className="pt-4 mt-4 border-t border-slate-800/60">
                    <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-slate-800 text-indigo-300 border border-slate-700/60">
                      {step.badge}
                    </span>
                  </div>
                </div>
              );
            })}
          </div>
        </section>

        {/* Feature Grid */}
        <section className="relative z-10 py-12 px-4 sm:px-6 max-w-6xl mx-auto w-full border-t border-slate-800/60">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="p-6 rounded-2xl bg-slate-900/30 border border-slate-800/70 space-y-2.5">
              <div className="w-8 h-8 rounded-lg bg-emerald-500/10 text-emerald-400 flex items-center justify-center">
                <ShieldCheck className="w-4 h-4" />
              </div>
              <h3 className="text-sm font-bold text-slate-200">Zero Hallucination Guarantee</h3>
              <p className="text-xs text-slate-400 leading-relaxed">
                If relevant passages are not found in your knowledge base, the system transparently reports coverage boundaries rather than fabricating answers.
              </p>
            </div>

            <div className="p-6 rounded-2xl bg-slate-900/30 border border-slate-800/70 space-y-2.5">
              <div className="w-8 h-8 rounded-lg bg-indigo-500/10 text-indigo-400 flex items-center justify-center">
                <Zap className="w-4 h-4" />
              </div>
              <h3 className="text-sm font-bold text-slate-200">Multi-LLM Failover</h3>
              <p className="text-xs text-slate-400 leading-relaxed">
                Automated model routing powered by LiteLLM gracefully switches between Gemini 1.5 Flash, GLM-4, and Mistral/Groq with sub-second failover.
              </p>
            </div>

            <div className="p-6 rounded-2xl bg-slate-900/30 border border-slate-800/70 space-y-2.5">
              <div className="w-8 h-8 rounded-lg bg-violet-500/10 text-violet-400 flex items-center justify-center">
                <FileDown className="w-4 h-4" />
              </div>
              <h3 className="text-sm font-bold text-slate-200">PDF Intelligence Export</h3>
              <p className="text-xs text-slate-400 leading-relaxed">
                Generate formatted research reports summarizing full multi-turn inquiries, referenced URLs, and indexed passage tables for stakeholders.
              </p>
            </div>
          </div>
        </section>

        {/* Footer */}
        <footer className="relative z-10 py-6 border-t border-slate-800/80 text-center text-xs text-slate-400">
          <p>
            Research Assistant with Persistent Memory • Enterprise RAG Platform
          </p>
        </footer>
      </div>
    </AppShell>
  );
}
