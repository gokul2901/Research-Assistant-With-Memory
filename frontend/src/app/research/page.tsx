"use client";

import React from "react";
import { AppShell } from "@/components/layout/AppShell";
import { ResearchChat } from "@/components/research/ResearchChat";
import { EvidencePanel } from "@/components/research/EvidencePanel";
import { useResearch } from "@/context/ResearchContext";
import { useResearchChat } from "@/hooks/useChat";

export default function ResearchWorkspacePage() {
  const { currentSessionId } = useResearch();
  const { messages } = useResearchChat(currentSessionId);

  // Get latest assistant message for the evidence panel
  const latestAssistantMessage = [...messages]
    .reverse()
    .find((m) => m.role === "assistant");

  return (
    <AppShell>
      <div className="flex-1 flex overflow-hidden h-[calc(100vh-3.5rem)]">
        {/* CENTER: Research Conversation */}
        <ResearchChat sessionId={currentSessionId} />

        {/* RIGHT: Sources & Evidence Panel */}
        <EvidencePanel latestMessage={latestAssistantMessage} />
      </div>
    </AppShell>
  );
}
