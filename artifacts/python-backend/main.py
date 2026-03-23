"""
FastAPI backend for the Autonomous Energy Researcher Agent.
Manages research jobs, serves results, and interfaces with the Python AI pipeline.
"""

import logging
import os
import sys
import threading
import uuid
from datetime import datetime, timezone
from typing import Dict, Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(__file__))

from config.settings import API_HOST, API_PORT, CORS_ORIGINS
from agents.research_agent import ResearchAgent
from agents.analysis_agent import AnalysisAgent
from agents.summary_agent import SummaryAgent
from database.faiss_store import get_faiss_store
from database.storage import save_report, load_report, list_reports

# Configure structured logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
)
logger = logging.getLogger(__name__)

# ─── FastAPI App ──────────────────────────────────────────────────────
app = FastAPI(
    title="Autonomous Energy Researcher Agent",
    description="Multi-agent AI system for energy research",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── In-Memory Job Store ──────────────────────────────────────────────
# Maps job_id -> job status dict
_jobs: Dict[str, Dict] = {}
_jobs_lock = threading.Lock()


# ─── Pydantic Models ──────────────────────────────────────────────────
class ResearchRequest(BaseModel):
    query: str
    maxSources: int = 5


class SearchRequest(BaseModel):
    query: str
    topK: int = 3


# ─── Background Research Runner ───────────────────────────────────────
def run_research_pipeline(job_id: str, query: str, max_sources: int):
    """
    Run the full multi-agent research pipeline in a background thread.
    Updates job status throughout the process.
    """

    def update_progress(msg: str):
        with _jobs_lock:
            if job_id in _jobs:
                _jobs[job_id]["progress"] = msg

    try:
        with _jobs_lock:
            _jobs[job_id]["status"] = "running"
            _jobs[job_id]["progress"] = "Starting research pipeline..."

        # Agent 1: Research
        research_agent = ResearchAgent(max_sources=max_sources)
        research_data = research_agent.run(query, progress_callback=update_progress)

        # Agent 2: Analysis
        analysis_agent = AnalysisAgent()
        analysis_data = analysis_agent.run(
            query, research_data, progress_callback=update_progress
        )

        # Agent 3: Summary / Report Generation
        summary_agent = SummaryAgent()
        update_progress("✍️ Generating structured report with AI...")
        report = summary_agent.run(
            query, analysis_data, progress_callback=update_progress
        )

        # Save to local storage
        save_report(report)

        # Add to FAISS vector store
        update_progress("💾 Saving to knowledge repository...")
        faiss_store = get_faiss_store()
        faiss_store.add_report(report)

        # Mark job as complete
        with _jobs_lock:
            _jobs[job_id]["status"] = "completed"
            _jobs[job_id]["progress"] = "Research complete!"
            _jobs[job_id]["report"] = report
            _jobs[job_id]["completedAt"] = datetime.now(timezone.utc).isoformat()

        logger.info(f"Research job {job_id} completed successfully")

    except Exception as e:
        logger.error(f"Research job {job_id} failed: {e}", exc_info=True)
        with _jobs_lock:
            _jobs[job_id]["status"] = "failed"
            _jobs[job_id]["error"] = str(e)
            _jobs[job_id]["completedAt"] = datetime.now(timezone.utc).isoformat()


# ─── API Routes ───────────────────────────────────────────────────────

@app.get("/healthz")
def health_check():
    """Health check endpoint."""
    return {"status": "ok"}


@app.post("/research")
def start_research(req: ResearchRequest):
    """
    Start a new research job asynchronously.
    Returns a job ID that can be polled for status.
    """
    if not req.query or len(req.query.strip()) < 3:
        raise HTTPException(status_code=400, detail="Query must be at least 3 characters")

    job_id = str(uuid.uuid4())
    started_at = datetime.now(timezone.utc).isoformat()

    with _jobs_lock:
        _jobs[job_id] = {
            "jobId": job_id,
            "status": "pending",
            "query": req.query.strip(),
            "progress": "Queued...",
            "report": None,
            "error": None,
            "startedAt": started_at,
            "completedAt": None,
        }

    # Run pipeline in background thread
    thread = threading.Thread(
        target=run_research_pipeline,
        args=(job_id, req.query.strip(), req.maxSources),
        daemon=True,
    )
    thread.start()

    return {
        "jobId": job_id,
        "status": "pending",
        "message": f"Research job started for query: {req.query}",
    }


@app.get("/research/{job_id}")
def get_research_job(job_id: str):
    """Get the status and result of a research job."""
    with _jobs_lock:
        job = _jobs.get(job_id)

    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    return job


@app.get("/history")
def get_history():
    """Return a list of all stored research reports (summaries)."""
    reports = list_reports()
    return {"reports": reports, "total": len(reports)}


@app.get("/history/{report_id}")
def get_report(report_id: str):
    """Return a specific research report by ID."""
    report = load_report(report_id)
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    return report


@app.post("/search")
def semantic_search(req: SearchRequest):
    """Perform semantic search across stored research reports."""
    faiss_store = get_faiss_store()
    results = faiss_store.search(req.query, top_k=req.topK)

    return {
        "results": [
            {
                "reportId": r.get("report_id", ""),
                "query": r.get("query", ""),
                "title": r.get("title", ""),
                "score": r.get("score", 0.0),
                "snippet": r.get("snippet", ""),
                "createdAt": r.get("created_at", ""),
            }
            for r in results
        ],
        "total": len(results),
    }


# ─── Entry Point ──────────────────────────────────────────────────────
if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PYTHON_API_PORT", str(API_PORT)))
    logger.info(f"Starting Autonomous Energy Researcher Agent on port {port}")
    uvicorn.run(app, host=API_HOST, port=port, log_level="info")
