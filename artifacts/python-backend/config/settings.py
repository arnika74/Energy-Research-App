"""
Configuration and settings for the Autonomous Energy Researcher Agent.
All configurable parameters are centralized here.
"""

import os

# ─── LLM Configuration ───────────────────────────────────────────────
# Primary model: mistralai/Mistral-7B-Instruct-v0.2
# Fallback model: google/flan-t5-base (lighter, faster)
LLM_MODEL_NAME = os.getenv("LLM_MODEL_NAME", "google/flan-t5-base")
LLM_MAX_NEW_TOKENS = int(os.getenv("LLM_MAX_NEW_TOKENS", "512"))
LLM_TEMPERATURE = float(os.getenv("LLM_TEMPERATURE", "0.7"))
LLM_DEVICE = os.getenv("LLM_DEVICE", "cpu")

# ─── Embedding Model ─────────────────────────────────────────────────
EMBEDDING_MODEL_NAME = os.getenv(
    "EMBEDDING_MODEL_NAME", "sentence-transformers/all-MiniLM-L6-v2"
)

# ─── Search Configuration ─────────────────────────────────────────────
MAX_SEARCH_RESULTS = int(os.getenv("MAX_SEARCH_RESULTS", "8"))
MAX_CONTENT_LENGTH = int(os.getenv("MAX_CONTENT_LENGTH", "3000"))
REQUEST_TIMEOUT = int(os.getenv("REQUEST_TIMEOUT", "10"))

# ─── Storage Configuration ────────────────────────────────────────────
DATA_DIR = os.getenv("DATA_DIR", os.path.join(os.path.dirname(__file__), "..", "data"))
REPORTS_DIR = os.path.join(DATA_DIR, "reports")
FAISS_INDEX_DIR = os.path.join(DATA_DIR, "faiss_index")
FAISS_INDEX_PATH = os.path.join(FAISS_INDEX_DIR, "research.index")
METADATA_PATH = os.path.join(FAISS_INDEX_DIR, "metadata.json")

# ─── API Configuration ────────────────────────────────────────────────
API_HOST = os.getenv("API_HOST", "0.0.0.0")
API_PORT = int(os.getenv("API_PORT", "8001"))
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "*").split(",")

# ─── Agent Configuration ──────────────────────────────────────────────
RESEARCH_AGENT_MAX_SOURCES = int(os.getenv("RESEARCH_AGENT_MAX_SOURCES", "5"))
SCRAPER_DELAY = float(os.getenv("SCRAPER_DELAY", "0.5"))
