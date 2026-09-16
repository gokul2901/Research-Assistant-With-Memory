import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { chatApi } from "@/api/chat";
import { ChatRequest, ChatResponse, ChatSessionHistoryResponse, ChatMessageHistoryItem } from "@/types";
import { toast } from "sonner";
import { useState, useCallback, useEffect } from "react";

export const CHAT_HISTORY_QUERY_KEY = (sessionId: string) => ["chat", "history", sessionId];

export function useChatHistory(sessionId: string | null) {
  return useQuery({
    queryKey: sessionId ? CHAT_HISTORY_QUERY_KEY(sessionId) : ["chat", "history", "none"],
    queryFn: () => (sessionId ? chatApi.getSessionHistory(sessionId) : null),
    enabled: !!sessionId,
    retry: false, // Don't spam retries if session history isn't created in backend yet
  });
}

export function useResearchChat(sessionId: string) {
  const queryClient = useQueryClient();
  const [localMessages, setLocalMessages] = useState<ChatMessageHistoryItem[]>([]);
  const [isSubmitting, setIsSubmitting] = useState<boolean>(false);

  // Load history from backend
  const {
    data: historyData,
    isLoading: isHistoryLoading,
    error: historyError,
    refetch: refetchHistory,
  } = useChatHistory(sessionId);

  // Sync localMessages when backend history arrives
  useEffect(() => {
    if (historyData?.messages) {
      setLocalMessages(historyData.messages);
    } else {
      setLocalMessages([]);
    }
  }, [historyData, sessionId]);

  const askMutation = useMutation({
    mutationFn: (req: ChatRequest) => chatApi.askQuestion(req),
    onMutate: async (newQuestionReq) => {
      setIsSubmitting(true);
      // Optimistically push user message
      const tempUserMsg: ChatMessageHistoryItem = {
        message_id: `temp_user_${Date.now()}`,
        role: "user",
        content: newQuestionReq.question,
        timestamp: new Date().toISOString(),
      };
      setLocalMessages((prev) => [...prev, tempUserMsg]);
    },
    onSuccess: (chatResponse: ChatResponse) => {
      setIsSubmitting(false);
      // Create assistant message with citations and source metadata
      const assistantMsg: ChatMessageHistoryItem = {
        message_id: `resp_${Date.now()}`,
        role: "assistant",
        content: chatResponse.answer,
        timestamp: new Date().toISOString(),
        citations: chatResponse.citations,
        sources: chatResponse.sources,
        model_used: chatResponse.model_used,
        retrieved_chunk_count: chatResponse.retrieved_chunks_count,
        is_grounded: chatResponse.is_grounded,
        execution_time_ms: chatResponse.execution_time_ms,
      };

      setLocalMessages((prev) => [...prev, assistantMsg]);
      // Invalidate query to sync full backend state if needed
      queryClient.invalidateQueries({ queryKey: CHAT_HISTORY_QUERY_KEY(sessionId) });
    },
    onError: (error: Error) => {
      setIsSubmitting(false);
      toast.error(error.message || "Failed to generate grounded research response.");
    },
  });

  const sendQuestion = useCallback(
    async (
      question: string,
      options?: {
        topK?: number;
        similarityThreshold?: number;
        sourceFilters?: string[];
        modelOverride?: string;
      }
    ) => {
      if (!question.trim() || isSubmitting) return;

      const payload: ChatRequest = {
        question: question.trim(),
        session_id: sessionId,
        top_k: options?.topK ?? 5,
        similarity_threshold: options?.similarityThreshold ?? 0.35,
        source_filters: options?.sourceFilters,
        model_override: options?.modelOverride,
      };

      return askMutation.mutateAsync(payload);
    },
    [askMutation, isSubmitting, sessionId]
  );

  return {
    messages: localMessages,
    isHistoryLoading,
    isSubmitting: isSubmitting || askMutation.isPending,
    historyError,
    sendQuestion,
    refetchHistory,
  };
}
