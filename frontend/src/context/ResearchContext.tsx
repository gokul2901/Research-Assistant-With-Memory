"use client";

import React, { createContext, useContext, useEffect, useState, useCallback } from "react";
import { CitationItem, SourceMetadataRef, ResearchSessionMeta } from "@/types";

interface ResearchContextType {
  // Session State
  currentSessionId: string;
  setCurrentSessionId: (id: string) => void;
  sessions: ResearchSessionMeta[];
  createSession: (title?: string) => string;
  renameSession: (id: string, newTitle: string) => void;
  deleteSession: (id: string) => void;
  updateSessionActivity: (id: string, question: string) => void;

  // Evidence & Citation Selection State
  activeCitation: CitationItem | null;
  setActiveCitation: (citation: CitationItem | null) => void;
  activeEvidenceSourceId: string | null;
  setActiveEvidenceSourceId: (sourceId: string | null) => void;
  activeSources: SourceMetadataRef[];
  setActiveSources: (sources: SourceMetadataRef[]) => void;

  // Add Source Modal State
  isAddSourceOpen: boolean;
  setIsAddSourceOpen: (open: boolean) => void;

  // Ingestion Drawer / Status State
  isIngestionDrawerOpen: boolean;
  setIsIngestionDrawerOpen: (open: boolean) => void;

  // Right Panel State (desktop and mobile)
  isEvidencePanelOpen: boolean;
  setIsEvidencePanelOpen: (open: boolean) => void;
}

const ResearchContext = createContext<ResearchContextType | undefined>(undefined);

const SESSIONS_STORAGE_KEY = "research_assistant_sessions_v1";
const ACTIVE_SESSION_STORAGE_KEY = "research_assistant_active_session_id";

export function ResearchProvider({ children }: { children: React.ReactNode }) {
  const [currentSessionId, setCurrentSessionIdState] = useState<string>("session_main");
  const [sessions, setSessions] = useState<ResearchSessionMeta[]>([]);
  const [activeCitation, setActiveCitation] = useState<CitationItem | null>(null);
  const [activeEvidenceSourceId, setActiveEvidenceSourceId] = useState<string | null>(null);
  const [activeSources, setActiveSources] = useState<SourceMetadataRef[]>([]);
  const [isAddSourceOpen, setIsAddSourceOpen] = useState<boolean>(false);
  const [isIngestionDrawerOpen, setIsIngestionDrawerOpen] = useState<boolean>(false);
  const [isEvidencePanelOpen, setIsEvidencePanelOpen] = useState<boolean>(true);

  // Load sessions from localStorage
  useEffect(() => {
    try {
      const savedSessions = localStorage.getItem(SESSIONS_STORAGE_KEY);
      const savedActive = localStorage.getItem(ACTIVE_SESSION_STORAGE_KEY);

      if (savedSessions) {
        const parsed: ResearchSessionMeta[] = JSON.parse(savedSessions);
        if (parsed && parsed.length > 0) {
          setSessions(parsed);
          if (savedActive && parsed.some((s) => s.id === savedActive)) {
            setCurrentSessionIdState(savedActive);
          } else {
            setCurrentSessionIdState(parsed[0].id);
          }
          return;
        }
      }

      // Initialize default first session
      const defaultSession: ResearchSessionMeta = {
        id: `session_${Date.now()}`,
        title: "Initial Research Workspace",
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString(),
        questionCount: 0,
        previewText: "Start querying across your indexed knowledge sources.",
      };
      setSessions([defaultSession]);
      setCurrentSessionIdState(defaultSession.id);
      localStorage.setItem(SESSIONS_STORAGE_KEY, JSON.stringify([defaultSession]));
      localStorage.setItem(ACTIVE_SESSION_STORAGE_KEY, defaultSession.id);
    } catch {
      // Fallback
    }
  }, []);

  const setCurrentSessionId = useCallback((id: string) => {
    setCurrentSessionIdState(id);
    localStorage.setItem(ACTIVE_SESSION_STORAGE_KEY, id);
    // Reset active citation and source filters when switching session
    setActiveCitation(null);
    setActiveEvidenceSourceId(null);
  }, []);

  const createSession = useCallback((title?: string) => {
    const newId = `session_${Date.now()}_${Math.random().toString(36).substring(2, 7)}`;
    const newSession: ResearchSessionMeta = {
      id: newId,
      title: title || `Research Session ${new Date().toLocaleDateString()}`,
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
      questionCount: 0,
      previewText: "New empty research session",
    };

    setSessions((prev) => {
      const updated = [newSession, ...prev];
      localStorage.setItem(SESSIONS_STORAGE_KEY, JSON.stringify(updated));
      return updated;
    });

    setCurrentSessionId(newId);
    return newId;
  }, [setCurrentSessionId]);

  const renameSession = useCallback((id: string, newTitle: string) => {
    setSessions((prev) => {
      const updated = prev.map((s) =>
        s.id === id ? { ...s, title: newTitle.trim() || s.title, updatedAt: new Date().toISOString() } : s
      );
      localStorage.setItem(SESSIONS_STORAGE_KEY, JSON.stringify(updated));
      return updated;
    });
  }, []);

  const deleteSession = useCallback((id: string) => {
    setSessions((prev) => {
      const filtered = prev.filter((s) => s.id !== id);
      const remaining = filtered.length > 0 ? filtered : [
        {
          id: `session_${Date.now()}`,
          title: "General Research",
          createdAt: new Date().toISOString(),
          updatedAt: new Date().toISOString(),
          questionCount: 0,
        },
      ];
      localStorage.setItem(SESSIONS_STORAGE_KEY, JSON.stringify(remaining));

      if (id === currentSessionId) {
        setCurrentSessionId(remaining[0].id);
      }
      return remaining;
    });
  }, [currentSessionId, setCurrentSessionId]);

  const updateSessionActivity = useCallback((id: string, question: string) => {
    setSessions((prev) => {
      const updated = prev.map((s) => {
        if (s.id === id) {
          return {
            ...s,
            updatedAt: new Date().toISOString(),
            questionCount: (s.questionCount || 0) + 1,
            previewText: question.slice(0, 80),
          };
        }
        return s;
      });
      // Sort so most recently active is first
      updated.sort((a, b) => new Date(b.updatedAt).getTime() - new Date(a.updatedAt).getTime());
      localStorage.setItem(SESSIONS_STORAGE_KEY, JSON.stringify(updated));
      return updated;
    });
  }, []);

  return (
    <ResearchContext.Provider
      value={{
        currentSessionId,
        setCurrentSessionId,
        sessions,
        createSession,
        renameSession,
        deleteSession,
        updateSessionActivity,
        activeCitation,
        setActiveCitation,
        activeEvidenceSourceId,
        setActiveEvidenceSourceId,
        activeSources,
        setActiveSources,
        isAddSourceOpen,
        setIsAddSourceOpen,
        isIngestionDrawerOpen,
        setIsIngestionDrawerOpen,
        isEvidencePanelOpen,
        setIsEvidencePanelOpen,
      }}
    >
      {children}
    </ResearchContext.Provider>
  );
}

export function useResearch() {
  const context = useContext(ResearchContext);
  if (!context) {
    throw new Error("useResearch must be used within a ResearchProvider");
  }
  return context;
}
