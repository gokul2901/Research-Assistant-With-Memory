"use client";

import React, { useEffect } from "react";
import { useParams } from "next/navigation";
import { AppShell } from "@/components/layout/AppShell";
import { ResearchChat } from "@/components/research/ResearchChat";
import { EvidencePanel } from "@/components/research/EvidencePanel";
import { useResearch } from "@/context/ResearchContext";
import { useResearchChat } from "@/hooks/useChat";

export default function IndividualSessionPage() {
  const params = useParams();
  const rawId = params?.id;
  const sessionId = Array.isArray(rawId) ? rawId[0] : rawId || "session_main";

  const { setCurrentSessionId } = useResearch();
  const { messages } = useResearchChat(sessionId);

  useEffect(() => {
    if (sessionId) {
      setCurrentSessionId(sessionId);
    }
  }, [sessionId, setCurrentSessionId]);

  const latestAssistantMessage = [...messages]
    .reverse()
    .find((m) => m.role === "assistant");

  return (
    <AppShell>
      <div className="flex-1 flex overflow-hidden h-[calc(100vh-3.5rem)]">
        {/* CENTER: Research Conversation */}
        <ResearchChat sessionId={sessionId} />

        {/* RIGHT: Sources & Evidence Panel */}
        <EvidencePanel latestMessage={latestAssistantMessage} />
      </div>
    </AppShell>
  );
}
