"""Centralized configuration for the Autonomous Energy Researcher Agent."""

import os

# LLM
LLM_MODEL_NAME = os.getenv("LLM_MODEL_NAME", "google/flan-t5-base")
LLM_MAX_NEW_TOKENS = int(os.getenv("LLM_MAX_NEW_TOKENS", "256"))

# Embedding
EMBEDDING_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

# Scraper
REQUEST_TIMEOUT = int(os.getenv("REQUEST_TIMEOUT", "5"))
MAX_CONTENT_LENGTH = int(os.getenv("MAX_CONTENT_LENGTH", "1500"))
SCRAPER_MAX_WORKERS = int(os.getenv("SCRAPER_MAX_WORKERS", "5"))

# Storage
_HERE = os.path.dirname(__file__)
DATA_DIR = os.path.join(_HERE, "..", "data")
REPORTS_DIR = os.path.join(DATA_DIR, "reports")
FAISS_INDEX_DIR = os.path.join(DATA_DIR, "faiss_index")
FAISS_INDEX_PATH = os.path.join(FAISS_INDEX_DIR, "research.index")
METADATA_PATH = os.path.join(FAISS_INDEX_DIR, "metadata.json")

# API
API_HOST = "0.0.0.0"
API_PORT = int(os.getenv("PYTHON_API_PORT", "8000"))
