"""
Sentence-transformer embeddings. Loaded once at startup and reused.
"""

import logging
from typing import List

import numpy as np

logger = logging.getLogger(__name__)

_model = None


def load_embedding_model() -> None:
    """Preload the embedding model. Call once at startup."""
    global _model
    if _model is not None:
        return
    from config.settings import EMBEDDING_MODEL_NAME
    from sentence_transformers import SentenceTransformer
    logger.info(f"Loading embedding model: {EMBEDDING_MODEL_NAME}")
    _model = SentenceTransformer(EMBEDDING_MODEL_NAME)
    logger.info("Embedding model loaded")


def _get_model():
    global _model
    if _model is None:
        load_embedding_model()
    return _model


def embed_text(text: str) -> np.ndarray:
    return _get_model().encode(text, convert_to_numpy=True, normalize_embeddings=True)


def embed_texts(texts: List[str]) -> np.ndarray:
    return _get_model().encode(
        texts, convert_to_numpy=True, normalize_embeddings=True,
        batch_size=32, show_progress_bar=False,
    )


def get_embedding_dimension() -> int:
    return _get_model().get_sentence_embedding_dimension()
