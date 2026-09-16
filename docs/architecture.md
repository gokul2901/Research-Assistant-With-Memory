# System Architecture & Technical Specifications

> **Comprehensive architectural overview of the Research Assistant with Persistent Memory platform, detailing component interactions, multi-agent orchestration, data flows, and storage design.**

---

## 🏛️ 1. High-Level Architecture

The platform follows a modern, decoupled client-server architecture built for scalable document ingestion, agentic orchestration, persistent vector retrieval, and grounded question answering:

```mermaid
flowchart TB
    subgraph ClientLayer["🖥️ Presentation Layer (Next.js 16 + Tailwind CSS)"]
        UI["Web Dashboard & Chat Interface"]
        SourceUI["Source Management & Evidence Panel"]
        ExportUI["PDF Report Generator"]
    end

    subgraph APILayer["⚡ API Gateway (FastAPI)"]
        Router["FastAPI REST Router (/api/v1)"]
        ChatEP["/chat & /chat/history"]
        IngestEP["/ingest & /sources"]
        ExportEP["/export/pdf"]
    end

    subgraph AgentLayer["🧠 Agentic Layer (LangGraph Multi-Agent)"]
        Supervisor["Supervisor Agent (Intent Classifier)"]
        RAGAgent["RAG Specialist Agent"]
        GeneralAgent["General Conversational Agent"]
        LLMRouter["LiteLLM Multi-Model Router (Mistral / Gemini / GLM)"]
    end

    subgraph RAGCore["🔬 RAG Pipeline & Components"]
        DataProc["Data Processor (Chunking & Ingestion)"]
        Embedder["FastEmbed (BAAI/bge-small-en-v1.5)"]
        Retriever["Dense Retriever & Re-ranker"]
        CitationEngine["Grounding & Citation Attribution Engine"]
    end

    subgraph StorageLayer["💾 Persistent Storage & Automation"]
        ChromaSources[("ChromaDB: research_sources")]
        ChromaChunks[("ChromaDB: research_chunks")]
        n8n["n8n Webhook Automation Engine"]
    end

    UI --> Router
    SourceUI --> IngestEP
    ExportUI --> ExportEP

    ChatEP --> Supervisor
    Supervisor -->|intent: rag_query| RAGAgent
    Supervisor -->|intent: general| GeneralAgent

    RAGAgent --> Retriever
    Retriever --> Embedder
    Embedder --> ChromaChunks
    Retriever --> CitationEngine
    RAGAgent --> LLMRouter

    IngestEP --> DataProc
    DataProc --> Embedder
    DataProc --> ChromaSources
    DataProc --> ChromaChunks
    n8n -.-> IngestEP
```

---

## 🧩 2. Component Breakdown

### 2.1 Backend Architecture (`Backend/src/`)

The backend is written in Python (FastAPI) and structured into modular, single-responsibility layers:

```
Backend/src/
├── agents/                      # Multi-agent orchestrators (LangGraph)
│   ├── supervisor/              # Query routing and intent classification graph
│   │   ├── graph.py             # StateGraph definition & execution
│   │   └── router.py            # Zero-shot intent categorization
│   ├── rag_agent/               # Grounded retrieval node
│   │   └── agent.py             # Context fetching, prompt formatting, LLM call
│   └── llm/                     # Resilient model abstraction
│       └── provider.py          # LiteLLM failover router (Mistral -> Gemini -> GLM)
├── rag/                         # Modular RAG subsystems
│   ├── components/
│   │   ├── data_processor/      # Chunking, FastEmbed embeddings, Ingestion pipeline
│   │   │   ├── chunking.py      # Recursive markdown chunker with overlap
│   │   │   ├── embeddings.py    # Local FastEmbed BGE-small-en ONNX runtime
│   │   │   └── ingestion.py     # Document pre-processing and validation
│   │   ├── vector_store/        # ChromaDB persistent store repository
│   │   │   ├── chroma_client.py # Thread-safe persistent Chroma client
│   │   │   └── repository.py    # Dual-collection CRUD and deduplication
│   │   ├── retrieval/           # Search & re-ranking engines
│   │   │   ├── search.py        # Cosine similarity vector search
│   │   │   └── reranker.py      # Cross-score normalization & top-k filtering
│   │   └── citations/           # Evidence verification & attribution
│   │       └── engine.py        # Citation mapper ([1], [2]) and grounding checks
│   ├── prompts/                 # Anti-hallucination prompt templates
│   │   └── templates.py         # System prompts and strict constraint templates
│   └── rag_pipeline.py          # Unified RAG orchestrator interface
├── api/                         # FastAPI routing and controllers
│   ├── routes/                  # /chat, /ingest, /sources, /health, /export
│   └── schemas/                 # Pydantic request and response contracts
├── services/                    # Business logic services
│   ├── chat_service.py          # Chat session history and multi-turn state
│   ├── ingestion_service.py     # Synchronous and async URL ingestion
│   └── source_service.py        # Source listing, counts, and purge operations
├── scraper/                     # Resilient web scraping
│   ├── fetcher.py               # User-Agent rotation, timeout handling
│   └── cleaner.py               # HTML boiler-plate stripping, Markdown preservation
└── config/                      # Settings & environment variables via pydantic-settings
```

