// =============================================================================
// Common Backend API Responses
// =============================================================================

export interface APIResponse<T> {
  success: boolean;
  message: string;
  data: T;
  error?: string | null;
}

export interface HealthStatus {
  status: "healthy" | "degraded" | "unhealthy" | string;
  version: string;
  environment: string;
  vectorstore_status: string;
  indexed_sources_count: number;
  indexed_chunks_count: number;
  active_primary_llm: string;
  fallback_llms: string[];
}

// =============================================================================
// Source Management Types
// =============================================================================

export interface Source {
  source_id: string;
  url: string;
  title: string;
  domain: string;
  date_added: string;
  last_updated: string;
  content_hash: string;
  status: "indexed" | "failed" | "processing" | "duplicate" | "updated" | string;
  chunk_count: number;
  character_count: number;
  error_message?: string | null;
}

export interface SourceListResponse {
  total_sources: number;
  sources: Source[];
}

export interface DomainStat {
  domain: string;
  source_count: number;
  chunk_count: number;
}

export interface SourceStatistics {
  total_sources: number;
  total_chunks: number;
  total_characters: number;
  indexed_sources: number;
  failed_sources: number;
  domain_breakdown: DomainStat[];
}

export interface SourceRefreshResponse {
  source_id: string;
  url: string;
  status: string;
  message: string;
  old_hash: string;
  new_hash: string;
  chunk_count: number;
}

// =============================================================================
// Ingestion Types
// =============================================================================

export interface IngestUrlRequest {
  url?: string;
  urls?: string[];
  force_refresh?: boolean;
}

export interface IngestionItemResult {
  source_id: string;
  url: string;
  title: string;
  domain: string;
  status: "indexed" | "failed" | "duplicate" | "updated" | string;
  chunk_count: number;
  character_count: number;
  content_hash: string;
  date_added: string;
  error_message?: string | null;
}

export interface IngestionSummaryResponse {
  total_requested: number;
  successful_count: number;
  failed_count: number;
  duplicate_count: number;
  results: IngestionItemResult[];
}

// Pipeline stages for animated ingestion feedback
export type IngestionStage =
  | "QUEUED"
  | "FETCHING"
  | "PROCESSING"
  | "CHUNKING"
  | "EMBEDDING"
  | "INDEXING"
  | "COMPLETED"
  | "FAILED";

// =============================================================================
// Chat & Research Types
// =============================================================================

export interface ChatRequest {
  question: string;
  session_id?: string;
  top_k?: number;
  similarity_threshold?: number;
  source_filters?: string[];
  model_override?: string;
}

export interface CitationItem {
  citation_index: number;
  source_id: string;
  url: string;
  title: string;
  chunk_id?: string | null;
  snippet?: string | null;
}

export interface SourceMetadataRef {
  source_id: string;
  url: string;
  title: string;
  domain: string;
  chunk_count: number;
}

export interface ChatResponse {
  question: string;
  answer: string;
  citations: CitationItem[];
  sources: SourceMetadataRef[];
  session_id: string;
  model_used: string;
  retrieved_chunks_count: number;
  is_grounded: boolean;
  execution_time_ms: number;
}

export interface ChatMessageHistoryItem {
  message_id: string;
  role: "user" | "assistant" | "system";
  content: string;
  timestamp: string;
  citations?: CitationItem[];
  sources?: SourceMetadataRef[];
  model_used?: string;
  retrieved_chunk_count?: number;
  is_grounded?: boolean;
  execution_time_ms?: number;
}

export interface ChatSessionHistoryResponse {
  session_id: string;
  total_messages: number;
  created_at: string;
  messages: ChatMessageHistoryItem[];
}

// =============================================================================
// PDF Export Types
// =============================================================================

export interface ExportPDFRequest {
  session_id?: string;
  question_ids?: string[];
  report_title?: string;
  include_sources_summary?: boolean;
  include_full_citations?: boolean;
}

export interface ExportPDFResponse {
  download_url: string;
  file_name: string;
  file_size_bytes: number;
  generated_at: string;
}

// =============================================================================
// Local Session Management Types
// =============================================================================

export interface ResearchSessionMeta {
  id: string;
  title: string;
  createdAt: string;
  updatedAt: string;
  questionCount: number;
  previewText?: string;
}
