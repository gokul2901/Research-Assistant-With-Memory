"use client";

import React from "react";
import { useResearch } from "@/context/ResearchContext";
import { CitationItem } from "@/types";

export interface CitationMarkerProps {
  index: number;
  citation?: CitationItem;
  onClick?: () => void;
}

export function CitationMarker({ index, citation, onClick }: CitationMarkerProps) {
  const { activeCitation, setActiveCitation, setIsEvidencePanelOpen } = useResearch();

  const isSelected = activeCitation?.citation_index === index;

  const handleClick = (e: React.MouseEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (citation) {
      setActiveCitation(citation);
    }
    setIsEvidencePanelOpen(true);
    onClick?.();
  };

  return (
    <button
      type="button"
      onClick={handleClick}
      className={`inline-flex items-center justify-center font-mono font-bold text-[10px] px-1.5 py-0.2 mx-0.5 rounded transition-all duration-150 cursor-pointer align-baseline select-none ${
        isSelected
          ? "bg-indigo-500 text-white shadow-md shadow-indigo-500/40 ring-2 ring-indigo-400/50 scale-105"
          : "bg-indigo-500/15 text-indigo-300 hover:bg-indigo-500/30 hover:text-indigo-200 border border-indigo-500/30 hover:scale-105"
      }`}
      title={citation ? `[Source ${index}] ${citation.title}` : `Source [${index}]`}
      aria-label={`Jump to citation ${index}`}
    >
      [{index}]
    </button>
  );
}