---

## 🤖 3. Multi-Agent System (LangGraph)

The platform utilizes **LangGraph** to construct a dynamic decision graph:

```mermaid
stateDiagram-v2
    [*] --> SupervisorNode: User Query Received
    SupervisorNode --> IntentEvaluation: Evaluate Query Context & Keywords
    
    IntentEvaluation --> RAGAgentNode: Requires External / Domain Knowledge
    IntentEvaluation --> GeneralAgentNode: Conversational / Greetings / Meta
    
    RAGAgentNode --> RetrievalStep: Embed Query & Retrieve ChromaDB Chunks
    RetrievalStep --> CitationStep: Ground Context & Map Numerical Citations
    CitationStep --> LLMGenerationStep: Synthesize Response with Mistral AI
    
    GeneralAgentNode --> DirectLLMStep: Direct Response Generation
    
    LLMGenerationStep --> EndState: Return Grounded Response + Evidence
    DirectLLMStep --> EndState: Return General Response
    EndState --> [*]
```

### Agent Roles:
1. **Supervisor Agent (`src/agents/supervisor/`)**:
   - Inspects user input and chat history.
   - Routes to `rag_agent` if the query relates to indexed documents, research topics, or domain-specific queries.
   - Routes to `general_agent` for conversational pleasantries, formatting requests, or meta questions.

2. **RAG Agent (`src/agents/rag_agent/`)**:
   - Fetches dense vector embeddings for the query.
   - Queries ChromaDB persistent collections with similarity thresholds.
   - Formats citations (`[1]`, `[2]`, etc.) referencing exact chunk identifiers and source URLs.
   - Applies strict anti-hallucination prompt guardrails.

---

## ⚡ 4. AI & Embeddings Architecture

```
                      +-------------------------------------------------+
                      |           LiteLLM Provider Failover             |
                      +------------------------+------------------------+
                                               |
              +--------------------------------+--------------------------------+
              |                                |                                |
              v (Tier 1: Primary)              v (Tier 2: Fallback)             v (Tier 3: Fallback)
    +-------------------+            +-------------------+            +-------------------+
    |    Mistral AI     |            |   Google Gemini   |            |     Zhipu GLM     |
    | open-mistral-nemo | ===FAIL==> | gemini-2.5-flash  | ===FAIL==> |    glm-4-flash    |
    +-------------------+            +-------------------+            +-------------------+
```

### Embedding Architecture:
- **Model**: `BAAI/bge-small-en-v1.5`
- **Engine**: `FastEmbed` (ONNX Runtime)
- **Dimensionality**: 384 dimensions
- **Characteristics**: 100% local, zero latency external API overhead, zero cost, deterministic embeddings.

### LLM Orchestration:
- Unified via `LiteLLM` with transparent retry and fallback mechanisms.
- Primary Model: **Mistral AI (`open-mistral-nemo`)** with 128k context window and top-tier instruction following.

---

## 🗄️ 5. Persistent Storage & Deduplication (ChromaDB)

The vector store manages two distinct collections persisted to disk at `./data/chromadb/`:

```mermaid
erDiagram
    RESEARCH_SOURCES ||--o{ RESEARCH_CHUNKS : "1-to-Many"
    
    RESEARCH_SOURCES {
        string id PK "SHA256(URL)"
        string url "Original Web URL"
        string title "Extracted Page Title"
        int chunk_count "Total Chunks Indexed"
        string created_at "ISO Timestamp"
        string status "ACTIVE / DELETED"
    }

    RESEARCH_CHUNKS {
        string id PK "source_id_chunk_idx"
        string source_id FK "References RESEARCH_SOURCES.id"
        string text "Segmented Markdown Content"
        int chunk_index "0-indexed position"
        float embedding "384-d vector"
    }
```

### Deduplication Logic:
1. **URL Normalization & Hash**: Incoming URLs are stripped of tracking query params and lowercased.
2. **Content Hash Check**: SHA-256 hash of extracted text verifies if the document has changed.
3. **Additive Persistence**: If a source already exists, it is either skipped or refreshed without duplicate vector generation.

---

## 🛡️ 6. Guardrails & Anti-Hallucination

The system enforces strict hallucination boundaries:
- **System Prompt Rules**: The LLM is instructed to answer strictly from the retrieved context.
- **Strict Fallback Sentence**: If the retrieved context does not contain sufficient facts to answer the question, the system produces the deterministic phrase:
  > *"The requested information was not found in the provided source."*
- **Citation Cross-Validation**: Every factual claim maps to an explicit `[N]` reference backed by an indexed source in the Evidence Panel.
