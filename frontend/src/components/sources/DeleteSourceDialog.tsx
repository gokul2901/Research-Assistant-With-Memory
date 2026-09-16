"use client";

import React from "react";
import { Modal } from "@/ui/Modal";
import { Button } from "@/ui/Button";
import { Source } from "@/types";
import { useDeleteSource } from "@/hooks/useSources";
import { AlertTriangle, Trash2 } from "lucide-react";

export interface DeleteSourceDialogProps {
  source: Source | null;
  isOpen: boolean;
  onClose: () => void;
}

export function DeleteSourceDialog({
  source,
  isOpen,
  onClose,
}: DeleteSourceDialogProps) {
  const deleteMutation = useDeleteSource();

  if (!source) return null;

  const handleDelete = async () => {
    try {
      await deleteMutation.mutateAsync(source.source_id);
      onClose();
    } catch {
      // Handled in mutation
    }
  };

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title="Delete Knowledge Source"
      maxWidth="sm"
    >
      <div className="space-y-4">
        <div className="flex items-start gap-3 p-3.5 rounded-xl bg-red-950/20 border border-red-500/25 text-xs text-red-200">
          <AlertTriangle className="w-5 h-5 text-red-400 shrink-0 mt-0.5" />
          <div className="space-y-1">
            <p className="font-semibold text-red-300">Permanent Action</p>
            <p className="text-red-300/80 leading-relaxed">
              This will permanently purge <strong>{source.title || source.domain}</strong> and all{" "}
              <strong>{source.chunk_count} vector embeddings</strong> from ChromaDB memory.
            </p>
          </div>
        </div>

        <div className="p-3 rounded-lg bg-slate-950/60 border border-slate-800 text-xs space-y-1">
          <p className="text-slate-400">Target URL:</p>
          <p className="font-mono text-[11px] text-slate-300 truncate">{source.url}</p>
        </div>

        <div className="flex items-center justify-end gap-2.5 pt-2 border-t border-slate-800/80">
          <Button
            type="button"
            variant="ghost"
            size="sm"
            onClick={onClose}
            disabled={deleteMutation.isPending}
          >
            Cancel
          </Button>
          <Button
            type="button"
            variant="danger"
            size="sm"
            isLoading={deleteMutation.isPending}
            onClick={handleDelete}
            leftIcon={<Trash2 className="w-3.5 h-3.5" />}
          >
            Delete Permanently
          </Button>
        </div>
      </div>
    </Modal>
  );
}
