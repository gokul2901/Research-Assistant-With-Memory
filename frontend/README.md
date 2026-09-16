# Research Assistant with Persistent Memory — Frontend

> **"Drop URLs. Build knowledge. Ask anything."**

A commercial-grade, production-ready AI research interface engineered with **Next.js (App Router)**, **React**, **TypeScript**, **Tailwind CSS**, **Framer Motion**, **TanStack Query**, and **Lucide Icons**.

---

## 🏛️ Architecture & Highlights

### 1. Three-Zone Research Workspace (`/research`)
- **Left Zone (Sidebar)**: Real-time Knowledge Memory metrics (Total Indexed Sources, Vector Chunks in ChromaDB), Quick navigation, and Recent sources list.
- **Center Zone (Research Chat)**: Grounded AI conversation engine featuring auto-parsed inline citations (`[1]`, `[2]`), execution latency pills, model attribution, and prompt starters.
- **Right Zone (Evidence & Sources Panel)**: Interactive citation inspector displaying exact text passages, document titles, domains, cosine similarity references, and direct external links.

### 2. Knowledge Source Management (`/sources`)
- Comprehensive overview of all indexed knowledge URLs.
- Aggregate metrics: Total Sources, Indexed Chunks, Active Domains, and Failed Ingestions.
- In-memory search by title, domain, or URL with multi-status filters and sorting (Newest, Oldest, Most Chunks, A-Z).
- Source Refresh (re-scrape and update vector embeddings) and Source Deletion (permanent vector purge with confirmation modal).

### 3. Multi-URL Batch Ingestion Modal (`Add Knowledge`)
- Support for single URL entry or newline-separated batch pasting.
- Dynamic visual pipeline tracker reflecting actual backend stages:
  `QUEUED → FETCHING → CHUNKING → EMBEDDING → INDEXING → COMPLETED/FAILED`
- Force-refresh toggle to overwrite cached content hashes.

### 4. Zero-Hallucination Grounding Gate
- If query passages are not found in the persistent knowledge base, the system renders a dedicated **Source Coverage Check** card encouraging the user to index additional documentation rather than fabricating unsupported claims.

### 5. Research Sessions (`/sessions` & `/sessions/[id]`)
- Multi-turn research inquiries organized chronologically into *Today's Research*, *Yesterday*, and *Previous Research*.
- Client-side persistence synchronized with backend session history (`/api/v1/chat/history/{session_id}`).
- Session renaming and deletion.

### 6. PDF Intelligence Report Generation
- Direct integration with `/api/v1/export/pdf`.
- Backend generates the PDF containing session Q&As, source summary tables, and full citation references, followed by automatic browser download.

### 7. System Diagnostics & Appearance (`/settings`)
- Health probes checking vectorstore status (`connected`/`degraded`), active primary LLM (Gemini 1.5 Flash), and fallback hierarchy (GLM-4, Groq/Mistral).
- Seamless Dark Mode (primary) and Light Mode toggles.

---

## 🚀 Quickstart & Connecting Frontend to Backend

### 1. Start the FastAPI Backend
From the project root:
```bash
# Activate virtual environment if configured
python main.py
```
Backend will start on: **`http://127.0.0.1:8000`**

### 2. Configure Environment Variables
Inside `frontend/.env.local`:
```env
NEXT_PUBLIC_API_BASE_URL=http://127.0.0.1:8000
```

### 3. Start the Next.js Development Server
```bash
cd frontend
npm run dev
```
Open **`http://localhost:3000`** in your browser.

### 4. Build for Production
```bash
cd frontend
npm run build
npm run start
```

---

## 📁 Frontend Directory Structure

```
frontend/
├── .env.local
├── .env.example
├── package.json
├── tsconfig.json
└── src/
    ├── types/
    │   └── index.ts               # Strict TypeScript API contracts
    ├── api/
    │   ├── client.ts              # Axios instance & error interceptors
    │   ├── sources.ts             # Source CRUD & statistics
    │   ├── ingest.ts              # Batch URL ingestion
    │   ├── chat.ts                # Grounded Q&A & session history
    │   ├── export.ts              # PDF intelligence report export
    │   └── health.ts              # Health & vectorstore diagnostics
    ├── hooks/
    │   ├── useSources.ts          # React Query hooks for sources
    │   ├── useChat.ts             # React Query hooks for chat & citations
    │   ├── useSessions.ts         # Session helpers
    │   ├── useHealth.ts           # Diagnostic polling hook
    │   └── useExport.ts           # PDF report trigger & download hook
    ├── context/
    │   ├── ThemeContext.tsx       # Dark / Light theme provider
    │   └── ResearchContext.tsx    # Active session, citation selection, modals
    ├── components/
    │   ├── layout/
    │   │   ├── Navbar.tsx         # Top bar with stats & theme toggle
    │   │   ├── Sidebar.tsx        # Left knowledge memory sidebar
    │   │   ├── MobileNav.tsx      # Mobile bottom bar
    │   │   └── AppShell.tsx       # Master layout frame
    │   ├── research/
    │   │   ├── ResearchChat.tsx   # Central chat workspace
    │   │   ├── ChatMessage.tsx    # Grounded message bubble with inline citations
    │   │   ├── QuestionInput.tsx  # Natural language prompt bar & RAG tuner
    │   │   ├── CitationMarker.tsx # Interactive clickable citation badge [1]
    │   │   ├── EvidencePanel.tsx  # Right zone evidence passage viewer
    │   │   └── NotFoundCoverage.tsx # Anti-hallucination coverage banner
    │   ├── sources/
    │   │   ├── SourceList.tsx     # Filterable, sortable sources grid
    │   │   ├── SourceCard.tsx     # Source metadata card with refresh/delete
    │   │   ├── AddSourceModal.tsx # Multi-URL ingestion & pipeline progress
    │   │   └── DeleteSourceDialog.tsx # Permanent deletion confirmation
    │   ├── sessions/
    │   │   ├── SessionList.tsx    # Categorized sessions overview
    │   │   └── SessionCard.tsx    # Session metadata & rename/delete actions
    │   └── ui/
    │       ├── Button.tsx
    │       ├── Badge.tsx
    │       ├── Modal.tsx
    │       ├── Skeleton.tsx
    │       ├── EmptyState.tsx
    │       └── Tooltip.tsx
    └── app/
        ├── layout.tsx             # Root layout with fonts & providers
        ├── globals.css            # Dark glass design system & custom scrollbars
        ├── page.tsx               # Landing & visual pipeline page
        ├── research/page.tsx      # 3-zone Research Workspace
        ├── sources/page.tsx       # Knowledge Sources Manager
        ├── sessions/page.tsx      # Sessions Overview
        ├── sessions/[id]/page.tsx # Individual Session Deep Dive
        └── settings/page.tsx      # Diagnostics & Appearance
```
