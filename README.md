# Autonomous Energy Researcher Agent

An AI-powered research assistant that autonomously searches the web, extracts content from multiple sources, analyzes the data using a multi-agent pipeline, and generates a structured research report — all using **free, open-source tools**.

---

## Project Structure

```
project/
├── artifacts/
│   ├── python-backend/          ← Python AI backend (FastAPI)
│   │   ├── main.py              ← FastAPI app entry point
│   │   ├── requirements.txt     ← Python dependencies
│   │   ├── agents/
│   │   │   ├── research_agent.py   ← Web search + scraping
│   │   │   ├── analysis_agent.py   ← Content filtering + key points
│   │   │   └── summary_agent.py    ← LLM report generation
│   │   ├── tools/
│   │   │   ├── search_tool.py      ← DuckDuckGo search
│   │   │   ├── scraper_tool.py     ← Concurrent BeautifulSoup scraper
│   │   │   └── embedding_tool.py   ← Sentence transformer embeddings
│   │   ├── database/
│   │   │   ├── faiss_store.py      ← FAISS vector database
│   │   │   └── storage.py          ← JSON file storage
│   │   ├── models/
│   │   │   └── llm_model.py        ← HuggingFace LLM (flan-t5-base)
│   │   ├── config/
│   │   │   └── settings.py         ← All configuration
│   │   └── data/                   ← Auto-created at runtime
│   │       ├── reports/            ← Stored research reports (JSON)
│   │       └── faiss_index/        ← FAISS vector index files
│   │
│   ├── api-server/              ← Node.js API proxy (Express)
│   │   └── src/
│   │       └── routes/
│   │           └── proxy.ts        ← Forwards /api/* to Python backend
│   │
│   └── energy-researcher/       ← React frontend (Vite)
│       └── src/
│           ├── pages/
│           │   ├── Home.tsx        ← Search input + history sidebar
│           │   ├── JobView.tsx     ← Live progress tracker
│           │   ├── ReportView.tsx  ← Full report display
│           │   └── Search.tsx      ← Semantic search page
│           └── components/
│               └── layout/
│                   ├── Sidebar.tsx
│                   └── AppLayout.tsx
```

---

## Prerequisites

Install these before proceeding:

| Tool | Version | Download |
|------|---------|----------|
| **Python** | 3.11+ | https://python.org/downloads |
| **Node.js** | 18+ | https://nodejs.org |
| **pnpm** | Latest | `npm install -g pnpm` |
| **Git** | Any | https://git-scm.com |

> **Note:** The first run downloads ~1 GB of AI model weights (HuggingFace models). After that, they are cached locally.

---

## Local Setup — Step by Step

### Step 1: Clone the repository

```bash
git clone <your-repo-url>
cd <project-folder>
```

---

### Step 2: Install Python dependencies

```bash
cd artifacts/python-backend

# Create a virtual environment (recommended)
python -m venv venv

# Activate it
# On macOS/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Install all packages
pip install -r requirements.txt
```

> This installs: FastAPI, sentence-transformers, transformers (HuggingFace), faiss-cpu, duckduckgo-search, beautifulsoup4, and others.

---

### Step 3: Install Node.js dependencies

Go back to the project root:

```bash
cd ../..   # back to project root
pnpm install
```

This installs dependencies for all three Node.js packages:
- `@workspace/api-server` — the Express proxy server
- `@workspace/energy-researcher` — the React frontend
- All shared libraries

---

### Step 4: Start the Python AI Backend

Open **Terminal 1**:

```bash
cd artifacts/python-backend

# Activate your virtual environment if not already active
source venv/bin/activate   # macOS/Linux
or: venv\Scripts\activate  (Windows)

# Start the backend
PYTHON_API_PORT=8000 python main.py #macOS/Linux
$env:PYTHON_API_PORT=8000; python main.py 
#windows
```

You should see:
```
Preloading models...
Embedding model loaded
LLM loaded successfully
All models ready
Uvicorn running on http://0.0.0.0:8000
```

> The first startup takes 30–60 seconds while AI models download and load. Subsequent startups are much faster (models are cached).

---

### Step 5: Start the Node.js API Server

Open **Terminal 2**:

