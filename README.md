# Research Assistant with Persistent Memory (RAG Platform)

> **Enterprise-Grade Retrieval-Augmented Generation (RAG) Platform & Knowledge Management System**

![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-009688.svg?style=flat&logo=fastapi&logoColor=white)
![Next.js](https://img.shields.io/badge/Next.js-16.3-black.svg?style=flat&logo=next.js&logoColor=white)
![ChromaDB](https://img.shields.io/badge/ChromaDB-Persistent-FF6F00.svg?style=flat)
![LiteLLM](https://img.shields.io/badge/LiteLLM-Multi--Model-blue.svg)
![FastEmbed](https://img.shields.io/badge/FastEmbed-ONNX%20Local-green.svg)
![n8n](https://img.shields.io/badge/n8n-Workflow%20Automation-EA4B71.svg?style=flat&logo=n8n&logoColor=white)
![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB.svg?style=flat&logo=python&logoColor=white)

---

## 📋 Table of Contents
1. [What It Does](#-1-what-it-does)
2. [Which AI Models Are Used and Why](#-2-which-ai-models-are-used-and-why)
3. [How to Run the Application](#-3-how-to-run-the-application)
4. [n8n Automation & Every Node Explained](#-4-n8n-automation--every-node-explained)
5. [Environment Variables Reference (`.env`)](#-5-environment-variables-reference-env)
6. [API Endpoints Overview](#-6-api-endpoints-overview)
lP/;l,ikmujnyhbtvgrcfe}
---

## 🌟 1. What It Does

**Research Assistant with Persistent Memory** is a complete, full-stack RAG (Retrieval-Augmented Generation) application designed for deep online research, document indexing, and grounded knowledge retrieval.

Users submit web URLs (articles, documentation, blogs, or Wikipedia entries). The platform scrapes, cleans, chunks, embeds, and permanently stores the knowledge in ChromaDB. When users ask questions, the system retrieves the most relevant passages and synthesizes an answer strictly backed by citations mapped directly to the original web sources.

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
- **Zero-Hallucination Guardrails & General Knowledge Fallback**:
  - When indexed sources are relevant, the AI answers strictly from the context with zero external hallucinations.
  - When a query cannot be answered by the knowledge base, the system intelligently falls back to general knowledge with a clear visual badge, preventing false claims.
- **n8n Automation Engine**:
  - Out-of-the-box integration for external, event-driven web scraping workflows via secure webhooks.
- **Exportable PDF Reports**:
  - One-click PDF generation compiles questions, grounded answers, citations, and metadata into a publication-ready research report.

---

## 🧠 2. Which AI Models Are Used and Why

The platform employs a hybrid AI strategy: a high-speed local embedding model combined with a multi-provider LLM failover router.

```
                   +--------------------------------------------+
                   |                User Question               |
                   +---------------------+----------------------+
                                         |
                       [ FastEmbed / BAAI/bge-small-en-v1.5 ]
                                         v
                         Vector Search in ChromaDB
                                         |
                         Passages Retrieved & Re-ranked
                                         |
                   +---------------------+----------------------+
                   |          LiteLLM Multi-Model Router        |
                   +---------------------+----------------------+
                                         |
           +-----------------------------+-----------------------------+
           |                             |                             |
           v (Primary)                   v (Fallback 1)                v (Fallback 2)
+---------------------+       +---------------------+       +---------------------+
| Google Gemini       |       | Zhipu GLM           |       | Groq LLaMA 3.3      |
| gemini-2.5-flash    | ===>  | glm-4               | ===>  | 70b-versatile       |
+---------------------+       +---------------------+       +---------------------+
```

### 1. Vector Embedding Model: `BAAI/bge-small-en-v1.5` (via FastEmbed)
- **What it is**: A state-of-the-art sentence transformer model running locally via the `fastembed` ONNX runtime.
- **Why it was chosen**:
  - **100% Local & Free**: Runs directly on the CPU/GPU with zero external API calls, eliminating API costs and rate limits.
  - **High Performance**: Ranks at the top of the MTEB (Massive Text Embedding Benchmark) for semantic retrieval.
  - **Lightweight 384 Dimensions**: Provides high retrieval accuracy with low memory and disk footprint in ChromaDB.
  - **Ultra-Low Latency**: Batch vectorizes chunks in milliseconds.

### 2. Primary LLM: `gemini/gemini-2.5-flash` (via LiteLLM)
- **What it is**: Google’s flagship high-efficiency multimodal and text reasoning model.
- **Why it was chosen**:
  - **Sub-Second Response Times**: Rapid token streaming ensures chat feels immediate and interactive.
  - **Massive Context Window**: Effortlessly ingests multiple large text chunks and citations without truncation.
  - **Instruction Adherence**: Excels at strictly following system prompts to enforce citation grounding (`[Source X]`) and prevent hallucinations.
  - **Cost-Effective**: High rate limits and low token cost for production workloads.

### 3. Fallback LLM 1: `zhipu/glm-4` (via LiteLLM)
- **What it is**: Advanced multilingual model developed by Zhipu AI.
- **Why it was chosen**:
  - Serves as the primary failover provider if Google Gemini experiences API rate limits (HTTP 429), regional outages, or transient network timeouts.
  - Strong analytical reasoning and high adherence to structured RAG prompts.

### 4. Fallback LLM 2: `groq/llama-3.3-70b-versatile` (via LiteLLM)
- **What it is**: Meta’s open-weights LLaMA 3.3 70B hosted on Groq’s LPU (Language Processing Unit) hardware.
- **Why it was chosen**:
  - **Extreme Generation Speed**: Operates at 250+ tokens/second.
  - Independent hardware infrastructure guarantees high availability if both Google and Zhipu APIs are unavailable.

---

## 🚀 3. How to Run the Application

### Prerequisites
- **Python 3.10+** (Python 3.11 recommended)
- **Node.js 18+** and **npm**
- Modern Web Browser (Chrome, Edge, Firefox)

---

### Step 1: Clone the Repository & Configure Environment
```bash
git clone https://github.com/your-username/research-assistant.git
cd "Capstone project"
```

Verify your `.env` file exists in the project root (see [Section 5](#-5-environment-variables-reference-env) for full details).

---

### Step 2: Set Up and Start the Backend (FastAPI)

1. Open a terminal and navigate to the backend directory:
   ```powershell
   cd Backend
   ```

2. Create and activate a Python virtual environment:
   ```powershell
   # Windows PowerShell:
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   ```

3. Install required Python packages:
   ```powershell
   pip install -r ..\requirements.txt
   ```

4. Start the FastAPI server using the module runner:
   ```powershell
   python -m src.main
   ```
   *Alternative:*
   ```powershell
   uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
   ```

5. Verify the backend is online:
   - **API Root**: [http://localhost:8000](http://localhost:8000)
   - **Interactive Swagger Docs**: [http://localhost:8000/docs](http://localhost:8000/docs)
   - **System Health Endpoint**: [http://localhost:8000/api/v1/health](http://localhost:8000/api/v1/health)

---

### Step 3: Set Up and Start the Frontend (Next.js)

1. Open a second terminal window and navigate to the frontend directory:
   ```powershell
   cd frontend
   ```

2. Install Node dependencies:
   ```powershell
   npm install
   ```

3. Launch the Next.js development server:
   ```powershell
   npm run dev
   ```

4. Open your browser and navigate to:
   - **Research Interface**: 👉 **[http://localhost:3000/research](http://localhost:3000/research)**
   - **Knowledge Base Sources**: 👉 **[http://localhost:3000/sources](http://localhost:3000/sources)**

---

## ⚡ 4. n8n Automation & Every Node Explained

The project includes an automated n8n workflow definition located at:
📁 [`Backend/n8n/web_scraping_workflow.json`](file:///c:/Users/HP/Documents/Capstone%20project/Backend/n8n/web_scraping_workflow.json)

This workflow enables event-driven scraping where n8n fetches the web page, cleans the content, and calls back into the FastAPI backend for vectorization.

```
[ FastAPI Backend ]
        |
        | 1. Dispatches Job (POST)
        v
+-----------------------+     +-----------------------+     +-----------------------+
|  Node 1:              | ==> |  Node 2:              | ==> |  Node 3:              |
|  Webhook Trigger      |     |  Validate Input       |     |  Fetch Webpage HTML   |
+-----------------------+     +-----------------------+     +-----------------------+
                                                                        |
+-----------------------+     +-----------------------+                 |
|  FastAPI Storage      | <== |  Node 5:              | <== [ Node 4: Content Cleaning ]
|  /ingestion/callback  |     |  Callback POST        |     |  & Markdown Extraction   |
+-----------------------+     +-----------------------+     +-----------------------+
```

### Detailed Breakdown of Every n8n Node:

#### 1. Node 1: Webhook Trigger (`n8n-nodes-base.webhook`)
- **Name in Canvas**: `Webhook Trigger`
- **Method**: `POST`
- **Path**: `research-assistant/scrape` (or `scrape-url`)
- **What it does**:
  - Serves as the HTTP entry point for incoming scraping requests.
  - Receives the JSON body payload:
    ```json
    {
      "job_id": "job_12345",
      "source_id": "src_67890",
      "url": "https://en.wikipedia.org/wiki/Ducati",
      "callback_url": "http://localhost:8000/api/v1/ingestion/callback"
    }
    ```
- **Key Setting**: `Respond: When Last Node Finishes`.

#### 2. Node 2: Validate Input (`n8n-nodes-base.code`)
- **Name in Canvas**: `Validate Input`
- **Language**: JavaScript
- **What it does**:
  - Validates that mandatory fields (`url`, `job_id`, `source_id`, `callback_url`) are present.
  - Enforces URL security standards (checks that the scheme begins with `http://` or `https://`).
  - Throws a descriptive error if required parameters are missing before any network requests occur.

#### 3. Node 3: Fetch Webpage HTML (`n8n-nodes-base.httpRequest`)
- **Name in Canvas**: `Fetch Webpage HTML`
- **Method**: `GET`
- **URL**: `={{ $json.url }}`
- **What it does**:
  - Performs an asynchronous HTTP request to fetch the raw HTML of the destination page.
  - Sends realistic browser headers (`User-Agent: ResearchAssistantBot/1.0`, `Accept: text/html...`) to prevent simple anti-bot blocking.
  - Handles HTTP redirects automatically and enforces a 20-second timeout.

#### 4. Node 4: Content Cleaning & Extraction (`n8n-nodes-base.code`)
- **Name in Canvas**: `Content Cleaning & Extraction`
- **Language**: JavaScript
- **What it does**:
  - **Noise Removal**: Strips out `<script>`, `<style>`, `<nav>`, `<footer>`, `<header>`, and HTML comments.
  - **Structure Conversion**: Converts `<h1>`, `<h2>`, `<h3>` tags into clean Markdown headings (`#`, `##`, `###`) and converts `<li>` to Markdown bullets (`- `).
  - **Metadata Extraction**: Extracts the page `<title>` and `<link rel="canonical">` URL.
  - **Threshold Validation**: Checks that extracted readable text exceeds 30 characters. If content is empty or blocked, flags `status: "failed"`.

#### 5. Node 5: Callback POST / Dispatch (`n8n-nodes-base.httpRequest`)
- **Name in Canvas**: `Send Callback to FastAPI`
- **Method**: `POST`
- **URL**: `={{ $json.callback_url }}`
- **What it does**:
  - Transmits the cleaned text, metadata, and status back to the FastAPI backend at `/api/v1/ingestion/callback`.
  - Injects the `X-N8N-Callback-Secret` header for cryptographic authentication.
  - FastAPI then runs recursive chunking, generates embeddings, and indexes the document into ChromaDB.

---

### How to Use n8n in Test vs. Production Mode

| Mode | Webhook URL Format | How to Trigger |
| :--- | :--- | :--- |
| **Test Mode** | `https://<tenant>.app.n8n.cloud/webhook-test/...` | Must click the orange **"Listen for test event"** button in the n8n canvas before sending the request. |
| **Production Mode** | `https://<tenant>.app.n8n.cloud/webhook/...` | Must toggle the switch in the top-right corner from **Inactive** to **Active**. Runs continuously in the background. |

> **Note on Localhost with n8n Cloud**:  
> If using n8n Cloud with a local backend, n8n cannot directly reach `http://localhost:8000`. Use a tunneling tool such as [ngrok](https://ngrok.com/) (`ngrok http 8000`) and provide the public URL as the `callback_url`.

---

## ⚙️ 5. Environment Variables Reference (`.env`)

The application configuration is managed via Pydantic Settings and loaded from the root `.env` file.

| Variable Name | Default Value | Description |
| :--- | :--- | :--- |
| **Application Settings** | | |
| `APP_NAME` | `"Research Assistant with Persistent Memory"` | Name of the application displayed in logs and OpenAPI docs. |
| `APP_ENV` | `"development"` | Environment mode (`development` or `production`). |
| `DEBUG` | `true` | Enables verbose debug logging and auto-reload. |
| `PORT` | `8000` | Backend port number. |
| `HOST` | `"0.0.0.0"` | Host binding interface (`0.0.0.0` binds to all network interfaces). |
| `API_V1_PREFIX` | `"/api/v1"` | URL prefix for all REST API endpoints. |
| `SECRET_KEY` | `"[production-secret-key]"` | Internal secret key used for session signing and hashing. |
| `ALLOWED_ORIGINS` | `["*"]` | Allowed CORS origins for browser security. |
| **Vector Database (ChromaDB)** | | |
| `CHROMA_PERSIST_DIRECTORY`| `"./data/chromadb"` | Local directory where ChromaDB indexes are saved persistently. |
| `CHROMA_COLLECTION_SOURCES`| `"research_sources"`| Collection name storing high-level source metadata and content hashes. |
| `CHROMA_COLLECTION_CHUNKS` | `"research_chunks"` | Collection name storing chunk text embeddings and metadata. |
| **Embedding Configuration** | | |
| `EMBEDDING_PROVIDER` | `"fastembed"` | Embedding backend engine (`fastembed` for local ONNX, or `openai`). |
| `EMBEDDING_MODEL` | `"BAAI/bge-small-en-v1.5"` | Name of the pre-trained embedding model. |
| `EMBEDDING_DIMENSION` | `384` | Output vector dimension (must match the model dimension). |
| `EMBEDDING_BATCH_SIZE` | `32` | Number of text chunks vectorized in a single batch. |
| **Multi-LLM Router Configuration** | | |
| `PRIMARY_MODEL` | `"gemini/gemini-2.5-flash"` | Primary LLM used for answering questions. |
| `FALLBACK_MODEL_1` | `"zhipu/glm-4"` | First fallback LLM if primary model encounters rate limits or errors. |
| `FALLBACK_MODEL_2` | `"groq/llama-3.3-70b-versatile"`| Second fallback LLM for rapid disaster-recovery responses. |
| **API Keys** | | |
| `GEMINI_API_KEY` | `""` | Google AI Studio API key for Gemini models. |
| `ZHIPUAI_API_KEY` / `GLM_API_KEY` | `""` | Zhipu AI key for GLM-4 fallback. |
| `GROQ_API_KEY` | `""` | Groq Cloud API key for ultra-fast LLaMA 3.3. |
| `OPENAI_API_KEY` | `""` | Optional OpenAI key (used if `EMBEDDING_PROVIDER="openai"`). |
| **Chunking Configuration** | | |
| `CHUNK_SIZE` | `800` | Maximum character length of each semantic document chunk. |
| `CHUNK_OVERLAP` | `150` | Character overlap between consecutive chunks to preserve context. |
| **Retrieval Configuration** | | |
| `DEFAULT_TOP_K` | `5` | Number of most similar chunks retrieved per question. |
| `DEFAULT_SIMILARITY_THRESHOLD` | `0.15` | Minimum cosine similarity score required for a chunk to be accepted. |
| `MAX_TOP_K` | `20` | Hard cap on the maximum top-k chunks a client can request. |
| **n8n Automation & Webhooks** | | |
| `N8N_WEBHOOK_URL` | `"https://.../webhook/..."` | Target URL of your n8n workflow trigger. |
| `N8N_CALLBACK_SECRET` | `"production-n8n-secret..."` | Secret header (`X-N8N-Callback-Secret`) verifying n8n callbacks. |
| **Web Scraping & Ingestion** | | |
| `SCRAPER_USER_AGENT` | `"ResearchAssistantBot/1.0"`| User-Agent sent with scraping requests. |
| `SCRAPER_TIMEOUT_SECONDS` | `20` | Request timeout for web page fetching. |
| `SCRAPER_MAX_RETRIES` | `3` | Max retry attempts with exponential backoff on network failures. |
| `MAX_RESPONSE_SIZE_MB` | `10` | Maximum allowable HTML file download size. |
| `MAX_CONTENT_LENGTH` | `1000000` | Max character length of raw page content processed. |
| `MAX_REDIRECTS` | `5` | Maximum number of HTTP redirects followed. |
| `MAX_CONCURRENT_SCRAPES` | `5` | Semaphore limit for concurrent scraping operations. |
| **PDF Export Settings** | | |
| `PDF_EXPORT_DIR` | `"./data/exports"` | Output directory where generated research PDF reports are stored. |

---

## 🔌 6. API Endpoints Overview

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `POST` | `/api/v1/ingest` | Ingest single or batch URLs into the knowledge base. |
| `POST` | `/api/v1/chat` | Ask a research question with multi-source retrieval and citations. |
| `GET` | `/api/v1/sources` | List all indexed sources with chunk counts and status. |
| `GET` | `/api/v1/sources/{id}` | Get metadata for a specific indexed source. |
| `DELETE`| `/api/v1/sources/{id}` | Delete a source and remove all its vector chunks from ChromaDB. |
| `PUT` | `/api/v1/sources/{id}/refresh`| Re-scrape and re-index an existing source URL. |
| `POST` | `/api/v1/webhook/n8n` | Webhook endpoint receiving external URL lists from n8n. |
| `POST` | `/api/v1/ingestion/callback`| Secure callback endpoint receiving scraped data from n8n workflows. |
| `POST` | `/api/v1/export/pdf` | Generate and download a formatted PDF research report of a session. |
| `GET` | `/api/v1/health` | Comprehensive health check (ChromaDB, models, memory). |

---

## 🧪 Testing & Verification

Run the automated backend test suite:
```powershell
pytest Backend/src/tests/ -v
```

Run an end-to-end Python demo query:
```powershell
python demo_client.py
```
