# Research Assistant with Persistent Memory (RAG Platform)

> **Enterprise-Grade Retrieval-Augmented Generation (RAG) Platform & Knowledge Management System with LangGraph Agents**

![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-009688.svg?style=flat&logo=fastapi&logoColor=white)
![Next.js](https://img.shields.io/badge/Next.js-16.3-black.svg?style=flat&logo=next.js&logoColor=white)
![ChromaDB](https://img.shields.io/badge/ChromaDB-Persistent-FF6F00.svg?style=flat)
![LangGraph](https://img.shields.io/badge/LangGraph-Agentic%20Orchestration-blueviolet.svg)
![Mistral AI](https://img.shields.io/badge/Mistral%20AI-open--mistral--nemo-orange.svg)
![LiteLLM](https://img.shields.io/badge/LiteLLM-Multi--Model-blue.svg)
![FastEmbed](https://img.shields.io/badge/FastEmbed-ONNX%20Local-green.svg)
![n8n](https://img.shields.io/badge/n8n-Workflow%20Automation-EA4B71.svg?style=flat&logo=n8n&logoColor=white)
![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB.svg?style=flat&logo=python&logoColor=white)

---

## 📋 Table of Contents
1. [What It Does](#-1-what-it-does)
2. [System Architecture & LangGraph Agents](#-2-system-architecture--langgraph-agents) *(Deep Dive: [docs/architecture.md](docs/architecture.md))*
3. [AI Models & Embedding Strategy](#-3-ai-models--embedding-strategy)
4. [Platform Workflows & Pipelines](#-platform-workflows--data-pipelines) *(Deep Dive: [docs/workflow.md](docs/workflow.md))*
5. [How to Run the Application](#-4-how-to-run-the-application)
6. [n8n Automation & Webhook Workflow](#-5-n8n-automation--webhook-workflow)
7. [Environment Variables Reference (`.env`)](#-6-environment-variables-reference-env)
8. [API Endpoints Overview](#-7-api-endpoints-overview)
9. [Documentation Hub](#-documentation-hub)

---

## 🌟 1. What It Does

**Research Assistant with Persistent Memory** is a full-stack RAG (Retrieval-Augmented Generation) application designed for deep online research, document indexing, and grounded knowledge retrieval.

Users submit web URLs (articles, documentation, blogs, or Wikipedia entries). The platform automatically scrapes, cleans, chunks, embeds, and permanently stores the knowledge in ChromaDB. When users ask questions, the system retrieves the most relevant passages and synthesizes an answer strictly backed by citations mapped directly to the original web sources.

### Core Capabilities:
- **Intelligent Web Scraping & Ingestion**:
  - Automatically fetches and cleans web content using browser header rotation, anti-bot protection handling, and HTML noise removal (stripping ads, scripts, navbars, and footers).
  - Preserves hierarchical markdown structure (headings `#`, `##`, `###`, lists, and code blocks).
- **Persistent Multi-Session Memory (ChromaDB)**:
  - Additive vector database persists all indexed sources across server restarts.
  - Multi-level deduplication (URL hash + SHA-256 content hashing) avoids duplicate re-indexing.
- **Strict Grounding & Citation Attribution**:
  - Answers are directly linked to indexed passages with citation chips (`[1]`, `[2]`).
  - Interactive Evidence Panel allows users to view the exact text chunks and source metadata that generated the answer.
- **Zero-Hallucination Guardrails**:
  - When context is not found in the indexed sources, the system replies:
    `"The requested information was not found in the provided source."`
- **LangGraph Multi-Agent Routing**:
  - Supervisor Agent dynamically classifies query intents and routes to specialized RAG or general conversational pipelines.
- **n8n Automation Engine**:
  - Out-of-the-box integration for external, event-driven web scraping workflows via secure webhooks.
- **Exportable PDF Reports**:
  - One-click PDF generation compiles questions, grounded answers, citations, and metadata into a publication-ready research report.

---

## 🏛️ 2. System Architecture & LangGraph Agents

The system is built on a clean **two-pillar architecture**:

```
                       +---------------------------------------+
                       |             User Question             |
                       +-------------------+-------------------+
                                           |
                                           v
                             +---------------------------+
                             |     Supervisor Agent      |
                             |   (Intent Classifier)     |
                             +-------------+-------------+
                                           |
                   +-----------------------+-----------------------+
                   | (rag_query)                                   | (general)
                   v                                               v
        +----------------------+                        +----------------------+
        |      RAG Agent       |                        |    General Agent     |
        |  (Dense Retrieval &  |                        |  (Conversational LLM |
        | Citation Attribution)|                        |      Responses)      |
        +----------+-----------+                        +----------+-----------+
                   |                                               |
                   v                                               v
       +-----------------------+                        +----------------------+
       | FastEmbed + ChromaDB  |                        |     Final Output     |
       |  (Persistent Memory)  |                        +----------------------+
       +-----------------------+
```

### Folder Structure
```
Capstone project/
├── Backend/
│   ├── src/
│   │   ├── agents/
│   │   │   ├── supervisor/      # Supervisor Graph & Intent Router
│   │   │   ├── rag_agent/       # RAG Agent node & execution
│   │   │   └── llm/             # Multi-LLM Failover Router
│   │   ├── rag/
│   │   │   ├── components/
│   │   │   │   ├── retrieval/   # Semantic search & re-ranking
│   │   │   │   ├── vector_store/# ChromaDB Persistent Repository
│   │   │   │   ├── data_processor/# Ingestion, chunking, embeddings
│   │   │   │   └── citations/   # Citation attribution & grounding engine
│   │   │   ├── prompts/         # Anti-hallucination prompt templates
│   │   │   └── rag_pipeline.py  # Orchestrator for RAG components
│   │   ├── api/                 # FastAPI routes and middlewares
│   │   ├── services/            # ChatService, IngestionService, SourceService
│   │   └── scraper/             # Webpage fetcher, cleaner & extractor
│   └── n8n/                     # Exported n8n workflow definitions
├── frontend/                    # Next.js 16 (App Router) + Tailwind CSS
├── n8n/                         # Webhook workflow JSON
├── main.py                      # Root backend entry point
└── requirements.txt             # Python dependencies
```

---

## 🧠 3. AI Models & Embedding Strategy

```
                   +--------------------------------------------+
                   |          LiteLLM Multi-Model Router        |
                   +---------------------+----------------------+
                                         |
           +-----------------------------+-----------------------------+
           |                             |                             |
           v (Primary)                   v (Fallback 1)                v (Fallback 2)
+---------------------+       +---------------------+       +---------------------+
| Mistral AI          |       | Google Gemini       |       | Zhipu GLM           |
| open-mistral-nemo   | ===>  | gemini-2.5-flash    | ===>  | glm-4-flash         |
+---------------------+       +---------------------+       +---------------------+
```

### 1. Local Vector Embeddings: `BAAI/bge-small-en-v1.5` (via FastEmbed)
- **100% Local & Free**: Runs directly on the CPU/GPU with zero external API calls or costs.
- **Lightweight 384 Dimensions**: Provides high retrieval accuracy with minimal disk footprint in ChromaDB.
- **High-Speed ONNX Runtime**: Embeds text chunks in milliseconds.

### 2. Primary LLM: `mistral/open-mistral-nemo` (via Mistral AI & LiteLLM)
- **128k Context Window**: Effortlessly ingests multiple retrieved passages and citations without truncation.
- **Strict Grounding**: Follows system prompt constraints to cite sources and prevent hallucinations.
- **Automatic Fallback Chain**: Tiered failover to `mistral/open-mistral-7b`, `gemini/gemini-2.5-flash`, and `openai/glm-4-flash`.

---

## 🚀 4. How to Run the Application

### Prerequisites
- **Python 3.10+** (Python 3.11 / 3.12 recommended)
- **Node.js 18+** and **npm**
- Modern Web Browser (Chrome, Edge, Firefox)

---

### Step 1: Start the Backend (FastAPI)

From the project root:
```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run backend server
python main.py
```
Backend will start on: **`http://127.0.0.1:8000`**  
Interactive API Docs (Swagger): **`http://127.0.0.1:8000/docs`**

---

### Step 2: Start the Frontend (Next.js)

Open a second terminal window:
```bash
cd frontend

# 1. Install node dependencies
npm install

# 2. Start Next.js development server
npm run dev
```
Frontend will be available on: **`http://localhost:3000`**

---

## ⚡ 5. n8n Automation & Webhook Workflow

The project includes an **n8n Workflow** for automated web scraping and webhook callbacks:

- **Workflow File**: [`n8n/research_assistant_workflow.json`](n8n/research_assistant_workflow.json)

### Workflow Steps:
1. **Webhook Node**: Receives incoming URL ingestion requests (`POST /webhook/research-assistant/scrape`).
2. **Code in JavaScript**: Validates incoming parameters (`job_id`, `source_id`, `url`, `callback_url`).
3. **HTTP Request**: Downloads the webpage HTML.
4. **Content Cleaning**: Strips scripts, styles, boilerplate, and normalizes headings into clean markdown.
5. **Metadata Extraction**: Extracts titles, domain names, word counts, and language.
6. **Callback Dispatch**: Posts extracted content back to the FastAPI backend at `/api/v1/ingestion/callback`.

---

## ⚙️ 6. Environment Variables Reference (`.env`)

Create a `.env` file in the project root:

```env
# Application Settings
APP_NAME="Research Assistant with Persistent Memory"
APP_ENV="development"
DEBUG=true
PORT=8000
HOST="0.0.0.0"
API_V1_PREFIX="/api/v1"

# Vector Database (ChromaDB)
CHROMA_PERSIST_DIRECTORY="./data/chromadb"
CHROMA_COLLECTION_SOURCES="research_sources"
CHROMA_COLLECTION_CHUNKS="research_chunks"

# Embedding Configuration
EMBEDDING_PROVIDER="fastembed"
EMBEDDING_MODEL="BAAI/bge-small-en-v1.5"
EMBEDDING_DIMENSION=384
EMBEDDING_BATCH_SIZE=32

# Multi-Model Router Configuration
PRIMARY_MODEL="mistral/open-mistral-nemo"
FALLBACK_MODEL_1="mistral/open-mistral-7b"
FALLBACK_MODEL_2="mistral/ministral-8b-latest"

# LLM API Keys
MISTRAL_API_KEY="your-mistral-api-key"
GEMINI_API_KEY="your-gemini-api-key"
ZHIPUAI_API_KEY="your-zhipu-api-key"
GLM_API_KEY="your-zhipu-api-key"

# Chunking & Retrieval
CHUNK_SIZE=800
CHUNK_OVERLAP=150
DEFAULT_TOP_K=5
DEFAULT_SIMILARITY_THRESHOLD=0.15
```

---

## 📡 7. API Endpoints Overview

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/v1/health` | System health diagnostics (ChromaDB, active LLM, chunk counts) |
| `POST` | `/api/v1/ingest` | Synchronous ingestion for single or batch URLs |
| `GET` | `/api/v1/sources` | List all indexed sources with pagination and filtering |
| `DELETE` | `/api/v1/sources/{id}` | Delete source and purge associated vectors from ChromaDB |
| `POST` | `/api/v1/chat` | Query RAG pipeline via LangGraph Supervisor Agent |
| `GET` | `/api/v1/chat/history/{session_id}` | Retrieve multi-turn chat session history |
| `POST` | `/api/v1/export/pdf` | Generate and download publication-ready research PDF report |

---

## 🧪 Testing

Run the comprehensive pytest suite:
```bash
cd Backend
python -m pytest src/tests/ -v
```
*(All 23 unit and integration tests passing)*

---

## 📚 8. Documentation Hub

For in-depth architectural designs, sequence diagrams, and detailed pipeline specifications:
- 🏛️ **[System Architecture Guide](docs/architecture.md)**: Deep dive into the modular RAG subsystems, LangGraph agents, LiteLLM multi-tier fallback, and ChromaDB persistence models.
- 🔄 **[Platform Workflows & Pipelines](docs/workflow.md)**: Step-by-step ingestion workflows, retrieval pipelines, n8n webhook architectures, and PDF generation processes.

