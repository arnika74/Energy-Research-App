"""
FAISS Vector Database for storing and searching research report embeddings.
Enables semantic similarity search across all stored research outputs.
"""

import json
import logging
import os
from typing import List, Dict, Optional, Tuple

import numpy as np
import faiss

from config.settings import FAISS_INDEX_PATH, METADATA_PATH
from tools.embedding_tool import embed_text, get_embedding_dimension

logger = logging.getLogger(__name__)


class FAISSStore:
    """
    Manages a FAISS index for semantic search over research reports.
    Uses cosine similarity (via normalized vectors + inner product).
    """

    def __init__(self):
        self.index: Optional[faiss.Index] = None
        self.metadata: List[Dict] = []
        self._initialize()

    def _initialize(self):
        """Load existing index or create a new one."""
        os.makedirs(os.path.dirname(FAISS_INDEX_PATH), exist_ok=True)

        if os.path.exists(FAISS_INDEX_PATH) and os.path.exists(METADATA_PATH):
            try:
                self._load()
                logger.info(f"Loaded FAISS index with {self.index.ntotal} vectors")
                return
            except Exception as e:
                logger.warning(f"Failed to load existing index: {e}, creating new one")

        self._create_new_index()

    def _create_new_index(self):
        """Create a fresh FAISS inner-product index (cosine sim with normalized vecs)."""
        dim = get_embedding_dimension()
        self.index = faiss.IndexFlatIP(dim)  # Inner product = cosine sim for L2-normed vecs
        self.metadata = []
        logger.info(f"Created new FAISS index (dim={dim})")

    def _load(self):
        """Load index and metadata from disk."""
        self.index = faiss.read_index(FAISS_INDEX_PATH)
        with open(METADATA_PATH, "r") as f:
            self.metadata = json.load(f)

    def _save(self):
        """Persist index and metadata to disk."""
        os.makedirs(os.path.dirname(FAISS_INDEX_PATH), exist_ok=True)
        faiss.write_index(self.index, FAISS_INDEX_PATH)
        with open(METADATA_PATH, "w") as f:
            json.dump(self.metadata, f, indent=2)

    def add_report(self, report: Dict) -> bool:
        """
        Embed and add a research report to the index.

        Args:
            report: Research report dict with id, query, title, introduction, etc.

        Returns:
            True if successfully added
        """
        try:
            # Create a rich text representation for embedding
            text_to_embed = self._report_to_text(report)
            embedding = embed_text(text_to_embed)

            # FAISS expects float32 2D array
            vector = np.array([embedding], dtype=np.float32)
            self.index.add(vector)

            # Store metadata for retrieval
            self.metadata.append(
                {
                    "report_id": report.get("id", ""),
                    "query": report.get("query", ""),
                    "title": report.get("title", ""),
                    "created_at": report.get("createdAt", ""),
                    "snippet": report.get("introduction", "")[:300],
                    "source_count": len(report.get("references", [])),
                }
            )

            self._save()
            logger.info(f"Added report to FAISS index: {report.get('id')}")
            return True

        except Exception as e:
            logger.error(f"Failed to add report to FAISS: {e}")
            return False

    def search(self, query: str, top_k: int = 3) -> List[Dict]:
        """
        Semantic search for similar research reports.

        Args:
            query: Search query string
            top_k: Number of top results to return

        Returns:
            List of dicts with report metadata and similarity scores
        """
        if self.index is None or self.index.ntotal == 0:
            return []

        try:
            query_embedding = embed_text(query)
            query_vector = np.array([query_embedding], dtype=np.float32)

            k = min(top_k, self.index.ntotal)
            distances, indices = self.index.search(query_vector, k)

            results = []
            for score, idx in zip(distances[0], indices[0]):
                if idx < 0 or idx >= len(self.metadata):
                    continue
                meta = self.metadata[idx].copy()
                meta["score"] = float(score)
                results.append(meta)

            return results

        except Exception as e:
            logger.error(f"FAISS search error: {e}")
            return []

    def _report_to_text(self, report: Dict) -> str:
        """Combine report fields into a single string for embedding."""
        parts = [
            report.get("query", ""),
            report.get("title", ""),
            report.get("introduction", ""),
            " ".join(report.get("keyInsights", [])),
            report.get("conclusion", ""),
        ]
        return " ".join(p for p in parts if p)

    @property
    def total_vectors(self) -> int:
        """Return the number of stored vectors."""
        return self.index.ntotal if self.index else 0


# Singleton instance
_faiss_store: Optional[FAISSStore] = None


def get_faiss_store() -> FAISSStore:
    """Get or create the singleton FAISS store."""
    global _faiss_store
    if _faiss_store is None:
        _faiss_store = FAISSStore()
    return _faiss_store
