# Autonomous Energy Researcher Agent

## Overview

A full-stack AI-powered research system using a multi-agent architecture. Users enter an energy-related query, and autonomous AI agents search the web, extract content, analyze data, generate structured reports, and store them in a FAISS vector knowledge base.

## Architecture

```
User Query
  → Research Agent (DuckDuckGo search + web scraping)
  → Analysis Agent (content filtering + key point extraction)
  → Summary Agent (LLM report generation)
  → FAISS Knowledge Repository + Local JSON storage
  → React Frontend
```

## Tech Stack

### Frontend
- **React + Vite** — `artifacts/energy-researcher/`
- **Tailwind CSS** + shadcn/ui components
- **TanStack React Query** for data fetching and polling
- **Wouter** for client-side routing
- **Framer Motion** for animations

### Node.js API Server
- **Express 5** — `artifacts/api-server/`
- Acts as reverse proxy, forwarding `/api/research`, `/api/history`, `/api/search` to the Python backend
- Zod validation via generated OpenAPI schemas

### Python AI Backend
- **FastAPI** — `artifacts/python-backend/`
- Runs on port 8000 (PYTHON_API_PORT env var)
- **LLM**: `google/flan-t5-base` via HuggingFace Transformers (CPU, free)
- **Embeddings**: `sentence-transformers/all-MiniLM-L6-v2`
- **Vector DB**: FAISS (cosine similarity search)
- **Web Search**: DuckDuckGo (no API key required)
- **Web Scraping**: BeautifulSoup + requests

## Python Backend Structure

```
artifacts/python-backend/
├── main.py                    # FastAPI app entry point
├── requirements.txt           # Python dependencies
├── agents/
│   ├── research_agent.py      # Web search + content extraction
│   ├── analysis_agent.py      # Content filtering + key point extraction
│   └── summary_agent.py       # LLM report generation
├── tools/
│   ├── search_tool.py         # DuckDuckGo search
│   ├── scraper_tool.py        # BeautifulSoup web scraping
│   └── embedding_tool.py      # Sentence transformer embeddings
├── database/
│   ├── faiss_store.py         # FAISS vector store
│   └── storage.py             # JSON file storage for reports
├── models/
│   └── llm_model.py           # HuggingFace model loader
├── config/
│   └── settings.py            # Centralized configuration
└── data/
    ├── reports/               # Stored research reports (JSON)
    └── faiss_index/           # FAISS index files
```

## Running Workflows

- **Python AI Backend**: `cd artifacts/python-backend && python main.py` (port 8000)
- **API Server**: `pnpm --filter @workspace/api-server run dev` (port 8080, proxied)
- **Frontend**: `pnpm --filter @workspace/energy-researcher run dev` (port 19334, proxied to `/`)

## API Endpoints

All endpoints are available at `/api`:
- `GET /api/healthz` — Health check
- `POST /api/research` — Start a research job `{query, maxSources?}`
- `GET /api/research/:jobId` — Poll job status + report
- `GET /api/history` — List all stored reports
- `GET /api/history/:reportId` — Get full report
- `POST /api/search` — Semantic search `{query, topK?}`

## Key Rules

- Do NOT use OpenAI or paid APIs — only free HuggingFace models
- Python backend must be running for research to work
- FAISS index stored at `artifacts/python-backend/data/faiss_index/`
- Reports stored at `artifacts/python-backend/data/reports/`
- Change LLM model via `LLM_MODEL_NAME` env var (default: `google/flan-t5-base`)
