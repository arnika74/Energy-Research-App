
# Energy Research App

An AI-powered application that performs automated web research, analyzes content using a multi-agent pipeline, and generates structured reports.

The system mimics a research assistant by combining web search, scraping, analysis, and summarization into a single workflow.

---

## 🧰 Tech Stack

| Layer            | Technology                          |
| ---------------- | ----------------------------------- |
| Frontend         | React (Vite), Tailwind CSS          |
| Backend          | FastAPI (Python), Node.js (Express) |
| AI / LLM         | HuggingFace Transformers (Flan-T5)  |
| Embeddings       | Sentence Transformers               |
| Vector Database  | FAISS                               |
| Web Scraping     | BeautifulSoup, Requests             |
| Search Engine    | DuckDuckGo                          |
| Containerization | Docker, Docker Compose              |
| Cloud (Optional) | AWS                                 |
| Architecture     | Multi-Agent System                  |

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

## ⚙️ Prerequisites

| Tool    | Version |
| ------- | ------- |
| Python  | 3.11+   |
| Node.js | 18+     |
| pnpm    | Latest  |
| Docker  | Latest  |
| Git     | Any     |

---

# 🐳 Running with Docker (Recommended)

## Step 1: Clone Repository

```bash
git clone https://github.com/arnika74/Energy-Research-App.git
cd Energy-Research-App
```

---

## Step 2: Start All Services

```bash
docker compose up --build
```

---

## Step 3: Run in Background (Optional)

```bash
docker compose up -d --build
```

---

## 🌐 Application URLs

| Service        | URL                   |
| -------------- | --------------------- |
| Frontend       | http://localhost:3000 |
| API Server     | http://localhost:8080 |
| Python Backend | http://localhost:8000 |

---

## 🛑 Stop Application

```bash
docker compose down
```

## 🖥️ Local Setup — Step by Step

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

> This installs FastAPI, sentence-transformers, HuggingFace transformers, faiss-cpu, duckduckgo-search, beautifulsoup4, and other dependencies.

---

### Step 3: Install Node.js dependencies

```bash
cd ../..   # back to project root
pnpm install
```

This installs dependencies for:

* `@workspace/api-server` — Express proxy server
* `@workspace/energy-researcher` — React frontend
* Shared libraries

---

### Step 4: Start the Python AI Backend

Open **Terminal 1**:

```bash
cd artifacts/python-backend

# Activate environment (if not active)
source venv/bin/activate        # macOS/Linux
# OR
venv\Scripts\activate          # Windows

# Start backend
PYTHON_API_PORT=8000 python main.py     # macOS/Linux
# OR
$env:PYTHON_API_PORT=8000; python main.py   # Windows
```

You should see:

```
Preloading models...
Embedding model loaded
LLM loaded successfully
All models ready
Uvicorn running on http://0.0.0.0:8000
```

> First startup may take 30–60 seconds due to model loading.

---

### Step 5: Start the Node.js API Server

Open **Terminal 2**:

```bash
# From project root
PYTHON_API_PORT=8000 pnpm --filter @workspace/api-server run dev     # macOS/Linux
# OR
$env:PYTHON_API_PORT=8000; pnpm --filter @workspace/api-server run dev   # Windows
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
VITE ready
Local: http://localhost:5173/
```

---

### Step 7: Open the App

Visit:

👉 http://localhost:8000

---

## ⚠️ Common Issues

| Issue                         | Solution                      |
| ----------------------------- | ----------------------------- |
| Container name already exists | `docker rm -f python-backend` |
| Port already in use           | Kill process using port       |
| Old containers conflict       | `docker container prune`      |

---

## 🧠 How It Works

```
User Query
   ↓
Research Agent → Web search + scraping
   ↓
Analysis Agent → Filters and extracts key points
   ↓
Summary Agent → Generates final report using LLM
   ↓
Storage → Saves report + FAISS indexing
   ↓
Frontend → Displays results
```

---

## 🔌 API Endpoints

| Method | Endpoint       | Description     |
| ------ | -------------- | --------------- |
| GET    | /healthz       | Health check    |
| POST   | /research      | Start research  |
| GET    | /research/{id} | Get report      |
| GET    | /history       | List reports    |
| GET    | /history/{id}  | View report     |
| POST   | /search        | Semantic search |

---

## 📌 Notes

* First run may take time due to model download
* No external paid APIs required
* Works offline after initial setup

---

