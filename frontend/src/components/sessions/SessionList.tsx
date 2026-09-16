"use client";

import React, { useState, useMemo } from "react";
import { ResearchSessionMeta } from "@/types";
import { SessionCard } from "./SessionCard";
import { useResearch } from "@/context/ResearchContext";
import { Button } from "@/ui/Button";
import { EmptyState } from "@/ui/EmptyState";
import { Plus, Search, Layers, Calendar } from "lucide-react";
import { useRouter } from "next/navigation";

export interface SessionListProps {
  sessions: ResearchSessionMeta[];
}

export function SessionList({ sessions }: SessionListProps) {
  const router = useRouter();
  const { createSession, currentSessionId } = useResearch();
  const [searchQuery, setSearchQuery] = useState("");

  const handleCreate = () => {
    const newId = createSession();
    router.push(`/sessions/${encodeURIComponent(newId)}`);
  };

  const filteredSessions = useMemo(() => {
    if (!searchQuery.trim()) return sessions;
    const q = searchQuery.toLowerCase();
    return sessions.filter(
      (s) =>
        s.title.toLowerCase().includes(q) ||
        (s.previewText && s.previewText.toLowerCase().includes(q))
    );
  }, [sessions, searchQuery]);

  // Group by timeframe (Today, Yesterday, Older)
  const grouped = useMemo(() => {
    const today: ResearchSessionMeta[] = [];
    const yesterday: ResearchSessionMeta[] = [];
    const older: ResearchSessionMeta[] = [];

    const now = new Date();
    const todayStart = new Date(now.getFullYear(), now.getMonth(), now.getDate()).getTime();
    const yesterdayStart = todayStart - 86400000;

    filteredSessions.forEach((s) => {
      const time = new Date(s.updatedAt || s.createdAt).getTime();
      if (time >= todayStart) {
        today.push(s);
      } else if (time >= yesterdayStart) {
        yesterday.push(s);
      } else {
        older.push(s);
      }
    });

    return { today, yesterday, older };
  }, [filteredSessions]);

  return (
    <div className="space-y-6">
      {/* Search and Action Bar */}
      <div className="flex flex-col sm:flex-row items-stretch sm:items-center justify-between gap-3">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
          <input
            type="text"
            placeholder="Search sessions by topic or question..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full pl-9 pr-4 py-2 rounded-xl bg-slate-900/60 border border-slate-800 text-xs text-slate-100 placeholder:text-slate-400 focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 transition-colors"
          />
        </div>

        <Button
          size="sm"
          variant="primary"
          onClick={handleCreate}
          leftIcon={<Plus className="w-3.5 h-3.5" />}
        >
          New Research Session
        </Button>
      </div>

      {/* Session Groups */}
      {filteredSessions.length === 0 ? (
        <EmptyState
          icon={<Layers className="w-6 h-6" />}
          title="No research sessions found"
          description="Start a new multi-turn research inquiry across your knowledge base."
          actionLabel="Create Session"
          onAction={handleCreate}
        />
      ) : (
        <div className="space-y-8">
          {grouped.today.length > 0 && (
            <div className="space-y-3">
              <h3 className="text-xs font-semibold uppercase tracking-wider text-slate-400 flex items-center gap-1.5">
                <Calendar className="w-3.5 h-3.5 text-indigo-400" />
                Today&apos;s Research
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {grouped.today.map((s) => (
                  <SessionCard
                    key={s.id}
                    session={s}
                    isSelected={s.id === currentSessionId}
                  />
                ))}
              </div>
            </div>
          )}

          {grouped.yesterday.length > 0 && (
            <div className="space-y-3">
              <h3 className="text-xs font-semibold uppercase tracking-wider text-slate-400 flex items-center gap-1.5">
                <Calendar className="w-3.5 h-3.5 text-slate-400" />
                Yesterday
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {grouped.yesterday.map((s) => (
                  <SessionCard
                    key={s.id}
                    session={s}
                    isSelected={s.id === currentSessionId}
                  />
                ))}
              </div>
            </div>
          )}

          {grouped.older.length > 0 && (
            <div className="space-y-3">
              <h3 className="text-xs font-semibold uppercase tracking-wider text-slate-400 flex items-center gap-1.5">
                <Calendar className="w-3.5 h-3.5 text-slate-400" />
                Previous Research
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {grouped.older.map((s) => (
                  <SessionCard
                    key={s.id}
                    session={s}
                    isSelected={s.id === currentSessionId}
                  />
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
