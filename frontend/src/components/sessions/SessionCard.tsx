"use client";

import React, { useState } from "react";
import { ResearchSessionMeta } from "@/types";
import { useResearch } from "@/context/ResearchContext";
import {
  MessageSquare,
  Calendar,
  Clock,
  Trash2,
  Edit2,
  Check,
  X,
  ArrowUpRight,
} from "lucide-react";
import { formatRelativeTime, formatDate, cn } from "@/lib/utils";
import { useRouter } from "next/navigation";

export interface SessionCardProps {
  session: ResearchSessionMeta;
  isSelected?: boolean;
}

export function SessionCard({ session, isSelected = false }: SessionCardProps) {
  const router = useRouter();
  const { setCurrentSessionId, renameSession, deleteSession } = useResearch();
  const [isEditing, setIsEditing] = useState(false);
  const [titleInput, setTitleInput] = useState(session.title);

  const handleOpen = () => {
    setCurrentSessionId(session.id);
    router.push(`/sessions/${encodeURIComponent(session.id)}`);
  };

  const handleSaveRename = (e: React.MouseEvent) => {
    e.stopPropagation();
    if (titleInput.trim()) {
      renameSession(session.id, titleInput.trim());
    }
    setIsEditing(false);
  };

  const handleCancelRename = (e: React.MouseEvent) => {
    e.stopPropagation();
    setTitleInput(session.title);
    setIsEditing(false);
  };

  const handleDelete = (e: React.MouseEvent) => {
    e.stopPropagation();
    if (confirm("Are you sure you want to delete this research session history? (Knowledge sources will remain intact)")) {
      deleteSession(session.id);
    }
  };

  return (
    <div
      onClick={handleOpen}
      className={cn(
        "group relative flex flex-col justify-between p-4 rounded-xl border bg-slate-900/40 backdrop-blur-sm transition-all duration-200 cursor-pointer",
        isSelected
          ? "border-indigo-500/80 bg-slate-900/80 ring-1 ring-indigo-500/40 shadow-lg shadow-indigo-950/40"
          : "border-slate-800/80 hover:border-slate-700/80 hover:bg-slate-900/60 shadow-sm"
      )}
    >
      <div className="space-y-2">
        {/* Title / Rename mode */}
        <div className="flex items-start justify-between gap-2">
          {isEditing ? (
            <div className="flex items-center gap-1.5 flex-1" onClick={(e) => e.stopPropagation()}>
              <input
                type="text"
                autoFocus
                value={titleInput}
                onChange={(e) => setTitleInput(e.target.value)}
                className="w-full px-2 py-1 rounded bg-slate-950 border border-slate-700 text-xs text-slate-100 focus:outline-none focus:border-indigo-500"
              />
              <button
                onClick={handleSaveRename}
                className="p-1 rounded text-emerald-400 hover:bg-slate-800"
              >
                <Check className="w-3.5 h-3.5" />
              </button>
              <button
                onClick={handleCancelRename}
                className="p-1 rounded text-slate-400 hover:bg-slate-800"
              >
                <X className="w-3.5 h-3.5" />
              </button>
            </div>
          ) : (
            <h4 className="text-sm font-semibold text-slate-100 group-hover:text-indigo-300 transition-colors line-clamp-1 flex-1">
              {session.title}
            </h4>
          )}

          <div className="flex items-center gap-1 opacity-60 group-hover:opacity-100 transition-opacity">
            <button
              onClick={(e) => {
                e.stopPropagation();
                setIsEditing(true);
              }}
              className="p-1 rounded hover:bg-slate-800 text-slate-400 hover:text-slate-200"
              title="Rename Session"
            >
              <Edit2 className="w-3.5 h-3.5" />
            </button>
            <button
              onClick={handleDelete}
              className="p-1 rounded hover:bg-slate-800 text-slate-400 hover:text-red-400"
              title="Delete Session"
            >
              <Trash2 className="w-3.5 h-3.5" />
            </button>
          </div>
        </div>

        {/* Preview Snippet */}
        <p className="text-xs text-slate-400 line-clamp-2 leading-relaxed">
          {session.previewText || "No questions recorded in this session yet."}
        </p>
      </div>

      {/* Metadata Bottom */}
      <div className="flex items-center justify-between pt-3 mt-3 border-t border-slate-800/60 text-[11px] text-slate-400">
        <span className="flex items-center gap-1 text-indigo-300 font-mono">
          <MessageSquare className="w-3 h-3 text-indigo-400" />
          {session.questionCount || 0} queries
        </span>
        <span className="flex items-center gap-1">
          <Clock className="w-3 h-3 text-slate-400" />
          {formatRelativeTime(session.updatedAt)}
        </span>
      </div>
    </div>
  );
}