```bash
# From project root
PYTHON_API_PORT=8000 pnpm --filter @workspace/api-server run dev #macOS/Linux
$env:PYTHON_API_PORT=8000; pnpm --filter @workspace/api-server run dev 
#windows
```

You should see:
```
Server listening on port 8080
```

---

### Step 6: Start the React Frontend

Open **Terminal 3**:

```bash
# From project root
pnpm --filter @workspace/energy-researcher run dev
```

You should see:
```
VITE ready in 600ms
Local: http://localhost:5173/
```

---

### Step 7: Open the app

Visit **http://localhost:5173** in your browser.

---

## Configuration (Optional)

Edit `artifacts/python-backend/config/settings.py` or set environment variables:

| Variable | Default | Description |
|----------|---------|-------------|
| `PYTHON_API_PORT` | `8000` | Port for the Python backend |
| `LLM_MODEL_NAME` | `google/flan-t5-base` | HuggingFace model to use |
| `LLM_MAX_NEW_TOKENS` | `256` | Max tokens generated per LLM call |
| `REQUEST_TIMEOUT` | `5` | Per-URL scraping timeout (seconds) |
| `MAX_CONTENT_LENGTH` | `1500` | Max characters extracted per webpage |
| `SCRAPER_MAX_WORKERS` | `5` | Concurrent scraping threads |

**To use a larger model** (better quality, slower):
```bash
LLM_MODEL_NAME=mistralai/Mistral-7B-Instruct-v0.2 python main.py
```
> Mistral-7B requires ~14 GB RAM. Use `google/flan-t5-base` (default) or `google/flan-t5-small` for low-memory systems.

---

## How It Works

```
User Query
  ↓
Research Agent    → DuckDuckGo search (8 results) + concurrent scraping (5 URLs)
  ↓
Analysis Agent    → Relevance filtering + key sentence extraction + references
  ↓
Summary Agent     → 2 LLM calls: (title + intro), (conclusion)
  ↓
Storage           → JSON file saved + FAISS embedding indexed
  ↓
Frontend          → Report with Title, Introduction, Insights, Conclusion, References
```

**Typical execution time:** 5–15 seconds per query  
**First run:** 30–90 seconds (model download + load)

---

## API Endpoints

The Python backend exposes these directly at `http://localhost:8000`:

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/healthz` | Health check |
| `POST` | `/research` | Start a research job `{"query": "...", "maxSources": 5}` |
| `GET` | `/research/{jobId}` | Poll job status and result |
| `GET` | `/history` | List all stored reports |
| `GET` | `/history/{reportId}` | Get a full report by ID |
| `POST` | `/search` | Semantic search `{"query": "...", "topK": 3}` |

The Node.js API server at port 8080 proxies all `/api/*` calls to the Python backend.

---

## Troubleshooting

**"Disk quota exceeded" during pip install**
```bash
pip cache purge
pip install --no-cache-dir -r requirements.txt
```

**DuckDuckGo returns 0 results**  
The search tool automatically retries 3 times with backoff. If it still fails, DuckDuckGo may be rate-limiting your IP. Wait 30 seconds and try again.

**Python backend 502/503 from Node server**  
Make sure the Python backend (Terminal 1) is running and listening on port 8000 before making API calls.

**"CUDA out of memory"**  
Set `LLM_DEVICE=cpu` or the model defaults to CPU automatically.

**Port already in use**  
Kill existing processes:
```bash
# macOS/Linux
kill -9 $(lsof -ti:8000)
kill -9 $(lsof -ti:8080)

# Windows
netstat -ano | findstr :8000
taskkill /PID <pid> /F
```

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| **AI / LLM** | `google/flan-t5-base` via HuggingFace Transformers |
| **Embeddings** | `sentence-transformers/all-MiniLM-L6-v2` |
| **Web Search** | DuckDuckGo (no API key) |
| **Web Scraping** | BeautifulSoup + requests (concurrent) |
| **Vector DB** | FAISS (local, in-memory + disk) |
| **Python API** | FastAPI + Uvicorn |
| **Node.js API** | Express 5 (proxy layer) |
| **Frontend** | React + Vite + Tailwind CSS |
| **State** | TanStack React Query (polling) |
