"""
FastAPI backend — Autonomous Energy Researcher Agent.
Models are preloaded at startup for fast first-request response.
"""

import logging
import os
import sys
import threading
import uuid
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from typing import Dict

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, field_validator

sys.path.insert(0, os.path.dirname(__file__))

from agents.research_agent import ResearchAgent
from agents.analysis_agent import AnalysisAgent
from agents.summary_agent import SummaryAgent
from database.faiss_store import get_faiss_store
from database.storage import save_report, load_report, list_reports
from config.settings import API_HOST, API_PORT

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
)
logger = logging.getLogger(__name__)


def _preload_models():
    """Lightweight mode — no heavy ML models."""
    try:
        logger.info("Skipping embedding + heavy model preload")
        from models.llm_model import load_model
        load_model()  # safe (you replaced it already)
    except Exception as e:
        logger.error(f"Startup issue: {e}")


@asynccontextmanager
async def lifespan(_app: FastAPI):
    threading.Thread(target=_preload_models, daemon=True).start()
    yield


app = FastAPI(title="Energy Researcher API", version="1.0.0", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory job store
_jobs: Dict[str, Dict] = {}
_lock = threading.Lock()


# ─── Request models ──────────────────────────────────────────────────
class ResearchRequest(BaseModel):
    query: str
    maxSources: int = 5

    @field_validator("query")
    @classmethod
    def query_not_empty(cls, v: str) -> str:
        v = v.strip()
        if len(v) < 3:
            raise ValueError("Query must be at least 3 characters")
        return v

    @field_validator("maxSources")
    @classmethod
    def clamp_sources(cls, v: int) -> int:
        return max(2, min(v, 8))


class SearchRequest(BaseModel):
    query: str
    topK: int = 3


# ─── Pipeline runner ─────────────────────────────────────────────────
def _run_pipeline(job_id: str, query: str, max_sources: int):
    def progress(msg: str):
        with _lock:
            if job_id in _jobs:
                _jobs[job_id]["progress"] = msg

    try:
        with _lock:
            _jobs[job_id]["status"] = "running"

        research_data = ResearchAgent(max_sources=max_sources).run(query, progress_cb=progress)
        analysis_data = AnalysisAgent().run(query, research_data, progress_cb=progress)

        progress("✍️ Generating structured report...")
        report = SummaryAgent().run(query, analysis_data, progress_cb=progress)

        save_report(report)

        progress("💾 Saving to knowledge base...")
        get_faiss_store().add_report(report)

        with _lock:
            _jobs[job_id].update(
                status="completed",
                progress="Done!",
                report=report,
                completedAt=datetime.now(timezone.utc).isoformat(),
            )
        logger.info(f"Job {job_id} completed")

    except Exception as e:
        logger.error(f"Job {job_id} failed: {e}", exc_info=True)
        with _lock:
            _jobs[job_id].update(
                status="failed",
                error=str(e),
                completedAt=datetime.now(timezone.utc).isoformat(),
            )


# ─── Routes ──────────────────────────────────────────────────────────
@app.get("/healthz")
def health():
    return {"status": "ok"}


@app.post("/research")
def start_research(req: ResearchRequest):
    job_id = str(uuid.uuid4())
    with _lock:
        _jobs[job_id] = {
            "jobId": job_id,
            "status": "pending",
            "query": req.query,
            "progress": "Queued...",
            "report": None,
            "error": None,
            "startedAt": datetime.now(timezone.utc).isoformat(),
            "completedAt": None,
        }
    threading.Thread(target=_run_pipeline, args=(job_id, req.query, req.maxSources), daemon=True).start()
    return {"jobId": job_id, "status": "pending", "message": f"Started: {req.query}"}


@app.get("/research/{job_id}")
def get_job(job_id: str):
    with _lock:
        job = _jobs.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job


@app.get("/history")
def get_history():
    reports = list_reports()
    return {"reports": reports, "total": len(reports)}


@app.get("/history/{report_id}")
def get_report(report_id: str):
    report = load_report(report_id)
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    return report


@app.post("/search")
def semantic_search(req: SearchRequest):
    store = get_faiss_store()
    raw = store.search(req.query, top_k=max(1, req.topK))
    return {
        "results": [
            {
                "reportId": r.get("report_id", ""),
                "query": r.get("query", ""),
                "title": r.get("title", ""),
                "score": round(float(r.get("score", 0)), 4),
                "snippet": r.get("snippet", ""),
                "createdAt": r.get("created_at", ""),
            }
            for r in raw
        ],
        "total": len(raw),
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=API_HOST, port=API_PORT, log_level="info")
